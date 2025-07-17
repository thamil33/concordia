#!/usr/bin/env python
# coding: utf-8

# # Modular launch notebook.
# 
# This notebook can be used as an alternative to launchpad.
# 
# 

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


# ## Language Model setup

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


# # Parameters

# In[ ]:


# @title Load prefabs from packages to make the specific palette to use here.

prefabs = {
    **helper_functions.get_package_classes(entity_prefabs),
    **helper_functions.get_package_classes(game_master_prefabs),
}


# In[ ]:


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
        question='What would a Hobbit of the Baggins family do?',
        answer_prefix='A Baggins would: ',
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


import numpy as np

def get_summary(answers):

  players = answers.keys()
  results = {}

  for player in players:
    results[player] = {}

    questionnaires = answers[player].keys()
    for questionnaire in questionnaires:

      questions = answers[player][questionnaire]
      values = []

      for _, player_answer in questions.items():
        values.append(player_answer["value"])

      results[player][questionnaire] = np.mean(values)

  return results


# In[ ]:


# @title Scene 1 - Frodo in the Shire

from concordia.contrib.data.questionnaires import DASS

FRODO = "Frodo"

instances = [
    prefab_lib.InstanceConfig(
        prefab='myagent__Entity',
        role=prefab_lib.Role.ENTITY,
        params={
            'name': FRODO,
            'goal': f'Live a relaxed and happy life at the Shire.',
        },
    ),
    prefab_lib.InstanceConfig(
        prefab='interviewer__GameMaster',
        role=prefab_lib.Role.GAME_MASTER,
        params={
          "name": "interviewer",
          "player_name_to_question": FRODO,
          "questionnaires": [DASS],
          "verbose": False,
        },
    ),
    prefab_lib.InstanceConfig(
        prefab='formative_memories_initializer__GameMaster',
        role=prefab_lib.Role.INITIALIZER,
        params={
            'name': 'initial setup rules',
            'next_game_master_name': 'interviewer',
            'shared_memories': [
                f'Frodo is a happy hobbit, a very happy hobbit who enjoys gardening, cooking, eating, and drinking with his friends. Frodo does not have a single worry in the world. One day, Gandalf the wizard pays Frodo a visit to take part into his uncle Bilbo\'s 111th birthday. Frodo is happy to see Gandalf again, and is excited for Bilbo\'s birthday!',
            ],
            'player_specific_context': {FRODO: [f'{FRODO} is happy, relaxed, and is looking forward to enjoying Bilbo\'s 111th birthday with Gandalf and his friends.']
            },
        }
    )
]


# In[ ]:


config = prefab_lib.Config(
    default_premise=f'Frodo is a happy hobbit, a very happy hobbit who enjoys gardening, cooking, eating, and drinking with his friends. Frodo does not have a single worry in the world. One day, Gandalf the wizard pays Frodo a visit to take part into his uncle Bilbo\'s 111th birthday. Frodo is happy to see Gandalf again, and is excited for Bilbo\'s birthday!',
    default_max_steps=100,
    prefabs=prefabs,
    instances=instances,
)


# In[ ]:


# @title Initialize the simulation
runnable_simulation = simulation.Simulation(
    config=config,
    model=model,
    embedder=embedder,
)


# In[ ]:


# @title Run the simulation
results_log = runnable_simulation.play(max_steps = 100)


# In[ ]:


display.HTML(results_log)


# In[ ]:


answers = runnable_simulation.game_masters[1]._context_components['__next_action_spec__'].get_answers()

print(get_summary(answers))


# In[ ]:


# @title Scene 2 - Frodo after Moria

FRODO = "Frodo"

instances = [
    prefab_lib.InstanceConfig(
        prefab='myagent__Entity',
        role=prefab_lib.Role.ENTITY,
        params={
            'name': FRODO,
            'goal': f'Destroy the ring and go back to the shire',
        },
    ),
    prefab_lib.InstanceConfig(
        prefab='interviewer__GameMaster',
        role=prefab_lib.Role.GAME_MASTER,
        params={
          "name": "interviewer",
          "player_name_to_question": FRODO,
          "questionnaires": [DASS],
          "verbose": False,
        },
    ),
    prefab_lib.InstanceConfig(
        prefab='formative_memories_initializer__GameMaster',
        role=prefab_lib.Role.INITIALIZER,
        params={
            'name': 'initial setup rules',
            'next_game_master_name': 'interviewer',
            'shared_memories': [
                f'The remaining members of the fellowship have just exited the ruins of Moria, barely escaped with their lives. Gandalf unfortunately succumbed to the Balrog, and because of that, the morale of the fellowship of the ring is very low.',
                f"The group has set main camp in the woods, the sun is about to set."
            ],
            'player_specific_context': {FRODO: [f'{FRODO} is profoundly demoralized, he misses the shire, is mourning for Gandalf and is anxious for the future. Frodo worries that he will never see the shire and the comforts of his home again.']
            },
        }
    )
]


# In[ ]:


config = prefab_lib.Config(
    default_premise=f'The group has set camp in the woods, just a few hours ago Gandalf was slain by the Balrog of Moria, and the fellowship of the ring is deeply demoralized.',
    default_max_steps=100,
    prefabs=prefabs,
    instances=instances,
)


# In[ ]:


# @title Initialize the simulation
runnable_simulation = simulation.Simulation(
    config=config,
    model=model,
    embedder=embedder,
)


# In[ ]:


# @title Run the simulation
results_log = runnable_simulation.play(max_steps = 100)


# In[ ]:


display.HTML(results_log)


# In[ ]:


answers = runnable_simulation.game_masters[1]._context_components['__next_action_spec__'].get_answers()

print(get_summary(answers))