from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import os


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("No está configurada la variable de entorno DATABASE_URL")


engine = create_async_engine(
    DATABASE_URL or "mysql+asyncmy://backend_user:REGINACORTES03@127.0.0.1:3306/backend",
    pool_pre_ping=True,
    future=True,
)

async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db():
    async with async_session_maker() as session:
        yield session