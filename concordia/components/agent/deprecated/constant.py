

"""A simple acting component that aggregates contexts from components."""

from concordia.components.agent.deprecated import action_spec_ignored
from concordia.typing.deprecated import logging

DEFAULT_PRE_ACT_KEY = 'Constant'


class Constant(action_spec_ignored.ActionSpecIgnored):
  """A simple component that returns a constant.
  """

  def __init__(
      self,
      state: str,
      pre_act_key: str = DEFAULT_PRE_ACT_KEY,
      logging_channel: logging.LoggingChannel = logging.NoOpLoggingChannel,
  ):
    """Initializes the agent.

    Args:
      state: the state of the component.
      pre_act_key: Prefix to add to the output of the component when called
        in `pre_act`.
      logging_channel: The channel to use for debug logging.

    Raises:
      ValueError: If the component order is not None and contains duplicate
        components.
    """
    super().__init__(pre_act_key)
    self._state = state
    self._logging_channel = logging_channel

  def _make_pre_act_value(self) -> str:
    self._logging_channel(
        {'Key': self.get_pre_act_key(), 'Value': self._state})
    return self._state
