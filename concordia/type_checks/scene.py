

"""Dataclasses used to structure simulations using scenes."""

from collections.abc import Callable, Sequence
import dataclasses
import datetime
from typing import Mapping, Union

from concordia.type_checks import entity as entity_lib


@dataclasses.dataclass(frozen=True)
class SceneTypeSpec:
  """A specification for a type of scene.

  Attributes:
    name: name of this type of scene.
    game_master: specify a game master to use for this type of scene.
    game_master_name: specify a game master to use for this type of scene.
    engine: specify a engine to use for this type of scene.
    default_premise: map player names to messages they receive before the scene.
      Messages may be either literal strings or functions of player name that
      return strings.
    action_spec: optionally specify an action spec other than the default for
      the game master to ask the agents to produce during steps of this scene.
    possible_participants: optionally specify a list of possible participants
      for this scene. If specified, the participants field in the
      SceneSpec will be intersected with this list to determine the
      actual participants for each scene.
  """

  name: str
  game_master_name: str | None = None
  default_premise: Mapping[str, Sequence[str | Callable[[str], str]]] | None = (
      None
  )
  action_spec: (
      Union[
          Mapping[str, entity_lib.ActionSpec],
          entity_lib.ActionSpec,
      ]
      | None
  ) = None
  possible_participants: Sequence[str] | None = None


@dataclasses.dataclass(frozen=True)
class SceneSpec:
  """Specify a specific scene.

  Attributes:
    scene_type: Select a specific type of scene.
    participants: Which players participate in the scene.
    num_rounds: How many rounds the scene lasts.
    start_time: Automatically advance the clock to this time when the scene
      starts.
    premise: Map player names to messages they receive before the scene
      (overrides the default premise of the scene type). Messages may be
      either literal strings or functions of player name that return strings.
  """

  scene_type: SceneTypeSpec
  participants: Sequence[str]
  num_rounds: int
  start_time: datetime.datetime | None = None
  premise: Mapping[str, Sequence[str | Callable[[str], str]]] | None = None
