from pydantic import BaseModel



class PromptBuilderInput(BaseModel):
  question: str
  stats: int