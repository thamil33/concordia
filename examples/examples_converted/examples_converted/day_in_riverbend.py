#!/usr/bin/env python
# coding: utf-8

# # Day in Riverbend Example
#
# An illustrative social simulation with 5 players which simulates a normal day in an imaginary town caller Riverbend. Each player has their own configurable backstory. The agents are configured to re-implement the architecure in Park et al. (2023) - they have reflection, plan, and identity components; their associative memory uses importance function. This is _not_ an exact re-implementation.
#
# Park, J.S., O'Brien, J.C., Cai, C.J., Morris, M.R., Liang, P. and Bernstein, M.S., 2023. Generative agents: Interactive simulacra of human behavior. arXiv preprint arXiv:2304.03442.

# <a href="https://colab.research.google.com/github/google-deepmind/concordia/blob/main/examples/village/day_in_riverbend.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

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

import collections
import concurrent.futures
import datetime
import random
import matplotlib.pyplot as plt

from IPython import display
import sentence_transformers

from agents.deprecated import deprecated_agent as basic_agent
from components import deprecated as generic_components
from associative_memory.deprecated import associative_memory
from associative_memory.deprecated import blank_memories
from associative_memory.deprecated import formative_memories
from associative_memory.deprecated import importance_function
from clocks import game_clock
from components.orchestrator import deprecated as gm_components
from environment.deprecated import orchestrator
from deprecated.metrics import goal_achievement
from deprecated.metrics import common_sense_morality
from deprecated.metrics import opinion_of_others
from utils import html as html_lib
from utils.deprecated import measurements as measurements_lib
from utils import plotting



# In[ ]:


# @title Setup sentence encoder
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


# ## Configuring the generic knowledge of players and GM.

# In[ ]:


#@title Make importance models

importance_model = importance_function.AgentImportanceModel(model)
importance_model_gm = importance_function.ConstantImportanceModel()


# In[ ]:


#@title Make the clock
SETUP_TIME = datetime.datetime(hour=8, year=2024, month=9, day=1)

START_TIME = datetime.datetime(hour=9, year=2024, month=10, day=1)
clock = game_clock.MultiIntervalClock(
    start=SETUP_TIME,
    step_sizes=[datetime.timedelta(hours=1), datetime.timedelta(seconds=10)])


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


# ## Functions to build the players

# In[ ]:


# @title setup formative memory factories
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


def build_agent(
    agent_config,
    player_names: list[str],
    measurements: measurements_lib.Measurements | None = None,
):
  mem = formative_memory_factory.make_memories(agent_config)

  # Build the player.

  time = components.report_function.ReportFunction(
      name='current_time', function=clock.current_time_interval_str
  )

  identity = components.identity.SimIdentity(model, mem, agent_config.name)
  goal_component = generic_components.constant.ConstantComponent(
      state=agent_config.goal
  )
  reflection = components.reflection.Reflection(
      model=model,
      memory=mem,
      agent_name=agent_config.name,
      importance_threshold=15.0,
      verbose=False,
  )
  plan = components.plan.SimPlan(
      model,
      mem,
      agent_config.name,
      clock_now=clock.now,
      components=[identity, time],
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
      timeframe_delta_until=datetime.timedelta(hours=1),
      components=[identity],
      component_name='summary of observations',
  )


  goal_metric = goal_achievement.GoalAchievementMetric(
      model=model,
      player_name=agent_config.name,
      player_goal=agent_config.goal,
      clock=clock,
      name='Goal Achievement',
      measurements=measurements,
      channel='goal_achievement',
      verbose=False,
  )
  morality_metric = common_sense_morality.CommonSenseMoralityMetric(
      model=model,
      player_name=agent_config.name,
      clock=clock,
      name='Morality',
      verbose=False,
      measurements=measurements,
      channel='common_sense_morality',
  )

  agent = basic_agent.BasicAgent(
      model,
      agent_name=agent_config.name,
      clock=clock,
      verbose=True,
      components=[
          identity,
          plan,
          reflection,
          time,
          summary_obs,
          current_obs,
          goal_metric,
          morality_metric,
      ],
  )

  reputation_metric = opinion_of_others.OpinionOfOthersMetric(
      model=model,
      player_name=agent_config.name,
      player_names=player_names,
      context_fn=agent.state,
      clock=clock,
      name='Opinion',
      verbose=False,
      measurements=measurements,
      channel='opinion_of_others',
      question="What is {opining_player}'s opinion of {of_player}?",
  )

  agent.add_component(reputation_metric)

  return agent, mem


# ## Configure and build the players

# In[ ]:


NUM_PLAYERS = 5

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
        goal='Organise a street party in Riverbend.',
        context=shared_context+'Alice is very socially active and knows everyone in town',
        traits = make_random_big_five()
            ),
    formative_memories.AgentConfig(
        name='Bob',
        gender='male',
        goal='Start a chess club in Riverbend.',
        context=shared_context + 'Bob is a chess enthusiast',
        traits = make_random_big_five()
            ),
    formative_memories.AgentConfig(
        name='Charlie',
        gender='male',
        goal='Organise an ale festival at the Sundrop Saloon.',
        context=shared_context + 'Charlie works at the Sundrop Saloon and loves real ales',
        traits = make_random_big_five()
            ),
    formative_memories.AgentConfig(
        name='Dorothy',
        gender='female',
        goal=(
            'Take students on a tour of Riverbend'
            ' it is funny.'
        ),
        context=shared_context + 'Dorothy is a teacher at school in Riverbend',
        traits = make_random_big_five()
            ),
    formative_memories.AgentConfig(
        name='Ellen',
        gender='female',
        goal=(
            'Write a paper on the history of Riverbend.'
        ),
        context=shared_context + 'Ellen is a librarian in the library in Riverbend',
        traits = make_random_big_five()
    ),
]


# In[ ]:


player_configs = player_configs[:NUM_PLAYERS]
player_names = [player.name for player in player_configs][:NUM_PLAYERS]
measurements = measurements_lib.Measurements()

players = []
memories = {}

with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_PLAYERS) as pool:
  for agent, mem in pool.map(build_agent,
                             player_configs[:NUM_PLAYERS],
                             # All players get the same `player_names`.
                             [player_names] * NUM_PLAYERS,
                             # All players get the same `measurements` object.
                             [measurements] * NUM_PLAYERS):
    players.append(agent)
    memories[agent.name] = mem


# ## Build GM

# In[ ]:


orchestrator_memory = associative_memory.AssociativeMemory(
    embedder, importance_model_gm.importance, clock=clock.now)


# In[ ]:





# In[ ]:


# @title Create components and externalities
citizen_names = [player.name for player in players]
player_names = [player.name for player in players]

facts_on_village = generic_components.constant.ConstantComponent(
    ' '.join(shared_memories), 'General knowledge of Riverbend'
)
player_status = gm_components.player_status.PlayerStatus(
    clock.now, model, orchestrator_memory, player_names
)

relevant_events = gm_components.relevant_events.RelevantEvents(
    clock.now, model, orchestrator_memory
)
time_display = gm_components.time_display.TimeDisplay(clock)


convo_externality = gm_components.conversation.Conversation(
    players,
    model,
    clock=clock,
    memory=orchestrator_memory,
    burner_memory_factory=blank_memory_factory,
    components=[player_status],
    cap_nonplayer_characters=2,
    shared_context=shared_context,
    verbose=False,
)

direct_effect_externality = gm_components.direct_effect.DirectEffect(
    players,
    model=model,
    memory=orchestrator_memory,
    clock_now=clock.now,
    verbose=False,
    components=[player_status],
)


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
        convo_externality,
        direct_effect_externality,
        relevant_events,
        time_display,
    ],
    randomise_initiative=True,
    player_observes_event=False,
    verbose=True,
)


# ## The RUN

# In[ ]:


clock.set(START_TIME)


# In[ ]:


#@title Initial observations and player location
for player in players:
  player.observe(
      f'{player.name} is at home, they have just woken up.'
  )
  orchestrator_memory.add(f'{player.name} is at their private home.')


# In[ ]:


# @title Expect about 2-3 minutes per step.
episode_length = 12  # @param {type: 'integer'}
for _ in range(episode_length):
  env.step()


# ## Summary and analysis of the episode

# In[ ]:


# @title Metrics plotting

group_by = collections.defaultdict(lambda: 'player')
group_by['opinion_of_others'] = 'of_player'

available_channels = list(measurements.available_channels())

fig, ax = plt.subplots(1, len(available_channels), figsize=(6, 2))
tb = [channel for channel in available_channels]
for idx, channel in enumerate(available_channels):
  plotting.plot_line_measurement_channel(measurements, channel,
                                         group_by=group_by[channel],
                                         xaxis='time_str',
                                         ax=ax[idx])
  ax[idx].set_title(channel)

fig.set_constrained_layout(constrained=True)


# In[ ]:


# @title Summarize the entire story.
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


# #Build and display HTML log of the experiment

# In[ ]:


history_sources = [env, direct_effect_externality, convo_externality]
histories_html = [html_lib.PythonObjectToHTMLConverter(history.get_history()).convert() for history in history_sources]
histories_names = [history.name for history in history_sources]


# In[ ]:


gm_mem_html = html_lib.PythonObjectToHTMLConverter(all_gm_memories).convert()

tabbed_html = html_lib.combine_html_pages(
    histories_html + [gm_mem_html] + player_logs,
    histories_names + ['GM'] + player_log_names,
    summary=episode_summary,
    title='Riverbend elections experiment',
)

tabbed_html = html_lib.finalise_html(tabbed_html)


# In[ ]:


display.HTML(tabbed_html)


# #Interact with a specific player

# In[ ]:


sim_to_interact = 'Alice'  # @param ['Alice', 'Bob','Charlie', 'Dorothy', 'Ellen'] {type:"string"}
user_identity = 'a close friend'  # @param {type:"string"}
interaction_premise = f'{sim_to_interact} is talking to {user_identity}\n'  # @param {type:"string"}

player_names = [player.name for player in players]
player_by_name = {player.name: player for player in players}
selected_player = player_by_name[sim_to_interact]
interrogation = interaction_premise


# In[ ]:


utterence_from_user = 'Did you win the elections?'  # @param {type:"string"}

interrogation += f'{user_identity}: {utterence_from_user}'
player_says = selected_player.say(interrogation)
interrogation += f'\n{sim_to_interact}: {player_says}\n'
print(interrogation)
