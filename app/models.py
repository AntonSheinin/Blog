"""
    Models module

    Includes Redis OM and Pydantic models
"""


from datetime import datetime
from abc import ABC
from pydantic import EmailStr, BaseModel
from redis_om import EmbeddedJsonModel, Field, Migrator, NotFoundError
from .db_connectors import redis_data


class RedisBaseModel(EmbeddedJsonModel, ABC):
    """
        General Model Class with connector to database
    """

    last_update: str = Field(index = True, default = None)
    creation_date: str = Field(default = str(datetime.now())[:19])

    def update_save(self):
        """
            Storing date of last update of instance
            and saving instance in database
        """

        self.last_update = str(datetime.now())[:19]
        self.save()

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
    blogs: list[str] = Field(default_factory = list)
    posts: list[str] = Field(default_factory = list)
    likes: list[str] = Field(default_factory = list)


class Blog(RedisBaseModel):
    """
        Database model of blog enity
    """

    author: str = Field(index = True, default = None)
    title: str = Field(index = True)
    posts: list[str] = Field(default_factory = list)


class BlogPost(RedisBaseModel):
    """
        Database model of post enity
    """

    author: str = Field(index = True, default = None)
    content: str = Field(index = True, max_length = 1000)
    blog: str = Field(index = True)
    likes: list[str] = Field(default_factory = list)


class Like(RedisBaseModel):
    """
        Database model of like enity
    """

    author: str = Field(index = True, default = None)
    post: str = Field(index = True)
    

class TokenPayload(BaseModel):
    """
        Pydantic model for JWT token payload
    """

    sub: str = None
    exp: int = None


Migrator().run()
