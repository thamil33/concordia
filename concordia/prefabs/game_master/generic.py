"""A prefab containing a generic game master."""

from collections.abc import Mapping, Sequence
import copy
import dataclasses
from typing import Any

from concordia.agents import entity_agent_with_logging
from concordia.associative_memory import basic_associative_memory
from concordia.components import agent as actor_components
from concordia.components import game_master as gm_components
from concordia.language_model import language_model
from concordia.thought_chains import thought_chains as thought_chains_lib
from concordia.types_concordia import prefab as prefab_lib


@dataclasses.dataclass
class GameMaster(prefab_lib.Prefab):
  """A prefab entity implementing a generic game master."""

  description: str = 'A general purpose game master.'
  params: Mapping[str, Any] = dataclasses.field(
      default_factory=lambda: {
          'name': 'default rules',
          # Provide a comma-separated list of thought chain steps to use in the
          # event resolution component.
          'extra_event_resolution_steps': '',
          'extra_components': {},
          # A mapping from component name to the index at which to insert it
          # in the component order. If not specified, the extra components
          # will be inserted at the end of the component order.
          'extra_components_index': {},
          # If true, the actors will alternate in a round robin fashion.
          # Otherwise, the actors will be chosen by call to the game master.
          'acting_order': 'game_master_choice',
      }
  )
  entities: (
      Sequence[entity_agent_with_logging.EntityAgentWithLogging]
  ) = ()

  def build(
      self,
      model: language_model.LanguageModel,
      memory_bank: basic_associative_memory.AssociativeMemoryBank,
  ) -> entity_agent_with_logging.EntityAgentWithLogging:
    """Build a game master (i.e. a kind of entity).

    Args:
      model: The language model to use.
      memory_bank: The memory bank to use.

    Returns:
      An entity.
    """

    extra_components = self.params.get('extra_components', {})
    extra_components_index = self.params.get('extra_components_index', {})

    if extra_components_index and extra_components:
      if extra_components_index.keys() != extra_components.keys():
        raise ValueError(
            'extra_components_index must have the same keys as'
            ' extra_components.'
        )

    name = self.params.get('name')
    extra_event_resolution_steps = self.params.get(
        'extra_event_resolution_steps', ''
    )
    assert isinstance(extra_event_resolution_steps, str)  # For pytype.

    if ',' in extra_event_resolution_steps:
      extra_event_resolution_steps = [
          step.strip()
          for step in extra_event_resolution_steps.split(',')
          if step
      ]
    else:
      extra_event_resolution_steps = [extra_event_resolution_steps]

    memory_component_key = actor_components.memory.DEFAULT_MEMORY_COMPONENT_KEY
    memory_component = actor_components.memory.AssociativeMemory(
        memory_bank=memory_bank
    )

    instructions_key = 'instructions'
    instructions = gm_components.instructions.Instructions()

    examples_synchronous_key = 'examples'
    examples_synchronous = gm_components.instructions.ExamplesSynchronous()

    player_names = [entity.name for entity in self.entities]
    player_characters_key = 'player_characters'
    player_characters = gm_components.instructions.PlayerCharacters(
        player_characters=player_names,
    )

    observation_to_memory_key = 'observation_to_memory'
    observation_to_memory = actor_components.observation.ObservationToMemory()

    observation_component_key = (
        actor_components.observation.DEFAULT_OBSERVATION_COMPONENT_KEY
    )
    observation = actor_components.observation.LastNObservations(
        history_length=1000,
    )

    display_events_key = 'display_events'
    display_events = gm_components.event_resolution.DisplayEvents(
        model=model,
        pre_act_label=(
            'Story so far (ordered from oldest to most recent events)'),
    )

    relevant_memories_key = 'relevant_memories'
    relevant_memories = (
        actor_components.all_similar_memories.AllSimilarMemories(
            model=model,
            components=[
                display_events_key,
            ],
            num_memories_to_retrieve=5,
            pre_act_label='Background info',
        )
    )

    make_observation_key = (
        gm_components.make_observation.DEFAULT_MAKE_OBSERVATION_COMPONENT_KEY
    )
    make_observation = gm_components.make_observation.MakeObservation(
        model=model,
        player_names=player_names,
        components=[
            instructions_key,
            player_characters_key,
            relevant_memories_key,
            display_events_key,
        ],
        reformat_observations_in_specified_style=(
            'The format to use when describing the '
            'current situation to a player is: '
            '"//date or time//situation description".'
        ),
    )

    next_acting_kwargs = dict(
        model=model,
        components=[
            instructions_key,
            player_characters_key,
            relevant_memories_key,
            display_events_key,
        ],
    )
    next_actor_key = gm_components.next_acting.DEFAULT_NEXT_ACTING_COMPONENT_KEY
    acting_order = self.params.get(
        'acting_order', 'game_master_choice'
    )
    if acting_order == 'fixed':
      next_actor = gm_components.next_acting.NextActingInFixedOrder(
          sequence=player_names,
      )
    elif acting_order == 'game_master_choice':
      next_actor = gm_components.next_acting.NextActing(
          **next_acting_kwargs,
          player_names=player_names,
      )
    elif acting_order == 'random':
      next_actor = gm_components.next_acting.NextActingInRandomOrder(
          player_names=player_names,
      )
    else:
      raise ValueError(f'Unsupported acting order: {acting_order}')

    next_action_spec_kwargs = copy.copy(next_acting_kwargs)
    next_action_spec_key = (
        gm_components.next_acting.DEFAULT_NEXT_ACTION_SPEC_COMPONENT_KEY
    )
    next_action_spec = gm_components.next_acting.NextActionSpec(
        **next_action_spec_kwargs,
        player_names=player_names,
    )

    # Define thinking steps for the event resolution component to use whenever
    # it converts putative events like action suggestions into real events in
    # the simulation.
    account_for_agency_of_others = thought_chains_lib.AccountForAgencyOfOthers(
        model=model, players=self.entities, verbose=False
    )

    event_resolution_steps = [
        thought_chains_lib.maybe_inject_narrative_push,
        account_for_agency_of_others,
        thought_chains_lib.result_to_who_what_where,
    ]
    if extra_event_resolution_steps:
      for step in extra_event_resolution_steps:
        if step:
          event_resolution_steps.append(getattr(thought_chains_lib, step))

    event_resolution_components = [
        instructions_key,
        player_characters_key,
        relevant_memories_key,
        display_events_key,
    ]

    event_resolution_key = (
        gm_components.switch_act.DEFAULT_RESOLUTION_COMPONENT_KEY
    )
    event_resolution = gm_components.event_resolution.EventResolution(
        model=model,
        event_resolution_steps=event_resolution_steps,
        components=event_resolution_components,
        notify_observers=True,
    )

    components_of_game_master = {
        instructions_key: instructions,
        examples_synchronous_key: examples_synchronous,
        player_characters_key: player_characters,
        relevant_memories_key: relevant_memories,
        observation_component_key: observation,
        observation_to_memory_key: observation_to_memory,
        display_events_key: display_events,
        memory_component_key: memory_component,
        make_observation_key: make_observation,
        next_actor_key: next_actor,
        next_action_spec_key: next_action_spec,
        event_resolution_key: event_resolution,
    }

    component_order = list(components_of_game_master.keys())

    if extra_components:
      components_of_game_master.update(extra_components)
      if extra_components_index:
        for component_name in extra_components.keys():
          component_order.insert(
              extra_components_index[component_name],
              component_name,
          )
      else:
        component_order = list(components_of_game_master.keys())

    act_component = gm_components.switch_act.SwitchAct(
        model=model,
        entity_names=player_names,
        component_order=component_order,
    )

    game_master = entity_agent_with_logging.EntityAgentWithLogging(
        agent_name=name,
        act_component=act_component,
        context_components=components_of_game_master,
    )

    return game_master
