from fastapi import FastAPI, UploadFile, HTTPException
from .data import load_dataset
from . import data
from .schemas import AskRequest
from .chain.pipeline import oraklet
from .chain.steps import PromptBuilderInput
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/health")
async def health():
  logger.info(f"Health check requested")
  return{"status": "ok"}

@app.post("/data/upload")
async def upload_data(file: UploadFile):
  if not file.filename.endswith(".csv"):
    raise HTTPException(status_code=400, detail="Gotta have a CSV duuuude")
  
  contents = await file.read()
  if len(contents) > 524288000:
    raise HTTPException(status_code=400, detail="File is to big maximum is 500mb")
  metadata = load_dataset(contents)
  logger.info(f"CSV uploaded: {file.filename}, size: {len(contents)} bytes")
  return metadata

@app.get("/data/stats")
async def get_stats():
  if data.dataset is None:
    raise HTTPException(status_code=404, detail="Gotta have a dataset uploaded")
  logger.info(f"Got the {data} from CSV filme")
  return data.dataset.describe().to_dict()

@app.post("/ai/ask")
async def ask(body: AskRequest):
  if data.dataset is None:
    logger.error(f"AI ask failed: No dataset uploaded")
    raise HTTPException(status_code=400, detail="Gotta have CSV uploaded")
  
  result = oraklet.invoke(PromptBuilderInput(
    question=body.question,
    stats=data.dataset.describe().to_dict()
  ))
  logger.info(f"AI ask: question='{body.question}' ")

  return result



