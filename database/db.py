import os
from sqlmodel import create_engine, Session
from load_dotenv import load_dotenv


load_dotenv()

engine = create_engine(os.environ.get("DB_URL", ""))


def get_session():
    with Session(engine) as session:
        yield session
