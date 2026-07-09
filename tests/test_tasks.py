import pytest

def test_health_check(client):
    response=client.get('/health')
    assert response.status_code==200
    assert response.json() == {'status': "ok"}


def test_create_task(client):
    response=client.post("/tasks",json={"title":"Test task"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test task"
    assert data["status"] == "pending"
    assert "id" in data

def test_get_task(client):
    create_response=client.post("/tasks", json={"title": "Test task"})
    id=create_response.json()["id"]
    response=client.get(f"/tasks/{id}")
    assert response.status_code == 200 
    assert response.json()["title"] == "Test task"

def test_get_nonexistent_task_returns_404(client):
    response = client.get("/tasks/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_create_task_without_title_returns_422(client):
    response = client.post("/tasks", json = {"status": "done"})
    assert response.status_code == 422
    
def test_delete_nonexistent_task_returns_404(client):
    response = client.delete("/tasks/99999")
    assert response.status_code == 404

def test_patch_nonexistent_task_returns_404(client):
    response = client.patch("/tasks/99999", json = {"status": "done"})
    assert response.status_code == 404

@pytest.mark.parametrize("bad_status", ["bananas", "complete", "PENDING", "in progress"])
def test_invalid_status_is_rejected(client, bad_status):
    response = client.post("/tasks", json = {"title": "Task", "status": bad_status})
    assert response.status_code == 422

def test_update_task_full(client):
    created = client.post("/tasks", json = {"title": "Task", "status":"in_progress", "description": "desc"}).json()
    id = created["id"]
    response = client.put(f"/tasks/{id}", json = {
        "title": "Updated Task",
        "status": "done",
        "description": "new desc"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Task"
    assert data["status"] == "done"

def test_update_task_partial(client):
    created = client.post("/tasks", json = {"title": "A Task"}).json()
    id = created["id"]

    response = client.patch(f"/tasks/{id}", json = {
        "status": "done"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "done"
    assert data["title"]  == "A Task"

def test_delete_task_then_confirm_gone(client):

    created = client.post("/tasks", json = {"title": "Delete me"}).json()

    task_id = created["id"]

    response = client.delete(f"/tasks/{task_id}")

    assert response.status_code == 204

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 404

def test_filter_task_by_status(client):

    client.post("/tasks", json = {"title": "Task 1", "status": "in_progress"})
    client.post("/tasks", json = {"title": "Task 2", "status": "done"})
    client.post("/tasks", json = {"title": "Task 3", "status": "done"})

    response = client.get(f"/tasks?status=done")

    assert response.status_code == 200

    assert response.json()["total_tasks"] == 2


