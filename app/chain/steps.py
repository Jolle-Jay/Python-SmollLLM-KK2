from pydantic import BaseModel
from .runnable import Runnable
from transformers import pipeline
import logging

logger=logging.getLogger(__name__)

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
    logger.info("Step1 : PromptBuilder - Building propmt")
    stats_summary = ""
    for column, values in data.stats.items():
      stats_summary += f"{column}: mean={values['mean']:.1f}, min={values['min']:.1f}, max={values['max']:.1f}\n"



    return PromptBuilderOutput(
      prompt=[
        {"role": "system", "content": "Du är en datanalytiker, Svara kortfattat på svenska"},
        {"role": "user", "content": f"Svara på {stats_summary} och din fråga kommer att vara {data.question}"}
      ],
      question=data.question
      )
  
class LLMRunner(Runnable[PromptBuilderOutput, LLMRunnerOutput ]):
  pipe = pipeline ("text-generation", model="HuggingFaceTB/SmolLM2-1.7B-Instruct")

  def invoke(self, data: PromptBuilderOutput) -> LLMRunnerOutput:
    logger.info("Step2 : LLMRunner - Calling a model")
    result = self.pipe(data.prompt, max_new_tokens=200)
    return LLMRunnerOutput(raw_text=result[0]["generated_text"][-1]["content"], question=data.question)
  
class ResponseParser(Runnable[LLMRunnerOutput, ResponseParserOutput]):
  def invoke(self, data: LLMRunnerOutput) -> ResponseParserOutput:
    answer = data.raw_text
    if "Svar:" in answer:
      answer = answer.split("Svar:")[1].strip()
    logger.info("Step3 : ResponseParser - Parsing the question in to an answer")
    return ResponseParserOutput(
      question=data.question,
      answer=answer,
      model="HuggingFaceTB/SmolLM2-1.7B-Instruct"
    )