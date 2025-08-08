

"""A modular entity agent using the new component system with side logging."""

from collections.abc import Mapping
import copy
import types
from typing import Any

from concordia.agents import entity_agent
from concordia.associative_memory import formative_memories
from concordia.type_checks import entity as entity_lib
from concordia.type_checks import entity_component
from concordia.utils import measurements as measurements_lib


class EntityAgentWithLogging(entity_agent.EntityAgent,
                             entity_lib.EntityWithLogging):
  """An agent that exposes the latest information of each component."""

  def __init__(
      self,
      agent_name: str,
      act_component: entity_component.ActingComponent,
      context_processor: (
          entity_component.ContextProcessorComponent | None
      ) = None,
      context_components: Mapping[str, entity_component.ContextComponent] = (
          types.MappingProxyType({})
      ),
      config: formative_memories.AgentConfig | None = None,
  ):
    """Initializes the agent.

    The passed components will be owned by this entity agent (i.e. their
    `set_entity` method will be called with this entity as the argument).

    Whenever `get_last_log` is called, the latest values published in all the
    channels in the given measurements object will be returned as a mapping of
    channel name to value.

    Args:
      agent_name: The name of the agent.
      act_component: The component that will be used to act.
      context_processor: The component that will be used to process contexts. If
        None, a NoOpContextProcessor will be used.
      context_components: The ContextComponents that will be used by the agent.
      config: The agent configuration, used for checkpointing and debug.
    """
    super().__init__(agent_name=agent_name,
                     act_component=act_component,
                     context_processor=context_processor,
                     context_components=context_components)
    self._component_logging = measurements_lib.Measurements()

    for component_name, component in self._context_components.items():
      if isinstance(component, entity_component.ComponentWithLogging):
        channel_name = component_name
        component.set_logging_channel(
            self._component_logging.get_channel(channel_name).append
        )
    if isinstance(act_component, entity_component.ComponentWithLogging):
      act_component.set_logging_channel(
          self._component_logging.get_channel('__act__').append
      )
    if isinstance(context_processor, entity_component.ComponentWithLogging):
      context_processor.set_logging_channel(
          self._component_logging.get_channel('__context_processor__').append
      )
    self._config = copy.deepcopy(config)

  def get_all_logs(self):
    return self._component_logging.get_all_channels()

  def get_last_log(self):
    log: dict[str, Any] = {}
    for channel_name in sorted(self._component_logging.available_channels()):
      log[channel_name] = self._component_logging.get_last_datum(channel_name)
    return log

  def get_config(self) -> formative_memories.AgentConfig | None:
    return copy.deepcopy(self._config)
