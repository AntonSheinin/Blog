# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=maybe-no-member

import datetime
from abc import ABC
from pydantic import EmailStr, Field, BaseModel
from redis_om import EmbeddedJsonModel, Migrator
from .db_connectors import redis_data


class RedisBaseModel(EmbeddedJsonModel, ABC):
    class Meta:
        database = redis_data


class User(RedisBaseModel):
    first_name: str = Field(index=True, full_text_search=True)
    last_name: str = Field(index=True, full_text_search=True)
    email: EmailStr = Field(index=True, full_text_search=True)
    password: str = Field(min_length = 8)
    signup_date: datetime.date = Field(default = datetime.date.today())
    blogs: list[str] = Field(default_factory = list)
    posts: list[str] = Field(default_factory = list)
    likes: list[str] = Field(default_factory = list)


class Blog(RedisBaseModel):
    author: str = Field(index=True, full_text_search=True, default = None)
    title: str = Field(index=True, full_text_search=True)
    creation_date: datetime.date = Field(default = datetime.date.today())
    posts: list[str] = Field(default_factory=list)


class BlogPost(RedisBaseModel):
    author: str = Field(index=True, full_text_search=True, default = None)
    content: str = Field(index=True, full_text_search=True, max_length = 1000)
    blog: str = Field(index=True, full_text_search=True)
    creation_date: datetime.date = Field(default = datetime.date.today())
    likes: list[str] = Field(default_factory=list)


class Like(RedisBaseModel):
    author: str = Field(index=True, full_text_search=True, default = None)
    post: str = Field(index=True, full_text_search=True)
    creation_date: datetime.date = Field(default = datetime.date.today())


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None


Migrator().run()
