from ..chain.steps import PromptBuilder, PromptBuilderInput, PromptBuilderOutput, LLMRunner, LLMRunnerOutput

def test_prompt_builder():
  input = PromptBuilderInput(question="You are a dataanalityc, answer short on these", stats={"age": {"mean": 30.0}})
  result = PromptBuilder().invoke(input)
  assert result.question == "You are a dataanalityc, answer short on these"
  assert result.prompt [0]["role"] == "system"

def test_llm_runner(monkeypatch):
  monkeypatch.setattr(LLMRunner, "invoke", lambda self, data: LLMRunnerOutput(raw_text="Fake answer", question="What is the mean age?"))
  input = PromptBuilderOutput(prompt=[{"role": "system", "content": "test"}], question="What is the mean age?")
  result = LLMRunner().invoke(input)
  assert result.raw_text == "Fake answer"
  assert result.question == "What is the mean age?"