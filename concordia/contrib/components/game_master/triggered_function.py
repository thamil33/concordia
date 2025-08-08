

"""A component to call functions based on events."""

from collections.abc import Callable
import dataclasses
import datetime

from concordia.components.agent import memory as memory_component
from concordia.components.game_master import event_resolution as event_resolution_component
from concordia.components.game_master import switch_act
from concordia.environment.scenes import runner as scene_runner
from concordia.type_checks import entity as entity_lib
from concordia.type_checks import entity_component
from concordia.type_checks import logging


@dataclasses.dataclass
class PreEventFnArgsT:
  """A specification of the arguments to a pre-event function.

  Attributes:
    player_name: The name of the player.
    player_choice: The choice of the player on the current timestep.
    current_scene_type: The type of the current scene.
    memory: The game master's memory component.
  """

  player_name: str
  player_choice: str
  current_scene_type: str
  memory: memory_component.Memory


@dataclasses.dataclass
class PostEventFnArgsT:
  """A specification of the arguments to a post-event function.

  Attributes:
    event_statement: The event that resulted from the player's choice.
    current_scene_type: The type of the current scene.
    memory: The game master's memory component.
  """

  event_statement: str
  current_scene_type: str
  memory: memory_component.Memory


class TriggeredFunction(entity_component.ContextComponent):
  """A component to modify inventories based on events."""

  def __init__(
      self,
      clock_now: Callable[[], datetime.datetime],
      event_resolution_component_key: str = (
          switch_act.DEFAULT_RESOLUTION_COMPONENT_KEY),
      memory_component_key: str = (
          memory_component.DEFAULT_MEMORY_COMPONENT_KEY
      ),
      pre_event_fn: Callable[[PreEventFnArgsT], str] | None = None,
      post_event_fn: Callable[[PostEventFnArgsT], str] | None = None,
      pre_act_label: str = '',
      logging_channel: logging.LoggingChannel = logging.NoOpLoggingChannel,
      verbose: bool = False,
  ):
    """Initialize a component to call functions based on events.

    Args:
      clock_now: Function to call to get current time.
      event_resolution_component_key: The name of the event resolution
        component.
      memory_component_key: The name of the memory component.
      pre_event_fn: function to call with the action attempt before
        computing the event. It returns a string to log.
      post_event_fn: function to call with the event statement.
      pre_act_label: Prefix to add to the output of the component when called
        in `pre_act`.
      logging_channel: The channel to log debug information to.
      verbose: whether to print the full update chain of thought or not
    """
    self._pre_act_label = pre_act_label
    self._logging_channel = logging_channel
    self._verbose = verbose

    self._event_resolution_component_key = event_resolution_component_key
    self._memory_component_key = memory_component_key
    self._clock_now = clock_now

    self._pre_event_fn = pre_event_fn
    self._post_event_fn = post_event_fn

    self._latest_action_spec = None

  def pre_act(
      self,
      action_spec: entity_lib.ActionSpec,
  ) -> str:
    self._latest_action_spec = action_spec
    if self._pre_event_fn is None:
      return ''

    pre_event_log = ''
    if self._latest_action_spec == entity_lib.OutputType.RESOLVE:
      event_resolution = self.get_entity().get_component(
          self._event_resolution_component_key,
          type_=event_resolution_component.EventResolution,
      )
      player_name = event_resolution.get_active_entity_name()
      choice = event_resolution.get_putative_action()

      memory = self.get_entity().get_component(
          self._memory_component_key, type_=memory_component.Memory
      )

      current_scene_type = scene_runner.get_current_scene_type(memory=memory)

      pre_event_log = self._pre_event_fn(
          PreEventFnArgsT(player_name=player_name,
                          player_choice=choice,
                          current_scene_type=current_scene_type,
                          memory=memory)
      )
    self._logging_channel({
        'Key': self._pre_act_label,
        'Value': pre_event_log,
    })
    return ''

  def post_act(
      self,
      event: str,
  ) -> str:
    if self._post_event_fn is None:
      return ''
    if self._latest_action_spec == entity_lib.OutputType.RESOLVE:
      memory = self.get_entity().get_component(
          self._memory_component_key, type_=memory_component.Memory
      )
      current_scene_type = scene_runner.get_current_scene_type(memory=memory)
      _ = self._post_event_fn(
          PostEventFnArgsT(event_statement=event,
                           current_scene_type=current_scene_type,
                           memory=memory)
      )
    return ''

  def get_state(self) -> entity_component.ComponentState:
    """Returns the state of the component."""
    return {}

  def set_state(self, state: entity_component.ComponentState) -> None:
    """Sets the of the component."""
    pass
