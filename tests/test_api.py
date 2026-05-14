"""Tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

from sqlalchemy.pool import StaticPool
from app.models import Base

# In-memory SQLite — StaticPool ensures all connections share the same DB
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client():
    # Create all tables on test engine
    Base.metadata.create_all(bind=test_engine)

    mock_scheduler = MagicMock()
    mock_scheduler.running = False

    with patch("app.database.engine", test_engine), \
         patch("app.services.scheduler.scheduler", mock_scheduler):

        from app.main import app
        from app.database import get_db
        app.dependency_overrides[get_db] = override_get_db

        with TestClient(app, raise_server_exceptions=True) as c:
            yield c

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Automation Toolkit" in r.json()["name"]


def test_list_jobs_empty(client):
    r = client.get("/jobs/")
    assert r.status_code == 200
    assert r.json() == []


def test_upload_csv(client):
    csv_content = b"name,age\nAlice,25\nBob,30\nAlice,25\n"
    r = client.post(
        "/jobs/upload",
        files={"file": ("test.csv", csv_content, "text/csv")},
        data={"notify_telegram": "false", "notify_email": "false", "notify_whatsapp": "false"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["job_id"] == 1
    assert body["status"] == "processing"


def test_upload_invalid_type(client):
    r = client.post(
        "/jobs/upload",
        files={"file": ("test.txt", b"hello", "text/plain")},
        data={},
    )
    assert r.status_code == 400


def test_get_job_not_found(client):
    r = client.get("/jobs/999")
    assert r.status_code == 404


def test_list_tasks_empty(client):
    r = client.get("/tasks/")
    assert r.status_code == 200
    assert r.json() == []


def test_create_task_invalid_cron(client):
    r = client.post("/tasks/", json={
        "name": "Test", "filename": "test.csv",
        "cron_expr": "not-a-cron",
    })
    assert r.status_code == 400


def test_get_task_not_found(client):
    r = client.get("/tasks/999")
    assert r.status_code == 404
