

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