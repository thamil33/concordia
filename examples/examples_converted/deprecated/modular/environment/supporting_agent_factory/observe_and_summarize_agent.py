

"""An Agent Factory."""

import datetime

from agents.deprecated import entity_agent_with_logging
from associative_memory.deprecated import associative_memory
from associative_memory.deprecated import formative_memories
from clocks import game_clock
from components.agent import deprecated as agent_components
from contrib.components.agent.deprecated import observations_since_last_update
from contrib.components.agent.deprecated import situation_representation_via_narrative
from deprecated.memory_bank import legacy_associative_memory
from language_model import language_model
from utils.deprecated import measurements as measurements_lib


def _get_class_name(object_: object) -> str:
  return object_.__class__.__name__


def build_agent(
    *,
    config: formative_memories.AgentConfig,
    model: language_model.LanguageModel,
    memory: associative_memory.AssociativeMemory,
    clock: game_clock.MultiIntervalClock,
    update_time_interval: datetime.timedelta | None = None,
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
  if config.extras.get('main_character', False):
    raise ValueError('This function is meant for a supporting character '
                     'but it was called on a main character.')

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
  observation = observations_since_last_update.ObservationsSinceLastUpdate(
      model=model,
      clock_now=clock.now,
      pre_act_key=observation_label,
      logging_channel=measurements.get_channel(
          'ObservationsSinceLastUpdate').on_next,
  )

  situation_representation_label = (
      f'\nQuestion: What situation is {agent_name} in right now?\nAnswer')
  situation_representation = (
      situation_representation_via_narrative.SituationRepresentation(
          model=model,
          clock_now=clock.now,
          pre_act_key=situation_representation_label,
          logging_channel=measurements.get_channel(
              'SituationRepresentation'
          ).on_next,
      )
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

  entity_components = (
      # Components that provide pre_act context.
      instructions,
      time_display,
      situation_representation,
      observation,
  )
  components_of_agent = {_get_class_name(component): component
                         for component in entity_components}
  components_of_agent[
      agent_components.memory_component.DEFAULT_MEMORY_COMPONENT_NAME] = (
          agent_components.memory_component.MemoryComponent(raw_memory))

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
