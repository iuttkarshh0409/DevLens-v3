from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import DATABASE_URL, SQL_POOL_SIZE, SQL_MAX_OVERFLOW

is_sqlite = "sqlite" in DATABASE_URL.lower()

engine_kwargs = {}
if not is_sqlite:
    engine_kwargs.update({
        "pool_size": SQL_POOL_SIZE,
        "max_overflow": SQL_MAX_OVERFLOW
    })

engine = create_async_engine(DATABASE_URL, **engine_kwargs)
async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with async_session() as session:
        yield session
