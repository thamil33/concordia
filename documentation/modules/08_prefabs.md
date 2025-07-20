# Prefab Patterns Analysis

Prefabs are factory classes that assemble components into functional agents with specific personalities and capabilities. This document analyzes the discovered cognitive architecture patterns.

## Discovered Cognitive Architecture Patterns

### 1. Basic Cognitive Pattern ([`concordia/prefabs/entity/basic.py`](../../../concordia/prefabs/entity/basic.py))
**Flow**: Instructions → Goal → Memory Retrieval → Self-Perception → Situation Perception → Person-by-Situation → Observations → Memory Storage

**Key insight**: Mirrors human decision-making process - identity + situation + past experience + goal → action

**Components Used**:
- [`Instructions`](../../../concordia/components/agent/instructions.py) - Basic behavioral guidelines
- [`Constant`](../../../concordia/components/agent/constant.py) - Goal representation
- [`AllSimilarMemories`](../../../concordia/components/agent/all_similar_memories.py) - Relevant past experiences
- [`SelfPerception`](../../../concordia/components/agent/question_of_recent_memories.py) - "What kind of person am I?"
- [`SituationPerception`](../../../concordia/components/agent/question_of_recent_memories.py) - "What's happening now?"
- [`PersonBySituation`](../../../concordia/components/agent/question_of_recent_memories.py) - "What would someone like me do here?"
- [`LastNObservations`](../../../concordia/components/agent/observation.py) - Recent events
- [`ObservationToMemory`](../../../concordia/components/agent/observation.py) - Memory storage
- [`AssociativeMemory`](../../../concordia/components/agent/memory.py) - Memory interface

### 2. Planning Cognitive Pattern ([`concordia/prefabs/entity/basic_with_plan.py`](../../../concordia/prefabs/entity/basic_with_plan.py))
**Flow**: Basic Pattern + **Plan Component** (inserted after Person-by-Situation)

**Key insights**:
- [`Plan`](../../../concordia/components/agent/plan.py) component references: Self-Perception, Situation Perception, Observations, Goal
- Has **adaptive replanning**: Uses LLM to decide if current plan needs updating
- **Time horizon reasoning**: Automatically determines planning timeframe or uses forced horizon
- **State persistence**: Plans persist across actions until explicitly changed

**Additional Components**:
- [`Plan`](../../../concordia/components/agent/plan.py) - Adaptive planning with time horizon reasoning

### 3. Minimal Pattern ([`concordia/prefabs/entity/minimal.py`](../../../concordia/prefabs/entity/minimal.py))
**Flow**: Instructions → Observations → Memory Storage

**Key insight**: Configurable foundation - includes `extra_components` system for runtime customization

**Components Used**:
- [`Instructions`](../../../concordia/components/agent/instructions.py) or [`Constant`](../../../concordia/components/agent/constant.py) - Behavioral guidelines
- [`LastNObservations`](../../../concordia/components/agent/observation.py) - Recent events
- [`ObservationToMemory`](../../../concordia/components/agent/observation.py) - Memory storage
- [`AssociativeMemory`](../../../concordia/components/agent/memory.py) - Memory interface
- **Runtime configurable components** via `extra_components` parameter

### 4. Assistant Pattern ([`concordia/prefabs/entity/fake_assistant_with_configurable_system_prompt.py`](../../../concordia/prefabs/entity/fake_assistant_with_configurable_system_prompt.py))
**Flow**: System Prompt → Observations → Memory Storage

**Key insight**: Simplified pattern for AI assistant simulation - no self-reflection or planning

**Components Used**:
- [`Constant`](../../../concordia/components/agent/constant.py) - System prompt
- [`LastNObservations`](../../../concordia/components/agent/observation.py) - Recent events
- [`ObservationToMemory`](../../../concordia/components/agent/observation.py) - Memory storage
- [`AssociativeMemory`](../../../concordia/components/agent/memory.py) - Memory interface

### 5. Configurator Pattern ([`concordia/prefabs/configurator/basic.py`](../../../concordia/prefabs/configurator/basic.py))
**Flow**: Instructions → Simulation Perception → Actor Perception → Observations → Memory

**Key insight**: Meta-agent pattern for setting up other agents - specialized question components for simulation design

**Components Used**:
- [`Instructions`](../../../concordia/components/agent/instructions.py) - Configurator guidelines
- [`QuestionOfRecentMemories`](../../../concordia/components/agent/question_of_recent_memories.py) - Simulation design questions
- [`QuestionOfRecentMemories`](../../../concordia/components/agent/question_of_recent_memories.py) - Actor design questions
- [`LastNObservations`](../../../concordia/components/agent/observation.py) - Recent events
- [`ObservationToMemory`](../../../concordia/components/agent/observation.py) - Memory storage
- [`AssociativeMemory`](../../../concordia/components/agent/memory.py) - Memory interface

## Game Master Prefab Patterns

### Psychology Experiment Pattern ([`concordia/prefabs/game_master/psychology_experiment.py`](../../../concordia/prefabs/game_master/psychology_experiment.py))
**Purpose**: Generic framework for psychology experiments with custom observation and action specification components

**Key Components**:
- [`Instructions`](../../../concordia/components/game_master/instructions.py) - Game master guidelines
- [`PlayerCharacters`](../../../concordia/components/game_master/instructions.py) - Player information
- [`SceneTracker`](../../../concordia/components/game_master/scene_tracker.py) - Scene progression
- [`NextActingFromSceneSpec`](../../../concordia/components/game_master/next_acting.py) - Turn order from scenes
- [`EventResolution`](../../../concordia/components/game_master/event_resolution.py) - Action processing
- **Custom experiment components** - Provided via `experiment_component_class`

### Marketplace Pattern ([`concordia/prefabs/game_master/marketplace.py`](../../../concordia/prefabs/game_master/marketplace.py))
**Purpose**: Economic simulation with trading, orders, and market dynamics

**Key Components**:
- Standard game master components plus:
- **Custom marketplace component** - Handles orders, trades, and market mechanics

### Situated Pattern ([`concordia/prefabs/game_master/situated.py`](../../../concordia/prefabs/game_master/situated.py))
**Purpose**: Location-based simulations with world state tracking

**Key Components**:
- [`WorldState`](../../../concordia/components/game_master/world_state.py) - Location and environment tracking
- [`MakeObservation`](../../../concordia/components/game_master/make_observation.py) - Location-aware observations
- [`NextActing`](../../../concordia/components/game_master/next_acting.py) - Turn management
- [`EventResolution`](../../../concordia/components/game_master/event_resolution.py) - World state updates

### Dialogic and Dramaturgic Pattern ([`concordia/prefabs/game_master/dialogic_and_dramaturgic.py`](../../../concordia/prefabs/game_master/dialogic_and_dramaturgic.py))
**Purpose**: Conversation-focused simulations with scene progression

**Key Components**:
- [`SceneTracker`](../../../concordia/components/game_master/scene_tracker.py) - Scene-based progression
- [`NextActingFromSceneSpec`](../../../concordia/components/game_master/next_acting.py) - Scene-driven turn order
- [`SendEventToRelevantPlayers`](../../../concordia/components/game_master/event_resolution.py) - Targeted event distribution

## Component Assembly Patterns

### Memory Pattern Pairing
All prefabs follow a consistent memory pattern:
1. **Storage**: [`ObservationToMemory`](../../../concordia/components/agent/observation.py) during `pre_observe()`
2. **Interface**: [`AssociativeMemory`](../../../concordia/components/agent/memory.py) for component access
3. **Retrieval**: Context-aware components like [`AllSimilarMemories`](../../../concordia/components/agent/all_similar_memories.py)

### Component Ordering Strategy
Strategic component ordering affects reasoning quality:
- **Instructions first** - Sets behavioral foundation
- **Goal early** - Influences subsequent reasoning
- **Dependencies after references** - Components referencing others come later
- **Memory storage last** - Processes all observations

### Context Chain Building
Components build reasoning chains through references:
- [`SelfPerception`](../../../concordia/components/agent/question_of_recent_memories.py) → [`PersonBySituation`](../../../concordia/components/agent/question_of_recent_memories.py)
- [`SituationPerception`](../../../concordia/components/agent/question_of_recent_memories.py) → [`PersonBySituation`](../../../concordia/components/agent/question_of_recent_memories.py)
- [`SituationPerception`](../../../concordia/components/agent/question_of_recent_memories.py) → [`AllSimilarMemories`](../../../concordia/components/agent/all_similar_memories.py)

## Usage Guidelines

### When to Use Each Pattern

**Basic Pattern**: General-purpose agents with human-like reasoning
**Planning Pattern**: Agents that need strategic thinking and goal pursuit
**Minimal Pattern**: Custom agents or prototyping
**Assistant Pattern**: AI assistant simulations or simple reactive agents
**Configurator Pattern**: Meta-agents for simulation setup

### Customization Strategies

1. **Parameter modification**: Change names, goals, instructions via `params`
2. **Component substitution**: Replace standard components with specialized ones
3. **Component addition**: Add extra components for specific functionality
4. **Ordering adjustment**: Modify `component_order` for different reasoning flows
