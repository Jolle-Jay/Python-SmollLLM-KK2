from pydantic import BaseModel
from .runnable import Runnable
from .pipeline import Pipeline


class PromptBuilderInput(BaseModel):
  question: str
  stats: dict


class PromptBuilderOutput(BaseModel):
  prompt: str
  question: str

class LLMRunnerOutput(BaseModel):
  raw_text: str
  question: str

class ResponseParserOutput(BaseModel):
  question: str
  answer: str
  model: str

class PromptBuilder(Runnable[PromptBuilderInput, PromptBuilderOutput]):
  def invoke(self, data: PromptBuilderInput) -> PromptBuilderOutput:
    prompt = f"""Du är en dataanalytiker. Svara kortfattat på svenska.
    Statistik från dataset:
    {data.stats}
    
    Fråga: {data.question}

    Svar:"""


    return PromptBuilderOutput(prompt=prompt)
  
class LLMRunner(Runnable[PromptBuilderOutput, LLMRunnerOutput ]):
  def invoke(self, data: PromptBuilderOutput) -> LLMRunnerOutput:
    pipe = pipeline("text-generation", model="HuggingFaceTB/SmolLM2-135M-Instruct")
    result = pipe(data.prompt, max_new_tokens=200)
    return LLMRunnerOutput(raw_text=result[0]["generated_text"], question=data.question)