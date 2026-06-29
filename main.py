from fastapi import FastAPI
from routers import tasks



app = FastAPI(title="Task Manager API")

app.include_router(tasks.router)



# models.Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Task Manager API is running!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
