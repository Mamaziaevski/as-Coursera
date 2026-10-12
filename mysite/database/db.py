from pathlib import Path
from sqlalchemy import text, event
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from ..config import settings


database_url = settings.DATABASE_URL
if database_url.startswith("sqlite:///"):
    database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
url = make_url(database_url)
if url.database != ":memory:" and not Path(url.database).is_absolute():
    url = url.set(database=str(Path(__file__).resolve().parents[2] / url.database))
engine = create_async_engine(url, connect_args={"timeout": 15})


@event.listens_for(engine.sync_engine, "connect")
def enable_foreign_keys(connection, record):
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


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

async def begin_group_write(db: AsyncSession):
    await db.rollback()
    await db.execute(text("BEGIN IMMEDIATE"))