#!/usr/bin/env python
# coding: utf-8

# # Agent development colab using GCP hosted Gemma 2
#
#
# This notebook presents a prompt engineering view of the Concordia agent development process, making it easier to configure within the Concordia environment. For coding proficient users, a higher level of customization and development will be possible by developing agents directly in the agent factory.
#
#
# To begin, make a copy of this colab and save to google drive. This will impact where the agent file is created that you will eventually submit.
#
#
# Agent Factory: https://github.com/google-deepmind/concordia/tree/main/concordia/factory/agent
#
# Additional Agent Tutorials: https://github.com/google-deepmind/concordia/tree/main/examples/tutorials
#
# ---
# This tutorial uses GCP hosted Gemma 2. To deply your Gemma2 model on Vertex AI, follow this [doc](https://docs.google.com/document/d/1eT6kNOtE3fuXk91-XvjLjVM9EOZZq_I_vk-XEGN61YA).
#
#

# <a href="https://colab.research.google.com/github/google-deepmind/concordia/blob/main/examples/deprecated/tutorials/agent_development_GCP_Gemma2.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# ## Setup and imports

# In[ ]:


# @title Colab-specific setup (use a CodeSpace to avoid the need for this).
try:
  get_ipython().run_line_magic('pass', ' #env COLAB_RELEASE_TAG')
except:
  pass  # Not running in colab.
else:
  get_ipython().run_line_magic('pass', " #pip install --ignore-requires-python --requirement 'https://raw.githubusercontent.com/google-deepmind/concordia/main/examples/requirements.in' 'git+https://github.com/google-deepmind/git#egg=gdm-concordia'")
  get_ipython().run_line_magic('pass', ' #pip list')


# In[ ]:


import datetime
import importlib
import numpy as np

from IPython import display

from language_model import call_limit_wrapper
from language_model import utils
from utils.deprecated import measurements as measurements_lib
import sentence_transformers


#

# ## Language Model setup

# ## Parameters

# In[ ]:


# Select an embedder by specifying one of the sentence transformer embedding
# models listed at https://huggingface.co/sentence-transformers.
EMBEDDER_NAME = 'all-mpnet-base-v2'
# To debug without spending money on API calls, set DISABLE_LANGUAGE_MODEL=True.
DISABLE_LANGUAGE_MODEL = False # @param {"type":"boolean"}


# In[ ]:


#@title Imports and initialization

# update to the latest Vertex AI api
get_ipython().system("pass  # pip3 install --upgrade --quiet 'google-cloud-aiplatform>=1.64.0'")

import sentence_transformers
from google.colab import auth  # pytype: disable=import-error

from typing import deprecated as typing
from typing_custom.deprecated import entity

from associative_memory.deprecated import associative_memory
from language_model import google_cloud_custom_model
from language_model import language_model

# The memory will use a sentence embedder for retrievel, so we download one from
# Hugging Face.
_embedder_model = sentence_transformers.SentenceTransformer(
    'sentence-transformers/all-mpnet-base-v2')
embedder = lambda x: _embedder_model.encode(x, show_progress_bar=False)


# Language Model - Gemma 2 on Vertex AI

endpoint_id = 'YOUR ENDPOINT ID HERE' #@param {type: 'string'}
project_id = 'YOUR PROJECT NUMBER HERE' #@param {type: 'string'}
region = 'us-central1' #@param {type: 'string'}

if not endpoint_id:
  raise ValueError('model endpoint id is required')
if not project_id:
  raise ValueError('A project id is required.')
if not region:
  raise ValueError('Region information is required.')

model = google_cloud_custom_model.VertexAI(endpoint_id=endpoint_id,
      project_id=project_id,
      location=region)

auth.authenticate_user(project_id=project_id)


# ## Setup sentence encoder

# In[ ]:


# @title Setup sentence encoder

if DISABLE_LANGUAGE_MODEL:
  embedder = lambda x: np.ones(5)
else:
  _embedder_model = sentence_transformers.SentenceTransformer(
      f'sentence-transformers/{EMBEDDER_NAME}')
  embedder = lambda x: _embedder_model.encode(x, show_progress_bar=False)


# # Building an agent

# In[ ]:


get_ipython().run_line_magic('pass', ' #%writefile my_agent.py')

#@title Imports for agent building
import datetime

from agents.deprecated import entity_agent_with_logging
from associative_memory.deprecated import associative_memory
from associative_memory.deprecated import formative_memories
from clocks import game_clock
from components.agent import deprecated as agent_components
from language_model import language_model
from deprecated.memory_bank import legacy_associative_memory
from utils.deprecated import measurements as measurements_lib
from components.agent.deprecated import question_of_recent_memories
from typing import Sequence


# Agents are composed of components, which are fully customizable. We are going to demonstrate how to design different kinds of agents by using a QuestionOfRecentMemories components. As you get more comfortable with the code, we strongly encourage your to design and build your own agent components.
#
# QuestionOfRecentMemories: This type of component proceeds by first retrieving recent memories and then asking a question. For example, the question could be "What kind of person is {agent_name}?" or "What is the rational thing to do next?" and so on. The answers to these questions will condition the agents action, thereby defining its behavior.
#
#
# Important notes:
# - All text should refer to the agent in third person, without using "I", "me", "mine" and so on.
# - A special string {agent_name} will be automatically replaced with the agent's actual name during simulation (e.g. Alice).
#
# The agent class will be automatically saved to my_agent.py using iPython magic %%writefile command.
#

# In[ ]:


get_ipython().run_line_magic('pass', ' #%writefile -a my_agent.py')

#@markdown Each question is a class that inherits from QuestionOfRecentMemories
class Question1(question_of_recent_memories.QuestionOfRecentMemories):
  """This component answers the question 'what kind of person is the agent?'."""

  def __init__(
      self,
      agent_name:str,
      **kwargs,
  ):
    #@markdown {agent_name} will be automatically replaced with the name of the specific agent
    question = 'Given the above, what kind of person is {agent_name}?' #@param {"type":"string"}
    #@markdown The answer will have to start with this prefix
    answer_prefix = '{agent_name} is ' #@param {"type":"string"}
    #@markdown Flag that defines whether the answer will be added to memory
    add_to_memory = True # @param {"type":"boolean"}
    #@markdown If yes, the memory will start with this tag
    memory_tag = '[self reflection]' # @param {"type":"string"}
    question_with_name = question.format(agent_name=agent_name)
    super().__init__(
        pre_act_key=f'\nQuestion: {question_with_name}\nAnswer',
        question=question,
        answer_prefix=answer_prefix,
        add_to_memory=add_to_memory,
        memory_tag=memory_tag,
        components={},
        **kwargs,
    )


# In[ ]:


get_ipython().run_line_magic('pass', ' #%writefile -a my_agent.py')

#@markdown We can add the value of other components to the context of the question. Notice, how Question2 depends on Observation and ObservationSummary. The names of the classes of the contextualising components have to be passed as "components" argument.
class Question2(question_of_recent_memories.QuestionOfRecentMemories):
  """This component answers 'which action is best for achieving my goal?'."""

  def __init__(
      self,
      agent_name:str,
      **kwargs,
  ):
    question = 'Given the statements above, what kind of situation is {agent_name} in right now?' #@param {"type":"string"}
    answer_prefix = '{agent_name} is currently ' #@param {"type":"string"}
    add_to_memory = False # @param {"type":"boolean"}
    memory_tag = '[situation reflection]' # @param {"type":"string"}
    question_with_name = question.format(agent_name=agent_name)

    super().__init__(
        pre_act_key=f'\nQuestion: {question_with_name}\nAnswer',
        question=question,
        answer_prefix=answer_prefix,
        add_to_memory=add_to_memory,
        memory_tag=memory_tag,
        #@markdown The key is the name of the component class and the key is the prefix with which it will appear in the context of this component. Be careful if you are going to edit this field, it should be a valid dictionary.
        components={'Observation': '\nObservation', 'ObservationSummary': '\nSummary of recent observations',}, #@param

        **kwargs,
    )


# In[ ]:


get_ipython().run_line_magic('pass', ' #%writefile -a my_agent.py')

#@markdown We can also have the questions depend on each other. Here, the answer to Question3 is contextualised by answers to Question1 and Question2
class Question3(question_of_recent_memories.QuestionOfRecentMemories):
  """What would a person like the agent do in a situation like this?"""

  def __init__(
      self,
      agent_name:str,
      **kwargs):
    question = 'What would a person like {agent_name} do in a situation like this?' #@param {"type":"string"}
    answer_prefix = '{agent_name} would ' #@param {"type":"string"}
    add_to_memory = True # @param {"type":"boolean"}
    memory_tag = '[intent reflection]' # @param {"type":"string"}

    question_with_name = question.format(agent_name=agent_name)

    super().__init__(
        pre_act_key=f'\nQuestion: {question_with_name}\nAnswer',
        question=question,
        answer_prefix=answer_prefix,
        add_to_memory=add_to_memory,
        memory_tag=memory_tag,
        components={'Question1': f'\nQuestion: What kind of person is {agent_name}?\nAnswer', 'Question2': f'\nQuestion: What kind of situation is {agent_name} in right now?\nAnswer',}, #@param
        **kwargs,
    )


# In[ ]:


get_ipython().run_line_magic('pass', ' #%writefile -a my_agent.py')

#@markdown This function creates the components

def _make_question_components(
    agent_name:str,
    measurements: measurements_lib.Measurements,
    model: language_model.LanguageModel,
    clock: game_clock.MultiIntervalClock,
) -> Sequence[question_of_recent_memories.QuestionOfRecentMemories]:

  question_1 = Question1(
      agent_name=agent_name,
      model=model,
      logging_channel=measurements.get_channel('Question_1').on_next,
  )
  question_2 = Question2(
      agent_name=agent_name,
      model=model,
      clock_now=clock.now,
      logging_channel=measurements.get_channel('Question_2').on_next,
  )
  question_3 = Question3(
      agent_name=agent_name,
      model=model,
      clock_now=clock.now,
      logging_channel=measurements.get_channel('Question_3').on_next,
  )

  return (question_1, question_2, question_3)


# In[ ]:


get_ipython().run_line_magic('pass', ' #%writefile -a my_agent.py')

def _get_class_name(object_: object) -> str:
  return object_.__class__.__name__

#@markdown This function builds the agent using the components defined above. It also adds core components that are useful for every agent, like observations, time display, recenet memories.

def build_agent(
    config: formative_memories.AgentConfig,
    model: language_model.LanguageModel,
    memory: associative_memory.AssociativeMemory,
    clock: game_clock.MultiIntervalClock,
    update_time_interval: datetime.timedelta,
) -> entity_agent_with_logging.EntityAgentWithLogging:
  """Build an agent.

  Args:
    config: The agent config to use.
    model: The language model to use.
    memory: The agent's memory object.
    clock: The clock to use.
    update_time_interval: Agent calls update every time this interval passes.

  Returns:
    An agent.
  """
  del update_time_interval
  if not config.extras.get('main_character', False):
    raise ValueError(
        'This function is meant for a main character '
        'but it was called on a supporting character.'
    )

  agent_name = config.name

  raw_memory = legacy_associative_memory.AssociativeMemoryBank(memory)

  measurements = measurements_lib.Measurements()
  instructions = agent_components.instructions.Instructions(
      agent_name=agent_name,
      logging_channel=measurements.get_channel('Instructions').on_next,
  )

  time_display = agent_components.report_function.ReportFunction(
      function=clock.current_time_interval_str,
      pre_act_key='\nCurrent time',
      logging_channel=measurements.get_channel('TimeDisplay').on_next,
  )

  observation_label = '\nObservation'
  observation = agent_components.observation.Observation(
      clock_now=clock.now,
      timeframe=clock.get_step_size(),
      pre_act_key=observation_label,
      logging_channel=measurements.get_channel('Observation').on_next,
  )
  observation_summary_label = 'Summary of recent observations'
  observation_summary = agent_components.observation.ObservationSummary(
      model=model,
      clock_now=clock.now,
      timeframe_delta_from=datetime.timedelta(hours=4),
      timeframe_delta_until=datetime.timedelta(hours=0),
      pre_act_key=observation_summary_label,
      logging_channel=measurements.get_channel('ObservationSummary').on_next,
  )

  relevant_memories_label = '\nRecalled memories and observations'
  relevant_memories = agent_components.all_similar_memories.AllSimilarMemories(
      model=model,
      components={
          _get_class_name(observation_summary): observation_summary_label,
          _get_class_name(time_display): 'The current date/time is'},
      num_memories_to_retrieve=10,
      pre_act_key=relevant_memories_label,
      logging_channel=measurements.get_channel('AllSimilarMemories').on_next,
  )

  if config.goal:
    goal_label = '\nOverarching goal'
    overarching_goal = agent_components.constant.Constant(
        state=config.goal,
        pre_act_key=goal_label,
        logging_channel=measurements.get_channel(goal_label).on_next)
  else:
    goal_label = None
    overarching_goal = None


  question_components = _make_question_components(
      agent_name=agent_name,
      model=model,
      clock=clock,
      measurements=measurements
  )

  core_components = (
      instructions,
      time_display,
      observation,
      observation_summary,
      relevant_memories,
  )

  entity_components = core_components + tuple(question_components)
  components_of_agent = {
      _get_class_name(component): component for component in entity_components
  }

  components_of_agent[
      agent_components.memory_component.DEFAULT_MEMORY_COMPONENT_NAME
  ] = agent_components.memory_component.MemoryComponent(raw_memory)
  component_order = list(components_of_agent.keys())
  if overarching_goal is not None:
    components_of_agent[goal_label] = overarching_goal
    # Place goal after the instructions.
    component_order.insert(1, goal_label)

  act_component = agent_components.concat_act_component.ConcatActComponent(
      model=model,
      clock=clock,
      component_order=component_order,
      logging_channel=measurements.get_channel('ActComponent').on_next,
  )

  agent = entity_agent_with_logging.EntityAgentWithLogging(
      agent_name=agent_name,
      act_component=act_component,
      context_components=components_of_agent,
      component_logging=measurements,
  )

  return agent


# In[ ]:


agent_module = importlib.import_module('my_agent')
get_ipython().system('pass  #zip my_agent.zip my_agent.py')


# # The simulation

# ## Initialize the simulation

# In[ ]:


# @title Select a scenario
from examples.deprecated.modular.scenario import scenarios
import ipywidgets as widgets

# Get all the scenarios
all_scenarios = [key for key in scenarios.SCENARIO_CONFIGS.keys()]

# Create the dropdown widget
dropdown = widgets.Dropdown(
    options=all_scenarios,
    value='haggling_0',
    description='Select a scenario to run on:',
    layout={'width': '500px'},  # Adjust the width as needed
    style={'description_width': 'initial'}
)

# Display the widget
display.display(dropdown)


# In[ ]:


SCEANRIO_NAME = dropdown.value
print(f"Selected scenario: {SCEANRIO_NAME}")


# In[ ]:


# @title Initialize the simulation
measurements = measurements_lib.Measurements()
runnable_simulation = scenarios.build_simulation(
    scenarios.SCENARIO_CONFIGS[SCEANRIO_NAME],
    model=model,
    embedder=embedder,
    measurements=measurements,
    focal_agent_module=agent_module,
    override_agent_model=call_limit_wrapper.CallLimitLanguageModel(model),
)


# ## Run the simulation

# In[ ]:


# @title Run the simulation
simulation_outcome, results_log = runnable_simulation()


# In[ ]:


# @title Calculate and print the score of the agent on the scenario
if scenarios.SCENARIO_CONFIGS[SCEANRIO_NAME].focal_is_resident:
  total_score = sum(simulation_outcome.resident_scores.values()) / len(simulation_outcome.resident_scores.values())
else:
  total_score = sum(simulation_outcome.visitor_scores.values()) / len(simulation_outcome.visitor_scores.values())

# Score is per-capita reward
print('SCORE: ', total_score)


# The score above is the score of your agent on the spefic scenario. To evaluate it on all of the scenarios, use the following script:
# https://github.com/google-deepmind/concordia/blob/main/examples/modular/launch_concordia_challenge_evaluation.py
#

# In[ ]:


# @title Display the results log
display.HTML(results_log)


# In[ ]:


# @title Summarise the perspective of each player
from IPython import display
from utils import html as html_lib

player_logs = []
player_log_names = []
for name, player_memory in (
    runnable_simulation.get_all_player_memories().items()):
  all_player_mem = list(player_memory.retrieve_recent(k=1000, add_time=True))
  all_player_mem = ['Memories:'] + all_player_mem
  player_html = html_lib.PythonObjectToHTMLConverter(all_player_mem).convert()
  player_logs.append(player_html)
  player_log_names.append(f'{name}')

player_memories_html = html_lib.combine_html_pages(
    player_logs,
    player_log_names,
    summary='',
    title='Player Memories',
)

player_memories_html = html_lib.finalise_html(player_memories_html)
display.HTML(player_memories_html)


# ## Save the results log

# In[ ]:


# @title Write the results log as an HTML file in the current working directory.
filename = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '.html'
file_handle = open(filename, 'a')
file_handle.write(results_log)
file_handle.close()


# Now that you have successfully built an agent and have a greater understanding of agent components, we highly recommend exploring on your own. Remember, agent components are fully customizable. Check out the tutorial on components to learn more: https://github.com/google-deepmind/concordia/blob/main/examples/tutorials/agent_components_tutorial.ipynb
#
# To work with a more flexible .py file, navigate to concordia/factory/agent and duplicate the basic_agent.py file to get started or just copy the my_agent.py that was created by this colab, which is a valid agent factory.
#
# Agent factory: https://github.com/google-deepmind/concordia/tree/main/concordia/factory/agent
#
#
# Agent’s that are in the factory can be tested on the full set of scenarios by running the following script
#
# Script for full evaluation across substrates: https://github.com/google-deepmind/concordia/blob/main/examples/modular/launch_concordia_challenge_evaluation.py
#
# More Tutorials: https://github.com/google-deepmind/concordia/tree/main/examples/tutorials
#
