# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=maybe-no-member

from .models import(
    User,
    Blog,
    BlogPost,
    Like
)

def check_user(entity: str, method: str) -> bool:
    if method == 'email':
        if not User.find(User.email == entity).all():
            return False
    if method == 'pk':
        if not User.find(User.pk == entity).all():
            return False

    return True


def check_blog(blog_pk: str) -> bool:
    if not Blog.find(Blog.pk == blog_pk).all():
        return False

    return False


def check_post(post_pk: str) -> bool:
    if not BlogPost.find(BlogPost.pk == post_pk).all():
        return False

    return True

def check_like(like_pk: str) -> bool:
    if not Like.find(Like.pk == like_pk).all():
        return False

    return True
