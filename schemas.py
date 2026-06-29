from pydantic import BaseModel,Field
from datetime import datetime
from enum import Enum


class TaskStatus(str,Enum):
    pending = "pending"
    done = "done"
    in_progress="in_progress"


class TaskCreate(BaseModel):
    title: str
    description: str | None=None
    status: TaskStatus = TaskStatus.pending
    due_date: datetime | None=None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None=None
    status: TaskStatus | None=None
    created_at: datetime = Field(default_factory=datetime.now)
    due_date: datetime | None=None

class TaskUpdate(BaseModel):
    title: str | None=None
    description: str | None=None
    status: TaskStatus | None=None
    due_date: datetime | None=None