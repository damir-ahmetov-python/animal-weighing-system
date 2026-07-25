
from sqlalchemy import create_engine
from app.core.config import settings
from sqlalchemy.orm import sessionmaker, Session

DB_URL = settings.db.url

engine = create_engine(url=DB_URL)

session_maker = sessionmaker(engine, expire_on_commit=True)

def get_db():
    """
    Возвращает сессию для работы с БД.
    Используется как зависимость в эндпоинтах.
    """

    with session_maker() as session:
        yield session