"""
    Models module

    Includes Redis OM and Pydantic models
"""


import datetime
from abc import ABC
from pydantic import EmailStr, BaseModel
from redis_om import EmbeddedJsonModel, Field, Migrator, NotFoundError
from .db_connectors import redis_data


class RedisBaseModel(EmbeddedJsonModel, ABC):
    """
        Abstract Model Class with connector to database
    """

    @classmethod
    def is_exist(cls, entity_pk):
        """
        Classmethod that implements existense checks of
        the class instance in database by instance's primary key

        """

        try:
            cls.get(entity_pk)
            return True

        except NotFoundError:
            return False

    class Meta:
        """
            Connector to database
        """

        database = redis_data


class User(RedisBaseModel):
    """
        Database model of user enity
    """

    first_name: str = Field(index = True)
    last_name: str = Field(index = True)
    email: EmailStr = Field(index = True)
    password: str = Field(min_length = 8)
    signup_date: datetime.date = Field(index = True, default = datetime.date.today())
    last_update: datetime.date = Field(index = True, default = None)
    blogs: list[str] = Field(default_factory = list)
    posts: list[str] = Field(default_factory = list)
    likes: list[str] = Field(default_factory = list)


class Blog(RedisBaseModel):
    """
        Database model of blog enity
    """

    author: str = Field(index = True, default = None)
    title: str = Field(index = True)
    creation_date: datetime.date = Field(index = True, default = datetime.date.today())
    last_update: datetime.date = Field(index = True, default = None)
    posts: list[str] = Field(default_factory = list)


class BlogPost(RedisBaseModel):
    """
        Database model of post enity
    """

    author: str = Field(index = True, default = None)
    content: str = Field(index = True, max_length = 1000)
    blog: str = Field(index = True)
    creation_date: datetime.date = Field(default = datetime.date.today())
    last_update: datetime.date = Field(index = True, default = None)
    likes: list[str] = Field(default_factory = list)


class Like(RedisBaseModel):
    """
        Database model of like enity
    """

    author: str = Field(index = True, default = None)
    post: str = Field(index = True)
    creation_date: datetime.date = Field(default = datetime.date.today())


class TokenPayload(BaseModel):
    """
        Pydantic model for JWT token payload
    """

    sub: str = None
    exp: int = None


Migrator().run()
