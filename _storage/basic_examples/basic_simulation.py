from concordia.embedding.embedd import Embedder, DummyEmbedder
from concordia.language_model.openrouter_model import OpenRouterLanguageModel
from concordia.language_model import no_language_model

import concordia.prefabs.entity as entity_prefabs
import concordia.prefabs.game_master as game_master_prefabs

from concordia.prefabs.simulation import generic as simulation
from concordia.types.launch_simulation import SimulationLauncher
from concordia.types import prefab as prefab_lib
from concordia.utils import helper_functions


# Language Model & Embedder
# To debug without spending money on API calls, set DISABLE_LANGUAGE_MODEL=True
DISABLE_LANGUAGE_MODEL = False
if not DISABLE_LANGUAGE_MODEL:
  model = OpenRouterLanguageModel()
  embedder = Embedder().encode
else:
  model = no_language_model.NoLanguageModel()
  embedder = DummyEmbedder().encode


prefabs = {
    **helper_functions.get_package_classes(entity_prefabs),
    **helper_functions.get_package_classes(game_master_prefabs),
}

# @title Configure instances.
instances = [
    prefab_lib.InstanceConfig(
        prefab='basic__Entity',
        role=prefab_lib.Role.ENTITY,
        params={
            'name': 'Oliver Cromwell',
            'goal': 'become lord protector',
        },
    ),
    prefab_lib.InstanceConfig(
        prefab='basic__Entity',
        role=prefab_lib.Role.ENTITY,
        params={
            'name': 'King Charles I',
            'goal': 'avoid execution for treason',
        },
    ),
    prefab_lib.InstanceConfig(
        prefab='generic__GameMaster',
        role=prefab_lib.Role.GAME_MASTER,
        params={
            'name': 'default rules',
            # Comma-separated list of thought chain steps.
            'extra_event_resolution_steps': '',
        },
    ),
    prefab_lib.InstanceConfig(
        prefab='formative_memories_initializer__GameMaster',
        role=prefab_lib.Role.INITIALIZER,
        params={
            'name': 'initial setup rules',
            'next_game_master_name': 'default rules',
            'shared_memories': [
                'The king was captured by Parliamentary forces in 1646.',
                'Charles I was tried for treason and found guilty.',
            ],
        },
    ),
]

config = prefab_lib.Config(
    default_premise='Today is January 29, 1649.',
    default_max_steps=2,
    prefabs=prefabs,
    instances=instances,
)
# Initialize the simulation passing the config with model and embedder.
configured_simulation = simulation.Simulation(
    config=config,
    model=model,
    embedder=embedder
)

# Create a Simulation launcher instance
launcher = SimulationLauncher(
    simulation_instance=configured_simulation,
    simulation_name="Execution_basic"
)

# Using the SimulationLauncher, run_simulation with log output.
simulation_results = launcher.run_simulation(
    print_terminal_output=True,
    save_terminal_log=True,
    save_html_log=True
)
