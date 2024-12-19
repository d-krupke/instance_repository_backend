from contextlib import contextmanager
from sqlmodel import SQLModel, Session, create_engine

# Assuming you have an engine created somewhere
engine = create_engine("sqlite:///database.db")


@contextmanager
def get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()

def get_db():
    with get_session() as session:
        yield session

def create_tables():
    SQLModel.metadata.create_all(engine)