"""Base class for OpenAI-compatible models."""

from collections.abc import Collection, Sequence

from concordia.language_model import language_model
from concordia.utils import sampling
from concordia.utils import measurements as measurements_lib
from openai import OpenAI
from typing_extensions import override


_MAX_MULTIPLE_CHOICE_ATTEMPTS = 150


class BaseOAICompatibleModel(language_model.LanguageModel):
  """Base class for models using an OpenAI-compatible API."""

  def __init__(
      self,
      model_name: str,
      client: OpenAI,
      measurements: measurements_lib.Measurements | None = None,
      channel: str = language_model.DEFAULT_STATS_CHANNEL,
  ):
    """Initializes the base instance.

    Args:
      model_name: The model name to use for the API call.
      client: An initialized OpenAI client.
      measurements: The measurements object to log usage statistics to.
      channel: The channel to write the statistics to.
    """
    self._model_name = model_name
    self._measurements = measurements
    self._channel = channel
    self._client = client

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
    """Samples text from the model."""
    # The system prompt and few-shot examples from the original file are kept.
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

    response = self._client.chat.completions.create(
        model=self._model_name,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
        stop=terminators,
        seed=seed,
    )

    if self._measurements is not None:
      self._measurements.publish_datum(
          self._channel,
          {'raw_text_length': len(response.choices[0].message.content)},
      )
    return response.choices[0].message.content

  @override
  def sample_choice(
      self,
      prompt: str,
      responses: Sequence[str],
      *,
      seed: int | None = None,
  ) -> tuple[int, str, dict[str, float]]:
    """Samples a choice from a list of responses."""
    prompt = (
        prompt
        + '\nRespond EXACTLY with one of the following strings:\n'
        + '\n'.join(responses)
        + '.'
    )

    sample = ''
    answer = ''
    for attempts in range(_MAX_MULTIPLE_CHOICE_ATTEMPTS):
      temperature = sampling.dynamically_adjust_temperature(
          attempts, _MAX_MULTIPLE_CHOICE_ATTEMPTS
      )

      sample = self.sample_text(
          prompt,
          temperature=temperature,
          seed=seed,
      )
      answer = sampling.extract_choice_response(sample)
      try:
        idx = responses.index(answer)
      except ValueError:
        continue
      else:
        if self._measurements is not None:
          self._measurements.publish_datum(
              self._channel, {'choices_calls': attempts}
          )
        debug = {}
        return idx, responses[idx], debug

    raise language_model.InvalidResponseError((
        f'Too many multiple choice attempts.\nLast attempt: {sample}, '
        + f'extracted: {answer}'
    ))
