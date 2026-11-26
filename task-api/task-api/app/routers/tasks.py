"""CRUD endpoints for the Task resource, mounted at /api/v1/tasks."""
import sqlite3
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.database import get_db
from app.schemas import ErrorResponse, Status, Priority, Task, TaskCreate, TaskUpdate

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])

# Reusable error documentation shown in Swagger
NOT_FOUND = {404: {"model": ErrorResponse, "description": "Task not found"}}
BAD_REQUEST = {400: {"model": ErrorResponse, "description": "Invalid request data"}}


def _get_task_or_404(db: sqlite3.Connection, task_id: int) -> dict:
    """Fetch one task row or raise a 404 error."""
    row = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return dict(row)


def _values(task: TaskCreate | TaskUpdate) -> tuple:
    """Convert a validated task body into SQL parameter values."""
    return (
        task.title,
        task.description,
        task.due_date.isoformat() if task.due_date else None,
        task.status,
        task.priority,
    )


@router.post(
    "",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task",
    responses={**BAD_REQUEST},
)
def create_task(task: TaskCreate, db: sqlite3.Connection = Depends(get_db)):
    """Create a new task. Only `title` is required."""
    cur = db.execute(
        "INSERT INTO tasks (title, description, due_date, status, priority) "
        "VALUES (?, ?, ?, ?, ?)",
        _values(task),
    )
    db.commit()
    return _get_task_or_404(db, cur.lastrowid)


@router.get(
    "",
    response_model=List[Task],
    summary="List tasks",
    responses={**BAD_REQUEST},
)
def list_tasks(
    status: Optional[Status] = Query(None, description="Filter by status"),
    priority: Optional[Priority] = Query(None, description="Filter by priority"),
    db: sqlite3.Connection = Depends(get_db),
):
    """Return all tasks. Optionally filter by `status` and/or `priority`."""
    query, params = "SELECT * FROM tasks WHERE 1=1", []
    if status:
        query += " AND status = ?"
        params.append(status)
    if priority:
        query += " AND priority = ?"
        params.append(priority)
    rows = db.execute(query + " ORDER BY id", params).fetchall()
    return [dict(r) for r in rows]


@router.get(
    "/{task_id}",
    response_model=Task,
    summary="Get one task",
    responses={**NOT_FOUND, **BAD_REQUEST},
)
def get_task(task_id: int, db: sqlite3.Connection = Depends(get_db)):
    """Return a single task by its id."""
    return _get_task_or_404(db, task_id)


@router.put(
    "/{task_id}",
    response_model=Task,
    summary="Update a task",
    responses={**NOT_FOUND, **BAD_REQUEST},
)
def update_task(task_id: int, task: TaskUpdate, db: sqlite3.Connection = Depends(get_db)):
    """Replace all fields of an existing task."""
    _get_task_or_404(db, task_id)  # 404 if it does not exist
    db.execute(
        "UPDATE tasks SET title=?, description=?, due_date=?, status=?, priority=? "
        "WHERE id=?",
        (*_values(task), task_id),
    )
    db.commit()
    return _get_task_or_404(db, task_id)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    responses={**NOT_FOUND, **BAD_REQUEST},
)
def delete_task(task_id: int, db: sqlite3.Connection = Depends(get_db)):
    """Delete a task. Returns no body on success."""
    _get_task_or_404(db, task_id)
    db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
