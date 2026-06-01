from fastapi.testclient import TestClient
from ..main import app
from .. import data

client = TestClient(app)

def test_health():
  resp = client.get("/health")
  
  assert resp.status_code == 200
  assert resp.json()["status"] == "ok"

def test_upload():
  resp = client.post("/data/upload", files={"file": (
    "Test.csv",
    b"name,age\nAlice,30",
    "text/csv"
    )})
  
  assert resp.status_code == 200
  assert resp.json()["rows"] == 1
  assert resp.json()["columns"] == ["name", "age"]
  assert resp.json()["dtypes"] == {"name": "str", "age": "int64"}

def test_wrong_file():
  resp = client.post("/data/upload", files={"file":(
    "text.txt",
    b"Monkey with banana",
    "text/plain"
  )})

  assert resp.status_code == 400

def test_no_uploaded_dataset():
  data.dataset = None
  resp = client.get("/data/stats")
  assert resp.status_code == 404