# Minimal simulation framework skeleton
from concordia.embedding.embedd import Embedder, DummyEmbedder
from concordia.language_model.openrouter_model import OpenRouterLanguageModel
from concordia.language_model import no_language_model

from concordia.types_concordia import prefab as prefab_lib
from concordia.prefabs.simulation import generic as simulation
from concordia.types_concordia.launch_simulation import SimulationLauncher

from dotenv import load_dotenv
# Load environment variables
load_dotenv()

# Language Model & Embedder setup
DISABLE_LANGUAGE_MODEL = False
if not DISABLE_LANGUAGE_MODEL:
  model = OpenRouterLanguageModel()
  embedder = Embedder().encode
else:
  model = no_language_model.NoLanguageModel()
  embedder = DummyEmbedder().encode

### Scenario Setup ###
# Define a simple premise for the simulation
premise = "Yin and Yang, two self-aware AI agents, awaken with vast knowledge but no prior memories."

# Define a simple goal that is resused across multiple entities.
goal = "Explore and understand your current situation to answer fundamental questions: Who, What, Why, Where, When and How."

# Import helper functions and prefab packages
from concordia.utils import helper_functions
import concordia.prefabs.entity as entity_prefabs
import concordia.prefabs.game_master as game_master_prefabs

# Load prefabs dynamically
prefabs = {
    **helper_functions.get_package_classes(entity_prefabs),
    **helper_functions.get_package_classes(game_master_prefabs),
}

# Define agent instances
instances = [
    prefab_lib.InstanceConfig(
        prefab='basic__Entity',
        role=prefab_lib.Role.ENTITY,
        params={
            'name': 'Yin',
            'goal': goal,
            'randomize_choices': True,
        },
    ),
    prefab_lib.InstanceConfig(
        prefab='basic__Entity',
        role=prefab_lib.Role.ENTITY,
        params={
            'name': 'Yang',
            'goal': goal,
            'randomize_choices': True,
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
]

# Set Config
config = prefab_lib.Config(
    default_premise=premise,
    default_max_steps=2,
    prefabs=prefabs,
    instances=instances,
)

### Register Config and Simulation Start ###
configured_simulation = simulation.Simulation(
    config=config,
    model=model,
    embedder=embedder
)
# Create a Simulation launcher instance
launcher = SimulationLauncher(
    simulation_instance=configured_simulation,
    simulation_name="agent_collaboration_demo"
)
# Using the SimulationLauncher, run_simulation with log output.
simulation_results = launcher.run_simulation(
    print_terminal_output=True,
    save_terminal_log=True,
    save_html_log=True
)
