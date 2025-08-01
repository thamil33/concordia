# Modified Concordia Framework

Concordia is an advanced Social simulation framework built on an Entity-Component-System (ECS) architecture.

## Example: `_adendum/alpha.py`
 The [_adendum/alpha.py](concordia\_adendum\alpha.py) script demonstrates a minimal Concordia simulation 
featuring two self-aware AI agents, Yin and Yang, who awaken in a shared 
environment and interact to explore fundamental philosophical questions.
 It showcases agent instantiation, prefab configuration, and the use of the
simulation launcher to run and log a multi-agent scenario. Its output log is
locatede at [log](./logs/agent_collaboration_demo_terminal.txt)

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
