"""A prefab implementing a slim, plan-driven entity."""

from collections.abc import Mapping
import dataclasses

from concordia.agents import entity_agent_with_logging
from concordia.associative_memory import basic_associative_memory
from concordia.components import agent as agent_components
from concordia.language_model import language_model
from concordia.type_checks import prefab as prefab_lib

@dataclasses.dataclass
class SlimAgent(prefab_lib.Prefab):
  """A prefab implementing a streamlined, planning-focused entity."""

  description: str = (
      'An entity that makes decisions by creating and executing a plan to '
      'achieve its goal.'
  )
  params: Mapping[str, str] = dataclasses.field(
      default_factory=lambda: {
          'name': 'SlimAgent',
          'goal': 'Live a fulfilling life.',
          'randomize_choices': True,
      }
  )

  def build(
      self,
      model: language_model.LanguageModel,
      memory_bank: basic_associative_memory.AssociativeMemoryBank,
  ) -> entity_agent_with_logging.EntityAgentWithLogging:
    """Build a slim, plan-driven agent.

    Args:
      model: The language model to use.
      memory_bank: The agent's memory_bank object.

    Returns:
      An entity agent.
    """
    agent_name = self.params.get('name', 'SlimAgent')
    agent_goal = self.params.get('goal', '')
    randomize_choices = self.params.get('randomize_choices', True)

    # 1. Core Components
    memory = agent_components.memory.AssociativeMemory(memory_bank=memory_bank)
    instructions = agent_components.instructions.Instructions(
        agent_name=agent_name,
    )
    observation_to_memory = agent_components.observation.ObservationToMemory()
    observation = agent_components.observation.LastNObservations(
        history_length=100,
    )
    goal = agent_components.constant.Constant(
        state=agent_goal, pre_act_label='\nGoal'
    )

    # 2. Behavioral Component: Plan
    # This is the primary driver of the agent's behavior.
    plan = agent_components.plan.Plan(
        model=model,
        goal_component_key='Goal',
        components=[
            'Instructions',
            agent_components.observation.DEFAULT_OBSERVATION_COMPONENT_KEY,
        ],
        pre_act_label='\nPlan',
    )

    # 3. Assemble Components
    components_of_agent = {
        'Instructions': instructions,
        'Goal': goal,
        'Plan': plan,
        'ObservationToMemory': observation_to_memory,
        agent_components.observation.DEFAULT_OBSERVATION_COMPONENT_KEY: observation,
        agent_components.memory.DEFAULT_MEMORY_COMPONENT_KEY: memory,
    }

    # 4. Action Component
    act_component = agent_components.concat_act_component.ConcatActComponent(
        model=model,
        component_order=list(components_of_agent.keys()),
        randomize_choices=randomize_choices,
    )

    # 5. Build the Agent
    agent = entity_agent_with_logging.EntityAgentWithLogging(
        agent_name=agent_name,
        act_component=act_component,
        context_components=components_of_agent,
    )

    return agent
