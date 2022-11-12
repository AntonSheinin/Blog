"""
    Main module

    Entrypoint and API endpoints
"""


import logging
from typing import Any
from fastapi_cache.backends.redis import RedisBackend
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache
from fastapi import Depends, FastAPI
from pydantic import ValidationError

from .errors import error_handling

from .models import (
    User,
    Blog,
    BlogPost,
    Like
)

from .auth import (
    get_hashed_password,
    create_access_token,
    create_refresh_token,
    verify_password,
    get_current_user
)

from .db_connectors import redis_cache


FastAPICache.init(RedisBackend(redis_cache), prefix="fastapi-cache")

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.post("/signup")
async def create_user(body: dict) -> User | Any:
    """
        Creating new user
    """

    if User.find(User.email == body['email']).all():
        error_handling('validation_error', 'email already exists')

    try:
        user = User(
            first_name = body['first_name'],
            last_name = body['last_name'],
            email = body['email'],
            password = body['password']
        )
        user.hash_pass = get_hashed_password(body['password'])
        user.password = None
        user.save()

    except ValidationError as validation_error:
        error_handling('validation_error', str(validation_error))

    logger.info('created user: %s', user.pk)
    return user


@app.post('/login')
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    """
        Authentication of user
    """

    if not User.find(User.email == form_data.username).all():
        error_handling('bad_request', 'email not found')

    user = User.find(User.email == form_data.username).all()[0]

    if not verify_password(form_data.password, user.hash_pass):
        error_handling('bad_request', 'incorrect email or password')

    logger.info('user %s logged in', user.pk)

    return {
        "access_token": create_access_token(user.email),
        "refresh_token": create_refresh_token(user.email)
    }


@app.get('/me')
@cache(expire=10)
async def get_current_user_data(user: User = Depends(get_current_user)) -> User:
    """
        Get logged user data
    """

    logger.info('logged user: %s', user.pk)

    return user


@app.put("/update-me")
async def update_user(body: dict, logged_user: User = Depends(get_current_user)) -> User:
    """
        Updating logged user data
    """

    logged_user.first_name = body["first_name"]
    logged_user.last_name = body["last_name"]

    try:
        logged_user.update_save()

    except ValidationError as validation_error:
        error_handling('validation_error', str(validation_error))

    logger.info('user %s updated', logged_user.pk)
    return logged_user


@app.delete("/delete-me")
async def delete_user(logged_user: User = Depends(get_current_user)) -> dict:
    """
        Deleting logged user
    """

    logger.info('user %s deleted', logged_user.pk)

    User.delete(logged_user.pk)

    return {"success": f"user {logged_user.pk} deleted successfully"}


@app.post("/create-blog")
async def create_blog(body: dict, logged_user: User = Depends(get_current_user)) -> Blog:
    """
        Creating new blog, author will be the logged user
    """

    try:
        blog = Blog(title = body['title'].strip(), author = logged_user.pk)
        blog.save()

    except ValidationError as validation_error:
        error_handling('validation_error', str(validation_error))

    logged_user.blogs.append(blog.pk)
    logged_user.update_save()

    logger.info('user %s created blog %s', logged_user.pk, blog.pk)

    return blog


@app.get("/blogs/{blog_pk}")
@cache(expire=10)
async def get_blog(blog_pk: str) -> Blog:
    """
        Getting blog
    """
    if not Blog.is_exist(blog_pk):
        error_handling('not_found', 'blog not found')

    logger.info('getting blog: %s', blog_pk)

    return Blog.get(blog_pk)


@app.put("/blogs/{blog_pk}")
async def update_blog(blog_pk: str, body: dict, logged_user: User = Depends(get_current_user)) -> Blog:
    """
        Updating the blog that belongs to the logger user
    """

    if not Blog.is_exist(blog_pk):
        error_handling('not_found', 'blog not found')

    if blog_pk not in logged_user.blogs:
        error_handling('unauthorized', "Someone else's blog")

    blog = Blog.get(blog_pk)

    try:
        blog.title = body["title"].strip()
        blog.update_save()

    except ValidationError as validation_error:
        error_handling('validation_error', str(validation_error))

    logger.info('blog %s updated', blog.pk)

    return blog


@app.delete("/blogs/{blog_pk}")
async def delete_blog(blog_pk: str, logged_user: User = Depends(get_current_user)) -> dict:
    """
        Deleting the blog that belongs to the logged user
     """

    if not Blog.is_exist(blog_pk):
        error_handling('not_found', 'blog not found')

    blog = Blog.get(blog_pk)

    if blog.author != logged_user.pk:
        error_handling('unauthorized', "Someone else's blog")

    if blog.posts:
        error_handling('forbidden', 'blog not empty')

    Blog.delete(blog_pk)

    logger.info('blog %s deleted', blog_pk)

    logged_user.blogs.remove(blog_pk)
    logged_user.update_save()

    return {"success": f"blog {blog_pk} deleted successfully"}


@app.get("/")
@cache(expire=10)
async def blog_list() -> list:
    """
        Getting the blog list
    """
    logger.info('getting the blog list')

    return Blog.all_pks()


@app.post("/create-post/{blog_pk}")
async def create_post(blog_pk: str, body: dict, logged_user: User = Depends(get_current_user)) -> BlogPost:
    """
        Creating the post in the blog that belongs to the logged user
    """

    if not Blog.is_exist(blog_pk):
        error_handling('not_found', 'blog not found')

    if blog_pk not in logged_user.blogs:
        error_handling('unauthorized', "Someone else's blog")

    try:
        post = BlogPost(content = body['content'].strip(), author = logged_user.pk, blog = blog_pk)
        post.save()

    except ValidationError as validation_error:
        error_handling('validation_error', str(validation_error))

    blog = Blog.get(blog_pk)
    blog.posts.append(post.pk)
    blog.update_save()

    logged_user.posts.append(post.pk)
    logged_user.update_save()

    logger.info('post %s created in blog %s', post.pk, blog.pk)

    return post


@app.put("/posts/{post_pk}")
async def update_post(post_pk: str, body: dict, logged_user: User = Depends(get_current_user)) -> BlogPost:
    """
        Updating the post in the blog that belongs to the logged user
    """

    if not BlogPost.is_exist(post_pk):
        error_handling('not_found', 'post not found')

    if post_pk not in logged_user.posts:
        error_handling('unauthorized', "Someone else's post")

    post = BlogPost.get(post_pk)

    try:
        post.content = body["content"].strip()
        post.update_save()

    except ValidationError as validation_error:
        error_handling('validation_error', str(validation_error))

    logger.info('post %s updated', post.pk)
    return post


@app.delete("/posts/{post_pk}")
async def delete_post(post_pk: str, logged_user: User = Depends(get_current_user)) -> dict:
    """
        Deleting the post that belongs to the logged user
    """

    if not BlogPost.is_exist(post_pk):
        error_handling('not_found', 'post not found')

    post = BlogPost.get(post_pk)

    if post.author != logged_user.pk:
        error_handling('unauthorized', "Someone else's post")

    blog = Blog.get(post.blog)

    logged_user.posts.remove(post.pk)
    logged_user.update_save()

    for like_pk in post.likes:
        like = Like.get(like_pk)
        user = User.get(like.author)
        user.likes.remove(like.pk)
        user.update_save()
        Like.delete(like.pk)

    blog.posts.remove(post.pk)
    blog.update_save()

    BlogPost.delete(post_pk)

    logger.info('post %s deleted', post_pk)

    return {"success": f"post {post_pk} deleted successfully"}


@app.post("/create-like/{post_pk}")
async def create_like(post_pk: str, logged_user: User = Depends(get_current_user)) -> Like:
    """
        Creating like for the post
    """

    if not BlogPost.is_exist(post_pk):
        error_handling('not_found', 'post not found')

    post = BlogPost.get(post_pk)

    try:
        like = Like(post = post_pk, author = logged_user.pk)
        like.save()

    except ValidationError as validation_error:
        error_handling('validation_error', str(validation_error))

    logged_user.likes.append(like.pk)
    logged_user.update_save()

    post.likes.append(like.pk)
    post.update_save()

    logger.info('like %s created for post %s', like.pk, post.pk)

    return like


@app.delete("/likes/{like_pk}")
async def delete_like(like_pk: str, logged_user: User = Depends(get_current_user)) -> dict:
    """
        Deleting the like that belongs to the logged user
    """

    if not Like.is_exist(like_pk):
        error_handling('not_found', 'like not found')

    like = Like.get(like_pk)

    if like.author != logged_user.pk:
        error_handling('unauthorized', "Someone else's like")

    post = BlogPost.get(like.post)
    post.likes.remove(like.pk)
    post.update_save()

    logged_user.likes.remove(like.pk)
    logged_user.update_save()

    Like.delete(like_pk)

    logger.info('like %s deleted', like_pk)

    return {"success": f"like {like_pk} deleted successfully"}
