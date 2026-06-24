from fastapi import FastAPI,HTTPException,Depends
from pydantic import BaseModel,Field
from datetime import datetime
from enum import Enum
from sqlalchemy.orm import Session
from database import engine,get_db
import models

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


app = FastAPI()



# models.Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Task Manager API is running!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks(status: TaskStatus | None = None,limit: int=10,db: Session = Depends(get_db)):
    query=db.query(models.Task)
    if status is not None:
        query=query.filter(models.Task.status==status.value)
    tasks=query.limit(limit).all()
    return {"tasks":tasks, "total_tasks":len(tasks)}

@app.get("/tasks/{task_id}",response_model=TaskResponse,response_model_exclude_none=True)
def get_task(task_id: int,db: Session = Depends(get_db)):
    task=db.query(models.Task).filter(models.Task.id==task_id).first()
    if task is None:
        raise HTTPException(status_code=404,detail=f"task with {task_id} not found")
    return task

@app.post("/tasks",status_code=201,response_model=TaskResponse,response_model_exclude_none=True)
def post_task(task: TaskCreate,db: Session = Depends(get_db)):
    new_task=models.Task(
        title=task.title,
        status=task.status.value,
        description=task.description,
        due_date=task.due_date
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.put("/tasks/{task_id}",response_model=TaskResponse,response_model_exclude_none=True)
def update_task(task_id: int, task: TaskCreate,db: Session = Depends(get_db)):
    existing_task=db.query(models.Task).filter(models.Task.id==task_id).first()
    if existing_task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found ")
    existing_task.title=task.title
    existing_task.description=task.description
    existing_task.status=task.status
    existing_task.due_date=task.due_date
    db.commit()
    db.refresh(existing_task)
    return existing_task

@app.delete("/tasks/{task_id}",status_code=204)
def delete_task(task_id: int,db: Session = Depends(get_db)):
    task=db.query(models.Task).filter(models.Task.id==task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    db.delete(task)
    db.commit()
    return 

@app.patch("/tasks/{task_id}", response_model=TaskResponse,response_model_exclude_none=True)
def patch_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    existing_task=db.query(models.Task).filter(models.Task.id==task_id).first()
    if existing_task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    patch_data=task.model_dump(exclude_unset=True)
    if "status" in patch_data and patch_data["status"] is not None:
        patch_data["status"]=patch_data["status"].value
    for key,value in patch_data.items():
        setattr(existing_task,key,value)
    db.commit()
    db.refresh(existing_task)
    return existing_task
    