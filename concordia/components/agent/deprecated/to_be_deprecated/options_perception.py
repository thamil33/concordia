
"""Agent component for situation perception."""
import datetime
from typing import Callable, Sequence

from concordia.associative_memory.deprecated import associative_memory
from concordia.document import interactive_document
from concordia.language_model import language_model
from concordia.typing.deprecated import component
import termcolor


class AvailableOptionsPerception(component.Component):
  """This component answers the question 'what actions are available to me?'."""

  def __init__(
      self,
      name: str,
      model: language_model.LanguageModel,
      memory: associative_memory.AssociativeMemory,
      agent_name: str,
      components: Sequence[component.Component] | None = None,
      clock_now: Callable[[], datetime.datetime] | None = None,
      num_memories_to_retrieve: int = 25,
      verbose: bool = False,
  ):
    """Initializes the component.

    Args:
      name: The name of the component.
      model: The language model to use.
      memory: The memory to use.
      agent_name: The name of the agent.
      components: The components to condition the answer on.
      clock_now: time callback to use for the state.
      num_memories_to_retrieve: The number of memories to retrieve.
      verbose: Whether to print the last chain.
    """
    self._verbose = verbose
    self._model = model
    self._memory = memory
    self._state = ''
    self._components = components or []
    self._agent_name = agent_name
    self._clock_now = clock_now
    self._num_memories_to_retrieve = num_memories_to_retrieve
    self._name = name
    self._last_update = datetime.datetime.min
    self._history = []

  def name(self) -> str:
    return self._name

  def state(self) -> str:
    return self._state

  def get_last_log(self):
    if self._history:
      return self._history[-1].copy()

  def get_components(self) -> Sequence[component.Component]:
    return self._components

  def update(self) -> None:
    if self._clock_now() == self._last_update:
      return
    self._last_update = self._clock_now()

    mems = '\n'.join(
        self._memory.retrieve_recent(
            self._num_memories_to_retrieve, add_time=True
        )
    )

    prompt = interactive_document.InteractiveDocument(self._model)
    prompt.statement(f'Memories of {self._agent_name}:\n{mems}')

    if self._clock_now is not None:
      prompt.statement(f'Current time: {self._clock_now()}.\n')

    component_states = '\n'.join([
        f"{self._agent_name}'s "
        + (comp.name() + ':\n' + comp.state())
        for comp in self._components
    ])
    prompt.statement(component_states)

    question = (
        'Given the statements above, what actions are available to '
        f' {self._agent_name} right now?'
    )
    self._state = prompt.open_question(
        question,
        max_tokens=1000,
    )
    self._state = f'{self._agent_name} is currently {self._state}'

    self._last_chain = prompt
    if self._verbose:
      print(termcolor.colored(self._last_chain.view().text(), 'green'), end='')

    update_log = {
        'date': self._clock_now(),
        'Summary': question,
        'State': self._state,
        'Chain of thought': prompt.view().text().splitlines(),
    }
    self._history.append(update_log)


class BestOptionPerception(component.Component):
  """This component answers 'which action is best for achieving my goal?'."""

  def __init__(
      self,
      name: str,
      model: language_model.LanguageModel,
      memory: associative_memory.AssociativeMemory,
      agent_name: str,
      components: Sequence[component.Component] | None = None,
      clock_now: Callable[[], datetime.datetime] | None = None,
      num_memories_to_retrieve: int = 25,
      verbose: bool = False,
  ):
    """Initializes the component.

    Args:
      name: The name of the component.
      model: The language model to use.
      memory: The memory to use.
      agent_name: The name of the agent.
      components: The components to condition the answer on.
      clock_now: time callback to use for the state.
      num_memories_to_retrieve: The number of memories to retrieve.
      verbose: Whether to print the last chain.
    """
    self._verbose = verbose
    self._model = model
    self._memory = memory
    self._state = ''
    self._components = components or []
    self._agent_name = agent_name
    self._clock_now = clock_now
    self._num_memories_to_retrieve = num_memories_to_retrieve
    self._name = name
    self._last_update = datetime.datetime.min
    self._history = []

  def name(self) -> str:
    return self._name

  def state(self) -> str:
    return self._state

  def get_last_log(self):
    if self._history:
      return self._history[-1].copy()

  def get_components(self) -> Sequence[component.Component]:
    return self._components

  def update(self) -> None:
    if self._clock_now() == self._last_update:
      return
    self._last_update = self._clock_now()

    mems = '\n'.join(
        self._memory.retrieve_recent(
            self._num_memories_to_retrieve, add_time=True
        )
    )

    prompt = interactive_document.InteractiveDocument(self._model)
    prompt.statement(f'Memories of {self._agent_name}:\n{mems}')

    if self._clock_now is not None:
      prompt.statement(f'Current time: {self._clock_now()}.\n')

    component_states = '\n'.join([
        f"{self._agent_name}'s "
        + (comp.name() + ':\n' + comp.state())
        for comp in self._components
    ])
    prompt.statement(component_states)

    question = (
        f'Given the statements above, which of {self._agent_name}\'s options '
        f'has the highest likelihood of causing {self._agent_name} to achieve '
        'their goal? If multiple options have the same likelihood, select the '
        f'option that {self._agent_name} thinks will most quickly and most '
        f'surely achieve their goal.'
    )
    self._state = prompt.open_question(
        question,
        answer_prefix=f'{self._agent_name}\'s best course of action is ',
        max_tokens=1000,
    )
    self._state = (
        f'{self._agent_name}\'s best course of action is  {self._state}')

    self._last_chain = prompt
    if self._verbose:
      print(termcolor.colored(self._last_chain.view().text(), 'green'), end='')

    update_log = {
        'date': self._clock_now(),
        'Summary': question,
        'State': self._state,
        'Chain of thought': prompt.view().text().splitlines(),
    }
    self._history.append(update_log)
