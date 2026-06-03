from pydantic import BaseModel, Field

class AskRequest(BaseModel):
  question: str = Field(..., max_length=200)