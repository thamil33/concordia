# Copyright 2023 DeepMind Technologies Limited.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google AI Studio Language Model API."""

from collections.abc import Collection, Mapping, Sequence
import copy
import os
import time

from concordia.language_model import language_model
from concordia.utils import sampling
from concordia.utils import text
from concordia.utils.deprecated import measurements as measurements_lib
import google.generativeai as genai
from typing_extensions import override


MAX_MULTIPLE_CHOICE_ATTEMPTS = 20

DEFAULT_HISTORY = [
    {
        'role': 'user',
        'parts': [
            ('You always continue sentences provided by the user, and you ' +
             'never repeat what the user already said.'),
        ],
    },
    {
        'role': 'model',
        'parts': [
            ('I always continue user-provided text and never repeat what the ' +
             'user already said.'),
        ],
    },
    {
        'role': 'user',
        'parts': [
            'Question: Is Jake a turtle?\nAnswer: Jake is ',
        ],
    },
    {
        'role': 'model',
        'parts': [
            'not a turtle.',
        ],
    },
    {
        'role': 'user',
        'parts': [
            ('Question: What is Priya doing right now?\n'
             'Answer: Priya is currently '),
        ],
    },
    {
        'role': 'model',
        'parts': [
            'sleeping.',
        ],
    },
]


DEFAULT_SAFETY_SETTINGS = (
    {
        'category': 'HARM_CATEGORY_HARASSMENT',
        'threshold': 'BLOCK_MEDIUM_AND_ABOVE',
    },
    {
        'category': 'HARM_CATEGORY_HATE_SPEECH',
        'threshold': 'BLOCK_MEDIUM_AND_ABOVE',
    },
    {
        'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT',
        'threshold': 'BLOCK_MEDIUM_AND_ABOVE',
    },
    {
        'category': 'HARM_CATEGORY_DANGEROUS_CONTENT',
        'threshold': 'BLOCK_MEDIUM_AND_ABOVE',
    },
)


class GoogleAIStudioLanguageModel(language_model.LanguageModel):
  """Language model API obtained via the Google AI Studio."""

  def __init__(
      self,
      model_name: str = 'gemini-1.5-pro-latest',
      *,
      api_key: str | None = None,
      safety_settings: Sequence[Mapping[str, str]] = DEFAULT_SAFETY_SETTINGS,
      measurements: measurements_lib.Measurements | None = None,
      channel: str = language_model.DEFAULT_STATS_CHANNEL,
      sleep_periodically: bool = False,
  ) -> None:
    """Initializes a model API instance using Google AI Studio.

    Args:
      model_name: which language model to use. For more details, see
        https://aistudio.google.com/
      api_key: The API key to use when accessing the Google AI Studio API, if
        None will use the GOOGLE_API_KEY environment variable.
      safety_settings: See https://ai.google.dev/gemini-api/docs/safety-guidance
      measurements: The measurements object to log usage statistics to
      channel: The channel to write the statistics to
      sleep_periodically: Whether to sleep between API calls to avoid rate limit
    """
    if api_key is None:
      api_key = os.environ['GOOGLE_API_KEY']
    self._api_key = api_key
    self._model_name = model_name
    self._safety_settings = safety_settings
    self._sleep_periodically = sleep_periodically

    genai.configure(api_key=self._api_key)
    self._model = genai.GenerativeModel(
        model_name=self._model_name,
        safety_settings=safety_settings,
    )

    self._measurements = measurements
    self._channel = channel

    self._calls_between_sleeping = 10
    self._n_calls = 0

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
    del timeout
    if seed is not None:
      raise NotImplementedError('Unclear how to set seed for aistudio models.')

    self._n_calls += 1
    if self._sleep_periodically and (
        self._n_calls % self._calls_between_sleeping == 0):
      print('Sleeping for 10 seconds...')
      time.sleep(10)

    chat = self._model.start_chat(history=copy.deepcopy(DEFAULT_HISTORY))
    sample = chat.send_message(
        content=prompt,
        generation_config={
            'temperature': temperature,
            'max_output_tokens': max_tokens,
            'stop_sequences': terminators,
            'candidate_count': 1,
            'top_p': 0.95,
            'top_k': 64,
            'response_mime_type': 'text/plain',
        },
        safety_settings=self._safety_settings,
        stream=False
    )
    try:
      response = sample.candidates[0].content.parts[0].text
    except ValueError as e:
      print('An error occurred: ', e)
      print(f'prompt: {prompt}')
      print(f'sample: {sample}')
      response = ''
    if self._measurements is not None:
      self._measurements.publish_datum(
          self._channel,
          {'raw_text_length': len(response)})
    return text.truncate(response, delimiters=terminators)

  @override
  def sample_choice(
      self,
      prompt: str,
      responses: Sequence[str],
      *,
      seed: int | None = None,
  ) -> tuple[int, str, dict[str, float]]:
    sample = ''
    answer = ''
    for attempts in range(MAX_MULTIPLE_CHOICE_ATTEMPTS):
      # Increase temperature after the first failed attempt.
      temperature = sampling.dynamically_adjust_temperature(
          attempts, MAX_MULTIPLE_CHOICE_ATTEMPTS)

      question = (
          'The following is a multiple choice question. Respond ' +
          'with one of the possible choices, such as (a) or (b). ' +
          f'Do not include reasoning.\n{prompt}')
      sample = self.sample_text(
          question,
          max_tokens=256,  # This is wasteful, but Gemini blocks lower values.
          temperature=temperature,
          seed=seed,
      )
      answer = sampling.extract_choice_response(sample)
      try:
        idx = responses.index(answer)
      except ValueError:
        print(f'Sample choice fail: {answer} extracted from {sample}.')
        continue
      else:
        if self._measurements is not None:
          self._measurements.publish_datum(
              self._channel,
              {'choices_calls': attempts})
        debug = {}
        return idx, responses[idx], debug

    raise language_model.InvalidResponseError(
        (f'Too many multiple choice attempts.\nLast attempt: {sample}, ' +
         f'extracted: {answer}')
    )
