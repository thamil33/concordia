## Overview

**Pysim** is a Python framework for building and running generative agent-based models. It enables simulations where entities—powered by Large Language Models (LLMs)—interact within a configurable environment. The framework is highly modular, supporting flexible construction of both agents and simulation control mechanisms.

---

### 1. Core Architecture

#### 1.1 Entities

- **EntityAgent** (`pysim/agents/entity_agent.py`): The core class for simulation participants. Each entity's behavior is defined by attachable components, not hardcoded logic.
    - **Initialization:** Entities are created with a unique name, an `act_component` (decision logic), optional `context_processor`, and a dictionary of `context_components`.
    - **Component-Driven:** Tasks like memory, planning, and observation are delegated to components, enabling diverse agent types.
    - **Lifecycle Phases:** Entities operate through phases (READY, PRE_ACT, POST_ACT, etc.), ensuring sequential and thread-safe operations.
    - **Actions & Observations:** Acting and observing both trigger component-driven phase transitions.
    - **Concurrency:** The `_parallel_call_` method enables concurrent execution across components.
    - **Logging:** `EntityAgentWithLogging` extends entities with logging capabilities.

#### 1.2 Orchestrators

- **Orchestrator:** Specialized entity managing the simulation's flow, environment, and event resolution. Built from components, just like agents.
    - **Role:** Controls turn-taking, generates observations, and resolves actions into events.
    - **Prefabs:** Pre-configured orchestrators (e.g., generic, dialogic) are available in `prefabs/orchestrator/`.

#### 1.3 Component System

- **Components:** Encapsulate logic or data for entities and orchestrators.
    - **Types:**
        - `ContextComponent`: Supplies context (pre_act, post_act, etc.).
        - `ActingComponent`: Decides actions.
        - `ContextProcessorComponent`: Processes context before acting.
    - **Agent Components:** Memory, planning, instructions, observation, etc.
    - **Orchestrator Components:** Turn management, event resolution, world state, etc.

---

### 2. Key Systems

#### 2.1 Language Model Integration

- **LanguageModel** (abstract): Defines the interface for LLM wrappers (`sample_text`, `sample_choice`).
- **Implementations:** LM Studio, OpenRouter, Ollama, PyTorch Gemma, and a dummy model.
- **Wrappers:** Add retry logic or call limits.

#### 2.2 Associative Memory

- **AssociativeMemoryBank:** Stores and retrieves memories using embeddings (with Pandas and SentenceTransformer).
- **FormativeMemory:** Generates initial memories for agents using LLMs.

#### 2.3 Clock System

- **GameClock:** Abstract interface for simulation clocks.
- **FixedIntervalClock / MultiIntervalClock:** Support fixed or variable time steps.

#### 2.4 Simulation Engines

- **Engine:** Abstract base for simulation loops.
- **Sequential Engine:** Turn-based loop managing entity actions, orchestrator decisions, and event resolution.

#### 2.5 Scene Management

- **Scenes:** Simulations can be structured into scenes, each with its own participants and context.
- **SceneTracker:** Orchestrator component for managing scenes and transitions.

#### 2.6 Thought Chains

- **Thought Chains:** Enable multi-step LLM reasoning for complex event resolution.

---

### 3. Configuration & Assembly

#### 3.1 Prefabs

- **Prefabs:** Templates for entities, orchestrators, and simulations.
    - **Entity Prefabs:** Standard agents with configurable components.
    - **Orchestrator Prefabs:** Pre-built orchestrators for common use cases.

#### 3.2 Configurator

- **BasicConfigurator:** Assembles simulations from prefabs and configuration dictionaries (model, memory, clock, scenes, etc.).
- **Build Process:** Instantiates all components, entities, orchestrators, and returns a complete simulation object.

---

### 4. Interaction & Logging

#### 4.1 Interactive Document

- **InteractiveDocument:** Utility for structured LLM interaction (open questions, multiple choice, yes/no).
- **Usage:** Used by components for prompting and parsing LLM responses.

#### 4.2 Simulation Output & Logging

- **Logging:** Detailed logs are produced by the engine and agent/orchestrator components for each simulation step.

---

### 5. Summary

Pysim offers a modular, extensible platform for generative agent-based modeling. Its component-based architecture, prefab system, and configurator make it easy to assemble complex simulations. With support for multiple LLM backends, robust memory, and structured interaction tools, Pysim is well-suited for research and development in agent-based AI.
