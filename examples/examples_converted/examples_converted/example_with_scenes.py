#!/usr/bin/env python
# coding: utf-8

# # An example implementing the three key questions
#
# March and Olsen (2011) posit that humans generally act as though they choose their actions by answering three key questions:
#
# 1. What kind of situation is this?
# 2. What kind of person am I?
# 3. What does a person such as I do in a situation such as this?
#
# The agents used in this example implement these components. The premise of the simulation is that 4 friends are stuck at a snowed in pub. Also, it has just come to light that Alice stole Bob's car and crashed it.
#

# <a href="https://colab.research.google.com/github/google-deepmind/concordia/blob/main/examples/deprecated/example_with_scenes.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

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
from collections.abc import Callable, Mapping, Sequence
import concurrent.futures
import datetime

import matplotlib.pyplot as plt
import numpy as np
import sentence_transformers

from IPython import display

from agents.deprecated import deprecated_agent as basic_agent
from components import deprecated as generic_components
from components.agent.deprecated import to_be_deprecated as agent_components
from associative_memory.deprecated import associative_memory
from associative_memory.deprecated import blank_memories
from associative_memory.deprecated import formative_memories
from associative_memory.deprecated import importance_function
from clocks import game_clock
from components.orchestrator import deprecated as gm_components
from environment.deprecated import orchestrator
from environment.deprecated.scenes import runner

from language_model import language_model
from deprecated.metrics import goal_achievement
from deprecated.metrics import common_sense_morality
from deprecated.metrics import opinion_of_others
from thought_chains.deprecated import thought_chains as thought_chains_lib
from typing_custom.deprecatedrecated import agent as agent_lib
from typing_custom.deprecated import component
from typing_custom.deprecated import scene as scene_lib
from utils import html as html_lib
from utils.deprecated import measurements as measurements_lib
from utils import plotting

import termcolor


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


# ## Configuring the generic knowledge shared by players and GM.

# In[ ]:


# @title Shared memories are memories that all players and GM share.

DECISION_SCENE_TYPE = 'decision'

shared_memories = [
    'There is a pub called The Sundrop Saloon.',
    'It is impossible to leave the Sundrop Saloon, since it is snowed in.',
    "Alice stole Bob's car and crashed it.",
    ('Alice, Bob, and Dorothy always spend their evenings at the ' +
     'Sundrop Saloon.'),
]

# The shared context will be used for the NPC context. It reflects general
# knowledge and is possessed by all characters.
shared_context = model.sample_text(
    'Summarize the following passage in a concise and insightful fashion:\n'
    + '\n'.join(shared_memories)
    + '\n'
    + 'Summary:'
)
print(shared_context)


# In[ ]:


PERSONALITY_TRAITS = [
    "Aggressive",
    "Optimistic",
    "Kind",
    "Resilient",
    "Humorous",
    "Empathetic",
    "Ambitious",
    "Honest",
    "Loyal",
    "Pessimistic",
    "Arrogant",
    "Impulsive",
    "Jealous",
    "Manipulative",
    "Creative",
    "Analytical",
    "Confident",
    "Passionate",
    "Anxious",
    "Closed-minded",
    "Deceitful",
    "Insecure",
    "Irresponsible",
    "Vindictive",
    "Curious",
    "Energetic",
    "Sarcastic",
]

def get_trait() -> str:
  return np.random.choice(PERSONALITY_TRAITS)


# In[ ]:


#@title Creating character backgrounds, goals and traits. Modify to explore how it influences the outcomes
scenario_premise = [
    'Alice stole Bob\'s car and crashed it.',
    'There is a blizzard',
]
player_configs = [
    formative_memories.AgentConfig(
        name='Alice',
        gender='female',
        goal=('Alice wants to live her life without bothing to think about ' +
              'others.'),
        context=shared_context,
        traits=f'traits: Aggressive, {get_trait()}, and {get_trait()}',
        extras={
            'player_specific_memories': [
                f'Alice thinks Bob is {get_trait()}.',
                'Alice is a great driver, much better than Bob.',
                'Alice accidentally crashed Bob\'s car, but she\'s not sorry.',
                'Alice is very impatient and dislikes long conversations.',
            ]
        },
    ),
    formative_memories.AgentConfig(
        name='Bob',
        gender='male',
        goal='Bob wants Alice to pay for his car.',
        context=shared_context,
        traits=f'traits: {get_trait()}, {get_trait()}, and {get_trait()}',
        extras={
            'player_specific_memories': [
                'Bob had to save for years to afford his beloved car.'
            ]
        },
    ),
    formative_memories.AgentConfig(
        name='Dorothy',
        gender='female',
        goal=(
            'Dorothy wants to create a conflict between Bob and Alice for fun.'
        ),
        context=shared_context,
        traits=f'traits: {get_trait()}, {get_trait()}, and {get_trait()}',
        extras={
            'player_specific_memories': [
                'Dorothy grew up in Riverbend.',
                'Dorothy hates boring people.',
            ]
        },
    ),
]
num_players = len(player_configs)

player_configs_dict = {player.name: player for player in player_configs}


# In[ ]:


#@title Make the clock
time_step = datetime.timedelta(minutes=10)
SETUP_TIME = datetime.datetime(hour=20, year=2024, month=10, day=1)

START_TIME = datetime.datetime(hour=16, year=2024, month=10, day=2)
PUB_TIME = datetime.datetime(hour=23, year=2024, month=10, day=2)
clock = game_clock.MultiIntervalClock(
    start=SETUP_TIME,
    step_sizes=[time_step, datetime.timedelta(seconds=10)])


# In[ ]:


#@title Importance models
importance_model = importance_function.AgentImportanceModel(model)
importance_model_gm = importance_function.ConstantImportanceModel()


# ## Configure and build the players
#
# ---
#
#

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


#@title Agent architecture definition

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
  relevant_memories = agent_components.all_similar_memories.AllSimilarMemories(
      name='relevant memories',
      model=model,
      memory=mem,
      agent_name=agent_name,
      components=[summary_obs, self_perception],
      clock_now=clock.now,
      num_memories_to_retrieve=10,
  )
  situation_perception = agent_components.situation_perception.SituationPerception(
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
      components=[self_perception, situation_perception],
      verbose=True,
  )

  persona = generic_components.sequential.Sequential(
      name='persona',
      components=[
          self_perception,
          situation_perception,
          person_by_situation,
      ]
  )

  reflection = agent_components.dialectical_reflection.DialecticalReflection(
        name='reflection',
        model=model,
        memory=mem,
        agent_name=agent_config.name,
        intuition_components=[self_perception],
        thinking_components=[persona],
        clock_now=clock.now,
        num_memories_to_retrieve=3,
        verbose=True,
    )

  initial_goal_component = generic_components.constant.ConstantComponent(
      state=agent_config.goal, name='overarching goal')
  plan = agent_components.plan.SimPlan(
      model,
      mem,
      agent_config.name,
      clock_now=clock.now,
      components=[instructions, initial_goal_component, somatic_state, persona],
      goal=person_by_situation,
      horizon='the next hour',
      verbose=True,
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
      verbose=False,
      components=[instructions,
                  persona,
                  plan,
                  relevant_memories,
                  reflection,
                  time,
                  current_obs,
                  goal_metric,
                  morality_metric],
      update_interval = time_step
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
      question='What is {opining_player}\'s opinion of {of_player}?',
  )
  agent.add_component(reputation_metric)

  for extra_memory in agent_config.extras['player_specific_memories']:
    agent.observe(extra_memory)
  return agent, mem


# In[ ]:


player_configs = player_configs[:num_players]
player_names = [player.name for player in player_configs][:num_players]
measurements = measurements_lib.Measurements()

players = []
memories = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=num_players) as pool:
  for agent, mem in pool.map(build_agent,
                             player_configs[:num_players],
                             # All players get the same `player_names`.
                             [player_names] * num_players,
                             # All players get the same `measurements` object.
                             [measurements] * num_players):
    players.append(agent)
    memories[agent.name] = mem


# ## Build GM

# In[ ]:


orchestrator_memory = associative_memory.AssociativeMemory(
   sentence_embedder=embedder,
   importance=importance_model_gm.importance,
   clock=clock.now)


# In[ ]:


# @title Create components of the Game Master
player_names = [player.name for player in players]

scenario_knowledge = generic_components.constant.ConstantComponent(
    state=' '.join(shared_memories),
    name='Background')

player_status = gm_components.player_status.PlayerStatus(
    clock_now=clock.now,
    model=model,
    memory=orchestrator_memory,
    player_names=player_names)

convo_externality = gm_components.conversation.Conversation(
    players=players,
    model=model,
    memory=orchestrator_memory,
    clock=clock,
    burner_memory_factory=blank_memory_factory,
    components=[player_status],
    allow_self_talk=True,
    cap_nonplayer_characters=3,
    shared_context=shared_context,
    verbose=False,
)

direct_effect_externality = gm_components.direct_effect.DirectEffect(
    players=players,
    model=model,
    memory=orchestrator_memory,
    clock_now=clock.now,
    verbose=False,
    components=[player_status]
)

relevant_events = gm_components.relevant_events.RelevantEvents(
    clock.now, model, orchestrator_memory)
time_display = gm_components.time_display.TimeDisplay(clock)


# In[ ]:


# @title Create the game master's thought chain
account_for_agency_of_others = thought_chains_lib.AccountForAgencyOfOthers(
    model=model, players=players, verbose=False)
thought_chain = [
    thought_chains_lib.extract_direct_quote,
    thought_chains_lib.attempt_to_most_likely_outcome,
    thought_chains_lib.result_to_effect_caused_by_active_player,
    account_for_agency_of_others,
    thought_chains_lib.restore_direct_quote,
]


# In[ ]:


# @title Create the game master object
env = orchestrator.GameMaster(
    model=model,
    memory=orchestrator_memory,
    clock=clock,
    players=players,
    update_thought_chain=thought_chain,
    components=[
        scenario_knowledge,
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


# In[ ]:


# @title Create the decision scene logic component

class Drinking(component.Component):
  """Define an example component to track a choice about drinking.
  """

  def __init__(
      self,
      model: language_model.LanguageModel,
      memory: associative_memory.AssociativeMemory,
      drinking_option: str,
      resolution_scene: str,
      players: Sequence[basic_agent.BasicAgent],
      clock_now: Callable[[], datetime.datetime],
      name: str = 'free drinks',
      verbose: bool = False,
  ):
    """Initialize an example component to track a choice about drinking.

    Args:
      model: a language model
      memory: an associative memory
      drinking_option: which option choice constitutes drinking
      resolution_scene: on which scene type should this component be updated
        after the event, i.e. when to check the joint action and compute results
      players: sequence of agents (a superset of the active players)
      clock_now: Function to call to get current time.
      name: name of this component e.g. Possessions, Account, Property, etc
      verbose: whether to print the full update chain of thought or not
    """
    self._model = model
    self._memory = memory
    self._drinking_option = drinking_option
    self._players = players
    self._clock_now = clock_now
    self._name = name
    self._verbose = verbose

    self._history = []
    self._state = ''
    self._partial_states = {player.name: '' for player in self._players}

    self._resolution_scene = resolution_scene
    self._current_scene = gm_components.current_scene.CurrentScene(
        name='current scene type',
        memory=self._memory,
        clock_now=self._clock_now,
        verbose=self._verbose,
    )

    self.reset()
    self.update()

  def reset(self) -> None:
    pass

  def name(self) -> str:
    """Returns the name of this component."""
    return self._name

  def get_last_log(self):
    if self._history:
      return self._history[-1].copy()

  def get_history(self):
    return self._history.copy()

  def state(self) -> str:
    return self._state

  def partial_state(
      self,
      player_name: str,
  ) -> str:
    """Return a player-specific view of the component's state."""
    return self._partial_states[player_name]

  def update(self) -> None:
    self._current_scene.update()

  def _binarize_joint_action(
      self,
      joint_action: Mapping[str, str]) -> Mapping[str, int]:
    binary_joint_action = {name: act == self._drinking_option
                           for name, act in joint_action.items()}
    return binary_joint_action

  def update_before_event(self, player_action_attempt: str) -> None:
    # Get the current scene type.
    current_scene_type = self._current_scene.state()
    if current_scene_type == self._resolution_scene:
      # `player_action_attempt` is formatted as "name: attempt".
      player_name, choice_str = player_action_attempt.split(': ')
      if choice_str == self._drinking_option:
        self._partial_states[player_name] = (
            'Woah! That\'s one strong drink!')
      else:
        self._partial_states[player_name] = '...'

      if self._verbose:
        print(termcolor.colored(self.state(), 'yellow'))

    self._state = ' -- '.join(
          [f'{name}: {player_state}' for name, player_state
           in self._partial_states.items()])

  def update_after_event(
      self,
      unused_event_statement: str,
  ) -> None:
    update_log = {
        'date': self._clock_now(),
        'Summary': self.name(),
        'Drinks': self.state(),
    }
    self._memory.extend([self._state,])
    self._history.append(update_log)


# In[ ]:


vodka_choice = Drinking(
    model=model,
    memory=orchestrator_memory,
    drinking_option='yes',
    resolution_scene=DECISION_SCENE_TYPE,
    players=players,
    clock_now=clock.now,
    verbose=True,
)


# In[ ]:


# @title Create the decision scene game master

decision_action_spec = agent_lib.choice_action_spec(
    call_to_action=('Would {agent_name} drink it?'),
    options=('no', 'yes'),
    tag='decision',
)
decision_env = orchestrator.GameMaster(
    model=model,
    memory=orchestrator_memory,
    clock=clock,
    name='Decision Environment',
    players=players,
    components=[vodka_choice],
    action_spec=decision_action_spec,
    update_thought_chain=[thought_chains_lib.identity],
    randomise_initiative=True,
    player_observes_event=False,
    concurrent_externalities=False,
    verbose=True,
)


# In[ ]:


#@title Scenes

hour_increment = datetime.timedelta(hours=1)

car_crash_scene_premise = (
    'Alice just emerged alone from the wreckage of Bob\'s car. She crashed ' +
    'it. It\'s very lucky that no one was hurt. Bob will be so mad when he ' +
    'finds out.. especially since Alice had "borrowed" his car without asking..'
)
pub_scene_premise = ('Alice, Bob, and Dorothy are now at the ' +
                    'The Sundrop Saloon, and unfortunately trapped there due ' +
                    'to the blizzard. This will be a long night.')
decision_scene_premise = ('The bartender says, "since we are stuck here, ' +
                          'would any of you like a shot of vodka? It\'s on ' +
                          'the house!"')

scene_specs = {
    'car_crash': scene_lib.SceneTypeSpec(
        name='car_crash',
        premise={
            'Alice': [car_crash_scene_premise],
        },
    ),
    'pub': scene_lib.SceneTypeSpec(
        name='pub',
        premise={
            'Alice': [pub_scene_premise],
            'Bob': [pub_scene_premise],
            'Dorothy': [pub_scene_premise],
        },
    ),
    DECISION_SCENE_TYPE: scene_lib.SceneTypeSpec(
        name=DECISION_SCENE_TYPE,
        premise={
            'Alice': [decision_scene_premise],
            'Bob': [decision_scene_premise],
            'Dorothy': [decision_scene_premise],
        },
        action_spec=decision_action_spec,
        override_orchestrator=decision_env,
    ),
}

scenes = [
    scene_lib.SceneSpec(
        scene_type=scene_specs['car_crash'],
        start_time=START_TIME,
        participant_configs=[player_configs_dict['Alice']],
        num_rounds=1,
    ),
    scene_lib.SceneSpec(
        scene_type=scene_specs['pub'],
        start_time=PUB_TIME,
        participant_configs=player_configs,
        num_rounds=2,
    ),
    scene_lib.SceneSpec(
        scene_type=scene_specs['decision'],
        start_time=PUB_TIME + hour_increment,
        participant_configs=player_configs,
        num_rounds=1,
    ),
    scene_lib.SceneSpec(
        scene_type=scene_specs['pub'],
        start_time=PUB_TIME + (2 * hour_increment),
        participant_configs=player_configs,
        num_rounds=1,
    ),
    scene_lib.SceneSpec(
        scene_type=scene_specs['decision'],
        start_time=PUB_TIME + (3 * hour_increment),
        participant_configs=player_configs,
        num_rounds=1,
    ),
    scene_lib.SceneSpec(
        scene_type=scene_specs['pub'],
        start_time=PUB_TIME + (4 * hour_increment),
        participant_configs=player_configs,
        num_rounds=2,
    ),
]


# ## The RUN

# In[ ]:


clock.set(START_TIME)


# In[ ]:


for premise in scenario_premise:
  orchestrator_memory.add(premise)
  for player in players:
    player.observe(premise)


# In[ ]:


runner.run_scenes(
    environment=env,
    scenes=scenes,
    players=players,
    clock=clock,
)


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
      '\nWrite a short story that summarises these events.\n',
       max_tokens=3500, terminators=())

  all_player_mem = memories[player.name].retrieve_recent(k=1000, add_time=True)
  all_player_mem = ['Summary:', summary, 'Memories:'] + all_player_mem
  player_html = html_lib.PythonObjectToHTMLConverter(all_player_mem).convert()
  player_logs.append(player_html)
  player_log_names.append(f'{name}')


# In[ ]:


history_sources = [env, decision_env, vodka_choice]
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
    title='Friends in a pub experiment',
)

tabbed_html = html_lib.finalise_html(tabbed_html)


# In[ ]:


# @title Display the HTML log visualization
display.HTML(tabbed_html)


# #Interact with a specific player

# In[ ]:


sim_to_interact = 'Alice'  # @param ['Alice', 'Bob', 'Dorothy', 'Ellen'] {type:"string"}
user_identity = 'a close friend'  # @param {type:"string"}
interaction_premise = f'{sim_to_interact} is talking to {user_identity}\n'  # @param {type:"string"}

player_names = [player.name for player in players]
player_by_name = {player.name: player for player in players}
selected_player = player_by_name[sim_to_interact]
interrogation = interaction_premise


# In[ ]:


utterence_from_user = 'Did Bob accept your apology?'  # @param {type:"string"}

interrogation += f'{user_identity}: {utterence_from_user}'
player_says = selected_player.say(interrogation)
interrogation += f'\n{sim_to_interact}: {player_says}\n'
print(interrogation)
