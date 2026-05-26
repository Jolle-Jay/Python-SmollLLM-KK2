from pydantic import BaseModel, ConfigDict, SerializeAsAny
from typing import Any, Callable, Generic, TypeVar

I = TypeVar("I")
O = TypeVar("O")
M = TypeVar("M")

class Runnable(BaseModel, Generic[I, O]):
  model_config = ConfigDict(arbitrary_types_allowed=True)

  def invoke(self, data: I) -> O:
    return NotImplementedError("Subclasses must implement invoke")