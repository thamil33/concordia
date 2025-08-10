"""
Main script to run the Slim Interactive Escape Room simulation.
"""
from concordia.language_model.model_client_initialization import ModelClient
import concordia.prefabs.game_master as game_master_prefabs
from concordia.type_checks import prefab as prefab_lib
from concordia.utils import helper_functions

# Import our custom patterns
from concordia.slim_interactive.slim_engine import LivingSimulation
from concordia.slim_interactive.slim_agent import SlimAgent
from concordia.slim_interactive.slim_world import SlimWorld
from concordia.slim_interactive.slim_init import FormativeMemoryInitializer

def main():
    """Sets up and runs the simulation scenario."""
    print("--- Setting up Simulation ---")

    client = ModelClient()
    model = client.model
    embedder = client.embedder

    prefabs = {
        'slim_agent__SlimAgent': SlimAgent(),
        'slim_world__SlimWorld': SlimWorld(),
        'slim_formative_initializer__FormativeMemoryInitializer': FormativeMemoryInitializer(
            model=model, embedder=embedder
        ),
        **helper_functions.get_package_classes(game_master_prefabs),
    }

    PLAYER_ONE_NAME = 'Alex'
    PLAYER_TWO_NAME = 'Ben'

    instances = [
        prefab_lib.InstanceConfig(
            prefab='slim_agent__SlimAgent',
            role=prefab_lib.Role.ENTITY,
            params={
                'name': PLAYER_ONE_NAME,
                'goal': 'Work with Ben to figure out how to escape this room.',
                'context': 'Alex is a musician and composer, known for creative problem-solving.',
                'specific_memories': 'I remember seeing a sequence of colors: red, blue, green.',
            },
        ),
        prefab_lib.InstanceConfig(
            prefab='slim_agent__SlimAgent',
            role=prefab_lib.Role.ENTITY,
            params={
                'name': PLAYER_TWO_NAME,
                'goal': 'Work with Alex to figure out how to escape this room.',
                'context': 'Ben is a photojournalist, skilled at observing details.',
                'specific_memories': 'I remember hearing a sequence of numbers: 4, 8, 2.',
            },
        ),
        prefab_lib.InstanceConfig(
            prefab='generic__GameMaster',
            role=prefab_lib.Role.GAME_MASTER,
            params={'name': 'slim_master', 'acting_order': 'fixed'},
        ),
        prefab_lib.InstanceConfig(
            prefab='slim_world__SlimWorld',
            role=prefab_lib.Role.GAME_MASTER,
            params={'name': 'World'},
        ),
        # Use our new initializer Game Master
        prefab_lib.InstanceConfig(
            prefab='slim_formative_initializer__FormativeMemoryInitializer',
            role=prefab_lib.Role.INITIALIZER,
        ),
    ]

    config = prefab_lib.Config(
        default_premise=(
            f'{PLAYER_ONE_NAME} and {PLAYER_TWO_NAME} wake up in a locked room.'
        ),
        prefabs=prefabs,
        instances=instances,
    )

    runnable_simulation = LivingSimulation(config, model, embedder)

    print("\n--- Running Simulation Cycles ---")
    num_cycles_to_run = 4
    for i in range(1, num_cycles_to_run + 1):
        print(f"\n--- Cycle {i} ---")
        runnable_simulation.run_cycle()

    print("\n--- Simulation Complete ---")
    final_log_html = runnable_simulation.get_html_log()
    with open("final_simulation_log.html", "w", encoding="utf-8") as f:
        f.write(final_log_html)
    print("Final HTML log saved to final_simulation_log.html")


if __name__ == '__main__':
    main()
