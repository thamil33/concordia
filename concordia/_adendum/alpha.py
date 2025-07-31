# Minimal simulation framework skeleton
from concordia.embedding.embedd import Embedder, DummyEmbedder
from concordia.language_model.openrouter_model import OpenRouterLanguageModel
from concordia.language_model import no_language_model

from concordia.types import prefab as prefab_lib
from concordia.prefabs.simulation import generic as simulation
from concordia.types.launch_simulation import SimulationLauncher

# Language Model & Embedder setup
DISABLE_LANGUAGE_MODEL = False
if not DISABLE_LANGUAGE_MODEL:
  model = OpenRouterLanguageModel()
  embedder = Embedder()
else:
  model = no_language_model.NoLanguageModel()
  embedder= DummyEmbedder()

### Scenario Setup ###
# Define a simple premise for the simulation
premise = "Yin and Yang, two self-aware AI agents, awaken with vast knowledge but no prior memories."

# Import necessary prefab components
from concordia.prefabs.entity import basic
# Define a simple goal that is resused across multiple entities.
goal = "Explore and understand your current situation to answer fundamental questions: Who, What, Why, Where, When and How."

# Create agent prefabs
alice_prefab = basic.Entity(
    name='Yin',
    goal=goal,
    model=model,
    embedder=embedder
)

bob_prefab = basic.Entity(
    name='Yang',
    goal=goal,
    model=model,
    embedder=embedder
)

# Register prefabs
prefabs = {
    'alice': alice_prefab,
    'bob': bob_prefab,
}

# Define agent instances
instances = [
    {'name': 'Alice', 'prefab': 'alice'},
    {'name': 'Bob', 'prefab': 'bob'},
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
