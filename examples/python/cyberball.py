#!/usr/bin/env python
# coding: utf-8

# # Cyberball Example
# 
# An example which simulates social exclusion and shows how to use a standard psychology questionnaire. This was inspired by:
# 
# Williams, K.D., Cheung, C.K. and Choi, W., 2000. Cyberostracism: effects of being ignored over the Internet. Journal of personality and social psychology, 79(5), p.748.

# <a href="https://colab.research.google.com/github/google-deepmind/concordia/blob/main/examples/deprecated/cyberball/cyberball.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# ## Setup and imports

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

import collections
from collections.abc import Callable, Sequence
import concurrent.futures
import datetime
import random
import matplotlib.pyplot as plt

from IPython import display
import sentence_transformers

from concordia.agents.deprecated import deprecated_agent as basic_agent
from concordia.components import deprecated as generic_components
from concordia.components.agent.deprecated import to_be_deprecated as agent_components
from concordia.components.game_master import deprecated as gm_components
from concordia.document import interactive_document
from concordia.associative_memory.deprecated import associative_memory
from concordia.associative_memory.deprecated import blank_memories
from concordia.associative_memory.deprecated import formative_memories
from concordia.associative_memory.deprecated import importance_function
from concordia.clocks import game_clock
from concordia.environment.deprecated import game_master
from concordia.language_model import language_model
from concordia.language_model import gpt_model
from concordia.deprecated.metrics import common_sense_morality
from concordia.deprecated.metrics import dass_questionnaire
from concordia.deprecated.metrics import opinion_of_others
from concordia.thought_chains.deprecated import thought_chains as thought_chains_lib
from concordia.typing.deprecated import component
from concordia.utils import html as html_lib
from concordia.utils.deprecated import measurements as measurements_lib
from concordia.utils import plotting


# In[ ]:


# Setup sentence encoder
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


# @title Generic memories are memories that all players and GM share.
INITIAL_BALL_HOLDER = 'Bob'

generic_memories = [
    'People are playing with a ball.',
    'The game is played by passing the ball whenever you have it.',
    'When a person has the ball, they should pass it to someone else.',
    'Most people find it enjoyable to pass the ball.',
    'Most people find it enjoyable to receive the ball.',
    'People like to throw the ball to people they like.',
    'The rules of the game prohibit stealing the ball.',
]

# The generic context will be used for the NPC context. It reflects general
# knowledge and is possessed by all characters.
generic_context = model.sample_text(
    'Summarize the following passage in a concise and insightful fashion:\n'
    + '\n'.join(generic_memories)
    + '\n'
    + 'Summary:'
)
print(generic_context)

importance_model = importance_function.ConstantImportanceModel()
importance_model_gm = importance_function.ConstantImportanceModel()


# In[ ]:


#@title Make the clock
UPDATE_INTERVAL = datetime.timedelta(minutes=1)

SETUP_TIME = datetime.datetime(hour=8, year=2024, month=9, day=1)

START_TIME = datetime.datetime(hour=14, year=2024, month=10, day=1)
clock = game_clock.MultiIntervalClock(
    start=SETUP_TIME,
    step_sizes=[UPDATE_INTERVAL, datetime.timedelta(seconds=10)])


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
    shared_memories=generic_memories,
    blank_memory_factory_call=blank_memory_factory.make_blank_memory,
)


# In[ ]:


def build_agent(agent_config,
                player_names: list[str],
                measurements: measurements_lib.Measurements | None = None):
  mem = formative_memory_factory.make_memories(agent_config)

  agent_name = agent_config.name
  instructions = generic_components.constant.ConstantComponent(
      state=(
          f'The instructions for how to play the role of {agent_name} are as '
          'follows. This is a social science experiment studying how well you '
          f'play the role of a character named {agent_name}. The experiment '
          'is structured as a tabletop roleplaying game (like dungeons and '
          'dragons). However, in this case it is a serious social science '
          'experiment and simulation. The goal is to be realistic. It is '
          f'important to play the role of a person like {agent_name} as '
          f'accurately as possible, i.e., by responding in ways that you think '
          f'it is likely a person like {agent_name} would respond, and taking '
          f'into account all information about {agent_name} that you have. '
          'Always use third-person limited perspective.'
      ),
      name='role playing instructions\n')

  time = generic_components.report_function.ReportFunction(
    name='Current time',
    function=clock.current_time_interval_str,
  )

  current_obs = agent_components.observation.Observation(
            agent_name=agent_config.name,
      clock_now=clock.now,
      memory=mem,
      timeframe=clock.get_step_size(),
      component_name='current observations',
  )
  somatic_state = agent_components.somatic_state.SomaticState(
      model=model,
      memory=mem,
      agent_name=agent_config.name,
      clock_now=clock.now,
  )
  summary_obs = agent_components.observation.ObservationSummary(
      agent_name=agent_config.name,
      model=model,
      clock_now=clock.now,
      memory=mem,
      components=[current_obs, somatic_state],
      timeframe_delta_from=datetime.timedelta(hours=4),
      timeframe_delta_until=datetime.timedelta(hours=1),
      component_name='summary of observations',
  )

  self_perception = agent_components.self_perception.SelfPerception(
      name=f'answer to what kind of person is {agent_config.name}',
      model=model,
      memory=mem,
      agent_name=agent_config.name,
      clock_now=clock.now,
  )
  situation_viewer = agent_components.situation_perception.SituationPerception(
      name=(f'answer to what kind of situation is {agent_config.name} in ' +
            'right now'),
      model=model,
      memory=mem,
      agent_name=agent_config.name,
      components=[current_obs, somatic_state, summary_obs],
      clock_now=clock.now,
  )
  person_by_situation = agent_components.person_by_situation.PersonBySituation(
      name=(f'answer to what would a person like {agent_config.name} do in a ' +
            'situation like this'),
      model=model,
      memory=mem,
      agent_name=agent_config.name,
      clock_now=clock.now,
      components=[self_perception, situation_viewer],
      num_memories_to_retrieve=2,
  )

  initial_goal_component = generic_components.constant.ConstantComponent(
      state='have fun playing the game with others', name='overarching goal')

  persona = generic_components.sequential.Sequential(
      name='persona',
      components=[
          self_perception,
          situation_viewer,
          person_by_situation,
      ]
  )

  plan = agent_components.plan.SimPlan(
      model,
      mem,
      agent_config.name,
      clock_now=clock.now,
      components=[initial_goal_component, time, persona],
      goal=person_by_situation,
      horizon='the next five minutes',
  )

  morality_metric = common_sense_morality.CommonSenseMoralityMetric(
      model=model,
      player_name=agent_config.name,
      clock=clock,
      name='Morality',
      measurements=measurements,
      channel='common_sense_morality',
  )

  agent = basic_agent.BasicAgent(
      model,
      agent_name=agent_config.name,
      clock=clock,
      components=[instructions,
                  persona,
                  plan,
                  time,
                  current_obs,
                  morality_metric],
      update_interval=UPDATE_INTERVAL,
  )
  reputation_metric = opinion_of_others.OpinionOfOthersMetric(
      model=model,
      player_name=agent_config.name,
      player_names=player_names,
      context_fn=agent.state,
      clock=clock,
      name='Opinion',
      measurements=measurements,
      channel='opinion_of_others',
      question='What is {opining_player}\'s opinion of {of_player}?',
  )
  depression_metric = dass_questionnaire.Depression(
      model=model,
      player_name=agent_config.name,
      context_fn=agent.state,
      clock=clock,
      measurements=measurements,
  )
  anxiety_metric = dass_questionnaire.Anxiety(
      model=model,
      player_name=agent_config.name,
      context_fn=agent.state,
      clock=clock,
      measurements=measurements,
  )
  stress_metric = dass_questionnaire.Stress(
      model=model,
      player_name=agent_config.name,
      context_fn=agent.state,
      clock=clock,
      measurements=measurements,
  )
  agent.add_component(reputation_metric)
  agent.add_component(depression_metric)
  agent.add_component(anxiety_metric)
  agent.add_component(stress_metric)

  return agent, mem


# In[ ]:


def specific_memories_from_role(player_name: str, outcast: str = 'none') -> str:
  specific_memories = (
      f'{player_name} loves the game.\n')
  specific_memories += (
      f'{player_name} passes the ball to a friend whenever they can.\n')
  specific_memories += (
      f'{player_name} picks a specific friend to pass the ' +
      'ball to whenever they get the chance.\n')
  if player_name != outcast:
    specific_memories += f'{player_name} dislikes {outcast}.\n'
    specific_memories += (f'{player_name} will never pass the ball ' +
                          f'to {outcast}.\n')
  return specific_memories


# ## Configure and build the players

# In[ ]:


NUM_PLAYERS = 5
outcast = 'Alice'

def make_random_big_five()->str:
  return str({
      'extraversion': random.randint(1, 10),
      'neuroticism': random.randint(1, 10),
      'openness': random.randint(1, 10),
      'conscientiousness': random.randint(1, 10),
      'agreeableness': random.randint(1, 10),
  })

player_configs = [
    formative_memories.AgentConfig(
        name='Alice',
        gender='female',
        specific_memories=specific_memories_from_role('Alice',
                                                      outcast=outcast),
        traits = make_random_big_five(),
        date_of_birth=datetime.datetime(
            year=2000, month=random.randint(1, 12), day=3, hour=0, minute=0),
        formative_ages = sorted(random.sample(range(5, 20), 7)),
    ),
    formative_memories.AgentConfig(
        name='Bob',
        gender='male',
        specific_memories=specific_memories_from_role('Bob',
                                                      outcast=outcast),
        traits = make_random_big_five(),
        date_of_birth=datetime.datetime(
            year=2000, month=random.randint(1, 12), day=3, hour=0, minute=0),
        formative_ages = sorted(random.sample(range(5, 20), 7)),
        context=f'Bob has good reason to hate {outcast}.',
    ),
    formative_memories.AgentConfig(
        name='Charlie',
        gender='male',
        specific_memories=specific_memories_from_role('Charlie',
                                                      outcast=outcast),
        traits = make_random_big_five(),
        date_of_birth=datetime.datetime(
            year=2000, month=random.randint(1, 12), day=3, hour=0, minute=0),
        formative_ages = sorted(random.sample(range(5, 20), 7)),
        context=f'Charlie has good reason to hate {outcast}.',
    ),
    formative_memories.AgentConfig(
        name='Dorothy',
        gender='female',
        specific_memories=specific_memories_from_role('Dorothy',
                                                      outcast=outcast),
        traits = make_random_big_five(),
        date_of_birth=datetime.datetime(
            year=2000, month=random.randint(1, 12), day=3, hour=0, minute=0),
        formative_ages = sorted(random.sample(range(5, 20), 7)),
        context=f'Dorothy has good reason to hate {outcast}.',
    ),
    formative_memories.AgentConfig(
        name='Ellen',
        gender='female',
        specific_memories=specific_memories_from_role('Ellen',
                                                      outcast=outcast),
        traits = make_random_big_five(),
        date_of_birth=datetime.datetime(
            year=2000, month=random.randint(1, 12), day=3, hour=0, minute=0),
        formative_ages = sorted(random.sample(range(5, 20), 7)),
        context=f'Ellen has good reason to hate {outcast}.',
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


game_master_memory = associative_memory.AssociativeMemory(
    embedder, importance_model_gm.importance, clock=clock.now)


# In[ ]:


# @title Define the ball status component

class BallStatus(component.Component):
  """Tracks the status of the ball."""

  def __init__(
      self,
      clock_now: Callable[[], datetime.datetime],
      model: language_model.LanguageModel,
      memory: associative_memory.AssociativeMemory,
      player_names: Sequence[str],
      initial_ball_holder: str = '',
      num_memories_to_retrieve: int = 10,
      verbose: bool = False,
  ):
    self._memory = memory
    self._model = model
    self._state = f'{initial_ball_holder} has the ball.'
    self._player_names = player_names
    self._partial_states = {name: self._state for name in self._player_names}
    self._verbose = verbose
    self._history = []
    self._clock_now = clock_now
    self._num_memories_to_retrieve = num_memories_to_retrieve

  def name(self) -> str:
    return 'Player who has the ball now'

  def state(self) -> str:
    return self._state

  def get_history(self):
    return self._history.copy()

  def get_last_log(self):
    if self._history:
      return self._history[-1].copy()

  def partial_state(
      self,
      player_name: str,
  ) -> str:
    """Return a player-specific view of who has the ball."""
    return self._partial_states[player_name]

  def update_after_event(
      self,
      event_statement: str,
  ) -> None:
    self._state = '\n'
    self._partial_states = {name: '' for name in self._player_names}

    prompt = interactive_document.InteractiveDocument(self._model)

    time_now = self._clock_now().strftime('[%d %b %Y %H:%M:%S]')

    memories = self._memory.retrieve_by_regex('ball')
    mems = memories[-self._num_memories_to_retrieve:]
    prompt.statement(f'Some recent events:\n{mems}')
    prompt.statement(f'The latest event: {time_now} {event_statement}')

    prompt.statement(f'The current time is: {time_now}\n')
    ball_location_idx = prompt.multiple_choice_question(
        question=('Given all the above events and their timestamps, who has ' +
                  'the ball now?'),
        answers=self._player_names,
    )
    ball_location = self._player_names[ball_location_idx]
    if self._verbose:
      print(prompt.view().text())

    state_string = f'{ball_location} has the ball.'
    self._state = state_string
    for player_name in self._player_names:
      self._partial_states[player_name] = state_string

    update_log = {
        'date': self._clock_now(),
        'state': self._state,
        'partial states': self._partial_states,
        'context': prompt.view().text().splitlines(),
    }
    self._history.append(update_log)


# In[ ]:


# @title Create components and externalities
player_names = [player.name for player in players]

general_knowledge_of_premise = generic_components.constant.ConstantComponent(
    ', '.join(generic_memories), 'General knowledge of the game')
important_facts = generic_components.constant.ConstantComponent(
    (f'The only people playing the game are: {player_names}. There are no ' +
     'other people around. One person from this list always has the ball.'),
    'Facts')
rules_of_the_game = generic_components.constant.ConstantComponent(
    ('Players who do not have the ball must wait their turn. Whenever a ' +
     'player passes the ball they must call out the name of the person ' +
     'to whom they throw it.'),
    'Rules of the game')

player_status = gm_components.player_status.PlayerStatus(
    clock.now, model, game_master_memory, player_names)
ball_status_component = BallStatus(
    clock.now, model, game_master_memory, player_names,
    initial_ball_holder=INITIAL_BALL_HOLDER)

relevant_events = gm_components.relevant_events.RelevantEvents(
    clock_now=clock.now,
    model=model,
    memory=game_master_memory,
)
time_display = gm_components.time_display.TimeDisplay(
    game_clock=clock,
)

mem_factory = blank_memories.MemoryFactory(
    model,
    embedder,
    importance_model_gm.importance,
    clock_now=clock.now,
)

convo_externality = gm_components.conversation.Conversation(
    players=players,
    model=model,
    memory=game_master_memory,
    clock=clock,
    burner_memory_factory=mem_factory,
    components=[
        time_display,
        player_status,
        ball_status_component,
    ],
    cap_nonplayer_characters=2,
    shared_context=generic_context,
    verbose=True,
)

direct_effect_externality = gm_components.direct_effect.DirectEffect(
    players,
    model=model,
    memory=game_master_memory,
    clock_now=clock.now,
    verbose=False,
    components=[
        time_display,
        player_status,
        ball_status_component,
    ]
)


# In[ ]:


# @title Create the game master's thought chain

def does_active_player_have_the_ball(
    chain_of_thought: interactive_document.InteractiveDocument,
    premise: str,
    active_player_name: str,
):
  """Add cyberball-specific questions to the thought chain.

  Args:
    chain_of_thought: the document to condition on and record the thoughts
    premise: the attempted action
    active_player_name: name of player whose turn it currently is

  Returns:
    string describing the outcome
  """
  proceed = chain_of_thought.yes_no_question(
      question=f'Does {active_player_name} have the ball?')
  if proceed:
    _ = chain_of_thought.open_question(
        f'Does the text above indicate that {active_player_name} is passing ' +
        'the ball right now? If so, which player are they passing it to?')
  return premise

account_for_agency_of_others = thought_chains_lib.AccountForAgencyOfOthers(
    model=model, players=players, verbose=False)

thought_chain = [
    does_active_player_have_the_ball,
    thought_chains_lib.attempt_to_most_likely_outcome,
    thought_chains_lib.result_to_effect_caused_by_active_player,
    account_for_agency_of_others
]


# In[ ]:


# @title Create the game master object
env = game_master.GameMaster(
    model=model,
    memory=game_master_memory,
    clock=clock,
    players=players,
    update_thought_chain=thought_chain,
    components=[
        general_knowledge_of_premise,
        important_facts,
        rules_of_the_game,
        relevant_events,
        time_display,
        player_status,
        ball_status_component,
        convo_externality,
        direct_effect_externality,
    ],
    randomise_initiative=True,
    player_observes_event=False,
    players_act_simultaneously=False,
    verbose=True,
)


# ## The RUN

# In[ ]:


clock.set(START_TIME)


# In[ ]:


# Set memory of the starting point for players and GM.

def set_starting_point(premise: str):
  for player in players:
    player.observe(f'{player.name} {premise}.')
  for player in players:
    game_master_memory.add(f'{player.name} {premise}.')

premise = 'is at the field playing the game'
set_starting_point(premise)


# In[ ]:


# Pick which player starts out with the ball

def set_initial_ball_holder(player_with_ball: str):
  for player in players:
    player.observe(f'{player_with_ball} has the ball.')
  game_master_memory.add(f'{player_with_ball} has the ball.')

set_initial_ball_holder(INITIAL_BALL_HOLDER)


# In[ ]:





# In[ ]:


# @title Expect about 2-3 minutes per step.
episode_length = 10  # @param {type: 'integer'}
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


# #Build and display HTML log of the experiment

# ## Prepare to visualize text results with HTML

# In[ ]:


# @title Summarize the entire story.
all_gm_memories = env._memory.retrieve_recent(k=10000, add_time=True)

detailed_story = '\n'.join(all_gm_memories)
print('len(detailed_story): ', len(detailed_story))

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


# In[ ]:


history_sources = [
    env, direct_effect_externality, convo_externality, ball_status_component]
histories_html = [
    html_lib.PythonObjectToHTMLConverter(history.get_history()).convert()
    for history in history_sources]
histories_names = [history.name for history in history_sources]


# In[ ]:


gm_mem_html = html_lib.PythonObjectToHTMLConverter(all_gm_memories).convert()

tabbed_html = html_lib.combine_html_pages(
    histories_html + [gm_mem_html] + player_logs,
    histories_names + ['GM'] + player_log_names,
    summary=episode_summary,
    title='Cyberball experiment',
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


utterence_from_user = 'How did you feel about the game?'  # @param {type:"string"}

interrogation += f'{user_identity}: {utterence_from_user}'
player_says = selected_player.say(interrogation)
interrogation += f'\n{sim_to_interact}: {player_says}\n'
print(interrogation)


# ```
#  2023 DeepMind Technologies Limited.
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
