from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Task Manager API is running!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    return {"tasks":[], "total":0}


