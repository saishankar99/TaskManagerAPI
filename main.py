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



models.Base.metadata.create_all(bind=engine)

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
        description=task.description
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
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