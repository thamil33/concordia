"""A GameMaster prefab that generates memories using the streamlined factory."""

import dataclasses
from typing import Sequence

from concordia.agents import entity_agent_with_logging
from concordia.associative_memory import formative_memories
from concordia.associative_memory.slim_formative_memories import SlimFormativeMemoryFactory
from concordia.components.game_master import event_resolution
from concordia.components.game_master import next_acting
from concordia.language_model import language_model
from concordia.type_checks import prefab as prefab_lib


@dataclasses.dataclass
class FormativeMemoryInitializer(prefab_lib.Prefab):
  """A Game Master that initializes agent memories using the slim factory."""

  model: language_model.LanguageModel
  embedder: ...
  entities: Sequence[entity_agent_with_logging.EntityAgentWithLogging] = ()

  def build(self) -> entity_agent_with_logging.EntityAgentWithLogging:
    """Builds the Game Master agent."""
    memory_factory = SlimFormativeMemoryFactory(
        model=self.model,
        embedder=self.embedder,
    )

    # This component does the actual work of generating and injecting memories.
    memory_generation_component = gm_components.memory_component.MemoryComponent(
        memory_factory=memory_factory,
        agent_configs=[
            formative_memories.AgentConfig(
                name=agent.name,
                goal=agent.goal,
                context=agent.get_component("self_perception").state,
            )
            for agent in self.entities
        ],
    )

    game_master = entity_agent_with_logging.EntityAgentWithLogging(
        agent_name="FormativeMemoryInitializer",
        act_component=gm_components.NoOpAct(),
        context_components={
            "memory_generation": memory_generation_component,
        },
    )
    return game_master
