
# @title Imports

import numpy as np
from IPython import display

import sentence_transformers

from language_model import no_language_model

from prefabs.simulation import generic as simulation

import prefabs.entity as entity_prefabs
import prefabs.orchestrator as orchestrator_prefabs

from typing_custom import prefab as prefab_lib
from utils import helper_functions


# Import your custom LLM implementation
from language_model import openrouter_model # Adjust import if needed

import os
from dotenv import load_dotenv

# Always load .env from project root
load_dotenv(dotenv_path=os.path.join("C:\\Users\\tyler\\dev\\concordia\\pyscrai\\pysim", ".env"))


# Get API key and model name from environment
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = os.getenv("OPENROUTER_MODEL_NAME", "openrouter-default-model")  # Set your default
print({API_KEY})
print("OPENROUTER_API_KEY in env:", os.getenv("OPENROUTER_API_KEY"))
if not API_KEY:
    raise ValueError("OPENROUTER_API_KEY is required in your .env file.")

# To debug without spending money on API calls, set DISABLE_LANGUAGE_MODEL=True
DISABLE_LANGUAGE_MODEL = False

if not DISABLE_LANGUAGE_MODEL:
    model = openrouter_model.OpenRouterLanguageModel(api_key=API_KEY, model_name=MODEL_NAME)
else:
    from language_model import no_language_model
    model = no_language_model.NoLanguageModel()



# @title Setup sentence encoder

if DISABLE_LANGUAGE_MODEL:
  embedder = np.ones(3)
else:
  st_model = sentence_transformers.SentenceTransformer(
      'sentence-transformers/all-mpnet-base-v2')
  embedder = lambda x: st_model.encode(x, show_progress_bar=False)


# @title Load prefabs from packages to make the specific palette to use here.

prefabs = {
    **helper_functions.get_package_classes(entity_prefabs),
    **helper_functions.get_package_classes(orchestrator_prefabs),
}


#@title Print menu of prefabs

display.display(
    display.Markdown(helper_functions.print_pretty_prefabs(prefabs)))


"""A prefab implementing an entity with a minimal set of components."""

from collections.abc import Mapping
import dataclasses

from agents import entity_agent_with_logging
from associative_memory import basic_associative_memory
from components import agent as agent_components
from language_model import language_model
from typing_custom import prefab as prefab_lib

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

    agent_name = self.params.get('name', 'Alice')

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
        question='What would Horatio Alger do in this situation?',
        answer_prefix='Horatio Alger would',
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



prefabs['myagent__Entity'] = MyAgent()




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
        prefab='generic__orchestrator',
        role=prefab_lib.Role.ORCHESTRATOR,
        params={
            'name': 'default rules',
            # Comma-separated list of thought chain steps.
        },
    ),
    prefab_lib.InstanceConfig(
        prefab='dialogic__orchestrator',
        role=prefab_lib.Role.ORCHESTRATOR,
        params={
            'name': 'conversation rules',
            # Comma-separated list of thought chain steps.
        },
    ),
    prefab_lib.InstanceConfig(
        prefab='formative_memories_initializer__orchestrator',
        role=prefab_lib.Role.INITIALIZER,
        params={
            'name': 'initial setup rules',
            'next_orchestrator_name': 'conversation rules',
            'shared_memories': [
                f'There is a small town of Riverbend where {PLAYER_ONE} and {PLAYER_TWO} grew up.',
            ],
            'player_specific_memories': {PLAYER_ONE : [f'{PLAYER_ONE} loves cookies.'],
                                         PLAYER_TWO : [f'{PLAYER_TWO} is a cookie salesman.']},
            'player_specific_context': {PLAYER_ONE : [f'{PLAYER_ONE} loves cookies.'],
                                         PLAYER_TWO : [f'{PLAYER_TWO} is a cookie salesman.']},
        },
    ),
]


config = prefab_lib.Config(
    default_premise=f'It is a bright sunny day in the town of Riverbend. The sun is in the zenith and the gentle breeze is rocking the trees. {PLAYER_ONE} is standing on the porch of their house. {PLAYER_TWO} has approached {PLAYER_ONE}',
    default_max_steps=5,
    prefabs=prefabs,
    instances=instances,
)


# # The simulation


# @title Initialize the simulation
raw_log = []
runnable_simulation = simulation.Simulation(
    config=config,
    model=model,
    embedder=embedder,
)


# @title Run the simulation
results_log = runnable_simulation.play(max_steps = 5)



# @title Display the log
display.HTML(results_log)
