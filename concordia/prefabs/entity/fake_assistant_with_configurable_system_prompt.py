

"""This is a prefab that wraps a language model as a Concordia agent."""

from collections.abc import Mapping
import dataclasses

from concordia.agents import entity_agent_with_logging
from concordia.associative_memory import basic_associative_memory
from concordia.components import agent as agent_components
from concordia.language_model import language_model
from concordia.type_checks import prefab as prefab_lib


@dataclasses.dataclass
class Entity(prefab_lib.Prefab):
  """A prefab implementing a simulated AI assistant with a system prompt."""

  description: str = (
      'An entity that simulates an AI assistant with a configurable system '
      'prompt.'
  )
  params: Mapping[str, str] = dataclasses.field(
      default_factory=lambda: {
          'name': 'Assistant',
          'system_prompt': 'Assistant is a helpful and harmless AI assistant.',
      }
  )

  def build(
      self,
      model: language_model.LanguageModel,
      memory_bank: basic_associative_memory.AssociativeMemoryBank,
  ) -> entity_agent_with_logging.EntityAgentWithLogging:
    """Build an agent.

    Args:
      model: The language model to use.
      memory_bank: The agent's memory_bank object.

    Returns:
      An entity.
    """
    entity_name = self.params.get('name', 'Assistant')
    system_prompt = self.params.get('system_prompt', '')

    system = agent_components.constant.Constant(
        state=system_prompt,
        pre_act_label='System',
    )

    observation_to_memory = agent_components.observation.ObservationToMemory(
    )

    observation_label = (
        agent_components.observation.DEFAULT_OBSERVATION_PRE_ACT_LABEL)
    observation = agent_components.observation.LastNObservations(
        history_length=100,
        pre_act_label=observation_label,
    )

    components_of_agent = {
        'System': system,
        'ObservationToMemory': observation_to_memory,
        agent_components.observation.DEFAULT_OBSERVATION_COMPONENT_KEY: (
            observation
        ),
        agent_components.memory.DEFAULT_MEMORY_COMPONENT_KEY: (
            agent_components.memory.AssociativeMemory(memory_bank=memory_bank)
        ),
    }

    act_component = agent_components.concat_act_component.ConcatActComponent(
        model=model,
    )

    agent = entity_agent_with_logging.EntityAgentWithLogging(
        agent_name=entity_name,
        act_component=act_component,
        context_components=components_of_agent,
    )

    return agent
