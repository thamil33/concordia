"""An interactive, persistent simulation engine using a simultaneous cycle."""

from collections.abc import Callable, Mapping
import copy
import functools
import json
import os
from typing import Any

from concordia.associative_memory import basic_associative_memory as associative_memory
from concordia.environment.engines import simultaneous
from concordia.language_model import language_model
from concordia.type_checks import entity as entity_lib
from concordia.type_checks import entity_component
from concordia.type_checks import prefab as prefab_lib
from concordia.type_checks import simulation as simulation_lib
from concordia.utils import html as html_lib
import numpy as np

# Import the new SlimAgent prefab from the correct path
from concordia.slim_interactive import slim_agent


Config = prefab_lib.Config
Role = prefab_lib.Role


class LivingSimulation(simulation_lib.Simulation):
  """A persistent, interactive simulation that runs in cycles."""

  def __init__(
      self,
      config: Config,
      model: language_model.LanguageModel,
      embedder: Callable[[str], np.ndarray],
  ):
    """Initializes the LivingSimulation.

    Args:
      config: The simulation configuration.
      model: The language model to use.
      embedder: The sentence embedder to use.
    """
    self._config = config
    self._model = model
    self._embedder = embedder
    self._engine = simultaneous.Simultaneous()
    self.game_masters = []
    self.entities = []
    self._raw_log = []
    self._entity_to_prefab_config: dict[str, prefab_lib.InstanceConfig] = {}
    self._checkpoint_counter = 0

    # All game masters share the same memory bank.
    self.game_master_memory_bank = associative_memory.AssociativeMemoryBank(
        sentence_embedder=embedder,
    )

    # Instantiate entities and game masters from the config
    all_data = self._config.instances
    gm_configs = [
        entity_cfg
        for entity_cfg in all_data
        if entity_cfg.role == Role.GAME_MASTER
    ]
    entities_configs = [
        entity_cfg for entity_cfg in all_data if entity_cfg.role == Role.ENTITY
    ]
    initializer_configs = [
        entity_cfg
        for entity_cfg in all_data
        if entity_cfg.role == Role.INITIALIZER
    ]

    for entity_config in entities_configs:
      self.add_entity(entity_config)

    for gm_config in initializer_configs + gm_configs:
      self.add_game_master(gm_config)


  def run_cycle(self, premise: str | None = None):
    """Runs a single cycle of the simulation.

    Args:
        premise: A string to use as the premise for this cycle. If None,
                 the simulation continues from the last state.
    """
    if premise is None:
        premise = self._config.default_premise

    # Ensure game masters are ordered Initializers first, then others.
    initializers = [
        gm
        for gm in self.game_masters
        if self._entity_to_prefab_config[gm.name].role == Role.INITIALIZER
    ]
    other_gms = [
        gm
        for gm in self.game_masters
        if self._entity_to_prefab_config[gm.name].role == Role.GAME_MASTER
    ]
    sorted_game_masters = initializers + other_gms

    self._engine.run_loop(
        game_masters=sorted_game_masters,
        entities=self.entities,
        premise=premise,
        max_steps=1,  # Run for a single cycle
        verbose=True,
        log=self._raw_log, # Append to the main log
    )

  def get_html_log(self) -> str:
      """Generates an HTML log of the entire simulation history."""
      html_log = html_lib.PythonObjectToHTMLConverter(self._raw_log).convert()
      return html_lib.finalise_html(html_log)


  def save(self, filepath: str):
    """Saves the current state of the simulation to a file.

    Args:
        filepath: The path to the file where the state will be saved.
    """
    checkpoint_data = self._make_checkpoint_data()
    try:
        with open(filepath, "w") as f:
            json.dump(checkpoint_data, f, indent=2)
        print(f"Simulation state saved to {filepath}")
    except IOError as e:
        print(f"Error saving simulation state: {e}")


  def load(self, filepath: str):
    """Loads the state of the simulation from a file.

    Args:
        filepath: The path to the file from which to load the state.
    """
    try:
        with open(filepath, "r") as f:
            checkpoint_data = json.load(f)
        self._load_from_checkpoint(checkpoint_data)
        print(f"Simulation state loaded from {filepath}")
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading simulation state: {e}")


  def _make_checkpoint_data(self) -> dict[str, Any]:
    """Creates a dictionary containing the simulation state."""
    checkpoint_data = {
        "entities": {},
        "game_masters": {},
        "raw_log": copy.deepcopy(self._raw_log),
        "checkpoint_counter": self._checkpoint_counter,
    }

    for entity in self.entities:
        prefab_config = self._entity_to_prefab_config.get(entity.name)
        if prefab_config:
            checkpoint_data["entities"][entity.name] = {
                "prefab_type": prefab_config.prefab,
                "entity_params": prefab_config.params,
                "components": entity.get_state(),
            }

    for gm in self.game_masters:
        prefab_config = self._entity_to_prefab_config.get(gm.name)
        if prefab_config:
            checkpoint_data["game_masters"][gm.name] = {
                "prefab_type": prefab_config.prefab,
                "entity_params": prefab_config.params,
                "role": prefab_config.role.name,
                "components": gm.get_state(),
            }

    self._checkpoint_counter += 1
    return checkpoint_data


  def _load_from_checkpoint(self, checkpoint: dict[str, Any]):
    """Restores the simulation state from a checkpoint dictionary."""
    self.entities = []
    self.game_masters = []
    self._entity_to_prefab_config = {}

    for entity_name, state in checkpoint.get("entities", {}).items():
        self._load_entity_from_state(entity_name, state, Role.ENTITY)

    for gm_name, state in checkpoint.get("game_masters", {}).items():
        role = Role[state.get("role", "GAME_MASTER")]
        self._load_entity_from_state(gm_name, state, role)

    for game_master in self.game_masters:
        if hasattr(game_master, "entities"):
            game_master.entities = self.entities

    self._raw_log = checkpoint.get("raw_log", [])
    self._checkpoint_counter = checkpoint.get("checkpoint_counter", 0)


  def _load_entity_from_state(
      self,
      entity_name: str,
      state: dict[str, Any],
      role: Role,
  ):
    """Loads a single entity or game master from a state dictionary."""
    prefab_type = state.get("prefab_type")
    params = state.get("entity_params")
    components_state = state.get("components")

    instance_config = prefab_lib.InstanceConfig(
        prefab=prefab_type,
        role=role,
        params=params,
    )

    if role == Role.ENTITY:
        self.add_entity(instance_config, state=components_state)
    else:
        self.add_game_master(instance_config, state=components_state)

  def add_entity(
      self,
      instance_config: prefab_lib.InstanceConfig,
      state: entity_component.EntityState | None = None,
  ):
    """Adds an entity to the simulation."""
    if instance_config.prefab == 'slim_agent__SlimAgent':
        entity_prefab = slim_agent.SlimAgent()
    else:
        entity_prefab = copy.deepcopy(self._config.prefabs[instance_config.prefab])

    entity_prefab.params = instance_config.params

    memory_bank = associative_memory.AssociativeMemoryBank(
        sentence_embedder=self._embedder,
    )
    entity = entity_prefab.build(model=self._model, memory_bank=memory_bank)

    if state:
      entity.set_state(state)

    self.entities.append(entity)
    self._entity_to_prefab_config[entity.name] = instance_config


  def add_game_master(
      self,
      instance_config: prefab_lib.InstanceConfig,
      state: entity_component.EntityState | None = None,
  ):
    """Adds a game master to the simulation."""
    game_master_prefab = copy.deepcopy(
        self._config.prefabs[instance_config.prefab]
    )
    game_master_prefab.params = instance_config.params
    game_master_prefab.entities = self.entities
    game_master = game_master_prefab.build(
        model=self._model, memory_bank=self.game_master_memory_bank
    )

    if state:
      game_master.set_state(state)

    self.game_masters.append(game_master)
    self._entity_to_prefab_config[game_master.name] = instance_config
