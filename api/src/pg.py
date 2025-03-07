"""
This file contains the code that interacts with the postgres database
"""


import asyncio
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import Column, Integer, String, select, func
import os

if os.getenv("DOCKER_NET") is not None:
    # use docker network if running in docker
    host = "database"
else:
    host = "localhost"

port = 5432
user = "admin"
password = "admin"
database = "cmg"

DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"

engine : AsyncEngine = create_async_engine(DATABASE_URL, echo=True)
SessionFactory = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False) # type: ignore -- supresses the 'no overload' error


class Base(DeclarativeBase):
    pass

class Meme(Base):
    __tablename__ = "memes"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    image = Column(String)
    caption = Column(String)
    upvotes = Column(Integer)

async def init_connection():
    """Reconnects to the database. This function is needed to run the tests. The connection is already established when this module is imported
    """
    engine : AsyncEngine = create_async_engine(DATABASE_URL, echo=True)
    SessionFactory = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False) # type: ignore -- supresses the 'no overload' error

async def close_connection():
    """Closes the database connection. This function is needed to run the tests. The connection is naturally closed when the program exits
    """

    await engine.dispose()

async def create_table():
    """Creates the 'memes' table if it does not already exist
    """


    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def destroy_db():
    """Drops the 'memes' table if it exists
    """

    async with engine.begin() as conn:
        # drop table if it exists
        await conn.run_sync(Base.metadata.drop_all)

@asynccontextmanager
async def get_session():
    async with SessionFactory() as session: # type: ignore -- supresses the 'no overload' error
        yield session

async def create_meme(url: str, caption: str, image: str):
    """Stores a meme in the database

    Args:
        url (str): the url to an image. The database does not verify that the url is valid. 
        caption (str): A caption for the meme
        image (str): The base64 encoded image
    """
    async with get_session() as session:
        async with session.begin():
            meme = Meme(url=url, caption=caption, upvotes=0, image=image)
            session.add(meme)
            await session.commit()


async def get_meme_by_id(id: int):
    """Retrieves a meme by its unique id
    """

    async with get_session() as session:
        async with session.begin():
            stmt = select(Meme).where(Meme.id == id)
            result = await session.execute(stmt)
            return result.scalars().first()

async def get_all_memes():
    """Returns all memes in the database. Used for testing purposes
    """

    async with get_session() as session:
        async with session.begin():
            stmt = select(Meme)
            result = await session.execute(stmt)
            return result.scalars().all()
        

async def get_top_ten_memes():
    """Returns the top 10 memes by upvotes
    """

    async with get_session() as session:
        async with session.begin():
            stmt = select(Meme).order_by(Meme.upvotes.desc()).limit(10)
            result = await session.execute(stmt)
            return result.scalars().all()
        
async def get_random_meme():
    """Returns a random meme
    """

    async with get_session() as session:
        async with session.begin():
            stmt = select(Meme).order_by(func.random()).limit(1)
            result = await session.execute(stmt)
            return result.scalars().first()

# Upvote

async def upvote_meme(id: int) -> bool:
    """Increments the upvotes of a meme by 1

    Args:
        id (int): The unique identifier of the meme

    Returns:
        bool: True if the meme was found and upvoted, False otherwise
    """

    async with get_session() as session:
        async with session.begin():
            stmt = select(Meme).where(Meme.id == id)
            result = await session.execute(stmt)
            meme = result.scalars().first()
            if meme is None:
                return False
            meme.upvotes += 1
            await session.commit()
            return True
        

async def downvote_meme(id: int) -> bool:
    """Decrements the upvotes of a meme by 1

    Args:
        id (int): The unique identifier of the meme

    Returns:
        bool: True if the meme was found and downvoted, False otherwise
    """

    async with get_session() as session:
        async with session.begin():
            stmt = select(Meme).where(Meme.id == id)
            result = await session.execute(stmt)
            meme = result.scalars().first()
            if meme is None:
                return False
            
            if meme.upvotes > 0:
                meme.upvotes -= 1

            await session.commit()
            return True


