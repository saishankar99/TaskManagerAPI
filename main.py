from fastapi import FastAPI,HTTPException

app = FastAPI()

fake_tasks=[
    {"id":1, "title":"Buy Groceries", "status":"pending"},
    {"id":2, "title":"Read fastapi docs", "status":"done"},
    {"id":3, "title":"Build task manager API", "status":"pending"}
]



@app.get("/")
def read_root():
    return {"message": "Task Manager API is running!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks(status: str | None = None):
    if status==None:
        return {"tasks":fake_tasks, "total":len(fake_tasks)}

    filtered = [task for task in fake_tasks if task["status"]==status]

    return {"tasks":filtered , "total": len(filtered)}

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in fake_tasks:
        if task["id"]==task_id:
            return task
    return HTTPException(status_code=404, detail=f"Task with id {task_id} not found")


