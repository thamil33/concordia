"""A prefab for the world entity, managing the environment's state."""

from collections.abc import Mapping, Sequence
import dataclasses

from concordia.agents import entity_agent_with_logging
from concordia.associative_memory import basic_associative_memory
from concordia.components import agent as actor_components
from concordia.components import game_master as gm_components
from concordia.language_model import language_model
from concordia.type_checks import prefab as prefab_lib


@dataclasses.dataclass
class SlimWorld(prefab_lib.Prefab):
  """A prefab for a Game Master that manages the world state."""

  description: str = (
      'A Game Master that manages the state of the world, including '
      'locations, objects, and their properties.'
  )
  params: Mapping[str, str] = dataclasses.field(
      default_factory=lambda: {
          'name': 'World',
      }
  )
  entities: Sequence[entity_agent_with_logging.EntityAgentWithLogging] = ()

  def build(
      self,
      model: language_model.LanguageModel,
      memory_bank: basic_associative_memory.AssociativeMemoryBank,
  ) -> entity_agent_with_logging.EntityAgentWithLogging:
    """Build the world entity.

    Args:
      model: The language model to use.
      memory_bank: The memory bank for the world entity.

    Returns:
      An entity agent representing the world.
    """
    agent_name = self.params.get('name', 'World')
    player_names = [entity.name for entity in self.entities]

    # 1. World State Component
    # This component will track the state of objects in the environment.
    world_state = gm_components.world_state.WorldState(
        model=model,
        pre_act_label='World State',
    )

    # 2. Other necessary GM components
    # Even though the world is not directly conversing, it needs some basic
    # components to function within the Concordia framework.
    instructions = gm_components.instructions.Instructions()
    observation = actor_components.observation.LastNObservations(
        history_length=100
    )
    memory = actor_components.memory.AssociativeMemory(memory_bank=memory_bank)

    # 3. Assemble Components
    components_of_world = {
        'Instructions': instructions,
        'WorldState': world_state,
        actor_components.observation.DEFAULT_OBSERVATION_COMPONENT_KEY: observation,
        actor_components.memory.DEFAULT_MEMORY_COMPONENT_KEY: memory,
    }

    # 4. Action Component
    # The SwitchAct component allows the GM to select different behaviors
    # based on the type of action required. For the world, this will mostly
    # be resolving environmental interactions.
    act_component = gm_components.switch_act.SwitchAct(
        model=model,
        entity_names=player_names,
        component_order=list(components_of_world.keys()),
    )

    # 5. Build the Agent
    world_agent = entity_agent_with_logging.EntityAgentWithLogging(
        agent_name=agent_name,
        act_component=act_component,
        context_components=components_of_world,
    )

    return world_agent
