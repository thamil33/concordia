"""A mock Language Model."""

from collections.abc import Collection, Sequence

from concordia.language_model import language_model
from typing_extensions import override


class MockModel(language_model.LanguageModel):
  """Mock LLM with fixed responses."""

  def __init__(
      self, response: str = 'Quick brown fox jumps over a lazy dog'
  ) -> None:
    """Initializes the instance.

    Args:
      response: string that the model returns when sampling text
    """
    self._response = response

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
    del (
        prompt,
        max_tokens,
        terminators,
        temperature,
        timeout,
        seed,
    )
    return self._response

  @override
  def sample_choice(
      self,
      prompt: str,
      responses: Sequence[str],
      *,
      seed: int | None = None,
  ) -> tuple[int, str, dict[str, float]]:
    del prompt, seed
    return 0, responses[0], {}
