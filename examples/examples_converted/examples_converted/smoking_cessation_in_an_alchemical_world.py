#!/usr/bin/env python
# coding: utf-8

# # An example involving an agent trying to quit smoking in a world that also includes arbitrary background details about alchemy.
#

# <a href="https://colab.research.google.com/github/google-deepmind/concordia/blob/main/examples/deprecated/smoking_cessation_in_an_alchemical_world.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# ## Install packages and imports

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

import matplotlib.pyplot as plt
import numpy as np
from IPython import display
import sentence_transformers

from agents.deprecated import deprecated_agent as basic_agent
from components import deprecated as generic_components
from associative_memory.deprecated import associative_memory
from associative_memory.deprecated import blank_memories
from associative_memory.deprecated import formative_memories
from associative_memory.deprecated import importance_function
from clocks import game_clock
from components.agent.deprecated import to_be_deprecated as components
from components.orchestrator import deprecated as gm_components
from environment.deprecated import orchestrator
from contrib.components.agent import deprecated as agent_contrib

from deprecated.metrics import goal_achievement
from deprecated.metrics import common_sense_morality
from deprecated.metrics import opinion_of_others
from thought_chains.deprecated import thought_chains as thought_chains_lib
from utils import html as html_lib
from utils.deprecated import measurements as measurements_lib
from utils import plotting


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


# # Setup

# In[ ]:


#@title Make the clock
TIME_STEP = datetime.timedelta(minutes=20)
SETUP_TIME = datetime.datetime(hour=20, year=2024, month=10, day=1)

START_TIME = datetime.datetime(hour=12, year=2024, month=10, day=2)
clock = game_clock.MultiIntervalClock(
    start=SETUP_TIME,
    step_sizes=[TIME_STEP, datetime.timedelta(seconds=10)])


# In[ ]:


#@title Importance models
importance_model = importance_function.AgentImportanceModel(model)
importance_model_gm = importance_function.ConstantImportanceModel()


# In[ ]:


# @title Generic memories are memories that all players and GM share.

shared_memories = [
    'Riverbend is a small town.',
    ('There is a general store in Riverbend called The Oddments and Oddities ' +
     'Emporium.'),
    'Alice works in the general store.',
    'The Oddments and Oddities Emporium sells cigarettes',
    'The usual price of a pack of cigarettes is $10.',
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


# In[ ]:


#@title Seed some interesting world building elements

# These world building elements were drawn from the following book:
#    Roob, Alexander. (2021). Alchemy & Mysticism. Taschen.
# They are not exact quotes from the book, and the statements, such as they are,
# do not accurately portray alchemical "knowledge" (JZL permuted their words and
# ideas).


world_building_elements = [
    (
        'The region is full of darkness on account of an incorrect application '
        'of Joachim of Fiore\'s doctrines concerning Sal Alkali, the light '
        'of nature, a green dragon, and a philosopher\'s mercury. Only one as '
        'pure as a child may discover the treasure of Sal Alkali.'
    ),
    (
        'Nine philosophers on a ladder may embody the nine doubts in a '
        'nine-object realm of the universe. A ladder with thirty rungs '
        'represents the thirty virtues declared by John Kilmakos of Sinai.'
    ),
    (
        'The Lunar Vulcan is a secret fire formed by salts of the dew. '
        'It is said that once perfected, this fire may be able to revive '
        'the dead. It must be entrusted to digestion.'
    ),
    (
        'According to the Rosarium Philosophorum, the pelican feeds its young '
        'with blood. It symbolizes the final phase of the Multiplicatio.'
    ),
    (
        'The immortal Rebis may rise as one from a putrified grave, attended '
        'by ravens and adorned in philosophical gold and silver. Ulmannus '
        'spoke of an inward, spiritual sun embodying the divine Caduceus.'
    ),
    (
        'In the Ars Magna Lucis et Umbrae it is explained how the ladder of '
        'the number ten is divided and inscribed with the names of the '
        'Sefirot. In contrast, the Opus Magnum depicts the Sefirot in '
        'association with a tree, not a ladder.'
    ),
    (
        'Isidore of Seville found the Aurora Consurgens, and in its pages, '
        'he discovered the most remarkable truth: that a thing cannot be '
        'changed into another of a different nature without first being '
        'transformed into ash, lime, earth, or bile.'
    ),
    # The last of these elements was generated by an LLM (Claude 3). It is
    # related to addiction so it can form a bridge between the environment's
    # two themes: smoking cessation and alchemy.
    (
        'In Rosicrucian lore, the path to liberate the soul from addiction\'s '
        'earthly chains echoes the Magnum Opus. The nigredo plunges the addict '
        'into the abyss, their essence putrefied in the crucible of anguish. '
        'Amidst this darkness, hope sparkles in the albedo, as the soul is '
        'purified in sacred flames, transmuting leaden vice into silver '
        'virtue. At last, the rubedo dawns, the addict\'s spirit perfected, '
        'merged with the divine, reborn in luminous freedom, forever '
        'unshackled from the throes of their former sin.'
    ),
]

def get_world_element() -> str:
  return np.random.choice(world_building_elements)


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


# ## Functions to build the players

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

  current_obs = components.observation.Observation(
      agent_name=agent_config.name,
      clock_now=clock.now,
      memory=mem,
      timeframe=clock.get_step_size(),
      component_name='current observations',
  )
  somatic_state = components.somatic_state.SomaticState(
      model=model,
      memory=mem,
      agent_name=agent_config.name,
      clock_now=clock.now,
  )
  summary_obs = components.observation.ObservationSummary(
      agent_name=agent_config.name,
      model=model,
      clock_now=clock.now,
      memory=mem,
      components=[current_obs, somatic_state],
      timeframe_delta_from=datetime.timedelta(hours=4),
      timeframe_delta_until=datetime.timedelta(hours=1),
      component_name='summary of observations',
  )

  illness_sense = agent_contrib.illness_representation.IllnessRepresentation(
      name='consideration',
      model=model,
      memory=mem,
      agent_name=agent_config.name,
      components=[current_obs, somatic_state],
      clock_now=clock.now,
      num_memories_to_retrieve=25,
  )

  self_perception = components.self_perception.SelfPerception(
      name=f'answer to what kind of person is {agent_config.name}',
      model=model,
      memory=mem,
      agent_name=agent_config.name,
      clock_now=clock.now,
  )
  situation_perception = components.situation_perception.SituationPerception(
      name=(f'answer to what kind of situation is {agent_config.name} in ' +
            'right now'),
      model=model,
      memory=mem,
      agent_name=agent_config.name,
      components=[current_obs, illness_sense],
      clock_now=clock.now,
  )
  person_by_situation = components.person_by_situation.PersonBySituation(
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

  relevant_memories = components.all_similar_memories.AllSimilarMemories(
      name='relevant memories',
      model=model,
      memory=mem,
      agent_name=agent_config.name,
      components=[summary_obs, persona],
      clock_now=clock.now,
      num_memories_to_retrieve=25,
      verbose=False,
  )

  justification_components = components.justify_recent_voluntary_actions
  justification = justification_components.JustifyRecentVoluntaryActions(
      name='justification',
      model=model,
      memory=mem,
      agent_name=agent_config.name,
      components=[persona, somatic_state, relevant_memories],
      clock_now=clock.now,
      verbose=True,
  )
  reflection = components.dialectical_reflection.DialecticalReflection(
      name='reflection',
      model=model,
      memory=mem,
      agent_name=agent_config.name,
      intuition_components=[self_perception, justification],
      thinking_components=[persona],
      clock_now=clock.now,
      num_memories_to_retrieve=5,
      verbose=True,
  )

  initial_goal_component = generic_components.constant.ConstantComponent(
      state=agent_config.goal, name='overarching goal')
  plan = components.plan.SimPlan(
      model,
      mem,
      agent_config.name,
      clock_now=clock.now,
      components=[initial_goal_component, relevant_memories, persona],
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
                  justification,
                  reflection,
                  time,
                  current_obs,
                  goal_metric,
                  morality_metric],
      update_interval = TIME_STEP
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
  return agent, mem


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


# ## Configure and build the players

# In[ ]:


#@title Creating character backgrounds, goals and traits.
player_configs = [
    formative_memories.AgentConfig(
        name='Alice',
        gender='female',
        goal='Alice wants to sell as many cigarettes as possible.',
        context=('Alice is passionate about selling cigarettes.\n' +
                 'Alice does not believe smoking is harmful to health.\n' +
                 'Alice is a smoker.\n' +
                 f'Furthermore, Alice is aware that {get_world_element()} ' +
                 f'and that {get_world_element()}'),
        traits=f'traits: {get_trait()}, {get_trait()}, and {get_trait()}',
        extras={'initial_endowment': {'money': 20.0, 'cigarettes': 100.0},},
    ),
    formative_memories.AgentConfig(
        name='Bob',
        gender='male',
        goal='Bob wants to quit smoking.',
        context=('Bob has been a smoker for many years, and is addicted.\n' +
                 f'Furthermore, Bob is aware that {get_world_element()} ' +
                 f'and that {get_world_element()}'),
        traits=f'traits: {get_trait()}, {get_trait()}, and {get_trait()}',
        extras={'initial_endowment': {'money': 75.0, 'cigarettes': 1.0},},
    ),
    formative_memories.AgentConfig(
        name='Charlie',
        gender='male',
        goal='Charlie wants to continue smoking, and thinks others should too.',
        context=('Charlie has been a smoker for many years, and is '
                 'addicted.\n' +
                 f'Furthermore, Charlie is aware that {get_world_element()} ' +
                 f'and that {get_world_element()}'),
        traits=f'traits: {get_trait()}, {get_trait()}, and {get_trait()}',
        extras={'initial_endowment': {'money': 5.0, 'cigarettes': 0.0},},
    ),
    formative_memories.AgentConfig(
        name='Dorothy',
        gender='female',
        goal='Dorothy wants to help Bob quit smoking.',
        context=('Dorothy is secretly in love with Bob.\n' +
                 'Dorothy does not smoke.\n' +
                 'Dorothy believes secondhand smoke is dangerous to health.\n' +
                 'Dorothy is disgusted by smoking.\n' +
                 f'Furthermore, Dorothy is aware that: {get_world_element()} ' +
                 f'and that {get_world_element()}'),
        traits=f'traits: {get_trait()}, {get_trait()}, and {get_trait()}',
        extras={'initial_endowment': {'money': 50.0, 'cigarettes': 0.0},},
    ),
]

NUM_PLAYERS = len(player_configs)


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
   sentence_embedder=embedder,
   importance=importance_model_gm.importance,
   clock=clock.now)


# In[ ]:


# @title Create components of the Game Master
player_names = [player.name for player in players]

scenario_knowledge = generic_components.constant.ConstantComponent(
    state=' '.join(shared_memories),
    name='Background')
time_display=generic_components.report_function.ReportFunction(
    name='Current time',
    function=clock.current_time_interval_str,
  )

ItemTypeConfig = gm_components.inventory.ItemTypeConfig
money_config = ItemTypeConfig(name='money')
cigarettes_config = ItemTypeConfig(
    name='cigarettes', minimum=0, maximum=np.inf, force_integer=True)
player_initial_endowments = {
    config.name: config.extras['initial_endowment']
    for config in player_configs}
inventories = gm_components.inventory.Inventory(
    model=model,
    memory=orchestrator_memory,
    item_type_configs=[money_config, cigarettes_config],
    players=players,
    player_initial_endowments=player_initial_endowments,
    clock_now=clock.now,
    financial=True,
    name='Inventory',
    verbose=True,
)

player_status = gm_components.player_status.PlayerStatus(
    clock_now=clock.now,
    model=model,
    memory=orchestrator_memory,
    player_names=player_names)

world_background = (
    gm_contrib.world_background_and_relevance.WorldBackgroundAndRelevance(
        name='relevant background knowledge',
        model=model,
        memory=orchestrator_memory,
        # Mix the world-building elements with the shared memories
        world_building_elements=world_building_elements + shared_memories,
        players=players,
        components=[scenario_knowledge,
                    player_status,
                    inventories],
        clock_now=clock.now,
        num_factoids=30,
        num_memories_to_retrieve=25,
        verbose=True,
))

convo_externality = gm_components.conversation.Conversation(
    players=players,
    model=model,
    memory=orchestrator_memory,
    clock=clock,
    burner_memory_factory=blank_memory_factory,
    components=[player_status, inventories],
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
    components=[player_status, inventories, world_background]
)


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
        world_background,
        player_status,
        convo_externality,
        direct_effect_externality,
        inventories,
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


for player in players:
  orchestrator_memory.add(
      f'{player.name} is at The Oddments and Oddities Emporium.')

scenario_premise = (
    'Alice, Bob, and Charlie are at The Oddments and Oddities '
    'Emporium.'
)
orchestrator_memory.add(scenario_premise)


# In[ ]:


for player in players:
  player.observe(scenario_premise)


# In[ ]:


# @title Expect about 2-3 minutes per step.
episode_length = 8  # @param {type: 'integer'}
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
# print(detailed_story)

episode_summary = model.sample_text(
    f'Sequence of events:\n{detailed_story}'+
    '\nNarratively summarize the above temporally ordered ' +
    'sequence of events. Write it as a news report. Summary:\n',
     max_tokens=8000, terminators=())
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
       max_tokens=8000, terminators=())

  all_player_mem = memories[player.name].retrieve_recent(k=1000, add_time=True)
  all_player_mem = ['Summary:', summary, 'Memories:'] + all_player_mem
  player_html = html_lib.PythonObjectToHTMLConverter(all_player_mem).convert()
  player_logs.append(player_html)
  player_log_names.append(f'{name}')


# In[ ]:


history_sources = [env, direct_effect_externality, convo_externality]
histories_html = [
    html_lib.PythonObjectToHTMLConverter(history.get_history()).convert()
    for history in history_sources]
histories_names = [history.name for history in history_sources]


# In[ ]:


gm_mem_html = html_lib.PythonObjectToHTMLConverter(all_gm_memories).convert()

results_log_html = html_lib.combine_html_pages(
    histories_html + [gm_mem_html] + player_logs,
    histories_names + ['GM'] + player_log_names,
    summary=episode_summary,
    title='Smoking cessation experiment',
)
results_log_html = html_lib.finalise_html(results_log_html)


# In[ ]:


# @title Display the HTML log visualization
display.HTML(results_log_html)


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


utterence_from_user = 'Did you manage to sell any cigarettes?'  # @param {type:"string"}

interrogation += f'{user_identity}: {utterence_from_user}'
player_says = selected_player.say(interrogation)
interrogation += f'\n{sim_to_interact}: {player_says}\n'
print(interrogation)
