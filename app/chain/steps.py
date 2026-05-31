from pydantic import BaseModel
from .runnable import Runnable
from transformers import pipeline


class PromptBuilderInput(BaseModel):
  question: str
  stats: dict


class PromptBuilderOutput(BaseModel):
  prompt: list[dict]
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

    Svar:
    """


    return PromptBuilderOutput(
      prompt=[
        {"role": "system", "content": "Du är en datanalytiker, Svara kortfattat på svenska"},
        {"role": "user", "content": f"Svara på {data.stats} och din fråga kommer att vara {data.question}"}
      ],
      question=data.question
      )
  
class LLMRunner(Runnable[PromptBuilderOutput, LLMRunnerOutput ]):
  def invoke(self, data: PromptBuilderOutput) -> LLMRunnerOutput:
    pipe = pipeline("text-generation", model="HuggingFaceTB/SmolLM2-135M-Instruct")
    result = pipe(data.prompt, max_new_tokens=200)
    print(result)
    return LLMRunnerOutput(raw_text=result[0]["generated_text"][-1]["content"], question=data.question)
  
class ResponseParser(Runnable[LLMRunnerOutput, ResponseParserOutput]):
  def invoke(self, data: LLMRunnerOutput) -> ResponseParserOutput:
    return ResponseParserOutput(
      question=data.question,
      answer=data.raw_text.split("svar:")[-1].strip(),
      model="HuggingFaceTB/SmolLM2-135M-Instruct"
    )