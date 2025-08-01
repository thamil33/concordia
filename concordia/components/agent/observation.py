"""A simple component to receive observations."""


from concordia.components.agent import action_spec_ignored
from concordia.components.agent import memory as memory_component
from concordia.types_concordia import entity_component

DEFAULT_OBSERVATION_COMPONENT_KEY = '__observation__'
DEFAULT_OBSERVATION_PRE_ACT_LABEL = (
    'Observations (ordered from oldest to latest)')

OBSERVATION_TAG = '[observation]'


class ObservationToMemory(action_spec_ignored.ActionSpecIgnored):
  """A component that adds observations to the memory."""

  def __init__(
      self,
      memory_component_key: str = (
          memory_component.DEFAULT_MEMORY_COMPONENT_KEY
      ),
  ):
    """Initializes the observation component.

    Args:
      memory_component_key: Name of the memory component to add observations to
        in `pre_observe` and to retrieve observations from in `pre_act`.
    """
    super().__init__('')
    self._memory_component_key = memory_component_key

  def pre_observe(
      self,
      observation: str,
  ) -> str:
    memory = self.get_entity().get_component(
        self._memory_component_key, type_=memory_component.Memory
    )
    observations = observation.split('\n\n\n')
    for observation in observations:
      if observation:
        memory.add(f'{OBSERVATION_TAG} {observation}')
    return ''

  def _make_pre_act_value(self) -> str:
    return ''


class LastNObservations(
    action_spec_ignored.ActionSpecIgnored, entity_component.ComponentWithLogging
):
  """A simple component to receive observations."""

  def __init__(
      self,
      history_length: int,
      memory_component_key: str = (
          memory_component.DEFAULT_MEMORY_COMPONENT_KEY
      ),
      pre_act_label: str = DEFAULT_OBSERVATION_PRE_ACT_LABEL,
  ):
    """Initializes the observation component.

    Args:
      history_length: The maximum number of observations to retrieve in
        `pre_act`.
      memory_component_key: Name of the memory component to add observations to
        in `pre_observe` and to retrieve observations from in `pre_act`.
      pre_act_label: Prefix to add to the output of the component when called in
        `pre_act`.
    """
    super().__init__(pre_act_label)
    self._memory_component_key = memory_component_key
    self._history_length = history_length

  def _make_pre_act_value(self) -> str:
    """Returns the latest observations to preact."""
    memory = self.get_entity().get_component(
        self._memory_component_key, type_=memory_component.Memory
    )

    mems = memory.retrieve_recent(limit=self._history_length)
    # Remove memories that are not observations.
    mems = [mem for mem in mems if OBSERVATION_TAG in mem]
    result = '\n'.join(mems) + '\n'
    self._logging_channel(
        {'Key': self.get_pre_act_label(), 'Value': result.splitlines()}
    )

    return result

  def get_state(self) -> entity_component.ComponentState:
    """Converts the component to JSON data."""
    return {}

  def set_state(self, state: entity_component.ComponentState) -> None:
    """Sets the component state from JSON data."""
    pass


class ObservationsSinceLastPreAct(
    action_spec_ignored.ActionSpecIgnored, entity_component.ComponentWithLogging
):
  """A component to retrieve observations obtained since the last `pre_act`."""

  def __init__(
      self,
      memory_component_key: str = (
          memory_component.DEFAULT_MEMORY_COMPONENT_KEY
      ),
      pre_act_label: str = DEFAULT_OBSERVATION_PRE_ACT_LABEL,
  ):
    """Initializes the observation component.

    Args:
      memory_component_key: Name of the memory component to add observations to
        in `pre_observe` and to retrieve observations from in `pre_act`.
      pre_act_label: Prefix to add to the output of the component when called in
        `pre_act`.
    """
    super().__init__(pre_act_label)
    self._memory_component_key = memory_component_key

    self._num_since_last_pre_act = 0

  def pre_observe(
      self,
      observation: str,
  ) -> str:
    self._num_since_last_pre_act += 1
    return ''

  def _make_pre_act_value(self) -> str:
    """Returns the latest observations to preact."""
    memory = self.get_entity().get_component(
        self._memory_component_key, type_=memory_component.Memory
    )

    result = ''
    if self._num_since_last_pre_act >= 1:
      mems = memory.retrieve_recent(limit=self._num_since_last_pre_act)
      # Remove memories that are not observations.
      mems = [mem for mem in mems if OBSERVATION_TAG in mem]
      result = '\n'.join(mems) + '\n'
      self._num_since_last_pre_act = 0

    self._logging_channel(
        {'Key': self.get_pre_act_label(), 'Value': result.splitlines()}
    )

    return result

  def get_state(self) -> entity_component.ComponentState:
    """Converts the component to JSON data."""
    with self._lock:
      return {'num_since_last_pre_act': self._num_since_last_pre_act}

  def set_state(self, state: entity_component.ComponentState) -> None:
    """Sets the component state from JSON data."""
    with self._lock:
      self._num_since_last_pre_act = state['num_since_last_pre_act']
