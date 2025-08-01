"""Utilities for chain-of-thought prompting."""

from collections.abc import Collection, Iterable, Iterator, Sequence
import contextlib
import random
import re

from concordia.document import document
from concordia.language_model import language_model
import numpy as np

DEFAULT_MAX_CHARACTERS = 200
DEFAULT_MAX_TOKENS = DEFAULT_MAX_CHARACTERS // 4

DEBUG_TAG = 'debug'
STATEMENT_TAG = 'statement'
QUESTION_TAG = 'question'
RESPONSE_TAG = 'response'
MODEL_TAG = 'model'
INTERACTIVE_TAGS = frozenset(
    {DEBUG_TAG, STATEMENT_TAG, QUESTION_TAG, RESPONSE_TAG, MODEL_TAG}
)


_YESNO = ['No', 'Yes']


def _letters():
  """Yields the letters from a to z."""
  yield from (chr(ord('a') + i) for i in range(26))


class InteractiveDocument(document.Document):
  """A document formed by interaction with a language model."""

  def __init__(
      self,
      model: language_model.LanguageModel,
      contents: Iterable[document.Content] = (),
      rng: np.random.Generator | None = None,
  ) -> None:
    """Initializes the instance.

    Args:
      model: language model to interact with.
      contents: initial contents of the document.
      rng: randomization source.
    """
    super().__init__(contents)
    if rng:
      self._rng = rng
    else:
      self._rng = np.random.default_rng()
    self._model = model
    self._model_view = self.view()
    # TODO: b/311191701 - debug log some useful stuff?

  def view(
      self,
      include_tags: Iterable[str] = (),
      exclude_tags: Iterable[str] = (DEBUG_TAG,),
  ) -> document.View:
    """Returns a view of the document.

    Args:
      include_tags: specifies which tags to include in the view.
      exclude_tags: specifies which tags to exclude from the view.
    """
    return super().view(include_tags=include_tags, exclude_tags=exclude_tags)

  def copy(self) -> 'InteractiveDocument':
    """See base class."""
    # TODO: b/311192069 - what about rng?
    return InteractiveDocument(
        model=self._model, contents=self.contents(), rng=self._rng
    )

  @contextlib.contextmanager
  def edit(self) -> Iterator['InteractiveDocument']:
    """See base class."""
    # TODO: b/311192069 - what about rng?
    edit = InteractiveDocument(model=self._model, rng=self._rng)
    yield edit
    self.extend(edit.contents())

  def debug(
      self, text: str, *, tags: Collection[str] = (), end: str = '\n'
  ) -> None:
    """Appends debug text to the document.

    Args:
      text: text to append.
      tags: additional tags for appended text.
      end: appended to `text`.
    """
    self.append(text + end, tags=[DEBUG_TAG, *tags])

  def statement(
      self, text: str, *, tags: Collection[str] = (), end: str = '\n'
  ) -> None:
    """Appends a statement to the document.

    Args:
      text: text to append.
      tags: additional tags for appended text.
      end: appended to `text`.
    """
    self.append(text + end, tags=[STATEMENT_TAG, *tags])

  def _question(
      self, text: str, *, tags: Collection[str] = (), end: str = ''
  ) -> None:
    """Appends a question to the document."""
    self.append(text + end, tags=[QUESTION_TAG, *tags])

  def _response(
      self, text: str, *, tags: Collection[str] = (), end: str = ''
  ) -> None:
    """Appends a response to the document."""
    self.append(text + end, tags=[RESPONSE_TAG, *tags])

  def _model_response(
      self, text: str, *, tags: Collection[str] = (), end: str = ''
  ) -> None:
    """Appends a response to the document that was generated by the model."""
    self.append(text + end, tags=[RESPONSE_TAG, MODEL_TAG, *tags])

  def open_question(
      self,
      question: str,
      *,
      forced_response: str | None = None,
      answer_prefix: str = '',
      answer_suffix: str = '',
      max_tokens: int = DEFAULT_MAX_TOKENS,
      terminators: Collection[str] = ('\n',),
      question_label: str = 'Question',
      answer_label: str = 'Answer',
  ) -> str:
    """Asks the agent an open question and appends it to the document.

    Args:
      question: the question to ask.
      forced_response: forces the document to provide this response. The LLM
        will not be consulted. If answer_prefix is in the forced response then
        remove it.
      answer_prefix: a prefix to append to the model's prompt.
      answer_suffix: a suffix to append to the model's response.
      max_tokens: the maximum number of tokens to sample from the model.
      terminators: strings that must not be present in the model's response. If
        emitted by the model the response will be truncated before them.
      question_label: the label to use for the question, typically "Question".
      answer_label: the label to use for the answer, typically "Answer".

    Returns:
      The agents truncated response (or `forced_response` is provided).
    """
    self._question(f'{question_label}: {question}\n')
    self._response(f'{answer_label}: {answer_prefix}')
    if forced_response is None:
      response = self._model.sample_text(
          prompt=self._model_view.text(),
          max_tokens=max_tokens,
          terminators=terminators,
      )
    else:
      response = forced_response
    response = response.removeprefix(answer_prefix)
    self._model_response(response)
    self._response(f'{answer_suffix}\n')
    return response

  def open_question_diversified(
      self,
      question: str,
      *,
      forced_response: str | None = None,
      num_samples: int = 10,
      max_tokens: int = DEFAULT_MAX_TOKENS,
      terminators: Collection[str] = (),
      question_label: str = 'Question',
      answer_label: str = 'Answer',
  ) -> str:
    """Asks the agent an open question and appends it to the document.

    The agent is asked to provide multiple answers, from which one is selected
    randomly. This increases the diversity of the answers.

    Args:
      question: the question to ask.
      forced_response: forces the document to provide this response. The LLM
        will not be consulted. If answer_prefix is in the forced response then
        remove it.
      num_samples: how many samples to generate.
      max_tokens: the maximum number of tokens to sample from the model.
      terminators: strings that must not be present in the model's response. If
        emitted by the model the response will be truncated before them.
        Importantly, the truncation is done on the final sample only and does
        not affect the intermediate samples.
      question_label: the label to use for the question, typically "Question".
      answer_label: the label to use for the answer, typically "Answer".

    Returns:
      The agents truncated response (or `forced_response` is provided).

    Raises:
      Warning: if the LLM does not generate the expected number of answers.
    """

    def truncate_string(s, tr):
      """Truncates a string to the first occurrence of any of the terminators.

      Args:
          s: The string to truncate.
          tr: A set of strings representing the terminators.

      Returns:
          The truncated string, or the original string if no terminator is
          found.
      """

      # Find the earliest index where any terminator appears
      earliest_index = len(s)  # Initialize to the end of the string
      for terminator in tr:
        index = s.find(terminator)
        if index != -1 and index < earliest_index:
          earliest_index = index

      # Truncate the string if a terminator was found
      if earliest_index < len(s):
        return s[:earliest_index]
      else:
        return s

    self._question(
        f'Task: generate {num_samples} {answer_label}s to the following'
        f' {question_label}:\nQuestion: {question}\n'
    )
    if forced_response is None:
      self._response(f'{answer_label}s:\n1. ')
      candidates = self._model.sample_text(
          prompt=self._model_view.text(),
          max_tokens=max_tokens * num_samples,
          terminators=[],
      )
      self.statement(candidates)

      candidates = candidates.splitlines()

      if len(candidates) != num_samples:
        self.debug(
            f'LLM generated {len(candidates)} answers instead of {num_samples}'
        )
        if len(candidates) < 2:
          raise Warning(
              f'LLM generated only {len(candidates)} initial answers.'
          )
      candidates = [re.sub(r'^\d+\.\s*', '', line) for line in candidates]
      response = random.choice(candidates)
      response = truncate_string(response, terminators)

    else:
      response = forced_response

    self._response(f'Final {answer_label}: ')
    self._model_response(f'{response}\n')
    return response

  def multiple_choice_question(
      self,
      question: str,
      answers: Sequence[str],
      randomize_choices: bool = True,
  ) -> int:
    """Presents a multiple choice to the agent.

    Args:
      question: the question to ask the agent.
      answers: the choice of answers
      randomize_choices: whether to randomize the order of the choices.

    Returns:
      The index of the sampled answer.
    """
    if randomize_choices:
      original_indices = self._rng.permutation(len(answers))
    else:
      original_indices = range(len(answers))
    options = {key: answers[i] for key, i in zip(_letters(), original_indices)}
    self._question(f'Question: {question}\n')
    for key, option in options.items():
      self._question(f'  ({key}) {option}\n')

    self._response('Answer: (')
    idx, response, debug = self._model.sample_choice(
        prompt=self._model_view.text(),
        responses=list(options.keys()),
    )
    self._model_response(response)
    self._response(')\n')
    self.debug(f'[{debug}]')
    return original_indices[idx]

  def yes_no_question(self, question: str) -> bool:
    """Presents a yes/no question to the agent.

    Args:
      question: the question to ask the agent.

    Returns:
      True iff the answer was answered with Yes.
    """
    return self.multiple_choice_question(question, _YESNO) == _YESNO.index(
        'Yes'
    )
