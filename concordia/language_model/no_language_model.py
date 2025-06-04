
"""Language model that always returns empty strings and choice 0 (for debug)."""

from collections.abc import Collection, Mapping, Sequence
from typing import Any

from concordia.language_model import language_model
from typing_extensions import override


class NoLanguageModel(language_model.LanguageModel):
  """Debuging model that always returns empty strings and choice 0."""

  def __init__(
      self,
  ) -> None:
    """Debuging model that always returns empty strings and choice 0."""
  pass

  @override
  def sample_text(
      self,
      prompt: str,
      *,
      max_tokens: int = language_model.DEFAULT_MAX_TOKENS,
      terminators: Collection[str] = language_model.DEFAULT_TERMINATORS,
      temperature: float = language_model.DEFAULT_TEMPERATURE,
      timeout: float = language_model.DEFAULT_TIMEOUT_SECONDS,
      seed: int | None = None,
  ) -> str:
    return ''

  @override
  def sample_choice(
      self,
      prompt: str,
      responses: Sequence[str],
      *,
      seed: int | None = None,
  ) -> tuple[int, str, Mapping[str, Any]]:
    return 0, responses[0], {}
