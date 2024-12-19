"""
This module provides database utility functions and context managers for managing SQLModel sessions.

Functions:
    get_session() -> Generator[Session, None, None]:
        Context manager that provides a SQLModel session. Ensures the session is properly closed after use.

    get_db() -> Generator[Session, None, None]:
        Generator function that yields a SQLModel session using the get_session context manager.

    create_tables() -> None:
        Creates all tables defined in the SQLModel metadata using the provided engine.
"""

from contextlib import contextmanager
from sqlmodel import SQLModel, Session, create_engine

engine = create_engine("sqlite:///database.db")


@contextmanager
def get_session():
    """
    Provides a database session for use in a context manager.

    Yields:
        Session: A SQLAlchemy session object.

    Ensures that the session is properly closed after use.
    """
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


def get_db():
    """
    Provides a database session for use in a context manager.

    Yields:
        session: A database session object.
    """
    with get_session() as session:
        yield session


def create_tables():
    """
    Create all tables in the database using the metadata defined in the SQLModel.

    This function uses the SQLAlchemy engine to create all tables defined in the
    SQLModel metadata. It ensures that the database schema is created according
    to the models defined in the application.

    Returns:
        None
    """
    SQLModel.metadata.create_all(engine)
