from ..chain.steps import PromptBuilder, PromptBuilderInput

def test_prompt_builder():
  input = PromptBuilderInput(question="You are a dataanalityc, answer short on these", stats={"age": {"mean": 30.0}})
  result = PromptBuilder().invoke(input)
  assert result.question == "You are a dataanalityc, answer short on these"
  assert result.prompt [0]["role"] == "system"