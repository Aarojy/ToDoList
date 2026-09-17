import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def register_user():
    client.post("/auth/register", json={"username": "test", "password": "test"})

@pytest.fixture
def auth_headers(register_user):
    response = client.post("/auth/token", data={"username": "test", "password": "test"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="function", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# --- HELPER FUNCTIONS ---


# --- TESTS ---

def test_register():
    response = client.post("/auth/register", json={"username": "test", "password": "test"})
    assert response.status_code == 201
    assert response.json()["username"] == "test"

def test_register_without_username():
    response = client.post("/auth/register", json={"username": "", "password": "test"})
    assert response.status_code == 422

def test_register_without_password():
    response = client.post("/auth/register", json={"username": "test", "password": ""})
    assert response.status_code == 422

def test_login(register_user):
    response = client.post("/auth/token", data={"username": "test", "password": "test"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    
def test_login_with_wrong_credentials(register_user):
    response = client.post("/auth/token", data={"username": "test", "password": "tset"})
    assert response.status_code == 401

def test_post_todo(auth_headers):
    todo_data = {"description": "TEST"}
    response = client.post("/todos/", json=todo_data, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "TEST"
    assert data["completed"] is False
    assert "id" in data

def test_get_todos(auth_headers):
    client.post("/todos/", json={"description": "TEST"}, headers=auth_headers)

    response = client.get("/todos/", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["description"] == "TEST"

def test_get_todos_empty_list(auth_headers):
    response = client.get("/todos/", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 0
    assert data == []

def test_update_todo(auth_headers):
    response = client.post("/todos/", json={"description": "TEST"}, headers=auth_headers)
    todo_id = response.json()["id"]

    update_data = {"description": "TEST", "completed": True}
    response = client.put(f"/todos/{todo_id}", json=update_data, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is True

def test_delete_todo(auth_headers):
    response = client.post("/todos/", json={"description": "TEST"}, headers=auth_headers)
    todo_id = response.json()["id"]

    delete_res = client.delete(f"/todos/{todo_id}", headers=auth_headers)
    assert delete_res.status_code == 200

    get_res = client.get("/todos/", headers=auth_headers)
    todo_ids = [todo["id"] for todo in get_res.json()]
    assert todo_id not in todo_ids
    

