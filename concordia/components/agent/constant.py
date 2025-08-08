

"""A simple acting component that aggregates contexts from components."""

from concordia.components.agent import action_spec_ignored
from concordia.type_checks import entity_component

DEFAULT_PRE_ACT_LABEL = 'Constant'


class Constant(
    action_spec_ignored.ActionSpecIgnored, entity_component.ComponentWithLogging
):
  """A simple component that returns a constant."""

  def __init__(
      self,
      state: str,
      pre_act_label: str = DEFAULT_PRE_ACT_LABEL,
  ):
    """Initializes the agent.

    Args:
      state: the state of the component.
      pre_act_label: Prefix to add to the output of the component when called
        in `pre_act`.

    Raises:
      ValueError: If the component order is not None and contains duplicate
        components.
    """
    super().__init__(pre_act_label)
    self._state = state

  def _make_pre_act_value(self) -> str:
    self._logging_channel(
        {'Key': self.get_pre_act_label(), 'Value': self._state})
    return self._state

  def get_state(self) -> entity_component.ComponentState:
    """Returns the state of the component."""
    return {}

  def set_state(self, state: entity_component.ComponentState) -> None:
    """Sets the state of the component."""
    pass
