# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=maybe-no-member

import datetime
from abc import ABC
from pydantic import EmailStr, Field, BaseModel
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis_om import EmbeddedJsonModel, Field, Migrator, get_redis_connection
import aioredis


REDIS_HOST = 'redis-data'
REDIS_URL = 'redis://redis-cache'
REDIS_DATA_PORT = 6379
REDIS_CACHE_PORT = 6378


redis_data = get_redis_connection(host=REDIS_HOST, port=REDIS_DATA_PORT, decode_responses=True)
redis_cache = aioredis.from_url(
    url=REDIS_URL,
    port=REDIS_CACHE_PORT,
    encoding="utf8",
    decode_responses=True,
    health_check_interval=10,
    socket_connect_timeout=5,
    retry_on_timeout=True,
    socket_keepalive=True
)

FastAPICache.init(RedisBackend(redis_cache), prefix="fastapi-cache")


class RedisBaseModel(EmbeddedJsonModel, ABC):
    class Meta:
        database = redis_data


class User(RedisBaseModel):
    first_name: str = Field(index=True, full_text_search=True)
    last_name: str = Field(index=True, full_text_search=True)
    email: EmailStr = Field(index=True, full_text_search=True)
    password: str
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
