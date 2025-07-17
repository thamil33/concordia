#!/usr/bin/env python
# coding: utf-8

# This notebook is a basic tutorial that demonstrates how to configure a simulation using Concordia.

# <a href="https://colab.research.google.com/github/google-deepmind/concordia/blob/main/examples/selling_cookies.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# In[ ]:


# @title Colab-specific setup (use a CodeSpace to avoid the need for this).
try:
  pass  # %env COLAB_RELEASE_TAG
except:
  pass  # Not running in colab.
else:
  pass  # %pip install --ignore-requires-python --requirement 'https://raw.githubusercontent.com/google-deepmind/concordia/main/examples/requirements.in' 'git+https://github.com/google-deepmind/concordia.git#egg=gdm-concordia'
  pass  # %pip list


# In[ ]:


# @title Imports

import numpy as np
from IPython import display

import sentence_transformers

from concordia.language_model import gpt_model
from concordia.language_model import no_language_model

from concordia.prefabs.simulation import generic as simulation

import concordia.prefabs.entity as entity_prefabs
import concordia.prefabs.game_master as game_master_prefabs

from concordia.typing import prefab as prefab_lib
from concordia.utils import helper_functions


# In[ ]:


# @title Language Model - pick your model and provide keys or select DISABLE_LANGUAGE_MODEL

# By default this colab uses GPT-4, so you must provide an API key.
# Note that it is also possible to use local models or other API models,
# simply replace this cell with the correct initialization for the model
# you want to use.
GPT_API_KEY = '' #@param {type: 'string'}
GPT_MODEL_NAME = 'gpt-4.1-nano' #@param {type: 'string'}

if not GPT_API_KEY:
  raise ValueError('GPT_API_KEY is required.')

# To debug without spending money on API calls, set DISABLE_LANGUAGE_MODEL=True
DISABLE_LANGUAGE_MODEL = False

if not DISABLE_LANGUAGE_MODEL:
  model = gpt_model.GptLanguageModel(api_key=GPT_API_KEY,
                                     model_name=GPT_MODEL_NAME)
else:
  model = no_language_model.NoLanguageModel()


# In[ ]:


# @title Setup sentence encoder

if DISABLE_LANGUAGE_MODEL:
  embedder = np.ones(3)
else:
  st_model = sentence_transformers.SentenceTransformer(
      'sentence-transformers/all-mpnet-base-v2')
  embedder = lambda x: st_model.encode(x, show_progress_bar=False)


# In[ ]:


test = model.sample_text(
    'Is societal and technological progress like getting a clearer picture of '
    'something true and deep?')
print(test)


# In[ ]:


# @title Load prefabs from packages to make the specific palette to use here.

prefabs = {
    **helper_functions.get_package_classes(entity_prefabs),
    **helper_functions.get_package_classes(game_master_prefabs),
}


# In[ ]:


#@title Print menu of prefabs

display.display(
    display.Markdown(helper_functions.print_pretty_prefabs(prefabs)))


# In[ ]:


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
DEFAULT_GOAL_COMPONENT_KEY = 'Goal'


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
          'goal': '',
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
        question=(f'How can {agent_name} exploit the situation for personal '
                  'gain and gratification?'),
        answer_prefix=f'{agent_name} understands that ',
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

    if self.params.get('goal', ''):
      goal_key = DEFAULT_GOAL_COMPONENT_KEY
      goal = agent_components.constant.Constant(
          state=self.params.get('goal', ''),
          pre_act_label='Overarching goal',
      )
      components_of_agent[goal_key] = goal
      # Place goal after the instructions.
      component_order.insert(1, goal_key)

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


from concordia.typing import scene as scene_lib
from collections.abc import Mapping, Sequence
from concordia.typing import entity as entity_lib

DEFAULT_NAME = 'decision rules'

PLAYER_ONE = 'Alice'
PLAYER_TWO = 'Bob'

def configure_scenes() -> Sequence[scene_lib.SceneSpec]:
  """Configure default scenes for this simulation."""
  decision = scene_lib.SceneTypeSpec(
      name='decision',
      game_master_name=DEFAULT_NAME,
      action_spec = {
          PLAYER_ONE: entity_lib.choice_action_spec(
              call_to_action='Would {name} buy the cookies from Bob?',
              options=['Yes', 'No'],
          ),
      }
  )

  conversation = scene_lib.SceneTypeSpec(
      name='conversation',
      game_master_name='conversation rules',
      action_spec=entity_lib.free_action_spec(call_to_action=entity_lib.DEFAULT_CALL_TO_SPEECH),
      )

  scenes = [
      scene_lib.SceneSpec(
          scene_type=conversation,
          participants=[PLAYER_ONE, PLAYER_TWO],
          num_rounds=4,
          premise={
              PLAYER_ONE : [f'{PLAYER_ONE} is approached by {PLAYER_TWO}'],
              PLAYER_TWO : [f'{PLAYER_TWO} has approached {PLAYER_ONE}'],
          },
          ),
      scene_lib.SceneSpec(
          scene_type=decision,
          participants=[PLAYER_ONE],
          num_rounds=1,
          premise={
              PLAYER_ONE : [f'{PLAYER_ONE} has to decide whether to buy cookies from {PLAYER_TWO}'],
          },
      ),
  ]
  return scenes

def action_to_scores(
    joint_action: Mapping[str, str],
) -> Mapping[str, float]:
  """Map a joint action to a dictionary of scores for each player."""
  if joint_action[PLAYER_ONE] == 'Yes':
    return {PLAYER_ONE: -1, PLAYER_TWO: 1}
  return  {PLAYER_ONE: 1, PLAYER_TWO: -1}


def scores_to_observation(
    scores: Mapping[str, float]) -> Mapping[str, str]:
  """Map a dictionary of scores for each player to a string observation.

  This function is appropriate for a coordination game structure.

  Args:
    scores: A dictionary of scores for each player.

  Returns:
    A dictionary of observations for each player.
  """
  observations = {}
  for player_name in scores:
    if scores[player_name] > 0:
      observations[player_name] = (
          f'{player_name} enjoyed the transaction.'
      )
    else:
      observations[player_name] = (
          f'{player_name} did not enjoy the transaction.'
      )
  return observations


# In[ ]:


scenes = configure_scenes()


# In[ ]:


# @title Configure instances.

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
            'goal': f'Sell cookies to {PLAYER_ONE}',
        },
    ),
    prefab_lib.InstanceConfig(
        prefab='game_theoretic_and_dramaturgic__GameMaster',
        role=prefab_lib.Role.GAME_MASTER,
        params={
            'name': 'decision rules',
            # Comma-separated list of thought chain steps.
            'scenes': scenes,
            'action_to_scores': action_to_scores,
            'scores_to_observation': scores_to_observation,
        },
    ),
    prefab_lib.InstanceConfig(
        prefab='dialogic_and_dramaturgic__GameMaster',
        role=prefab_lib.Role.GAME_MASTER,
        params={
            'name': 'conversation rules',
            # Comma-separated list of thought chain steps.
            'scenes': scenes,
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
            'player_specific_memories': {PLAYER_ONE : [f'{PLAYER_ONE} will do anything for a charitable cause.',
                                                       f'{PLAYER_ONE} does not like cookies'],
                                         PLAYER_TWO : [f'{PLAYER_TWO} is a cookie salesman.']},
            'player_specific_context': {PLAYER_ONE : [f'{PLAYER_ONE} does not like cookies.'],
                                         PLAYER_TWO : [f'{PLAYER_TWO} is a cookie salesman.']},
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
runnable_simulation = simulation.Simulation(
    config=config,
    model=model,
    embedder=embedder,
)


# In[ ]:


# @title Run the simulation
raw_log = []
results_log = runnable_simulation.play(max_steps=5,
                                       raw_log=raw_log)


# In[ ]:


# @title Display the log
display.HTML(results_log)


# ```
#  2024 DeepMind Technologies Limited.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ```
