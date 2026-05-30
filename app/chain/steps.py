from pydantic import BaseModel



class PromptBuilderInput(BaseModel):
  question: str
  stats: dict


class PromptBuilderOutput(BaseModel):
  prompt: str

class LLMRunnerOutput(BaseModel):
  raw_text: str
  question: str

class ResponseParserOutput(BaseModel):
  question: str
  answer: str
  model: str