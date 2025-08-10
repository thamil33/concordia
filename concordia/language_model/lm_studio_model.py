"""Language Model that uses a local LM Studio server."""

import os
from collections.abc import Collection

from concordia.language_model import language_model
from concordia.language_model.base_oai_compatible import BaseOAICompatibleModel
from concordia.utils import measurements as measurements_lib
import openai
from typing_extensions import override


class LmStudioModel(BaseOAICompatibleModel):
  """Language Model that uses a local model served by LM Studio."""

  def __init__(
      self,
      model_name: str | None = None,
      *,
      base_url: str | None = None,
      timeout: float | None = None,
      stream: bool = False,
      measurements: measurements_lib.Measurements | None = None,
      channel: str = language_model.DEFAULT_STATS_CHANNEL,
  ):
    """Initializes the instance.

    Args:
      model_name: The model identifier. If None, will use the LM_STUDIO_MODEL
        environment variable. Note: For LM Studio, this can often be a
        placeholder as the model is pre-loaded in the UI.
      base_url: The base URL of the LM Studio server. If None, will use the
        LM_STUDIO_URL environment variable, falling back to
        "http://127.0.0.1:1234/v1".
      timeout: The timeout for API requests in seconds. If None, will use the
        LM_STUDIO_TIMEOUT environment variable, falling back to 600.0 (10
        minutes).
      stream: Whether to stream the response from the model.
      measurements: The measurements object to log usage statistics to.
      channel: The channel to write the statistics to.
    """
    if base_url is None:
      base_url = os.environ.get('LM_STUDIO_URL', 'http://127.0.0.1:1234/v1')
    if model_name is None:
      model_name = os.environ.get('LM_STUDIO_MODEL')
    if timeout is None:
        timeout_str = os.environ.get('LM_STUDIO_TIMEOUT', '600.0')
        timeout = float(timeout_str)

    if not model_name:
      raise ValueError(
          'LM Studio model name must be provided either as the `model_name`'
          + ' argument or through the `LM_STUDIO_MODEL` environment variable.'
      )

    # LM Studio's local server does not require an API key.
    client = openai.OpenAI(
        api_key="lm-studio",
        base_url=base_url,
        timeout=timeout,
    )

    self._stream = stream

    super().__init__(
        model_name=model_name,
        client=client,
        measurements=measurements,
        channel=channel
    )

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
    """Samples text from the model, with optional streaming."""
    messages = [
        {
            'role': 'system',
            'content': (
                'You always continue sentences provided '
                + 'by the user and you never repeat what '
                + 'the user already said.'
            ),
        },
        {
            'role': 'user',
            'content': 'Question: Is Jake a turtle?\nAnswer: Jake is ',
        },
        {'role': 'assistant', 'content': 'not a turtle.'},
        {
            'role': 'user',
            'content': (
                'Question: What is Priya doing right now?\nAnswer: '
                + 'Priya is currently '
            ),
        },
        {'role': 'assistant', 'content': 'sleeping.'},
        {'role': 'user', 'content': prompt},
    ]

    if not self._stream:
      response = self._client.chat.completions.create(
          model=self._model_name,
          messages=messages,
          temperature=temperature,
          max_tokens=max_tokens,
          timeout=timeout,
          stop=terminators,
          seed=seed,
      )
      result = response.choices[0].message.content
    else:
      stream = self._client.chat.completions.create(
          model=self._model_name,
          messages=messages,
          temperature=temperature,
          max_tokens=max_tokens,
          timeout=timeout,
          stop=terminators,
          seed=seed,
          stream=True,
      )
      full_response = []
      for chunk in stream:
        content = chunk.choices[0].delta.content
        if content is not None:
          full_response.append(content)
      result = "".join(full_response)

    if self._measurements is not None:
      self._measurements.publish_datum(
          self._channel,
          {'raw_text_length': len(result)},
      )
    return result
