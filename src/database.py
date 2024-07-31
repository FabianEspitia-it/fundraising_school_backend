import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(os.getenv("DB_SOURCE"))

def create_extension_concurrently():
    with engine.begin() as conn:
        conn.execute(text("COMMIT"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        
create_extension_concurrently()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
