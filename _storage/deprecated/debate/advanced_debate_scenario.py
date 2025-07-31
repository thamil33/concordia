"""
Advanced Debate Scenario - Concordia Master Template Proof of Concept
====================================================================

This file demonstrates the use of the Concordia Master Template to create
a sophisticated debate scenario with multiple agents, advanced memory systems,
and comprehensive game master orchestration.

The scenario features:
- Multiple debaters with distinct personalities and positions
- A debate moderator game master
- Advanced memory and reasoning capabilities
- Real-time argument tracking and evaluation
- Comprehensive logging and analysis

Usage:
    python advanced_debate_scenario.py

Author: Agent Zero
Date: 2025-07-19
"""

import sys
import os

from modules.master_template import (
    ConcordiaMasterScenario,
    AgentConfig,
    GameMasterConfig,
    SimulationConfig,
    ConcordiaFeatureLibrary
)


def create_climate_debate_scenario():
    """
    Create a comprehensive climate change debate scenario.

    This scenario demonstrates:
    - Multiple agents with opposing viewpoints
    - Complex argumentation and reasoning
    - Memory-based persuasion attempts
    - Moderator-guided discussion
    """

    # Define agent configurations
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
            background="PhD in Climate Science from MIT, 15 years research experience",
            traits={
                "expertise": "climate_modeling",
                "communication_style": "academic",
                "evidence_preference": "peer_reviewed",
                "temperature": 0.3
            }
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
            background="Former McKinsey consultant, now at climate policy think tank",
            traits={
                "expertise": "policy_analysis",
                "communication_style": "business",
                "evidence_preference": "economic_data",
                "temperature": 0.5
            }
        ),

        AgentConfig(
            name="Emma Thompson",
            role="Environmental Activist",
            personality="Passionate, urgent, morally driven",
            goals=[
                "Emphasize the moral imperative for climate action",
                "Highlight immediate consequences",
                "Mobilize public support for radical change"
            ],
            background="15 years in environmental advocacy, founded youth climate movement",
            traits={
                "expertise": "grassroots_organizing",
                "communication_style": "emotional_appeal",
                "evidence_preference": "impact_stories",
                "temperature": 0.7
            }
        ),

        AgentConfig(
            name="Robert Sterling",
            role="Skeptical Economist",
            personality="Data-driven, skeptical of climate models, cost-conscious",
            goals=[
                "Question climate model accuracy",
                "Emphasize economic costs of climate action",
                "Argue for adaptation over mitigation"
            ],
            background="Nobel laureate in Economics, specializes in cost-benefit analysis",
            traits={
                "expertise": "economic_modeling",
                "communication_style": "academic_skeptic",
                "evidence_preference": "economic_data",
                "temperature": 0.4
            }
        )
    ]

    # Define game master configuration
    gm_config = GameMasterConfig(
        type="dialogic_and_dramaturgic",
        instructions="""
        You are the moderator of a high-stakes climate change debate.

        Your responsibilities:
        1. Ensure all participants have equal speaking time
        2. Fact-check claims when appropriate
        3. Guide discussion toward actionable solutions
        4. Maintain civil discourse
        5. Ask probing questions to clarify positions

        The debate format:
        - Opening statements (2 minutes each)
        - Rebuttal round (1 minute each)
        - Cross-examination (moderator questions)
        - Closing statements (1 minute each)

        Focus on evidence-based arguments and practical solutions.
        """,
        scene_type="formal_debate",
        context={
            "topic": "Climate Change: Urgency, Solutions, and Economic Trade-offs",
            "format": "structured_debate",
            "time_limit": "60 minutes",
            "audience": "policy makers and public",
            "stakes": "influence on upcoming climate legislation"
        }
    )

    # Define simulation configuration
    simulation_config = SimulationConfig(
        name="Climate_Change_Debate_2025",
        max_steps=20,
        clock_type="game",
        logging_enabled=True,
        save_html=True,
        save_terminal=True,
        print_output=True,
        random_seed=42
    )

    return agent_configs, gm_config, simulation_config


def create_ai_ethics_debate_scenario():
    """
    Create an AI ethics debate scenario.

    This scenario explores:
    - AI alignment and safety concerns
    - Economic disruption from AI
    - Regulatory approaches
    - Long-term societal impacts
    """

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
            background="Lead researcher at AI Safety Institute, published on AI alignment",
            traits={
                "expertise": "ai_safety",
                "risk_tolerance": "low",
                "time_horizon": "long_term",
                "temperature": 0.3
            }
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
            background="CEO of leading AI company, former Google executive",
            traits={
                "expertise": "ai_development",
                "risk_tolerance": "high",
                "time_horizon": "short_term",
                "temperature": 0.6
            }
        ),

        AgentConfig(
            name="Maria Santos",
            role="Labor Economist",
            personality="Data-driven, socially conscious, policy-focused",
            goals=[
                "Analyze AI's impact on employment",
                "Propose worker protection policies",
                "Balance innovation with social stability"
            ],
            background="Professor of Economics, specializes in technological unemployment",
            traits={
                "expertise": "labor_economics",
                "risk_tolerance": "medium",
                "time_horizon": "medium_term",
                "temperature": 0.4
            }
        ),

        AgentConfig(
            name="James Wright",
            role="Regulatory Policy Expert",
            personality="Balanced, institutionalist, implementation-focused",
            goals=[
                "Design practical AI governance frameworks",
                "Balance innovation and safety",
                "Create enforceable regulations"
            ],
            background="Former FTC commissioner, now at regulatory think tank",
            traits={
                "expertise": "regulatory_policy",
                "risk_tolerance": "medium",
                "time_horizon": "medium_term",
                "temperature": 0.5
            }
        )
    ]

    gm_config = GameMasterConfig(
        type="dialogic",
        instructions="""
        You are moderating a critical debate on AI ethics and governance.

        Key discussion points:
        1. How to balance AI innovation with safety concerns
        2. Economic disruption and job displacement
        3. International coordination on AI standards
        4. Timeline for different AI capabilities
        5. Regulatory frameworks that work globally

        Encourage specific policy proposals and concrete timelines.
        Ask for evidence backing claims about AI capabilities and risks.
        """,
        scene_type="policy_roundtable",
        context={
            "topic": "AI Ethics: Balancing Innovation, Safety, and Economic Impact",
            "format": "policy_discussion",
            "time_limit": "90 minutes",
            "audience": "policymakers and industry leaders",
            "stakes": "upcoming AI regulation legislation"
        }
    )

    simulation_config = SimulationConfig(
        name="AI_Ethics_Debate_2025",
        max_steps=25,
        clock_type="game",
        logging_enabled=True,
        save_html=True,
        save_terminal=True,
        print_output=True,
        random_seed=123
    )

    return agent_configs, gm_config, simulation_config


def run_debate_scenario(scenario_type="climate"):
    """
    Run a debate scenario using the master template.

    Args:
        scenario_type: Either "climate" or "ai_ethics"

    Returns:
        Simulation results
    """

    print(f"=== CONCORDIA MASTER TEMPLATE DEBATE SCENARIO ===")
    print(f"Scenario Type: {scenario_type}")
    print("=" * 50)

    # Get scenario configuration
    if scenario_type == "climate":
        agent_configs, gm_config, simulation_config = create_climate_debate_scenario()
    elif scenario_type == "ai_ethics":
        agent_configs, gm_config, simulation_config = create_ai_ethics_debate_scenario()
    else:
        raise ValueError(f"Unknown scenario type: {scenario_type}")

    # Display feature library
    library = ConcordiaFeatureLibrary()
    print("\n--- Available Features ---")
    print("Game Masters:", list(library.get_available_game_masters().keys()))
    print("Entity Types:", list(library.get_available_entity_types().keys()))
    print("Agent Components:", list(library.get_available_agent_components().keys()))
    print("GM Components:", list(library.get_available_gm_components().keys()))
    print("Clock Types:", list(library.get_clock_types().keys()))

    # Display scenario details
    print(f"\n--- Scenario Configuration ---")
    print(f"Simulation Name: {simulation_config.name}")
    print(f"Max Steps: {simulation_config.max_steps}")
    print(f"Game Master Type: {gm_config.type}")
    print(f"Number of Agents: {len(agent_configs)}")

    print(f"\n--- Agents ---")
    for agent in agent_configs:
        print(f"- {agent.name} ({agent.role}): {agent.personality}")

    # Create and run scenario
    print(f"\n--- Running Simulation ---")
    scenario = ConcordiaMasterScenario(
        scenario_type=scenario_type,
        agent_configs=agent_configs,
        gm_config=gm_config,
        simulation_config=simulation_config,
        use_language_model=True
    )

    try:
        results = scenario.run()
        print("\n=== SIMULATION COMPLETE ===")
        print(f"Simulation ID: {results['simulation_name']}")
        print(f"Timestamp: {results['timestamp']}")
        print("Results saved to HTML and terminal logs")

        return results

    except Exception as e:
        print(f"Error running simulation: {e}")
        return None


def demonstrate_template_usage():
    """
    Demonstrate various ways to use the master template.
    """

    print("=== CONCORDIA MASTER TEMPLATE DEMONSTRATION ===")

    # Show feature library
    library = ConcordiaFeatureLibrary()

    print("\n--- Available Game Masters ---")
    for gm_type, description in library.get_available_game_masters().items():
        print(f"  {gm_type}: {description}")

    print("\n--- Available Entity Types ---")
    for entity_type, description in library.get_available_entity_types().items():
        print(f"  {entity_type}: {description}")

    print("\n--- Available Agent Components ---")
    for component, description in library.get_available_agent_components().items():
        print(f"  {component}: {description}")

    print("\n--- Available GM Components ---")
    for component, description in library.get_available_gm_components().items():
        print(f"  {component}: {description}")

    print("\n--- Available Clock Types ---")
    for clock_type, description in library.get_clock_types().items():
        print(f"  {clock_type}: {description}")


if __name__ == "__main__":
    # Demonstrate template features
    demonstrate_template_usage()

    # Run climate debate scenario
    print("\n" + "="*60)
    print("RUNNING CLIMATE DEBATE SCENARIO")
    print("="*60)

    climate_results = run_debate_scenario("climate")

    # Run AI ethics debate scenario
    print("\n" + "="*60)
    print("RUNNING AI ETHICS DEBATE SCENARIO")
    print("="*60)

    ai_results = run_debate_scenario("ai_ethics")

    print("\n=== ALL SCENARIOS COMPLETE ===")
    print("Check the logs directory for detailed outputs")
