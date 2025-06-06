# Entity Agent

## Core: `EntityAgent`

The `EntityAgent` is a fundamental class in Concordia representing an agent (or "entity") in the simulation. Its behavior is defined by a collection of components, not hardcoded logic.

**Key aspects:**

- **Named Entity:** Each agent has a name (`agent_name`).
- **Acting Component:** Requires an `act_component` that determines how it chooses actions.
- **Context Processing:** Uses a `context_processor` (or a default `NoOpContextProcessor`) to handle information from context components.
- **Context Components:** Maintains a mapping of `context_components` that contribute to the agent's understanding and decision-making.
- **Phased Execution:** Operates in phases (e.g., `PRE_ACT`, `POST_ACT`, `PRE_OBSERVE`, `POST_OBSERVE`, `UPDATE`, `READY`) to manage information flow and component interactions.

---

## Type Schemas (Interfaces)

Concordia uses abstract base classes to define interfaces for its core elements:

- **`entity.Entity`:** Base class for any simulation entity. Defines:
  - `name()`: Returns the entity's name.
  - `act()`: Returns the intended action based on an `ActionSpec`.
  - `observe()`: Informs the entity of an observation.
- **`EntityWithLogging`:** Extends `Entity` with `get_last_log()` for debugging.
- **`entity_component.BaseComponent`:** Foundation for all components. Can be associated with an `EntityWithComponents` and provides state management (`get_state()`, `set_state()`).
- **`entity_component.ContextComponent`:** Extends `BaseComponent`. Provides context during agent lifecycle phases:
  - `pre_act()`, `post_act()`, `pre_observe()`, `post_observe()`, `update()`
- **`entity_component.ActingComponent`:** Specialized `BaseComponent` for deciding actions via `get_action_attempt()`.
- **`entity_component.ContextProcessorComponent`:** Processes combined contexts from other components.

---

## Components

Components are modular building blocks defining agent behavior and state.

### Standard Agent Components (`concordia.components.agent`)

- **`action_spec_ignored.ActionSpecIgnored`:** For components whose `pre_act` output can be cached.
- **`all_similar_memories.AllSimilarMemories`:** Retrieves memories similar to a constructed prompt.
- **`concat_act_component.ConcatActComponent`:** Aggregates context and uses a language model to generate actions.
- **`constant.Constant`:** Provides a fixed string as state/context.
- **`instructions.Instructions`:** Specialized `Constant` for default role-playing instructions.
- **`memory.Memory` (and `AssociativeMemory`, `ListMemory`):** Manages agent memory. `AssociativeMemory` uses a memory bank; `ListMemory` uses a list. Buffers additions, commits during `UPDATE`.
- **`observation.ObservationToMemory`:** Adds observations to memory.
- **`observation.LastNObservations`:** Provides last N observations as context.
- **`observation.ObservationsSinceLastPreAct`:** Provides observations since last `pre_act`.
- **`plan.Plan`:** Manages the agent's plan, re-evaluating based on context/goals.
- **`question_of_recent_memories.QuestionOfRecentMemories` (and subclasses):** Asks questions (e.g., self-perception, situation) based on recent memories, using a language model.
- **`report_function.ReportFunction`:** State is output of a function (e.g., current time).

### Contributed Components (`concordia.contrib.components.agent`)

- **`choice_of_component.ChoiceOfComponent`:** Dynamically selects a component based on the situation (using an LLM).
- **`situation_representation_via_narrative.SituationRepresentation`:** Generates a narrative summary of the current situation.

---

## Prefabs (`concordia.prefabs.entity`)

Prefabs are pre-configured entity setups, bundling components for specific behaviors.

- **`basic.Entity`:** Uses the "three key questions" approach:
  - "What situation am I in?"
  - "What kind of person am I?"
  - "What would a person like me do in this situation?"
  - Wires up components like `Instructions`, `ObservationToMemory`, `LastNObservations`, `SituationPerception`, `SelfPerception`, `PersonBySituation`, `AllSimilarMemories`, and optionally a `Constant` goal.
- **`basic_with_plan.Entity`:** Like `basic.Entity`, but adds a `Plan` component for explicit planning.
- **`minimal.Entity`:** Lean setup with essential components (memory, observations, instructions), configurable with a goal and extra components.

Each prefab has a `build()` method that takes a language model and memory bank, returning an initialized `EntityAgentWithLogging`.
