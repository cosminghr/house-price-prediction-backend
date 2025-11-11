import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.db import Base, init_db
from app.controllers.auth_controller import get_db as auth_get_db
from app.controllers.user_controller import get_db as users_get_db
from app.main import app

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[auth_get_db] = override_get_db
app.dependency_overrides[users_get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def _clean_db():
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
    yield


@pytest.fixture(scope="session", autouse=True)
def _init_db_once():
    init_db()
    yield


@pytest.fixture(scope="session")
def test_client():
    return TestClient(app)


@pytest.fixture
def client():
    init_db()
    with TestClient(app) as c:
        yield c
