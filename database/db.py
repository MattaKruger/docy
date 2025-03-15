from sqlmodel import create_engine, Session
from settings import Settings

settings = Settings()


engine = create_engine(f"postgresql://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}/{settings.DB_NAME}")


def get_session():
    with Session(engine) as session:
        yield session
