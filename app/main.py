from fastapi import FastAPI, UploadFile
from .data import load_dataset

app = FastAPI()

@app.get("/health")
async def health():
  return{"status": "ok"}

@app.post("/data/upload")
async def upload_data(file: UploadFile):
  if not file.filename.endswith(".csv"):
    raise HTTPException(status_code=400, detail="Gotta have a CSV duuuude")
  
  contents = await file.read()
  metadata = load_dataset(contents)
  return metadata


