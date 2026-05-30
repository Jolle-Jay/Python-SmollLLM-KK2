from pydantic import BaseModel
from .runnable import Runnable



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

class PromptBuilder(Runnable[PromptBuilderInput, PromptBuilderOutput]):
  def invoke(self, data: PromptBuilderInput) -> PromptBuilderOutput:
    prompt = f"{prompt}"
    return PromptBuilderOutput(prompt=prompt)