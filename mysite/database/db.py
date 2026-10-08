from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from ..config import settings


database_url = settings.DATABASE_URL.replace(
    "sqlite:///", "sqlite+aiosqlite:///", 1
)

engine= create_async_engine(database_url)
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass

async def get_db():
    async with SessionLocal() as db:
        yield db