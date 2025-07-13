


"""This component always returns the same string."""

from concordia.typing.deprecated import component


class ConstantComponent(component.Component):
  """A constant memory component."""

  def __init__(self, state: str, name: str = 'constant'):
    """Initializes the constant component.

    Args:
      state: The state of the memory component.
      name: The name of the memory component.
    """
    self._state = state
    self._name = name

  def name(self) -> str:
    """Returns the name of the memory component."""
    return self._name

  def state(self) -> str:
    """Returns the state of the memory component."""
    return self._state

  def update(self) -> None:
    """This component always returns the same string, update does nothing."""
    pass

  def set_state(self, state: str) -> None:
    """Set the constant state."""
    self._state = state
