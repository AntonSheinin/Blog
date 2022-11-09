"""
    Main module

    Entrypoint and API endpoints
"""


from datetime import datetime
import logging
from typing import Any
from fastapi_cache.backends.redis import RedisBackend
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache
from fastapi import HTTPException, status, Depends, FastAPI
from pydantic import ValidationError


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
        raise HTTPException(
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail = "user email already exists"
        )

    try:
        user = User(
            first_name = body['first_name'].strip(),
            last_name = body['last_name'].strip(),
            email = body['email'],
            password = get_hashed_password(body['password'])
        )

        logger.info('created user: %s', user.pk)

    except ValidationError:
        return

    return user.save()


@app.post('/login')
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    """
        Authentication of user
    """

    if not User.find(User.email == form_data.username).all():
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Incorrect email or password"
        )

    user = User.find(User.email == form_data.username).all()[0]

    hashed_pass = user.password

    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Incorrect email or password"
        )

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
async def update_user(body: dict, logged_user: User = Depends(get_current_user)) -> User | Any:
    """
        Updating logged user data
    """

    try:
        logged_user.first_name = body["first_name"].strip()
        logged_user.last_name = body["last_name"].strip()
        
        logger.info('user %s updated', logged_user.pk)

        return logged_user.update_save()

    except ValidationError:
        return


@app.delete("/delete-me")
async def delete_user(logged_user: User = Depends(get_current_user)) -> dict:
    """
        Deleting logged user
    """

    logger.info('user %s deleted', logged_user.pk)

    User.delete(logged_user.pk)

    return {"success": "user deleted successfully"}


@app.post("/create-blog")
async def create_blog(body: dict, logged_user: User = Depends(get_current_user)) -> User | Any:
    """
        Creating new blog, author will be the logged user
    """

    try:
        blog = Blog(title = body['title'].strip(), author = logged_user.pk)

        logged_user.blogs.append(blog.pk)
        logged_user.update_save()

        logger.info('user %s created blog %s', logged_user.pk, blog.pk)

        return blog.save()

    except ValidationError:
        return


@app.get("/blogs/{blog_pk}")
@cache(expire=10)
async def get_blog(blog_pk: str) -> Blog:
    """
        Getting blog
    """
    if not Blog.is_exist(blog_pk):
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Blog not found"
        )

    logger.info('getting blog: %s', blog_pk)

    return Blog.get(blog_pk)


@app.put("/blogs/{blog_pk}")
async def update_blog(blog_pk: str, body: dict, logged_user: User = Depends(get_current_user)) -> User | Any:
    """
        Updating the blog that belongs to the logger user
    """

    if not Blog.is_exist(blog_pk):
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Blog not found"
        )

    if blog_pk not in logged_user.blogs:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Someone else's blog"
        )

    blog = Blog.get(blog_pk)

    try:
        blog.title = body["title"].strip()
        
        logger.info('blog %s updated', blog.pk)

        return blog.update_save()

    except ValidationError:
        return


@app.delete("/blogs/{blog_pk}")
async def delete_blog(blog_pk: str, logged_user: User = Depends(get_current_user)) -> dict:
    """
        Deleting the blog that belongs to the logged user
     """

    if not Blog.is_exist(blog_pk):
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Blog not found"
        )

    blog = Blog.get(blog_pk)

    if blog.author != logged_user.pk:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Someone else's blog"
        )

    if blog.posts:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "blog not empty"
        )

    Blog.delete(blog_pk)

    logger.info('blog %s deleted', blog_pk)

    logged_user.blogs.remove(blog_pk)
    logged_user.update_save()
    
    return {"success": "blog deleted successfully"}


@app.get("/")
@cache(expire=10)
async def blog_list() -> list:
    """
        Getting the blog list
    """
    logger.info('getting the blog list')

    return Blog.all_pks()


@app.post("/create-post/{blog_pk}")
async def create_post(blog_pk: str, body: dict, logged_user: User = Depends(get_current_user)) -> BlogPost | Any:
    """
        Creating the post in the blog that belongs to the logged user
    """

    if not Blog.is_exist(blog_pk):
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Blog not found"
        )

    if blog_pk not in logged_user.blogs:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Someone else's blog"
        )

    try:
        post = BlogPost(content = body['content'].strip(), author = logged_user.pk, blog = blog_pk)

        logged_user.posts.append(post.pk)
        logged_user.update_save()

        blog = Blog.get(blog_pk)
        blog.posts.append(post.pk)
        blog.update_save()

        logger.info('post %s created in blog %s', post.pk, blog.pk)

        return post.save()

    except ValidationError:
        return


@app.put("/posts/{post_pk}")
async def update_post(post_pk: str, body: dict, logged_user: User = Depends(get_current_user)) -> BlogPost | Any:
    """
        Updating the post in the blog that belongs to the logged user
    """

    if not BlogPost.is_exist(post_pk):
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Post not found"
        )

    if post_pk not in logged_user.posts:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Someone else's post"
        )

    post = BlogPost.get(post_pk)

    try:
        post.content = body["content"].strip()
        
        logger.info('post %s updated', post.pk)

        return post.update_save()

    except ValidationError:
        return


@app.delete("/posts/{post_pk}")
async def delete_post(post_pk: str, logged_user: User = Depends(get_current_user)) -> dict:
    """
        Deleting the post that belongs to the logged user
    """

    if not BlogPost.is_exist(post_pk):
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Post not found"
        )

    post = BlogPost.get(post_pk)

    if post.author != logged_user.pk:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "Someone else's post"
        )

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

    return {"success": "post deleted successfully"}


@app.post("/create-like/{post_pk}")
async def create_like(post_pk: str, logged_user: User = Depends(get_current_user)) -> BlogPost | Any:
    """
        Creating like for the post
    """

    if not BlogPost.is_exist(post_pk):
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Post not found"
        )

    try:
        post = BlogPost.get(post_pk)
        like = Like(post = post_pk, author = logged_user.pk)

        logged_user.likes.append(like.pk)
        logged_user.update_save()

        post.likes.append(like.pk)
        post.update_save()

        logger.info('like %s created for post %s', like.pk, post.pk)

        return like.save()

    except ValidationError:
        return


@app.delete("/likes/{like_pk}")
async def delete_like(like_pk: str, logged_user: User = Depends(get_current_user)) -> dict:
    """
        Deleting the like that belongs to the logged user
    """

    if not Like.is_exist(like_pk):
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Like not found"
        )

    like = Like.get(like_pk)

    if like.author != logged_user.pk:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Someone else's like"
        )

    post = BlogPost.get(like.post)
    post.likes.remove(like.pk)
    post.update_save()

    logged_user.likes.remove(like.pk)
    logged_user.update_save()

    Like.delete(like_pk)

    logger.info('like %s deleted', like_pk)

    return {"success": "like deleted successfully"}
