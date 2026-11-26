"""Unit tests for the Task API. Run with: pytest -v"""
import pytest
from fastapi.testclient import TestClient

from app import database
from app.main import app

BASE = "/api/v1/tasks"


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Fresh, empty database for every test."""
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "test.db"))
    with TestClient(app) as c:  # starts the app (creates the table)
        yield c


def test_create_task(client):
    """POST /tasks creates a task and returns 201."""
    res = client.post(BASE, json={"title": "Study", "priority": "high"})
    assert res.status_code == 201
    body = res.json()
    assert body["id"] == 1
    assert body["title"] == "Study"
    assert body["status"] == "todo"  # default value


def test_create_task_without_title_returns_400(client):
    """Missing title is rejected with a 400 and an error message."""
    res = client.post(BASE, json={"priority": "low"})
    assert res.status_code == 400
    assert res.json()["error"]["code"] == 400


def test_list_and_filter_tasks(client):
    """GET /tasks returns all tasks and supports ?status= filtering."""
    client.post(BASE, json={"title": "A", "status": "done"})
    client.post(BASE, json={"title": "B"})
    assert len(client.get(BASE).json()) == 2
    done = client.get(BASE, params={"status": "done"}).json()
    assert [t["title"] for t in done] == ["A"]


def test_get_missing_task_returns_404(client):
    """Reading an id that does not exist returns 404."""
    res = client.get(f"{BASE}/999")
    assert res.status_code == 404
    assert res.json()["error"]["message"] == "Task with id 999 not found"


def test_update_task(client):
    """PUT /tasks/{id} replaces the task fields."""
    client.post(BASE, json={"title": "Old"})
    res = client.put(f"{BASE}/1", json={"title": "New", "status": "in_progress"})
    assert res.status_code == 200
    assert res.json()["title"] == "New"
    assert res.json()["status"] == "in_progress"


def test_delete_task(client):
    """DELETE /tasks/{id} returns 204 and the task is gone."""
    client.post(BASE, json={"title": "Temp"})
    assert client.delete(f"{BASE}/1").status_code == 204
    assert client.get(f"{BASE}/1").status_code == 404
