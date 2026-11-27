import os

os.environ["POSTGRES_DB"] = "osijek_test"

from alembic import command
from alembic.config import Config
import pytest
from app.core.database import engine
from sqlalchemy.orm import Session

# `scope="session"` means run once for the whole pytest run
# `autouse=True` means run without any test asking for it by name
@pytest.fixture(scope="session", autouse=True)
def build_tables():
    config = Config("alembic.ini")
    command.upgrade(config, "head")

# It opens a connection to database, and runs tests (`yield session`), after which it discards
# all changes so that osijek_test database is fresh, as nothing ever happened. This way, running
# the test twice won't throw error because tables will always be empty on start of the test
@pytest.fixture()
def session():
    connection = engine.connect()
    transaction = connection.begin()

    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    # It pauses and hands session out to the test
    yield session
    session.close()
    transaction.rollback()
    connection.close()