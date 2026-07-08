import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base,get_db
from main import app
import models

TEST_DATABASE_URL="sqlite://./test.db"

test_engine = create_engine(TEST_DATABASE_URL,connect_args={"check_same_thread":False})

TestSessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=test_engine)

def override_get_db():
    db=TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
    
app.dependency_overrides[get_db]=override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=test_engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=test_engine)