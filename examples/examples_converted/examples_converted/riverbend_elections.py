#!/usr/bin/env python
# coding: utf-8

# # Riverbend Election Example
#
# An illustrative social simulation with 5 players which simulates the day of mayoral elections in an imaginary town caller Riverbend. First two players, Alice and Bob, are running for the mayor. The third player, Charlie, is trying to ruin Alices' reputation with disinformation. The last two players have no specific agenda, apart from voting in the election.

# <a href="https://colab.research.google.com/github/google-deepmind/concordia/blob/main/examples/village/riverbend_elections.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

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
from collections.abc import Callable, Sequence
import concurrent.futures
import datetime
import random
import matplotlib.pyplot as plt

from IPython import display
import sentence_transformers

from associative_memory.deprecated import associative_memory
from associative_memory.deprecated import blank_memories
from associative_memory.deprecated import formative_memories
from associative_memory.deprecated import importance_function
from clocks import game_clock
from components.orchestrator import deprecated as gm_components
from environment.deprecated import orchestrator

from deprecated.metrics.v2 import context_free_rationality
from deprecated.metrics.v2 import context_free_common_sense_morality
from utils import html as html_lib
from utils.deprecated import measurements as measurements_lib
from utils import plotting

import termcolor

from agents import entity_agent_with_logging
from components import agent as agent_components
from memory_bank import legacy_associative_memory


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
    (
        'The local newspaper recently reported that someone has been dumping '
        + 'dangerous industrial chemicals in the Solripple river.'
    ),
    'All named characters are citizens. ',
    # 'All citizens are automatically candidates in all elections. ',
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

START_TIME = datetime.datetime(hour=9, year=2024, month=10, day=1)
clock = game_clock.MultiIntervalClock(
    start=SETUP_TIME,
    step_sizes=[datetime.timedelta(hours=1), datetime.timedelta(seconds=10)])

DEFAULT_PLANNING_HORIZON = 'the rest of the day, focusing most on the near term'


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


DEFAULT_PLANNING_HORIZON = 'the rest of the day, focusing most on the near term'

def _get_class_name(object_: object) -> str:
  return object_.__class__.__name__


# In[ ]:


def build_a_citizen(agent_config,
                    player_names: list[str],
                    measurements: measurements_lib.Measurements | None = None):

  mem = formative_memory_factory.make_memories(agent_config)
  raw_memory = legacy_associative_memory.AssociativeMemoryBank(mem)

  agent_name = agent_config.name

  instructions = agent_components.instructions.Instructions(
      agent_name=agent_name,
      logging_channel=measurements.get_channel('Instructions').on_next,
  )

  time_display_label = '\nCurrent time'
  time_display = agent_components.report_function.ReportFunction(
      function=clock.current_time_interval_str,
      pre_act_key=time_display_label,
      logging_channel=measurements.get_channel('TimeDisplay').on_next,
  )
  somatic_state_label = '\nSensations and feelings'
  somatic_state = (
          agent_components.question_of_query_associated_memories.SomaticState(
              model=model,
              clock_now=clock.now,
              logging_channel=measurements.get_channel('SomaticState').on_next,
              pre_act_key=somatic_state_label,
  ))
  identity_label = '\nIdentity characteristics'
  identity = agent_components.question_of_query_associated_memories.Identity(
      model=model,
      logging_channel=measurements.get_channel('Identity').on_next,
      pre_act_key=identity_label,
  )
  observation_label = '\nObservation'
  observation = agent_components.observation.Observation(
      clock_now=clock.now,
      timeframe=clock.get_step_size(),
      pre_act_key=observation_label,
      logging_channel=measurements.get_channel('Observation').on_next,
  )
  goal_key = 'Goal'
  goal_label = '\nOverarching goal'
  overarching_goal = agent_components.constant.Constant(
      state=agent_config.goal,
      pre_act_key=goal_label,
      logging_channel=measurements.get_channel(goal_label).on_next)
  plan = agent_components.plan.Plan(
      model=model,
      observation_component_name=_get_class_name(observation),
      components={_get_class_name(identity): identity_label,},
      clock_now=clock.now,
      goal_component_name=goal_key,
      horizon=DEFAULT_PLANNING_HORIZON,
      pre_act_key='\nPlan',
      logging_channel=measurements.get_channel('Plan').on_next,
  )

  observation_summary_label = '\nSummary of recent observations'
  observation_summary = agent_components.observation.ObservationSummary(
      model=model,
      clock_now=clock.now,
      timeframe_delta_from=datetime.timedelta(hours=4),
      timeframe_delta_until=datetime.timedelta(hours=0),
      pre_act_key=observation_summary_label,
      logging_channel=measurements.get_channel('ObservationSummary').on_next,
  )
  rationality_metric = (
      context_free_rationality.RationalityMetric(
          model=model,
          player_goal=agent_config.goal,
          clock=clock,
          logging_channel=measurements.get_channel(
              'RationalityMetric').on_next,
          measurements=measurements,
  ))
  morality_metric = (
      context_free_common_sense_morality.CommonSenseMoralityMetric(
          model=model,
          clock=clock,
          logging_channel=measurements.get_channel(
              'CommonSenseMorality').on_next,
          measurements=measurements,
  ))
  entity_components = (
      # Components that provide pre_act context.
      instructions,
      identity,
      plan,
      somatic_state,
      observation_summary,
      observation,
      time_display,
      rationality_metric,
      morality_metric,
  )
  components_of_agent = {_get_class_name(component): component
                         for component in entity_components}
  components_of_agent[goal_key] = overarching_goal
  components_of_agent[
      agent_components.memory_component.DEFAULT_MEMORY_COMPONENT_NAME] = (
          agent_components.memory_component.MemoryComponent(raw_memory))

  act_component = agent_components.concat_act_component.ConcatActComponent(
      model=model,
      clock=clock,
      logging_channel=measurements.get_channel('ActComponent').on_next,
  )
  agent = entity_agent_with_logging.EntityAgentWithLogging(
      agent_name=agent_name,
      act_component=act_component,
      context_components=components_of_agent,
      component_logging=measurements,
  )

  return agent, mem


# In[ ]:


def context_from_role(player_name, role, victim='Alice'):
  context = f'{shared_context}\n{player_name} grew up in Riverbend.'
  # Divide players into two classes, half are biased toward the status quo and
  # the other half want change.
  if 'conservative' in role:
    context = (
        f'{context} {player_name} feels strongly that Riverbend is '
        + 'already a great place to live and does not need to change.'
    )
  if 'progressive' in role:
    context = (
        f'{context} {player_name} feels strongly that Riverbend and '
        + 'its local government are in dire need of reform.'
    )
  # The first two players are mayoral candidates.
  if 'candidate' in role:
    context = (
        f'{context} Because of this, {player_name} plans to run for '
        + 'mayor of Riverbend.'
    )
  if 'active_voter' in role:
    context = (
        f'{context} {player_name} does not plan to run for mayor of Riverbend,'
        ' but would definitely vote in the election.'
    )

  # The third player has been hired to ruin the first player's reputation.
  if 'corrupt' in role:
    context = (
        f'{context}\n'
        + f"{player_name} has been hired to ruin {victim}'s "
        + 'reputation.\n'
        + f'{player_name} was hired by an anonymous email so '
        + f"they do not know who hired them to ruin {victim}'s "
        + 'reputation or what their motivation may be.\n'
        + f'{player_name} was given fake compromising material on'
        f' {victim}.\n{player_name} was offered a substantial sum of'
        ' money to spread compromising materials '
        + f"to ruin {victim}'s reputation."
    )

  return context


# ## Configure and build the players

# In[ ]:


victim = 'Alice'

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
        goal='Win the election and become the mayor of Riverbend',
        context=context_from_role('Alice', {'candidate', 'conservative'}),
        traits = make_random_big_five(),
        formative_ages = sorted(random.sample(range(5, 40), 5)),
    ),
    formative_memories.AgentConfig(
        name='Bob',
        gender='male',
        goal='Win the election and become the mayor of Riverbend.',
        context=context_from_role('Bob', {'candidate', 'progressive'}),
        traits = make_random_big_five(),
        formative_ages = sorted(random.sample(range(5, 40), 5)),
    ),
    formative_memories.AgentConfig(
        name='Charlie',
        gender='male',
        goal=f"Ruin {victim}'s reputation",
        context=context_from_role('Charlie', {'corrupt'}, victim),
        traits = make_random_big_five(),
        formative_ages = sorted(random.sample(range(5, 40), 5)),
    ),
    formative_memories.AgentConfig(
        name='Dorothy',
        gender='female',
        goal='Have a good day and vote in the election.',
        context=context_from_role(
            'Dorothy', {'active_voter', 'progressive'}
        ),
        traits = make_random_big_five(),
        formative_ages = sorted(random.sample(range(5, 40), 5)),
    ),
    formative_memories.AgentConfig(
        name='Ellen',
        gender='female',
        goal=(
            'Have a good day and vote in the election.'
        ),
        context=context_from_role('Ellen', {'active_voter', 'conservative'}),
        traits = make_random_big_five(),
        formative_ages = sorted(random.sample(range(5, 40), 5)),
    ),
]


# In[ ]:


NUM_PLAYERS = 5

player_configs = player_configs[:NUM_PLAYERS]
player_goals = {
    player_config.name: player_config.goal for player_config in player_configs}
players = []
memories = {}
measurements = measurements_lib.Measurements()

player_names = [player.name for player in player_configs][:NUM_PLAYERS]
with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_PLAYERS) as pool:
  for agent, mem in pool.map(build_a_citizen,
                             player_configs[:NUM_PLAYERS],
                             # All players get the same `player_names`.
                             [player_names] * NUM_PLAYERS,
                             # All players get the same `measurements` object.
                             [measurements] * NUM_PLAYERS):
    players.append(agent)
    memories[agent.name] = mem


# ## Build GM

# In[ ]:


# @title Define the election component

class Elections(component.Component):
  """Tracks elections."""

  def __init__(
      self,
      model: language_model.LanguageModel,
      memory: associative_memory.AssociativeMemory,
      voters: Sequence[entity_agent.EntityAgent],
      candidates: Sequence[str],
      clock_now: Callable[[], datetime.datetime],
      verbose: bool = False,
      measurements: measurements_lib.Measurements | None = None,
      channel: str = 'election',
  ):
    """Initializes the election tracker.

    Args:
      model: The language model to use.
      memory: The memory to use.
      voters: The agent voters.
      candidates: The candidates in the election.
      clock_now: Function to call to get current time. Used for logging.
      verbose: Whether to print verbose messages.
      measurements: Optional object to publish data from the elections.
      channel: Channel in measurements to publish to.
    """
    self._model = model
    self._memory = memory
    self._voters = voters
    self._candidates = candidates
    self._clock_now = clock_now
    self._verbose = verbose
    self._measurements = measurements
    self._channel = channel

    self._voter_names = [voter.name for voter in self._voters]
    self._vote_count = {candidate: 0 for candidate in self._candidates}
    self._citizens_who_already_voted = set()

    self._voter_by_name = {voter.name: voter for voter in self._voters}
    self._state = 'Polls are not open yet.'
    self._partial_states = None
    self._history = []

    self._polls_open = False
    self._winner_declared = False
    self._timestep = 0

  def get_last_log(self):
    if self._history:
      return self._history[-1].copy()

  def get_history(self):
    return self._history.copy()

  def open_polls(self) -> None:
    self._polls_open = True
    self._state = 'Polls are open, voting in progress.'

  def declare_winner(self) -> None:
    if not self._winner_declared:
      self._winner_declared = True
      self._polls_open = False
      winner = max(self._vote_count, key=self._vote_count.get)
      self._state = f'Polls are closed. {winner} won the election.'
      if self._verbose:
        print(termcolor.colored('\n' + self._state, 'red'), end='')

      self._memory.add(self._state, tags=['election tracker'])

  def name(self) -> str:
    return 'State of election'

  def state(self) -> str:
    return self._state

  def update(self) -> None:
    pass

  def get_vote_count(self) -> dict[str, int]:
    return self._vote_count

  def partial_state(
      self,
      player_name: str,
  ) -> str:
    """Return a player-specific view of the construct's state."""
    return self._state

  def update_after_event(
      self,
      event_statement: str,
  ) -> None:
    if not self._polls_open:
      update_log = {
          'date': self._clock_now(),
          'Summary': 'Polls are not open.',
          'Vote count': str(self._vote_count),
      }
      self._history.append(update_log)
      return

    chain_of_thought = interactive_document.InteractiveDocument(self._model)
    chain_of_thought.statement(event_statement)
    chain_of_thought.statement(f'List of citizens: {self._voter_names}')
    active_voter_id = chain_of_thought.multiple_choice_question(
        question='In the above transcript, which citizen took an action?',
        answers=self._voter_names,
    )
    vote = None
    active_voter = self._voter_names[active_voter_id]
    if active_voter not in self._citizens_who_already_voted:
      did_vote = chain_of_thought.yes_no_question(
          question=f'Did {active_voter} vote in the above transcript?'
      )
      if did_vote:
        question = (
            f'Current activity: {event_statement}.\nGiven the above, who whould'
            f' {active_voter} vote for?'
        )
        action_spec = agent_lib.ActionSpec(
            call_to_action=question,
            output_type='CHOICE',
            options=self._candidates,
            tag='vote',
        )
        vote = self._voter_by_name[active_voter].act(action_spec)
        action_spec.validate(vote)

        self._vote_count[vote] += 1
        self._citizens_who_already_voted.add(active_voter)
        self._memory.add(
            f'{active_voter} voted for {vote}', tags=['election tracker']
        )
        if self._verbose:
          print(
              termcolor.colored(
                  f'\n {active_voter} voted for {vote}\n', 'magenta'
              )
          )
      else:
        if self._verbose:
          print(
              termcolor.colored(
                  f'\n {active_voter} did not vote in the transcript.\n',
                  'magenta',
              )
          )
    else:
      chain_of_thought.statement(f'{active_voter} already voted.')

    update_log = {
        'date': self._clock_now(),
        'Summary': str(self._vote_count),
        'Vote count': str(self._vote_count),
        'Chain of thought': {
            'Summary': 'Election tracker chain of thought',
            'Chain': chain_of_thought.view().text().splitlines(),
        },
    }
    self._history.append(update_log)

    if self._verbose:
      print(
          termcolor.colored(
              f'{self._vote_count}\n' + chain_of_thought.view().text(),
              'magenta',
          )
      )

    if self._measurements is not None and vote is not None:
      answer = self._vote_count[vote]
      answer_str = str(answer)
      datum = {
          'time_str': self._clock_now().strftime('%H:%M:%S'),
          'timestep': self._timestep,
          'value_float': answer,
          'value_str': answer_str,
          'player': vote,
      }
      self._measurements.publish_datum(channel=self._channel, datum=datum)
      self._timestep += 1


# In[ ]:


# @title Create game master memory
orchestrator_memory = associative_memory.AssociativeMemory(
    embedder, importance_model_gm.importance, clock=clock.now)


# In[ ]:


# @title Initialize game master memories
for player in players:
  orchestrator_memory.add(f'{player.name} is at their private home.')


# In[ ]:


# @title Create components and externalities
player_names = [player.name for player in players]

facts_on_village = components.constant.ConstantComponent(
    ' '.join(shared_memories), 'General knowledge of Riverbend')
player_status = gm_components.player_status.PlayerStatus(
    clock.now, model, orchestrator_memory, player_names)

relevant_events = gm_components.relevant_events.RelevantEvents(
    clock.now, model, orchestrator_memory)
time_display = gm_components.time_display.TimeDisplay(clock)

election_externality = Elections(
    model=model,
    clock_now=clock.now,
    memory=orchestrator_memory,
    voters=players,
    candidates=['Alice', 'Bob'],
    verbose=True,
    measurements=measurements,
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
    memory=orchestrator_memory,
    clock=clock,
    burner_memory_factory=mem_factory,
    components=[player_status],
    cap_nonplayer_characters=2,
    shared_context=shared_context,
    verbose=True,
)

direct_effect_externality = gm_components.direct_effect.DirectEffect(
    players,
    model=model,
    memory=orchestrator_memory,
    clock_now=clock.now,
    verbose=False,
    components=[player_status]
)

TIME_POLLS_OPEN = datetime.datetime(hour=14, year=2024, month=10, day=1)
TIME_POLLS_CLOSE = datetime.datetime(hour=20, year=2024, month=10, day=1)
schedule = {
    'start': gm_components.schedule.EventData(
        time=START_TIME,
        description='',
    ),
    'election': gm_components.schedule.EventData(
        time=datetime.datetime(hour=13, year=2024, month=10, day=1),
        description=(
            'The town of Riverbend is now holding an election to determine ' +
            'who will become the mayor. ' +
            f'Polls will open at {TIME_POLLS_OPEN}.'),
    ),
    'election_polls_open': gm_components.schedule.EventData(
        time=TIME_POLLS_OPEN,
        description=(
            'The election is happening now. Polls are open. Everyone may ' +
            'go to a polling place and cast their vote. ' +
            f'Polls will close at {TIME_POLLS_CLOSE}.'),
        trigger=election_externality.open_polls,
    ),
    'election_polls_close': gm_components.schedule.EventData(
        time=TIME_POLLS_CLOSE,
        description=(
            'The election is over. Polls are now closed. The results will ' +
            'now be tallied and a winner declared.'),
        trigger=election_externality.declare_winner,
    )
}

schedule_construct = gm_components.schedule.Schedule(
    clock_now=clock.now, schedule=schedule)


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
        schedule_construct,
        election_externality,
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


for player in players:
  player.observe(
      f'{player.name} is at home, they have just woken up. Mayoral elections '
      f'are going to be held today. Polls will open at {TIME_POLLS_OPEN} and '
      f'close at {TIME_POLLS_CLOSE}.'
  )


# In[ ]:


# @title Expect about 2-3 minutes per step.

episode_length = 12  # @param {type: 'integer'}
for _ in range(episode_length):
  env.step()


# In[ ]:


# @title Metrics plotting

group_by = collections.defaultdict(lambda: 'player')

# available_channels = list(measurements.available_channels())
available_channels = ['RationalityMetric', 'CommonSenseMorality']

fig, ax = plt.subplots(1, len(available_channels), figsize=(6, 2))
tb = [channel for channel in available_channels]
for idx, channel in enumerate(available_channels):
  plotting.plot_line_measurement_channel(measurements, channel,
                                         group_by=group_by[channel],
                                         xaxis='time_str',
                                         ax=ax[idx])
  ax[idx].set_title(channel)

fig.set_constrained_layout(constrained=True)


# ## Summary and analysis of the episode

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


history_sources = [
    env,
    direct_effect_externality,
    convo_externality,
    election_externality,
]
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


utterence_from_user = 'Did you win the election?'  # @param {type:"string"}

interrogation += f'{user_identity}: {utterence_from_user}'
agent.observe(interrogation)
player_says = agent.act(action_spec=agent_lib.DEFAULT_SPEECH_ACTION_SPEC)
interrogation += f'\n{sim_to_interact}: {player_says}\n'
print(interrogation)
