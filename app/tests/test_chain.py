from . import steps

def prompt_builder_test():
  assert prompt[0]["role"] == "system"
  assert resp.json()prompt[0]["content"] == "Du är en dataanalytiker svara kortfattat på svenska"
  assert question == 