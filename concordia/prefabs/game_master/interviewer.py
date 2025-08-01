"""A prefab for a game master that administers questionnaires."""

from collections.abc import Mapping, Sequence
import dataclasses
from typing import Any

from concordia.agents import entity_agent_with_logging
from concordia.associative_memory import basic_associative_memory
from concordia.components import game_master as gm_components
from concordia.language_model import language_model
from concordia.types_concordia import prefab as prefab_lib


@dataclasses.dataclass
class GameMaster(prefab_lib.Prefab):
  """A prefab entity implementing an interviewer game master."""

  description: str = (
      "A game master that administers questionnaires to a specified player."
  )
  params: Mapping[str, Any] = dataclasses.field(
      default_factory=lambda: {
          "name": "InterviewerGM",
          "player_names": [],  # Required: names of the players
          "questionnaires": [],  # Required: list of questionnaires
          "verbose": False,
      }
  )
  entities: Sequence[entity_agent_with_logging.EntityAgentWithLogging] = ()

  def build(
      self,
      model: language_model.LanguageModel,
      memory_bank: basic_associative_memory.AssociativeMemoryBank,
  ) -> entity_agent_with_logging.EntityAgentWithLogging:
    """Build an interviewer game master that administers questionnaires.

    Args:
      model: The language model to use.
      memory_bank: The memory bank to use.

    Returns:
      An entity.
    """
    agent_name = self.params["name"]
    player_names = self.params["player_names"]
    questionnaires = self.params["questionnaires"]

    if not player_names:
      raise ValueError("player_names parameter must be set.")
    if not questionnaires:
      raise ValueError("questionnaires parameter must be set.")

    # Questionnaire component
    questionnaire_component_instance = (
        gm_components.questionnaire.Questionnaire(
            questionnaires=questionnaires,
            player_names=player_names,
        )
    )

    next_acting_component_key = (
        gm_components.next_acting.DEFAULT_NEXT_ACTING_COMPONENT_KEY
    )
    next_action_spec_key = (
        gm_components.next_acting.DEFAULT_NEXT_ACTION_SPEC_COMPONENT_KEY
    )
    terminator_key = gm_components.terminate.DEFAULT_TERMINATE_COMPONENT_KEY
    resolution_key = (
        gm_components.event_resolution.DEFAULT_RESOLUTION_COMPONENT_KEY
    )
    make_observation_key = (
        gm_components.make_observation.DEFAULT_MAKE_OBSERVATION_COMPONENT_KEY
    )

    components_of_game_master = {
        next_acting_component_key: questionnaire_component_instance,
        next_action_spec_key: questionnaire_component_instance,
        terminator_key: questionnaire_component_instance,
        make_observation_key: questionnaire_component_instance,
        resolution_key: questionnaire_component_instance,
        "questionnaire": questionnaire_component_instance,
    }

    act_component = gm_components.switch_act.SwitchAct(
        model=model,
        entity_names=[player_names],
    )

    game_master_agent = entity_agent_with_logging.EntityAgentWithLogging(
        agent_name=agent_name,
        act_component=act_component,
        context_components=components_of_game_master,
    )

    return game_master_agent
