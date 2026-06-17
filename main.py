from fastapi import FastAPI,HTTPException
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

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None=None
    status: TaskStatus | None=None
    created_at: datetime = Field(default_factory=datetime.now)

class TaskUpdate(BaseModel):
    title: str | None=None
    description: str | None=None
    status: TaskStatus | None=None

fake_tasks=[
    {"id":1, "title":"Buy Groceries", "status":"pending","description":None,"created_at": datetime.now()},
    {"id":2, "title":"Read fastapi docs", "status":"done","description": None,"created_at": datetime.now()},
    {"id":3, "title":"Build task manager API", "status":"pending", "description": None,"created_at": datetime.now()}
]

app = FastAPI()

from database import engine
import models

models.Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Task Manager API is running!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks(status: TaskStatus | None = None,limit: int=10):
    if status is None:
        return {"tasks":fake_tasks[:limit], "total":min(len(fake_tasks),limit)}

    filtered = [task for task in fake_tasks if task["status"]==status.value]

    return {"tasks":filtered[:limit] , "total": min(len(filtered),limit)}

@app.get("/tasks/{task_id}",response_model=TaskResponse,response_model_exclude_none=True)
def get_task(task_id: int):
    for task in fake_tasks:
        if task["id"]==task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

@app.post("/tasks",status_code=201,response_model=TaskResponse,response_model_exclude_none=True)
def post_task(task: TaskCreate):
    new_task={
        "id": len(fake_tasks)+1,
        "title": task.title,
        "status": task.status,
        "description": task.description,
        "created_at": datetime.now()
    }
    fake_tasks.append(new_task)
    return new_task

@app.put("/tasks/{task_id}",response_model=TaskResponse,response_model_exclude_none=True)
def update_task(task_id: int, task: TaskCreate):
    for index,existingtask in enumerate(fake_tasks):
        if existingtask["id"]==task_id:
            updated_task={
                "id": task_id,
                "title": task.title,
                "status": task.status,
                "description": task.description,
                "created_at": existingtask.get("created_at", datetime.now())
            }
            fake_tasks[index]=updated_task
            return updated_task
    raise HTTPException(status_code=404, detail=f"Task with id{task_id} not found")

@app.delete("/tasks/{task_id}",status_code=204)
def delete_task(task_id: int):
    for index,task in enumerate(fake_tasks):
        if task["id"]==task_id:
            fake_tasks.pop(index)
            return 
    raise HTTPException(status_code=404, detail=f"Task with id {task_id}  not found")

@app.patch("/tasks/{task_id}", response_model=TaskResponse,response_model_exclude_none=True)
def patch_task(task_id: int, task: TaskUpdate):
    for index,existing_task in enumerate(fake_tasks):
        if existing_task["id"]==task_id:
            patch_data=task.model_dump(exclude_unset=True)
            existing_task.update(patch_data)
            fake_tasks[index]=existing_task
            return existing_task
    raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")