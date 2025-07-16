"""Language Model that uses OpenRouter API."""

import os
import time
import logging
import inspect
from collections.abc import Collection, Mapping, Sequence
from typing import Any

from .language_model import (
    LanguageModel,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TERMINATORS,
    DEFAULT_TEMPERATURE,
    DEFAULT_TIMEOUT_SECONDS,
    DEFAULT_STATS_CHANNEL,
)
from concordia.language_model import language_model
from ..utils import sampling
from ..utils import measurements as measurements_lib
from openai import OpenAI, RateLimitError
from typing_extensions import override


_MAX_MULTIPLE_CHOICE_ATTEMPTS = 20


class BaseOpenRouterLanguageModel(language_model.LanguageModel):
  """Language Model that uses OpenRouter API."""
  def __init__(
      self,
      model_name: str,
      *,
      api_key: str | None = None,
      measurements: measurements_lib.Measurements | None = None,
      channel: str = DEFAULT_STATS_CHANNEL,
      verbose_logging: bool = False,
  ):
    """Initializes the instance.

    Args:
      model_name: The language model to use (e.g., "mistralai/mistral-small-3.1-24b-instruct:free").
      api_key: The OpenRouter API key. If None, will use the OPENROUTER_API_KEY environment variable.
      measurements: The measurements object to log usage statistics to.
      channel: The channel to write the statistics to.
      verbose_logging: If True, log detailed information about each LLM call including caller context.
    """
    if api_key is None:
      api_key = os.environ['OPENROUTER_API_KEY']

    self._model_name = model_name
    self._measurements = measurements
    self._channel = channel
    self._verbose_logging = verbose_logging
    self._logger = logging.getLogger(f"pysrcai.openrouter.{model_name}")

    # Configure logging level based on verbose setting
    if verbose_logging:
      self._logger.setLevel(logging.INFO)
      # Create console handler if none exists
      if not self._logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '[%(asctime)s] %(name)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)
        self._logger.propagate = False

    # Use OpenAI client with OpenRouter endpoint
    self._client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

  def _extract_entity_context(self, frame):
    """Extract entity/agent context from call stack."""
    current_frame = frame
    for _ in range(10):  # Look up to 10 frames back
      if current_frame is None:
        break

      local_vars = current_frame.f_locals

      # Look for common entity/agent variables
      for var_name in ['self', 'entity', 'agent', 'character']:
        if var_name in local_vars:
          obj = local_vars[var_name]
          if hasattr(obj, '_name'):
            return f"{obj.__class__.__name__}({obj._name})"
          elif hasattr(obj, 'name'):
            return f"{obj.__class__.__name__}({obj.name})"
          elif hasattr(obj, '__class__') and 'Entity' in obj.__class__.__name__:
            return f"{obj.__class__.__name__}"

      current_frame = current_frame.f_back

    return None

  @override
  def sample_text(
      self,
      prompt: str,
      *,
      max_tokens: int = DEFAULT_MAX_TOKENS,
      terminators: Collection[str] = DEFAULT_TERMINATORS,
      temperature: float = DEFAULT_TEMPERATURE,
      timeout: float = DEFAULT_TIMEOUT_SECONDS,
      seed: int | None = None,
  ) -> str:
    """Samples text from the OpenRouter model."""

    # Get caller context for verbose logging
    if self._verbose_logging:
      caller_frame = inspect.currentframe().f_back
      caller_info = f"{caller_frame.f_code.co_filename}:{caller_frame.f_lineno}"
      entity_context = self._extract_entity_context(caller_frame)

      self._logger.info(
          f"LLM Call from {entity_context or 'Unknown'} | "
          f"Caller: {caller_info} | "
          f"Model: {self._model_name} | "
          f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}"
      )

    messages = [{"role": "user", "content": prompt}]

    while True:
      try:
        response = self._client.chat.completions.create(
            model=self._model_name,
            messages=messages,
            max_tokens=max_tokens,
            seed=seed,
            timeout=timeout,
        )
        break  # Success, exit the retry loop
      except RateLimitError as e:
        if "429" in str(e) or "rate limit" in str(e).lower():
          print(f"Rate limit hit (429), waiting 61 seconds before retry...")
          time.sleep(61)
          continue
        else:
          raise  # Re-raise if it's not a 429 error
      except Exception as e:
        # For other exceptions, just re-raise
        raise

    result = response.choices[0].message.content

    # Handle terminators
    if terminators:
      for terminator in terminators:
        if terminator in result:
          result = result.split(terminator)[0]

    # Log measurements if available
    if self._measurements is not None:
      self._measurements.publish_datum(
          channel=self._channel,
          datum={'prompt_tokens': response.usage.prompt_tokens,
                 'completion_tokens': response.usage.completion_tokens,
                 'model': self._model_name})

    return result

  @override
  def sample_choice(
      self,
      prompt: str,
      responses: Sequence[str],
      *,
      seed: int | None = None,
  ) -> tuple[int, str, Mapping[str, Any]]:
    """Samples a response from those available using multiple choice."""
    question = (
        prompt +
        '\nRespond EXACTLY with one of the following options:\n' +
        '\n'.join(f'{i}: {response}' for i, response in enumerate(responses))
    )

    for _ in range(_MAX_MULTIPLE_CHOICE_ATTEMPTS):
      # Use sample_text which already has 429 handling
      answer = self.sample_text(question, seed=seed)

      # Try to parse the choice
      for i, response in enumerate(responses):
        if str(i) in answer[:10]:  # Look for the number in first part of answer
          return i, response, {'answer': answer}

      # If parsing fails, try fuzzy matching
      answer_lower = answer.lower()
      for i, response in enumerate(responses):
        if response.lower() in answer_lower:
          return i, response, {'answer': answer}

    # If all attempts fail, return random choice
    choice_idx = sampling.sample_from_scores([1.0] * len(responses), seed=seed)
    return choice_idx, responses[choice_idx], {'answer': answer, 'fallback': True}
