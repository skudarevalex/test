from sqlmodel import SQLModel, Session, create_engine 
from sqlalchemy import text
from contextlib import contextmanager
from .config import get_settings

engine = create_engine(url=get_settings().DATABASE_URL_psycopg, 
                       echo=True, pool_size=5, max_overflow=10)

@contextmanager
def get_session():
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        
def init_db():
    # Удаление таблиц с учетом зависимостей
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS mltask CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS \"user\" CASCADE"))
    
    # Создание новых таблиц
    SQLModel.metadata.create_all(engine)
