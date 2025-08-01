"""The abstract class that defines a simulation interface.
"""

import abc
from collections.abc import Callable

from concordia.language_model import language_model
from concordia.types_concordia import entity as entity_lib
from concordia.types_concordia import prefab as prefab_lib
import numpy as np


Config = prefab_lib.Config
Role = prefab_lib.Role


class Simulation(abc.ABC):
  """Define the simulation API object."""

  def __init__(
      self,
      config: Config,
      model: language_model.LanguageModel,
      embedder: Callable[[str], np.ndarray],
  ):
    """Initialize the simulation object.

    This simulation differentiates between game masters and entities. Game
    masters are responsible for creating the world state and resolving events.
    Entities are passive agents that react to the world state. Game masters are
    a kind of entity and both are interchangeable once instantiated. However,
    there is one critical difference in how they are configured which we
    implement here in this file. The difference is that game masters are
    configured with references to all entities, but entities are never
    given references to other entities or game masters.

    Args:
      config: the config to use.
      model: the language model to use.
      embedder: the sentence transformer to use.
    """
    raise NotImplementedError

  def get_game_masters(self) -> list[entity_lib.Entity]:
    """Get the game masters."""
    raise NotImplementedError

  def get_entities(self) -> list[entity_lib.Entity]:
    """Get the entities."""
    raise NotImplementedError

  def add_game_master(self, game_master: entity_lib.Entity):
    """Add a game master to the simulation."""
    raise NotImplementedError

  def add_entity(self, entity: entity_lib.Entity):
    """Add an entity to the simulation."""
    raise NotImplementedError

  def play(
      self,
      premise: str | None = None,
      max_steps: int | None = None,
  ) -> str:
    """Run the simulation.

    Args:
      premise: A string to use as the initial premise of the simulation.
      max_steps: The maximum number of steps to run the simulation for.

    Returns:
      html_results_log: browseable log of the simulation in HTML format
    """
    raise NotImplementedError
