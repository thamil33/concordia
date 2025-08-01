# Minimal simulation framwork skeleton
from concordia.embedding.embedd import Embedder, DummyEmbedder
from concordia.language_model.openrouter_model import OpenRouterLanguageModel
from concordia.language_model import no_language_model

from concordia.types_concordia import prefab as prefab_lib
from concordia.prefabs.simulation import generic as simulation
from concordia.types_concordia.launch_simulation import SimulationLauncher

# Language Model & Embedder setup
DISABLE_LANGUAGE_MODEL = False
if not DISABLE_LANGUAGE_MODEL:
  model = OpenRouterLanguageModel()
  embedder = Embedder()
else:
  model = no_language_model.NoLanguageModel()
  embedder= DummyEmbedder()

### Scenario Setup ###
# Setup prefabs and instances
premise = None

prefabs = {}

instances = []



# Set Config
config = prefab_lib.Config(
    default_premise=premise,
    default_max_steps=2,
    prefabs=prefabs,
    instances=instances,
)

### Final Config and Simulation Start ###
configured_simulation = simulation.Simulation(
    config=config,
    model=model,
    embedder=embedder
)
# Create a Simulation launcher instance
launcher = SimulationLauncher(
    simulation_instance=configured_simulation,
    simulation_name="change_me"
)
# Using the SimulationLauncher, run_simulation with log output.
simulation_results = launcher.run_simulation(
    print_terminal_output=True,
    save_terminal_log=True,
    save_html_log=True
)
