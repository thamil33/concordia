"""A language model that wraps a primary and a fallback model."""

from collections.abc import Collection, Sequence, Mapping
from typing import Any, Type

from concordia.language_model import language_model
import retry
from typing_extensions import override


class FallbackLanguageModel(language_model.LanguageModel):
  """Wraps a primary and a fallback model with specific retry logic."""

  def __init__(
      self,
      primary_model: language_model.LanguageModel,
      fallback_model: language_model.LanguageModel,
      primary_retry_exceptions: Collection[Type[Exception]] = (Exception,),
  ):
    """Initializes the FallbackLanguageModel.

    Args:
      primary_model: The main model to use.
      fallback_model: The model to use if the primary model fails.
      primary_retry_exceptions: Exceptions to trigger a retry on the primary.
    """
    self._primary_model = primary_model
    self._fallback_model = fallback_model
    self._primary_retry_exceptions = tuple(primary_retry_exceptions)

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
    try:
      # Decorator for the primary model with a limited number of retries.
      @retry.retry(
          self._primary_retry_exceptions,
          tries=2,
          delay=61,
          backoff=2, # Exponential backoff
          jitter=(1, 5)
      )
      def _call_primary():
        return self._primary_model.sample_text(
            prompt,
            max_tokens=max_tokens,
            terminators=terminators,
            temperature=temperature,
            seed=seed,
        )
      return _call_primary()
    except Exception as e:
      print(f"Primary model failed after retries: {e}. Switching to fallback.")
      # Decorator for the fallback model with unlimited retries.
      @retry.retry(
          Exception, # Retry on any exception for the fallback
          tries=-1,  # Infinite retries
          delay=61,
          backoff=2,
          jitter=(1, 5)
      )
      def _call_fallback():
        return self._fallback_model.sample_text(
            prompt,
            max_tokens=max_tokens,
            terminators=terminators,
            temperature=temperature,
            seed=seed,
        )
      return _call_fallback()

  @override
  def sample_choice(
      self,
      prompt: str,
      responses: Sequence[str],
      *,
      seed: int | None = None,
  ) -> tuple[int, str, Mapping[str, Any]]:
    try:
      @retry.retry(
          self._primary_retry_exceptions,
          tries=2,
          delay=61,
          backoff=2,
          jitter=(1, 5)
      )
      def _call_primary():
        return self._primary_model.sample_choice(prompt, responses, seed=seed)
      return _call_primary()
    except Exception as e:
      print(f"Primary model failed during choice sampling: {e}. Switching to fallback.")
      @retry.retry(
          Exception,
          tries=-1,
          delay=61,
          backoff=2,
          jitter=(1, 5)
      )
      def _call_fallback():
        return self._fallback_model.sample_choice(prompt, responses, seed=seed)
      return _call_fallback()
