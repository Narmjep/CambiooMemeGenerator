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
    engine : AsyncEngine = create_async_engine(DATABASE_URL, echo=True)
    SessionFactory = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False) # type: ignore -- supresses the 'no overload' error

async def close_connection():
    await engine.dispose()

async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def destroy_db():
    async with engine.begin() as conn:
        # drop table if it exists
        await conn.run_sync(Base.metadata.drop_all)

@asynccontextmanager
async def get_session():
    async with SessionFactory() as session:
        yield session

async def create_meme(url: str, caption: str, image: str):
    """Stores a meme in the database

    Args:
        url (str): the url to an image. The database does not verify that the url is valid
        caption (str): A caption for the meme
        image (str): The base64 encoded image
    """
    async with get_session() as session:
        async with session.begin():
            meme = Meme(url=url, caption=caption, upvotes=0, image=image)
            session.add(meme)
            await session.commit()


async def get_meme_by_id(id: int):
    async with get_session() as session:
        async with session.begin():
            stmt = select(Meme).where(Meme.id == id)
            result = await session.execute(stmt)
            return result.scalars().first()

async def get_all_memes():
    async with get_session() as session:
        async with session.begin():
            stmt = select(Meme)
            result = await session.execute(stmt)
            return result.scalars().all()
        

async def get_top_ten_memes():
    async with get_session() as session:
        async with session.begin():
            stmt = select(Meme).order_by(Meme.upvotes.desc()).limit(10)
            result = await session.execute(stmt)
            return result.scalars().all()
        
async def get_random_meme():
    async with get_session() as session:
        async with session.begin():
            stmt = select(Meme).order_by(func.random()).limit(1)
            result = await session.execute(stmt)
            return result.scalars().first()

# Upvote

async def upvote_meme(id: int) -> bool:
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


