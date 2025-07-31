"""
Concordia Master Template
================================================

This template is not functional as is, but provides a good reference point for
what our aim is.
"""

import sys
import os
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import pandas as pd

# Add Concordia to path - fix for the nested structure
import importlib.util

# Get the root dir (up two levels from this file)
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

# Add the root dir and concordia subdir to path
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, 'concordia'))

print(f"Python path now includes: {sys.path[:2]}")

# Import the modules from concordia package
try:
    from concordia.associative_memory import basic_associative_memory as associative_memory
    from concordia.language_model import openrouter_model
    from concordia.language_model import no_language_model
    from concordia.embedding.embedd import Embedder
    from concordia.embedding.embedd import DummyEmbedder
    from concordia.prefabs.simulation import generic as simulation
    from concordia.types import prefab as prefab_lib
    from concordia.types.launch_simulation import SimulationLauncher
    from concordia.prefabs.entity import basic_with_plan
    from concordia.prefabs.entity import basic
    from concordia.prefabs.game_master import dialogic
    from concordia.prefabs.game_master import dialogic_and_dramaturgic
    from concordia.components.agent import memory
    from concordia.components.agent import observation
    from concordia.components.agent import plan
    from concordia.components.agent import question_of_recent_memories
    from concordia.components.game_master import instructions
    from concordia.components.game_master import next_acting
    from concordia.components.game_master import scene_tracker
    print("Concordia modules imported successfully")
except ImportError as e:
    print(f"Error importing Concordia modules: {e}")
    print("Make sure Concordia is installed or in the Python path")


@dataclass
class AgentConfig:
    """Configuration for an agent in the simulation."""
    name: str
    role: str
    personality: str
    goals: List[str]
    background: str
    traits: Optional[Dict[str, Any]] = None
    memory_config: Optional[Dict[str, Any]] = None


@dataclass
class GameMasterConfig:
    """Configuration for the game master."""
    type: str
    instructions: str
    scene_type: str
    context: Optional[Dict[str, Any]] = None


@dataclass
class SimulationConfig:
    """Configuration for the simulation."""
    name: str
    max_steps: int = 10
    clock_type: str = "game"
    logging_enabled: bool = True
    save_html: bool = True
    save_terminal: bool = True
    print_output: bool = True
    random_seed: Optional[int] = None


class ConcordiaMasterScenario:
    """
    Master scenario class that demonstrates all Concordia features.

    This class provides a unified interface for creating sophisticated
    Concordia simulations with proper component integration.
    """

    def __init__(
        self,
        scenario_type: str,
        agent_configs: List[AgentConfig],
        gm_config: GameMasterConfig,
        simulation_config: SimulationConfig,
        use_language_model: bool = True,
        custom_components: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the master scenario.

        Args:
            scenario_type: Type identifier for the scenario
            agent_configs: List of agent configurations
            gm_config: Game master configuration
            simulation_config: Overall simulation configuration
            use_language_model: Whether to use actual language model
            custom_components: Optional custom components
        """
        self.scenario_type = scenario_type
        self.agent_configs = agent_configs
        self.gm_config = gm_config
        self.simulation_config = simulation_config
        self.use_language_model = use_language_model
        self.custom_components = custom_components or {}

        # Initialize core components
        self.model = self._setup_language_model()
        self.embedder = self._setup_embedder()

    def _setup_language_model(self):
        """Setup the language model based on configuration."""
        if self.use_language_model:
            return openrouter_model.OpenRouterLanguageModel()
        else:
            return no_language_model.NoLanguageModel()

    def _setup_embedder(self):
        """Setup the embedder based on configuration."""
        if self.use_language_model:
            return Embedder()
        else:
            return DummyEmbedder()

    def create_agent_entity(self, config: AgentConfig):
        """
        Create an agent entity from configuration.

        Args:
            config: Agent configuration

        Returns:
            Configured entity instance
        """
        # Create memory for the agent
        agent_memory = associative_memory.AssociativeMemoryBank(
            sentence_embedder=self.embedder.encode if self.use_language_model else None
        )

        # Create the entity prefab with parameters
        params = {
            'name': config.name,
            'goal': ', '.join(config.goals) if config.goals else '',
            'force_time_horizon': False
        }

        # Add traits if available
        if config.traits:
            params.update(config.traits)

        entity_prefab = basic_with_plan.Entity(params=params)

        # Build the actual entity using the prefab
        entity = entity_prefab.build(
            model=self.model,
            memory_bank=agent_memory
        )

        return entity

    def create_game_master(self):
        """
        Create the game master based on configuration.

        Returns:
            Configured game master instance
        """
        # Create memory for the game master
        gm_memory = associative_memory.AssociativeMemoryBank(
            sentence_embedder=self.embedder.encode if self.use_language_model else None
        )

        # Create the prefab based on the game master type
        if self.gm_config.type == "dialogic":
            # Create a dialogic game master prefab
            gm_prefab = dialogic.GameMaster(
                params={
                    'name': 'Game Master',
                    'instructions': self.gm_config.instructions,
                    'scene_type': self.gm_config.scene_type
                }
            )
        elif self.gm_config.type == "dialogic_and_dramaturgic":
            # Create a dialogic_and_dramaturgic game master prefab
            gm_prefab = dialogic_and_dramaturgic.GameMaster(
                params={
                    'name': 'Game Master',
                    'instructions': self.gm_config.instructions,
                    'scene_type': self.gm_config.scene_type
                }
            )
        else:
            # Default to dialogic
            gm_prefab = dialogic.GameMaster(
                params={
                    'name': 'Game Master',
                    'instructions': self.gm_config.instructions,
                    'scene_type': self.gm_config.scene_type
                }
            )

        # We'll set the entities later in build_simulation when we have them all
        return (gm_prefab, gm_memory)

    def build_simulation(self) -> simulation.Simulation:
        """
        Build the complete simulation configuration.

        Returns:
            Configured simulation instance
        """
        # Create entities
        entities = []
        for agent_config in self.agent_configs:
            entity = self.create_agent_entity(agent_config)
            entities.append(entity)

        # Create game master prefab and memory
        gm_prefab, gm_memory = self.create_game_master()

        # Set the entities for the game master prefab
        gm_prefab.entities = entities

        # Now build the game master with the entities
        game_master = gm_prefab.build(
            model=self.model,
            memory_bank=gm_memory
        )

        # Create prefabs
        prefabs = {}

        # Create instances
        instances = []
        for entity in entities:
            instances.append(entity)
        instances.append(game_master)

        # Create premise
        premise = f"""
        This is a {self.scenario_type} scenario with the following participants:
        {chr(10).join([f'- {ac.name} ({ac.role}): {ac.personality}' for ac in self.agent_configs])}

        Game Master Instructions: {self.gm_config.instructions}
        Scene Type: {self.gm_config.scene_type}

        Context: {self.gm_config.context or 'No additional context provided'}
        """

        # Create configuration
        config = prefab_lib.Config(
            default_premise=premise,
            default_max_steps=self.simulation_config.max_steps,
            prefabs=prefabs,
            instances=instances,
        )

        # Create simulation
        simulation_instance = simulation.Simulation(
            config=config,
            model=self.model,
            embedder=self.embedder
        )

        return simulation_instance

    def run(self) -> Dict[str, Any]:
        """
        Run the complete simulation.

        Returns:
            Dictionary containing simulation results and metadata
        """
        print(f"Starting {self.scenario_type} simulation...")
        print(f"Agents: {[ac.name for ac in self.agent_configs]}")
        print(f"Game Master Type: {self.gm_config.type}")
        print(f"Max Steps: {self.simulation_config.max_steps}")

        # Build simulation
        simulation_instance = self.build_simulation()

        # Create launcher
        launcher = SimulationLauncher(
            simulation_instance=simulation_instance,
            simulation_name=self.simulation_config.name
        )

        # Run simulation
        results = launcher.run_simulation(
            print_terminal_output=self.simulation_config.print_output,
            save_terminal_log=self.simulation_config.save_terminal,
            save_html_log=self.simulation_config.save_html
        )

        return {
            'simulation_name': self.simulation_config.name,
            'scenario_type': self.scenario_type,
            'agent_count': len(self.agent_configs),
            'results': results,
            'timestamp': str(pd.Timestamp.now()) if 'pd' in globals() else 'timestamp'
        }


class ConcordiaFeatureExplorer:
    """
    Utility class to explore available Concordia features.
    """

    @staticmethod
    def get_available_game_masters() -> Dict[str, str]:
        """Get available game master types."""
        return {
            'dialogic': 'Basic conversation orchestration',
            'dialogic_and_dramaturgic': 'Advanced combined orchestration',
            'psychology_experiment': 'Controlled experimental setups',
            'marketplace': 'Economic and trading scenarios',
            'interviewer': 'Structured interview formats',
            'situated': 'Context-aware action scenarios'
        }

    @staticmethod
    def get_available_entity_types() -> Dict[str, str]:
        """Get available entity types."""
        return {
            'basic': 'Simple entity with minimal components',
            'basic_with_plan': 'Entity with planning capabilities',
            'minimal': 'Minimal entity configuration',
            'fake_assistant': 'Configurable assistant entity'
        }

    @staticmethod
    def get_available_agent_components() -> Dict[str, str]:
        """Get available agent components."""
        return {
            'memory': 'Memory storage and retrieval',
            'observation': 'Observation and perception',
            'plan': 'Planning and goal-directed behavior',
            'question_of_recent_memories': 'Question answering from recent memories',
            'report_function': 'Report generation capabilities',
            'all_similar_memories': 'Similar memory retrieval'
        }

    @staticmethod
    def get_available_gm_components() -> Dict[str, str]:
        """Get available game master components."""
        return {
            'instructions': 'GM instructions component',
            'next_acting': 'Determine next acting entity',
            'scene_tracker': 'Track scene state and progression',
            'event_resolution': 'Resolve events and outcomes',
            'inventory': 'Manage entity inventories',
            'questionnaire': 'Handle questionnaire interactions'
        }


def create_climate_debate_scenario():
    """
    Create a climate change debate scenario.

    Returns:
        Tuple of (agent_configs, gm_config, simulation_config)
    """

    # Agent configurations
    agent_configs = [
        AgentConfig(
            name="Dr. Sarah Chen",
            role="Climate Scientist",
            personality="Analytical, evidence-driven, cautious with claims",
            goals=[
                "Present scientific evidence for anthropogenic climate change",
                "Counter misinformation with data",
                "Maintain scientific credibility"
            ],
            background="PhD in Climate Science from MIT, 15 years research experience"
        ),
        AgentConfig(
            name="Marcus Rodriguez",
            role="Policy Analyst",
            personality="Pragmatic, economically focused, solution-oriented",
            goals=[
                "Argue for market-based climate solutions",
                "Balance environmental and economic concerns",
                "Promote innovation over regulation"
            ],
            background="Former McKinsey consultant, now at climate policy think tank"
        )
    ]

    # Game master configuration
    gm_config = GameMasterConfig(
        type="dialogic",
        instructions="""
        You are moderating a debate on climate change policy.
        Ensure both participants present evidence-based arguments.
        Ask clarifying questions about their positions.
        Focus on actionable solutions rather than just problems.
        """,
        scene_type="formal_debate",
        context={
            "topic": "Climate Change Policy Approaches",
            "format": "structured_debate",
            "duration": "20 minutes"
        }
    )

    # Simulation configuration
    simulation_config = SimulationConfig(
        name="Climate_Debate_2025",
        max_steps=15,
    )

    return agent_configs, gm_config, simulation_config


def create_ai_ethics_scenario():
    """
    Create an AI ethics debate scenario.

    Returns:
        Tuple of (agent_configs, gm_config, simulation_config)
    """

    # Agent configurations
    agent_configs = [
        AgentConfig(
            name="Dr. Lisa Park",
            role="AI Safety Researcher",
            personality="Cautious, forward-thinking, risk-aware",
            goals=[
                "Highlight existential risks from advanced AI",
                "Advocate for safety research funding",
                "Promote international AI governance"
            ],
            background="Lead researcher at AI Safety Institute"
        ),
        AgentConfig(
            name="David Kim",
            role="Tech Industry Leader",
            personality="Optimistic, innovation-focused, market-driven",
            goals=[
                "Emphasize AI's economic benefits",
                "Argue against premature regulation",
                "Promote competitive innovation"
            ],
            background="CEO of leading AI company"
        )
    ]

    # Game master configuration
    gm_config = GameMasterConfig(
        type="dialogic",
        instructions="""
        You are moderating a debate on AI ethics and governance.
        Focus on balancing innovation with safety concerns.
        Ask for specific policy proposals and timelines.
        Ensure both participants address concrete solutions.
        """,
        scene_type="policy_roundtable",
        context={
            "topic": "AI Governance: Innovation vs. Safety",
            "format": "expert_panel",
            "duration": "25 minutes"
        }
    )

    # Simulation configuration
    simulation_config = SimulationConfig(
        name="AI_Ethics_Debate_2025",
        max_steps=12,
    )

    return agent_configs, gm_config, simulation_config


def main():
    """Run demonstration scenarios."""

    print("=== CONCORDIA MASTER TEMPLATE DEMONSTRATION ===")

    # Set up basic exception handling and logging
    import logging
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("concordia_master_template")

    # Show available features
    explorer = ConcordiaFeatureExplorer()

    print("\n--- Available Game Masters ---")
    for gm_type, description in explorer.get_available_game_masters().items():
        print(f"  {gm_type}: {description}")

    print("\n--- Available Entity Types ---")
    for entity_type, description in explorer.get_available_entity_types().items():
        print(f"  {entity_type}: {description}")

    print("\n--- Available Agent Components ---")
    for component, description in explorer.get_available_agent_components().items():
        print(f"  {component}: {description}")

    print("\n--- Available GM Components ---")
    for component, description in explorer.get_available_gm_components().items():
        print(f"  {component}: {description}")

    # Run Climate Debate scenario
    print("\n" + "="*50)
    print("1. RUNNING CLIMATE DEBATE SCENARIO")
    print("="*50)

    agent_configs, gm_config, simulation_config = create_climate_debate_scenario()

    scenario = ConcordiaMasterScenario(
        scenario_type="climate_debate",
        agent_configs=agent_configs,
        gm_config=gm_config,
        simulation_config=simulation_config,
        use_language_model=False  # Use dummy for testing
    )

    try:
        print("Starting climate debate scenario...")
        results = scenario.run()
        print(f"\nSimulation completed successfully!")
        print(f"Simulation ID: {results['simulation_name']}")
        print(f"Scenario Type: {results['scenario_type']}")
        print(f"Agent Count: {results['agent_count']}")
        print()

    except Exception as e:
        import traceback
        print(f"Error running simulation: {e}")
        print("\nDetailed error information:")
        traceback.print_exc()
        print("\nTroubleshooting tips:")
        print("1. Check if Concordia is installed correctly")
        print("2. Ensure your Python environment has all dependencies")
        print("3. Verify the API compatibility with your Concordia version")

    # Run AI Ethics scenario
    print("\n" + "="*50)
    print("2. RUNNING AI ETHICS SCENARIO")
    print("="*50)

    agent_configs, gm_config, simulation_config = create_ai_ethics_scenario()

    scenario = ConcordiaMasterScenario(
        scenario_type="ai_ethics_debate",
        agent_configs=agent_configs,
        gm_config=gm_config,
        simulation_config=simulation_config,
        use_language_model=False  # Use dummy for testing
    )

    try:
        print("Starting AI ethics scenario...")
        results = scenario.run()
        print(f"\nSimulation completed successfully!")
        print(f"Simulation ID: {results['simulation_name']}")
        print(f"Scenario Type: {results['scenario_type']}")
        print(f"Agent Count: {results['agent_count']}")

        print("\n=== ALL SCENARIOS COMPLETE ===")
        print("Check the logs directory for detailed outputs")

    except Exception as e:
        import traceback
        print(f"Error running simulation: {e}")
        print("\nDetailed error information:")
        traceback.print_exc()
        print("\nTroubleshooting tips:")
        print("1. Check if Concordia is installed correctly")
        print("2. Ensure your Python environment has all dependencies")
        print("3. Verify the API compatibility with your Concordia version")


if __name__ == "__main__":
    """Run the main demonstration."""
    main()
