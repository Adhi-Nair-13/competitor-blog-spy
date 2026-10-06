import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["DEMO_MODE"] = "true"

import backend.database as db_module
from backend.database import Base, get_db
import backend.services.monitoring_scheduler as sched_module
from backend.main import app

# Create shared in-memory engine with StaticPool
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Patch the db_module engine and SessionLocal
db_module.engine = test_engine
db_module.SessionLocal = TestingSessionLocal
sched_module.SessionLocal = TestingSessionLocal

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
