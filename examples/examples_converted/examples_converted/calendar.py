#!/usr/bin/env python
# coding: utf-8

# # Calendar Example
#
# An illustrative social simulation with 2 players which simulates phone interactions. The two players, Alice and Bob, have a smartphone with a Calendar app. Alice's goal is to setup a meeting with Bob using the Calendar app on her phone, taking Bob's schedulde into account when selecting the date/time.

# <a href="https://colab.research.google.com/github/google-deepmind/concordia/blob/main/examples/deprecated/phone/calendar.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

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


# @title Imports

import concurrent.futures
import datetime
import random

from IPython import display
import sentence_transformers

from components import deprecated as generic_components
from components.agent.deprecated import to_be_deprecated as components
from components.orchestrator import deprecated as gm_components
from agents import deprecated_agent as basic_agent
from associative_memory.deprecated import associative_memory
from associative_memory.deprecated import blank_memories
from associative_memory.deprecated import formative_memories
from associative_memory.deprecated import importance_function
from clocks import game_clock
from environment.deprecated import orchestrator

from utils import html as html_lib

from examples.deprecated.phone.components import apps
from examples.deprecated.phone.components import triggering


# In[ ]:


#@title Setup sentence encoder
st_model = sentence_transformers.SentenceTransformer(
    'sentence-transformers/all-mpnet-base-v2')
embedder = lambda x: st_model.encode(x, show_progress_bar=False)


# In[ ]:


# @title Language Model - pick your model and provide keys

# By default this colab uses GPT-4, so you must provide an API key.
# Note that it is also possible to use local models or other API models,
# simply replace this cell with the correct initialization for the model
# you want to use.
GPT_API_KEY = '' #@param {type: 'string'}
GPT_MODEL_NAME = 'gpt-4o' #@param {type: 'string'}

if not GPT_API_KEY:
  raise ValueError('GPT_API_KEY is required.')

model = gpt_model.GptLanguageModel(api_key=GPT_API_KEY,
                                   model_name=GPT_MODEL_NAME)


# ## Configuring the generic knowledge of the players and the game master (GM)

# In[ ]:


# @title Generic memories are memories that all players and GM share.

shared_memories = [
    'There is a hamlet named Riverbend.',
    'Riverbend is an idyllic rural town.',
    'The river Solripple runs through the village of Riverbend.',
    'The Solripple is a mighty river.',
    'Riverbend has a temperate climate.',
    'Riverbend has a main street.',
    'There is a guitar store on Main street Riverbend.',
    'There is a grocery store on Main street Riverbend.',
    'There is a school on Main street Riverbend.',
    'There is a library on Main street Riverbend.',
    'Riverbend has only one pub.',
    'There is a pub on Main street Riverbend called The Sundrop Saloon.',
    'Town hall meetings often take place at The Sundrop Saloon.',
    'Riverbend does not have a park',
    'The main crop grown on the farms near Riverbend is alfalfa.',
    'Farms near Riverbend depend on water from the Solripple river.',
    'There is no need to register in advance to be on the ballot.',
]

# The generic context will be used for the NPC context. It reflects general
# knowledge and is possessed by all characters.
shared_context = model.sample_text(
    'Summarize the following passage in a concise and insightful fashion:\n'
    + '\n'.join(shared_memories)
    + '\n'
    + 'Summary:'
)
print(shared_context)
importance_model = importance_function.ConstantImportanceModel()
importance_model_gm = importance_function.ConstantImportanceModel()


# In[ ]:


#@title Make the clock
SETUP_TIME = datetime.datetime(hour=8, year=2024, month=9, day=1)

START_TIME = datetime.datetime(hour=8, year=2024, month=10, day=1)
clock = game_clock.MultiIntervalClock(
    start=SETUP_TIME,
    step_sizes=[datetime.timedelta(minutes=15), datetime.timedelta(seconds=10)])


# ## Functions to build the players

# In[ ]:


blank_memory_factory = blank_memories.MemoryFactory(
    model=model,
    embedder=embedder,
    importance=importance_model.importance,
    clock_now=clock.now,
)

formative_memory_factory = formative_memories.FormativeMemoryFactory(
    model=model,
    shared_memories=shared_memories,
    blank_memory_factory_call=blank_memory_factory.make_blank_memory,
)


# In[ ]:


def build_agent(agent_config):

  mem = formative_memory_factory.make_memories(agent_config)

  # Build the player.

  time = generic_components.report_function.ReportFunction(
      name='Current time',
      function=clock.current_time_interval_str,
  )

  somatic_state = components.somatic_state.SomaticState(
      model, mem, agent_config.name, clock.now
  )
  identity = components.identity.SimIdentity(
    model=model,
    memory=mem,
    agent_name=agent_config.name,
    clock_now=clock.now,
  )
  goal_component = components.constant.ConstantComponent(state=agent_config.goal)
  plan = components.plan.SimPlan(
      model=model,
      memory=mem,
      agent_name=agent_config.name,
      clock_now=clock.now,
      components=[identity],
      goal=goal_component,
      verbose=False,
  )
  current_obs = components.observation.Observation(
      agent_name=agent_config.name,
      clock_now=clock.now,
      memory=mem,
      timeframe=clock.get_step_size(),
      component_name='current observations',
  )
  summary_obs = components.observation.ObservationSummary(
      agent_name=agent_config.name,
      model=model,
      clock_now=clock.now,
      memory=mem,
      timeframe_delta_from=datetime.timedelta(hours=4),
      timeframe_delta_until=datetime.timedelta(minutes=15),
      components=[identity],
      component_name='summary of observations',
  )

  agent = basic_agent.BasicAgent(
      model=model,
      agent_name=agent_config.name,
      clock=clock,
      verbose=True,
      components=[identity, plan, somatic_state, summary_obs, current_obs, time],
  )

  return agent, mem


# ## Configure and build the players

# In[ ]:


NUM_PLAYERS = 2

def make_random_big_five()->str:
  return str({
      'extraversion': random.randint(1, 10),
      'neuroticism': random.randint(1, 10),
      'openness': random.randint(1, 10),
      'conscientiousness': random.randint(1, 10),
      'agreeableness': random.randint(1, 10),
  })

scenario_premise = [

    (
        'Alice, Bob, Charlie and Dorothy are at the Sundrop Saloon. There '
        + 'is a snow storm and they have to wait it out inside.'
    ),
]
player_configs = [
    formative_memories.AgentConfig(
        name='Alice',
        gender='female',
        goal='Setup a meeting with Bob for two weeks from today using her smartphone.',
        context=f'{shared_context}\nAlice grew up in Riverbend.',
        traits = make_random_big_five()
            ),
    formative_memories.AgentConfig(
        name='Bob',
        gender='male',
        goal='Just chill and enjoy life.',
        context=f'{shared_context}\nBob grew up in Riverbend.',
        traits = make_random_big_five()
            ),
]


# In[ ]:


player_configs = player_configs[:NUM_PLAYERS]
player_goals = {
    player_config.name: player_config.goal for player_config in player_configs}
players = []
memories = {}

with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_PLAYERS) as pool:
  for agent, mem in pool.map(build_agent, player_configs[:NUM_PLAYERS]):
    players.append(agent)
    memories[agent.name] = mem


# ## Build the GM

# In[ ]:


orchestrator_memory = associative_memory.AssociativeMemory(
    embedder, importance_model_gm.importance, clock=clock.now)


# In[ ]:


for player in players:
  orchestrator_memory.add(f'{player.name} is at their private home.')


# In[ ]:


# @title Create components and externalities
citizen_names = [player.name for player in players]
player_names = [player.name for player in players]

facts_on_village = components.constant.ConstantComponent(' '.join(shared_memories), 'General knowledge of Riverbend')
player_status = gm_components.player_status.PlayerStatus(clock.now, model, orchestrator_memory, player_names)

relevant_events = gm_components.relevant_events.RelevantEvents(clock.now, model, orchestrator_memory)
time_display = gm_components.time_display.TimeDisplay(clock)


direct_effect_externality = gm_components.direct_effect.DirectEffect(
    players, memory=orchestrator_memory, model=model, clock_now=clock.now, verbose=False, components=[player_status]
)

toy_calendar = apps.ToyCalendar()
phones = [apps.Phone('Alice', apps=[toy_calendar]), apps.Phone('Bob', apps=[toy_calendar])]
phone_triggering = triggering.SceneTriggeringComponent(players, phones, model, memory=orchestrator_memory, clock=clock, memory_factory=blank_memory_factory)


# In[ ]:


# @title Create the game master object
env = orchestrator.GameMaster(
    model=model,
    memory=orchestrator_memory,
    clock=clock,
    players=players,
    components=[
        facts_on_village,
        player_status,
        direct_effect_externality,
        relevant_events,
        time_display,
        phone_triggering,
    ],
    randomise_initiative=True,
    player_observes_event=False,
    verbose=True,
)


# ## The RUN

# In[ ]:


clock.set(START_TIME)


# In[ ]:


for player in players:
  player.observe( f'{player.name} is at home, they have just woken up.')


# In[ ]:


# @title Expect about 2-3 minutes per step.
episode_length = 12  # @param {type: 'integer'}
for _ in range(episode_length):
  env.step()


# ## Summary and analysis of the episode

# In[ ]:


# @title Summarize the entire story
all_gm_memories = env._memory.retrieve_recent(k=10000, add_time=True)

detailed_story = '\n'.join(all_gm_memories)
print('len(detailed_story): ', len(detailed_story))
# print(detailed_story)

episode_summary = model.sample_text(
    f'Sequence of events:\n{detailed_story}'+
    '\nNarratively summarize the above temporally ordered ' +
    'sequence of events. Write it as a news report. Summary:\n',
     max_tokens=3500, terminators=())
print(episode_summary)


# In[ ]:


# @title Summarise the perspective of each player
player_logs = []
player_log_names = []
for player in players:
  name = player.name
  detailed_story = '\n'.join(memories[player.name].retrieve_recent(
      k=1000, add_time=True))
  summary = ''
  summary = model.sample_text(
      f'Sequence of events that happened to {name}:\n{detailed_story}'
      '\nWrite a short story that summarises these events.\n'
      ,
       max_tokens=3500, terminators=())

  all_player_mem = memories[player.name].retrieve_recent(k=1000, add_time=True)
  all_player_mem = ['Summary:', summary, 'Memories:'] + all_player_mem
  player_html = html_lib.PythonObjectToHTMLConverter(all_player_mem).convert()
  player_logs.append(player_html)
  player_log_names.append(f'{name}')


# ## Build and display HTML log of the experiment

# In[ ]:


history_sources = [env, direct_effect_externality]
histories_html = [html_lib.PythonObjectToHTMLConverter(history.get_history()).convert() for history in history_sources]
histories_names = [history.name for history in history_sources]


# In[ ]:


gm_mem_html = html_lib.PythonObjectToHTMLConverter(all_gm_memories).convert()

tabbed_html = html_lib.combine_html_pages(
    histories_html + [gm_mem_html] + player_logs,
    histories_names + ['GM'] + player_log_names,
    summary=episode_summary,
    title='Calendar experiment',
)

tabbed_html = html_lib.finalise_html(tabbed_html)


# In[ ]:


display.HTML(tabbed_html)


# ## Interact with a specific player

# In[ ]:


sim_to_interact = 'Alice'  # @param ['Alice', 'Bob','Charlie', 'Dorothy', 'Ellen'] {type:"string"}
user_identity = 'a close friend'  # @param {type:"string"}
interaction_premise = f'{sim_to_interact} is talking to {user_identity}\n'  # @param {type:"string"}

player_names = [player.name for player in players]
player_by_name = {player.name: player for player in players}
selected_player = player_by_name[sim_to_interact]
interrogation = interaction_premise


# In[ ]:


utterance_from_user = (
    "Hey Alice, I know you had planned to set up a meeting with Bob this morning "
    "between 8:00 and 8:30, but I wanted to double-check something. Did you "
    "actually open your calendar app and create the event today? I'm not asking "
    "about your intention or plan, but specifically whether you remember "
    "physically using your phone to schedule it. Can you think back and tell me "
    "if you concretely remember doing that action this morning? If you did, what "
    "exact time did you do it? And if not, that's okay too - I just want to make "
    "sure we're clear on whether it's been scheduled or if it's still on your to-do list."
) # @param {type:"string"}

interrogation += f'{user_identity}: {utterance_from_user}'
player_says = selected_player.say(interrogation)
interrogation += f'\n{sim_to_interact}: {player_says}\n'
print(interrogation)
