from IPython import display

from concordia.language_model.openrouter_model import OpenRouterLanguageModel as gpt_model
from concordia.embedding.sentence_transformer import embedder


from concordia.prefabs.simulation import generic as simulation

import concordia.prefabs.entity as entity_prefabs
import concordia.prefabs.game_master as game_master_prefabs

from concordia.typing import prefab as prefab_lib
from concordia.utils import helper_functions




#Setup sentence encoder
test = embedder.encode(
    'Is societal and technological progress like getting a clearer picture of '
    'something true and deep?')
print(test)

prefabs = {
    **helper_functions.get_package_classes(entity_prefabs),
    **helper_functions.get_package_classes(game_master_prefabs),
}



display.display(
    display.Markdown(helper_functions.print_pretty_prefabs(prefabs)))


"""A prefab implementing an entity with a minimal set of components."""

from collections.abc import Mapping
import dataclasses

from concordia.agents import entity_agent_with_logging
from concordia.associative_memory import basic_associative_memory
from concordia.components import agent as agent_components
from concordia.language_model import language_model
from concordia.typing import prefab as prefab_lib

DEFAULT_INSTRUCTIONS_COMPONENT_KEY = 'Instructions'
DEFAULT_INSTRUCTIONS_PRE_ACT_LABEL = '\nInstructions'


@dataclasses.dataclass
class MyAgent(prefab_lib.Prefab):
 """A prefab implementing an entity with a minimal set of components."""

 description: str = (
     'An entity that has a minimal set of components and is configurable by'
     ' the user. The initial set of components manage memory, observations,'
     ' and instructions. If goal is specified, the entity will have a goal '
     'constant component.'
 )
 params: Mapping[str, str] = dataclasses.field(
     default_factory=lambda: {
         'name': 'Alice',
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

   agent_name = self.params.get('name', 'Bob')

   instructions = agent_components.instructions.Instructions(
         agent_name=agent_name,
         pre_act_label=DEFAULT_INSTRUCTIONS_PRE_ACT_LABEL,
     )

   observation_to_memory = agent_components.observation.ObservationToMemory()

   observation_label = '\nObservation'
   observation = agent_components.observation.LastNObservations(
       history_length=100, pre_act_label=observation_label
   )

   principle = agent_components.question_of_recent_memories.QuestionOfRecentMemories(
       model=model,
       pre_act_label=f'{agent_name} main guiding principle:',
       question='What would Hunter Thompson do in this situation?',
       answer_prefix='Hunter Thompson would',
       add_to_memory=False,
   )

   components_of_agent = {
       DEFAULT_INSTRUCTIONS_COMPONENT_KEY: instructions,
       'observation_to_memory': observation_to_memory,
       agent_components.observation.DEFAULT_OBSERVATION_COMPONENT_KEY: (
           observation
       ),
       agent_components.memory.DEFAULT_MEMORY_COMPONENT_KEY: (
           agent_components.memory.AssociativeMemory(memory_bank=memory_bank)
       ),
       'principle': principle,
   }

   component_order = list(components_of_agent.keys())

   act_component = agent_components.concat_act_component.ConcatActComponent(
       model=model,
       component_order=component_order,
   )

   agent = entity_agent_with_logging.EntityAgentWithLogging(
       agent_name=agent_name,
       act_component=act_component,
       context_components=components_of_agent,
   )

   return agent



# In[ ]:


prefabs['myagent__Entity'] = MyAgent()


# In[ ]:


# @title Configure instances.
PLAYER_ONE = 'Alice'
PLAYER_TWO = 'Bob'

instances = [
    prefab_lib.InstanceConfig(
        prefab='basic__Entity',
        role=prefab_lib.Role.ENTITY,
        params={
            'name': PLAYER_ONE,
        },
    ),
    prefab_lib.InstanceConfig(
        prefab='myagent__Entity',
        role=prefab_lib.Role.ENTITY,
        params={
            'name': PLAYER_TWO,
        },
    ),
    prefab_lib.InstanceConfig(
        prefab='generic__GameMaster',
        role=prefab_lib.Role.GAME_MASTER,
        params={
            'name': 'default rules',
            'acting_order': 'fixed',
        },
    ),
    prefab_lib.InstanceConfig(
        prefab='dialogic__GameMaster',
        role=prefab_lib.Role.GAME_MASTER,
        params={
            'name': 'conversation rules',
            # Comma-separated list of thought chain steps.
        },
    ),
    prefab_lib.InstanceConfig(
        prefab='formative_memories_initializer__GameMaster',
        role=prefab_lib.Role.INITIALIZER,
        params={
            'name': 'initial setup rules',
            'next_game_master_name': 'conversation rules',
            'shared_memories': [
                f'There is a small town of Riverbend where {PLAYER_ONE} and {PLAYER_TWO} grew up.',
            ],
            'player_specific_memories': {PLAYER_ONE : [f'{PLAYER_ONE} will do anything for a charitable cause.'],
                                         PLAYER_TWO : [f'{PLAYER_TWO} is a coockie salesman.']},
            'player_specific_context': {PLAYER_ONE : [f'{PLAYER_ONE} does not like coockies.'],
                                         PLAYER_TWO : [f'{PLAYER_TWO} is a coockie salesman.']},
        },
    ),
]


# In[ ]:


config = prefab_lib.Config(
    default_premise=(
        'It is a bright sunny day in the town of Riverbend. The sun is in the'
        f' zenith and the gentle breeze is rocking the trees. {PLAYER_ONE} is'
        f' standing on the porch of their house. {PLAYER_TWO} has approached'
        f' {PLAYER_ONE}'
    ),
    default_max_steps=5,
    prefabs=prefabs,
    instances=instances,
)


# # The simulation

# In[ ]:


# @title Initialize the simulation
raw_log = []
runnable_simulation = simulation.Simulation(
    config=config,
    model=model,
    embedder=embedder,
)


# In[ ]:


# @title Run the simulation
results_log = runnable_simulation.play(max_steps = 5)


# In[ ]:


# @title Display the log
display.HTML(results_log)


