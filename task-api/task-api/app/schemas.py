"""Pydantic models: define and validate the JSON the API accepts and returns."""
from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

Status = Literal["todo", "in_progress", "done"]
Priority = Literal["low", "medium", "high"]


class TaskBase(BaseModel):
    """Fields shared by create, update and read."""

    title: str = Field(..., min_length=1, max_length=100, examples=["Finish API project"])
    description: Optional[str] = Field(None, max_length=500, examples=["Build, test and document it"])
    due_date: Optional[date] = Field(None, examples=["2026-12-01"], description="Format: YYYY-MM-DD")
    status: Status = Field("todo", description="One of: todo, in_progress, done")
    priority: Priority = Field("medium", description="One of: low, medium, high")

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        # Reject titles that are only spaces
        if not v.strip():
            raise ValueError("title must not be blank")
        return v.strip()


class TaskCreate(TaskBase):
    """Body of POST /tasks."""


class TaskUpdate(TaskBase):
    """Body of PUT /tasks/{id} (full replacement of the task)."""


class Task(TaskBase):
    """A task as returned by the API."""

    id: int = Field(..., examples=[1])
    created_at: str = Field(..., examples=["2026-11-26 03:48:00"])


class ErrorDetail(BaseModel):
    code: int = Field(..., examples=[404])
    message: str = Field(..., examples=["Task with id 99 not found"])


class ErrorResponse(BaseModel):
    """Every error from the API uses this shape."""

    error: ErrorDetail
