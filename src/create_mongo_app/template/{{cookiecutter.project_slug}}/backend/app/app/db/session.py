import asyncio

from app.core.config import settings
from app.__version__ import __version__
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.driver_info import DriverInfo

DRIVER_INFO = DriverInfo(name="full-stack-fastapi-mongodb", version=__version__)


class _MongoClientSingleton:
    _instance = None
    _loop = None

    def __new__(cls):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        # Rebind the client when the running loop changes rather than caching by
        # id(loop): recycled ids (after a loop is GC'd) could otherwise hand back
        # a client bound to a dead loop, and the old dict never evicted stale
        # entries. Holding the loop reference keeps the comparison reliable.
        if cls._instance is None or cls._loop is not loop:
            instance = super().__new__(cls)
            instance.mongo_client = AsyncMongoClient(
                settings.MONGO_DATABASE_URI, driver=DRIVER_INFO
            )
            cls._instance = instance
            cls._loop = loop
        return cls._instance


def MongoDatabase() -> AsyncDatabase:
    return _MongoClientSingleton().mongo_client[settings.MONGO_DATABASE]


async def ping():
    await MongoDatabase().command("ping")


__all__ = ["MongoDatabase", "ping"]
