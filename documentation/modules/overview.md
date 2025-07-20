# Concordia Framework Architecture Overview

A comprehensive guide to understanding the Concordia AI agent simulation framework's architecture, component system, and cognitive patterns.

## Framework Overview

**Concordia** is a sophisticated AI agent simulation framework that enables creating and running multi-agent simulations with human-like reasoning. Built on an Entity-Component-System (ECS) architecture, it provides modular cognitive components that can be assembled into complex agent personalities and behaviors.

### Core Philosophy
- **Composable Intelligence**: Build complex agent behaviors from simple, reusable components
- **Cognitive Realism**: Mirror human reasoning patterns through structured component flows
- **Memory-Driven Learning**: Agents learn and adapt through associative memory systems
- **Flexible Coordination**: Support diverse simulation scenarios from structured experiments to open-ended interactions

## Architecture Modules

### 📄 [Document System](document/README.md)
**CORE**: Interactive chain-of-thought reasoning engine that enables sophisticated AI cognition:
- **InteractiveDocument**: Structured conversations between components and language models
- **Chain-of-Thought Building**: Incremental context building with question-answer patterns
- **Reasoning Abstraction**: Transforms complex prompting into simple, testable building blocks
- **Model Integration**: Seamless language model interaction with debugging and testing support

### 🧠 [Components System](components/README.md)
The foundational building blocks for agent cognition:
- **Component Lifecycle**: READY → PRE_ACT → POST_ACT → PRE_OBSERVE → POST_OBSERVE → UPDATE
- **Context Passing**: Components reference each other's outputs to build reasoning chains
- **Strategic Ordering**: Component sequence affects reasoning quality and emergent behaviors
- **Cognitive Patterns**: Five discovered patterns from basic reactive to complex planning

### 🤖 [Agents](agents/README.md)
Entity implementations that participate in simulations:
- **EntityAgent**: Core agent using component-based cognitive architecture
- **Component Assembly**: Agents built by combining components in strategic orders
- **Lifecycle Integration**: Structured phases for reasoning, action, and learning
- **Automatic Learning**: Built-in memory integration for experience accumulation

### 🏭 [Prefabs](prefabs/README.md)
Factory patterns for assembling agents with specific cognitive architectures:
- **Basic Pattern**: Human-like reasoning with identity, situation, and goal synthesis
- **Planning Pattern**: Strategic agents with adaptive replanning and time horizon reasoning
- **Minimal Pattern**: Configurable foundation for custom agent development
- **Assistant Pattern**: Simplified AI assistant simulation
- **Configurator Pattern**: Meta-agents for simulation setup and design

### 💾 [Memory System](memory/README.md)
Associative memory providing context-aware storage and retrieval:
- **Semantic Storage**: Vector embeddings for similarity-based memory retrieval
- **Formative Memories**: Background personality and experience seeding
- **Context-Driven Retrieval**: Components query memory using current situation context
- **Learning Integration**: Automatic experience storage enables agent learning over time

### 🌍 [Environment System](environment/README.md)
Simulation coordination managing agent interactions and world state:
- **Engine Coordination**: Sequential and simultaneous interaction patterns
- **Game Master Role**: Special agents that manage simulation rules and progression
- **Scene Management**: Structured and dynamic interaction scenarios
- **State Management**: Centralized authority with distributed agent observations

## Key Concepts

### Interactive Document-Powered Reasoning
**Core Innovation**: Components use InteractiveDocument to have structured conversations with language models:
```
Component Context → Interactive Document → Question/Answer → LLM → Response Processing → Component Decision
```
This transforms complex AI prompting into simple, testable building blocks that enable sophisticated cognition.

### Component-Based Cognition
Agents think through sequences of components that each contribute specific reasoning capabilities:
```
Instructions → Goal → Memory Retrieval → Self-Perception →
Situation Assessment → Behavioral Synthesis → Action Generation
```
*Each step uses InteractiveDocument for AI-powered reasoning when needed.*

### Memory-Driven Consistency
All agents maintain associative memory that:
- **Stores experiences** automatically during simulation
- **Retrieves relevant context** for current situations
- **Maintains behavioral consistency** across time
- **Enables learning** from consequences and feedback

### Flexible Assembly Patterns
The framework supports diverse agent types through configurable assembly:
- **Parameter customization**: Names, goals, personalities via configuration
- **Component substitution**: Replace standard components with specialized versions
- **Component addition**: Extend base patterns with domain-specific capabilities
- **Ordering modification**: Adjust reasoning flows for different cognitive styles

### Multi-Agent Coordination
Simulations coordinate multiple agents through:
- **Shared environment**: Common observation and action space
- **Game master mediation**: Centralized rule enforcement and state management
- **Scene progression**: Structured or emergent interaction patterns
- **Event distribution**: Targeted or broadcast information sharing

## Getting Started

### Understanding the Framework
1. Start with [Components System](components/README.md) to understand the foundational architecture
2. Review [Prefabs](prefabs/README.md) to see complete cognitive architecture patterns
3. Explore [Memory System](memory/README.md) to understand how agents learn and maintain consistency
4. Study [Environment System](environment/README.md) for simulation coordination patterns

### Key File Locations
- **Core Agents**: [`concordia/agents/`](../../concordia/agents/)
- **Component Library**: [`concordia/components/agent/`](../../concordia/components/agent/) and [`concordia/components/game_master/`](../../concordia/components/game_master/)
- **Prefab Factories**: [`concordia/prefabs/entity/`](../../concordia/prefabs/entity/) and [`concordia/prefabs/game_master/`](../../concordia/prefabs/game_master/)
- **Memory Implementation**: [`concordia/associative_memory/`](../../concordia/associative_memory/)
- **Environment Engines**: [`concordia/environment/`](../../concordia/environment/)

### Development Patterns
- **Agent Creation**: Use prefab factories for standard patterns, manual assembly for custom architectures
- **Component Development**: Follow component interface and lifecycle patterns
- **Memory Integration**: Include ObservationToMemory and AssociativeMemory components
- **Simulation Design**: Choose appropriate engine and game master patterns for scenario needs

This modular architecture enables creating sophisticated AI agent simulations that can model complex human-like reasoning, social interactions, and learning behaviors across diverse domains and scenarios.

## 🏗️ Core Architecture Pattern

Concordia uses an **Entity-Component-System (ECS)** architecture where:
- **Entities** = Agents (players, game masters)
- **Components** = Modular pieces of functionality
- **Systems** = Environments that orchestrate interactions

## 📋 Module Overview & Interactions

### **1. `types/` - The Foundation**
**Role**: Defines the basic interfaces and contracts for the entire system

**Key Components**:
- [`concordia/types/entity_component.py`](../../concordia/types/entity_component.py) - Base classes for all components
- [`concordia/types/entity.py`](../../concordia/types/entity.py) - Basic entity interface
- Component lifecycle phases: `READY → PRE_ACT → POST_ACT → PRE_OBSERVE → POST_OBSERVE → UPDATE`

**How it interacts**: Every other module inherits from or implements these base types.

### **2. `agents/` - The Core Entities**
**Role**: The actual AI agents that think and act

**Key Components**:
- [`concordia/agents/entity_agent.py`](../../concordia/agents/entity_agent.py) - Basic modular agent using component system
- [`concordia/agents/entity_agent_with_logging.py`](../../concordia/agents/entity_agent_with_logging.py) - Enhanced version with detailed logging

**How it works**:
- Agents are containers that hold multiple components
- They orchestrate component calls during `act()` and `observe()` cycles
- Use threading locks to manage component lifecycle phases safely

### **3. `associative_memory/` - The Memory System**
**Role**: Provides semantic memory storage and retrieval

**Key Components**:
- [`concordia/associative_memory/basic_associative_memory.py`](../../concordia/associative_memory/basic_associative_memory.py) - Core memory bank with embedding-based retrieval
- Uses sentence embeddings to find semantically similar memories
- Thread-safe operations with pandas DataFrames

**How it interacts**:
- Components store observations and experiences here
- Agents retrieve relevant memories to inform decisions
- Supports both recent memory and associative (semantic) retrieval

### **4. `components/` - The Functional Building Blocks**
**Role**: Modular pieces of agent functionality

**Two main categories**:
- **[`concordia/components/agent/`](../../concordia/components/agent/)** - Components for individual agents (memory, perception, planning)
- **[`concordia/components/game_master/`](../../concordia/components/game_master/)** - Components for simulation management

**Key agent components**:
- [`concordia/components/agent/memory.py`](../../concordia/components/agent/memory.py) - Interface to associative memory
- [`concordia/components/agent/observation.py`](../../concordia/components/agent/observation.py) - Processes incoming observations
- [`concordia/components/agent/question_of_recent_memories.py`](../../concordia/components/agent/question_of_recent_memories.py) - Asks questions about recent experiences
- [`concordia/components/agent/concat_act_component.py`](../../concordia/components/agent/concat_act_component.py) - Combines component outputs for decision making

**How it works**: Each component provides specific functionality that gets combined into agent behavior.

### **5. `environment/` - The Simulation Engine**
**Role**: Manages the simulation flow and agent interactions

**Key Components**:
- [`concordia/environment/engine.py`](../../concordia/environment/engine.py) - Abstract interface for simulation engines
- [`concordia/environment/engines/sequential.py`](../../concordia/environment/engines/sequential.py) - Turn-based simulation
- [`concordia/environment/engines/simultaneous.py`](../../concordia/environment/engines/simultaneous.py) - Parallel action simulation

**Core functions**:
- `make_observation()` - Generate observations for agents
- `next_acting()` - Determine who acts next
- `resolve()` - Process action results
- `terminate()` - Decide if simulation should end

### **6. `prefabs/` - The Ready-to-Use Templates**
**Role**: Pre-configured agent and game master templates

**Structure**:
- **[`concordia/prefabs/entity/`](../../concordia/prefabs/entity/)** - Agent templates (basic, planning, specialized)
- **[`concordia/prefabs/game_master/`](../../concordia/prefabs/game_master/)** - Simulation manager templates
- **[`concordia/prefabs/configurator/`](../../concordia/prefabs/configurator/)** - Meta-agents for setting up simulations

**How they work**: Prefabs are factory classes that assemble components into functional agents with specific personalities and capabilities.

## 🔄 System Flow Example

Here's how a typical simulation step works:

1. **Environment** calls `next_acting()` to determine which agent acts
2. **Agent** enters `PRE_ACT` phase, all components provide context
3. **ActingComponent** combines contexts and generates an action
4. **Agent** enters `POST_ACT` phase, components process the action
5. **Environment** calls `resolve()` to process action effects
6. **Environment** generates observations via `make_observation()`
7. **Agents** enter `PRE_OBSERVE/POST_OBSERVE` phases to process observations
8. All agents enter `UPDATE` phase to commit changes to memory
9. Process repeats until `terminate()` returns True

## 🧩 Key Integration Patterns

**Memory Integration**:
- Components add observations to memory during `post_observe()`
- Components retrieve relevant memories during `pre_act()`
- Memory updates are committed during `UPDATE` phase

**Component Communication**:
- Components share context through the `ComponentContextMapping`
- Each component contributes labeled text that others can reference
- The `ActingComponent` combines all contexts for decision making

**Prefab Assembly**:
- Prefabs define which components to include and how to configure them
- They specify component order (important for context building)
- They handle parameter customization and dependency injection

## Critical Architectural Clarifications

### **Game Master's True Role**
**Game Masters are NOT separate from the Environment** - they're **specialized AI agents** that run INSIDE simulation engines:

- Built using the same [`EntityAgent`](../../concordia/agents/entity_agent.py) class as player agents
- Act as "AI simulation directors" (like AI dungeon masters)
- Make real-time decisions: who acts next, what observations to generate, how to resolve events
- The Engine calls specific methods on them, but they use AI reasoning to respond

**Relationship**: Environment/Engine = simulation framework; Game Master = AI decision-maker within that framework

### **Memory System Distribution**
Memory appears everywhere because it has different layers:
- **[`associative_memory/`](../../concordia/associative_memory/)** = Core storage system (the "database")
- **[`components/agent/memory.py`](../../concordia/components/agent/memory.py)** = Interface components (how agents access memory)
- **[`thought_chains/`](../../concordia/thought_chains/)** = Reasoning processes that USE memory (not memory itself)

### **Types vs Environment Distinction**
- **[`types/simulation.py`](../../concordia/types/simulation.py)** = Abstract interface ("what simulations should do")
- **[`environment/engine.py`](../../concordia/environment/engine.py)** = Concrete implementation ("how simulations work")

## 📚 Detailed Documentation

For in-depth analysis of specific modules, see:

- [Component System Deep Dive](components/README.md) - How components interact and communicate
- [Prefab Patterns Analysis](prefabs/README.md) - Cognitive architecture patterns and templates
- [Agent Architecture](agents/README.md) - How agents are built and orchestrated
- [Environment & Simulation](environment/README.md) - Simulation engines and game masters
- [Memory Systems](memory/README.md) - Storage, retrieval, and context-aware memory
- [Type System](types/README.md) - Foundation interfaces and contracts
