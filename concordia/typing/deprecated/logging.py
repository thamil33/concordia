

"""Types for logging."""

from collections.abc import Mapping, Sequence
import dataclasses
from typing import Any, Callable
from concordia.typing.deprecated import entity as entity_lib

LoggingChannel = Callable[[Mapping[str, Any]], None]

NoOpLoggingChannel = lambda x: None


@dataclasses.dataclass(frozen=True)
class Metric:
  question: str
  output_type: entity_lib.OutputType
  options: Sequence[str] | None = None
  context: str | None = None
