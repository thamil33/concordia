


"""This components report what the function returns at the moment.

For example, can be used for reporting current time
current_time_component = ReportFunction(
    'Current time',
    function=clock.current_time_interval_str)
"""

from typing import Callable
from concordia.typing.deprecated import component


class ReportFunction(component.Component):
  """A component that reports what the function returns at the moment."""

  def __init__(self, function: Callable[[], str], name: str = 'State'):
    """Initializes the component.

    Args:
      function: the function that returns a string to report as state of the
        component.
      name: The name of the component.
    """
    self._function = function
    self._name = name

  def name(self) -> str:
    """Returns the name of the component."""
    return self._name

  def state(self) -> str:
    """Returns the state of the component."""
    return self._function()

  def update(self) -> None:
    """This component always returns the same string, update does nothing."""
    pass
