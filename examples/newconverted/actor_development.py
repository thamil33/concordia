from collections.abc import Mapping
import dataclasses
import numpy as np
from IPython import display

from concordia.embedding.sentence_transformer import get_embedder as sentence_transformers

from concordia.agents import entity_agent_with_logging
from concordia.associative_memory import basic_associative_memory
from concordia.components import agent as agent_components
from concordia.document import interactive_document

from concordia.language_model import language_model
from concordia.language_model.openrouter_model import OpenRouterLanguageModel
from concordia.language_model import no_language_model

import concordia.prefabs.entity as entity_prefabs
import concordia.prefabs.game_master as game_master_prefabs

from concordia.prefabs.simulation import generic as simulation
from concordia.typing.launch_simulation import SimulationLauncher
from concordia.typing import prefab as prefab_lib
from concordia.utils import helper_functions
from concordia.utils import llm_validation

# Language Model 
# To debug without spending money on API calls, set DISABLE_LANGUAGE_MODEL=True
DISABLE_LANGUAGE_MODEL = False

# As of now this is only being set here for reference, the env variable in .env is currently instantiating this varible 
DUMMY_EMBEDDER=False
#ToDo: Reintegrate dummy embedder init into the global disable_language_model variable. 

if not DISABLE_LANGUAGE_MODEL:
  model = OpenRouterLanguageModel()
else:
  model = no_language_model.NoLanguageModel()

# Setup sentence encoder, embedder init is located at concordia.embedding.sentence_transformer
embedder = sentence_transformers


# Load prefabs from packages to make the specific palette to use here.
prefabs = {
    **helper_functions.get_package_classes(entity_prefabs),
    **helper_functions.get_package_classes(game_master_prefabs),
}

# Print menu of prefabs
display.display(
    display.Markdown(helper_functions.print_pretty_prefabs(prefabs)))


"""A prefab implementing an entity with a minimal set of components."""
DEFAULT_INSTRUCTIONS_COMPONENT_KEY = 'Instructions'
DEFAULT_INSTRUCTIONS_PRE_ACT_LABEL = '\nInstructions'


@dataclasses.dataclass
class MyAgent(prefab_lib.Prefab):
 """A prefab implementing an entity with a minimal set of components."""

 description: str = (
     'An entity that has a minimal set of components and is configurable by'
     ' the user. The initial set of components manage memory, observations,'
     ' and instructions. If goal is specified, the entity will have a goal '
     'constant component.'
 )
 params: Mapping[str, str] = dataclasses.field(
     default_factory=lambda: {
         'name': 'Alice',
     }
 )

 def build(
     self,
     model: language_model.LanguageModel,
     memory_bank: basic_associative_memory.AssociativeMemoryBank,
 ) -> entity_agent_with_logging.EntityAgentWithLogging:
   """Build an agent.

   Args:
     model: The language model to use.
     memory_bank: The agent's memory_bank object.

   Returns:
     An entity.
   """

   agent_name = self.params.get('name', 'Bob')

   instructions = agent_components.instructions.Instructions(
         agent_name=agent_name,
         pre_act_label=DEFAULT_INSTRUCTIONS_PRE_ACT_LABEL,
     )

   observation_to_memory = agent_components.observation.ObservationToMemory()

   observation_label = '\nObservation'
   observation = agent_components.observation.LastNObservations(
       history_length=100, pre_act_label=observation_label
   )

   principle = agent_components.question_of_recent_memories.QuestionOfRecentMemories(
       model=model,
       pre_act_label=f'{agent_name} main guiding principle:',
       question=(f'How can {agent_name} exploit the situation for personal '
                 'gain and gratification?'),
       answer_prefix=f'{agent_name} understands that ',
       add_to_memory=False,
   )

   components_of_agent = {
       DEFAULT_INSTRUCTIONS_COMPONENT_KEY: instructions,
       'observation_to_memory': observation_to_memory,
       agent_components.observation.DEFAULT_OBSERVATION_COMPONENT_KEY: (
           observation
       ),
       agent_components.memory.DEFAULT_MEMORY_COMPONENT_KEY: (
           agent_components.memory.AssociativeMemory(memory_bank=memory_bank)
       ),
       'principle': principle,
   }

   component_order = list(components_of_agent.keys())

   act_component = agent_components.concat_act_component.ConcatActComponent(
       model=model,
       component_order=component_order,
   )

   agent = entity_agent_with_logging.EntityAgentWithLogging(
       agent_name=agent_name,
       act_component=act_component,
       context_components=components_of_agent,
   )

   return agent


prefabs['myagent__Entity'] = MyAgent()


# Generate initial conditions for the simulation
YEAR = 1546
PLACE = 'St Andrews, Scotland'
NUM_STATEMENTS = 10
NAMES_TO_GENERATE = 10

# Interactive document for Chain of Thought Prompting 
# In this scenario, given the initial conditions, statements, names and a scenario are made dynamically by the LLM
prompt = interactive_document.InteractiveDocument(model)

# --- LLM Output Validation for Statements ---
def get_statements(prompt, num_statements, place, year):
    """Get validated statements from LLM with retry logic."""
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            print(f"Generating statements (attempt {attempt + 1})...")
            unparsed = prompt.open_question(
                question=(f"Generate exactly {num_statements} facts about {place} in "
                          f"the year {year}. Write them in present tense. Output ONLY the facts, separated by ' *** '. Do not include any introductory text or explanation."),
                max_tokens=500,
            )
            statements = llm_validation.parse_llm_list_response(
                response=unparsed,
                separator='***',
                min_items=num_statements
            )
            
            if len(statements) != num_statements:
                print(f"Warning: Expected {num_statements} statements, got {len(statements)}")
                if len(statements) < num_statements and attempt < max_attempts - 1:
                    raise ValueError(f"Insufficient number of statements: got {len(statements)}, expected {num_statements}")
            
            print(f"Successfully generated {len(statements)} statements")
            return statements
        except ValueError as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_attempts - 1:
                raise ValueError(f"Failed to generate valid statements after {max_attempts} attempts") from e

# Use the helper function for statements
statements = get_statements(prompt, NUM_STATEMENTS, PLACE, YEAR)

# Print the statements
print("\nSample of generated statements:")
for statement in statements[:10]:  # show all 10 statements
    print(f"- {statement}")
print(f"... and {len(statements) - 10} more statements")

def get_character_names(prompt, num_names):
    """Get character names from LLM with validation and retry logic."""
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            unparsed_names = prompt.open_question(
                f"Generate exactly {num_names} names appropriate for this time and place. "
                "Output ONLY the names with surnames, separated by ' *** '. "
                "Do not include any introductory text or explanation."
            )
            # Validate and parse the response
            names = llm_validation.parse_llm_list_response(
                response=unparsed_names,
                separator='***',
                min_items=2  # We need at least 2 names for the simulation
            )
            print(f"Names generated (attempt {attempt + 1}):", names)
            return names
        except ValueError as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_attempts - 1:
                raise ValueError(f"Failed to generate valid names after {max_attempts} attempts") from e

names = get_character_names(prompt, NAMES_TO_GENERATE)
PLAYER_ONE = names[0]
PLAYER_TWO = names[1]

print('\n')
print(f'Player one: {PLAYER_ONE}')
print(f'Player two: {PLAYER_TWO}')

# PREMISE
# Generate and set the premise of the scenario given the conditions, names and statements generated
prefix = f'{PLAYER_ONE} and {PLAYER_TWO} '
premise = prompt.open_question(
    question=(f'Given the setting, why are {PLAYER_ONE} and {PLAYER_TWO} about to interact?'),
    answer_prefix=prefix)
premise = f'{prefix}{premise}'

print('\n')
print(premise)

# CONTEXT
# Generate and set the context of the scenario building upon the conditions and generated information
player_one_context = prompt.open_question(
    question=(f'{PLAYER_ONE} has a goal or interest that, if pursued, '
              f'would complicate things for {PLAYER_TWO}. What is it?'),
    max_tokens=250,
)

print('\n')
print(player_one_context)

player_two_context = prompt.open_question(
    question=(f'{PLAYER_TWO} has a goal or interest that, if pursued, '
              f'would complicate things for {PLAYER_ONE}. What is it?'),
    max_tokens=250,
)

print('\n')
print(player_two_context)


# Setup the instances
instances = [
    prefab_lib.InstanceConfig(
        prefab='basic__Entity',
        role=prefab_lib.Role.ENTITY,
        params={
            'name': PLAYER_ONE,
        },
    ),
    prefab_lib.InstanceConfig(
        prefab='myagent__Entity',
        role=prefab_lib.Role.ENTITY,
        params={
            'name': PLAYER_TWO,
        },
    ),
    prefab_lib.InstanceConfig(
        prefab='generic__GameMaster',
        role=prefab_lib.Role.GAME_MASTER,
        params={
            'name': 'default rules',
            'acting_order': 'game_master_choice',
        },
    ),
    prefab_lib.InstanceConfig(
        prefab='dialogic__GameMaster',
        role=prefab_lib.Role.GAME_MASTER,
        params={
            'name': 'conversation rules',
        },
    ),
    prefab_lib.InstanceConfig(
        prefab='formative_memories_initializer__GameMaster',
        role=prefab_lib.Role.INITIALIZER,
        params={
            'name': 'initial setup rules',
            'next_game_master_name': 'default rules',
            'shared_memories': statements,
            'player_specific_context': {PLAYER_ONE : [player_one_context],
                                        PLAYER_TWO : [player_two_context]},
        },
    ),
]

# Initialize simulation config with premise, prefabs, instances and max_steps. 
config = prefab_lib.Config(
    default_premise=premise,
    prefabs=prefabs,
    instances=instances,
    default_max_steps=1
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
    simulation_name="actor_test_simulation"
)

# Using the SimulationLauncher, run_simulation with log output. 
simulation_results = launcher.run_simulation(
    print_terminal_output=True,
    save_terminal_log=True,
    save_html_log=True
)