from fastapi import FastAPI,HTTPException
from pydantic import BaseModel

app = FastAPI()

class TaskCreate(BaseModel):
    title: str
    description: str | None=None
    status: str 

fake_tasks=[
    {"id":1, "title":"Buy Groceries", "status":"pending","description":None},
    {"id":2, "title":"Read fastapi docs", "status":"done","description": None},
    {"id":3, "title":"Build task manager API", "status":"pending", "description": None}
]



@app.get("/")
def read_root():
    return {"message": "Task Manager API is running!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks(status: str | None = None,limit: int=10):
    if status==None:
        return {"tasks":fake_tasks[:min(len(fake_tasks),limit)], "total":min(len(fake_tasks),limit)}

    filtered = [task for task in fake_tasks if task["status"]==status]

    return {"tasks":filtered[:min(len(filtered),limit)] , "total": min(len(filtered),limit)}

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in fake_tasks:
        if task["id"]==task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

@app.post("/tasks",status_code=201)
def post_task(task: TaskCreate):
    new_task={
        "id": len(fake_tasks)+1,
        "title": task.title,
        "status": task.status,
        "description": task.description
    }
    fake_tasks.append(new_task)
    return new_task

