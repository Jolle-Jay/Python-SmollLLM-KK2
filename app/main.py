from fastapi import FastAPI, UploadFile, HTTPException
from .data import load_dataset
from . import data
from .schemas import AskRequest
from .chain.pipeline import oraklet
from .chain.steps import PromptBuilderInput

app = FastAPI()

@app.get("/health")
async def health():
  return{"status": "ok"}

@app.post("/data/upload")
async def upload_data(file: UploadFile):
  if not file.filename.endswith(".csv"):
    raise HTTPException(status_code=400, detail="Gotta have a CSV duuuude")
  
  contents = await file.read()
  if len(contents) > 524288000:
    raise HTTPException(status_code=400, detail="File is to big maximum is 500mb")
  metadata = load_dataset(contents)
  return metadata

@app.get("/data/stats")
async def get_stats():
  if data.dataset is None:
    raise HTTPException(status_code=404, detail="Gotta have a dataset uploaded")
  return data.dataset.describe().to_dict()

@app.post("/ai/ask")
async def ask(body: AskRequest):
  if data.dataset is None:
    raise HTTPException(status_code=400, detail="Gotta have CSV uploaded")
  
  result = oraklet.invoke(PromptBuilderInput(
    question=body.question,
    stats=data.dataset.describe().to_dict()
  ))
  return result



