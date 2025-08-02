# Modified Concordia Framework

Concordia is an advanced Social simulation framework built on an Entity-Component-System (ECS) architecture. I have customized the framework, originally created by Google Deepmind's team under the Open Apache License. 

## Development Objectives 

- Our end goal being the creation of a full stack (API backend with a gui frontend such as react, tailwind, etc) program, which would allow most aspects of the simulation to be configured, creating essentially 'Modules' which could then be ran, observed and recorded. 

- Currently, our focus is on fleshing out alpha.py, creating a full featured working example, giving us a guidepost for when begin work on the full stack interface. Start by familiarizing yourself with the Concordia Source code, utilizing the documentation to clarify any information, as well as analysis of alpha.py's current state.

## Installation 
-The Repo can easily be installed in python 3.11+ by using the command:
``` bash
pip install -e .
```

## Development Focus: `_adendum/alpha.py`
The [_adendum/alpha.py](concordia\_adendum\alpha.py) demonstrates a minimal Concordia simulation featuring two self-aware AI agents, Yin and Yang, who awaken in a shared environment and interact to explore fundamental philosophical questions.
It showcases the fundamentals, agent instantiation, prefab and instance configuration, as well as the use of the simulation launcher to run and log simulaltion involved two agents and a game_master. The output log is
located at [log](./logs/agent_collaboration_demo_terminal.txt)

## Documentation
- [Overview](./concordia_docs/Overview.md): Comprehensive project overview
- [Index](./concordia_docs/Index.md): Full documentation index

## Main Modules

- [agents/](./concordia/agents): Core agent implementations and orchestration
- [associative_memory/](./concordia/associative_memory): Associative and semantic memory systems
- [clocks/](./concordia/clocks): Simulation time management and event scheduling
- [components/](./concordia/components): Modular agent and simulation components
- [contrib/](./concordia/contrib): Community and experimental contributions
- [document/](./concordia/document): Document and InteractiveDocument reasoning engine
- [embedding/](./concordia/embedding): Embedding models for semantic memory and similarity
- [environment/](./concordia/environment): Simulation engine and environment management
- [language_model/](./concordia/language_model): Language model abstraction and integrations
- [prefabs/](./concordia/prefabs): Pre-built agent, simulation, and configuration templates
- [thought_chains/](./concordia/thought_chains): Pre-built reasoning workflows and patterns
- [types_concordia/](./concordia/types_concordia): Type definitions and interfaces for entities and components
- [utils/](./concordia/utils): Utility functions, metrics, and helpers

