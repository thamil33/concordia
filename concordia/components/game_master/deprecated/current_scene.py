

"""This component records the current scene type."""
import datetime
from typing import Callable

from concordia.associative_memory.deprecated import associative_memory
from concordia.typing.deprecated import component

import termcolor


class CurrentScene(component.Component):
  """Get the current scene, store it, and report it."""

  def __init__(
      self,
      name: str,
      memory: associative_memory.AssociativeMemory,
      clock_now: Callable[[], datetime.datetime] | None = None,
      verbose: bool = False,
  ):
    self._name = name
    self._memory = memory
    self._current_scene_type = ''

    self._clock_now = clock_now
    if clock_now is None:
      self._clock_now = lambda: ''

    self._verbose = verbose
    self._history = []

  def name(self) -> str:
    return self._name

  def state(self) -> str:
    return self._current_scene_type

  def update(self) -> None:
    self._current_scene_type = ''
    retrieved = self._memory.retrieve_by_regex(
        regex=r'\[scene type\].*',
        sort_by_time=True,
    )
    if retrieved:
      result = retrieved[-1]
      self._current_scene_type = result[
          result.find('[scene type]') + len('[scene type]') + 1:]

    if self._verbose:
      print(termcolor.colored(
          'The current scene type is: ' + self._current_scene_type, 'red'))

    update_log = {
        'date': self._clock_now(),
        'Summary': self._name,
        'State': self._current_scene_type,
    }
    self._history.append(update_log)
