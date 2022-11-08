import datetime
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


@app.post("/signup")
async def create_user(body: User) -> User | Any:
    """
        Creating new user
    """

    if not User.find(User.email == body.email).all():
        raise HTTPException(
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail = "user email already exists"
        )

    try:
        user = User(
            first_name = body.first_name.strip(),
            last_name = body.last_name.strip(),
            email = body.email,
            password = get_hashed_password(body.password)
        )

    except ValidationError:
        return

    return user.save()


@app.post('/login')
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    """
        Authentification of user
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

    return user


@app.put("/users/{user_pk}")
async def update_user(user_pk: str, body: dict, logged_user: User = Depends(get_current_user)) -> User | Any:
    """
        Updating logged user data
    """

    if not User.is_exist(user_pk):
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found"
        )

    if user_pk != logged_user.pk:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Someone else's user"
        )

    user = User.get(user_pk)

    try:
        user.first_name = body["first_name"].strip()
        user.last_name = body["last_name"].strip()
        user.last_update = datetime.date.today()

        return user.save()

    except ValidationError:
        return


@app.delete("/users/{user_pk}")
async def delete_user(user_pk: str, logged_user: User = Depends(get_current_user)) -> dict:
    """
        Deleting logged user
    """


    if not User.is_exist(user_pk):
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found"
        )

    if user_pk != logged_user.pk:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Someone else's user"
        )

    User.delete(user_pk)

    return {"success": "user deleted successfully"}


@app.post("/create-blog")
async def create_blog(body: Blog, logged_user: User = Depends(get_current_user)) -> User | Any:
    """
        Creating new blog, author will be the logged user
    """

    try:
        blog = Blog(title = body.title.strip(), author = logged_user.pk)
        logged_user.blogs.append(blog.pk)
        logged_user.save()

        return blog.save()

    except ValidationError:
        return


@app.get("/blogs/{blog_pk}")
@cache(expire=60)
async def get_blog(blog_pk: str) -> Blog:
    """
        Getting blog
    """
    if not Blog.is_exist(blog_pk):
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Blog not found"
        )

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
        blog.last_update = datetime.date.today()

        return blog.save()

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

    if Blog.get(blog_pk).author != logged_user.pk:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Someone else's blog"
        )

    Blog.delete(blog_pk)

    return {"success": "blog deleted successfully"}


@app.get("/")
@cache(expire=10)
async def blog_list() -> list:
    """
        Getting the blog list
    """
    return Blog.all_pks()


@app.post("/create-post")
async def create_post(body: BlogPost, logged_user: User = Depends(get_current_user)) -> BlogPost | Any:
    """
        Creating the post in the blog that belongs to the logged user
    """

    if not Blog.is_exist(body.blog_pk):
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Blog not found"
        )

    if body.blog_pk not in logged_user.blogs:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Someone else's blog"
        )

    try:
        post = BlogPost(content = body.content.strip(), author = logged_user.pk, blog = body.blog)

        logged_user.posts.append(post.pk)
        logged_user.save()

        blog = Blog.get(body.blog)
        blog.posts.append(post.pk)
        blog.save()

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
        post.last_update = datetime.date.today()

        return post.save()

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

    if BlogPost.get(post_pk).author != logged_user.pk:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "Someone else's post"
        )

    BlogPost.delete(post_pk)

    return {"success": "post deleted successfully"}


@app.post("/create-like")
async def create_like(body: Like, logged_user: User = Depends(get_current_user)) -> BlogPost | Any:
    """
        Creating like for the post
    """

    if not BlogPost.is_exist(body.post):
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Post not found"
        )

    try:
        post = BlogPost.get(body.post)
        like = Like(post = body.post, author = logged_user.pk)

        logged_user.likes.append(like.pk)
        post.likes.append(like.pk)

        logged_user.save()
        post.save()

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

    if Like.get(like_pk).author != logged_user.pk:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Someone else's like"
        )

    Like.delete(like_pk)

    return {"success": "like deleted successfully"}
