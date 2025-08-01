# Component System Deep Dive

The component system works through a **context-passing pipeline** that's more sophisticated than typical plugin architectures.

## Component types_concordia & Roles

### ActingComponent ([`concordia/components/agent/concat_act_component.py`](../../../concordia/components/agent/concat_act_component.py))
- **Role**: The "decision maker" - combines all context into final actions
- **Key insight**: It doesn't make decisions itself, it orchestrates other components' inputs
- **How it works**: Receives [`ComponentContextMapping`](../../../concordia/types_concordia/entity_component.py) (dict of component_name → context_string), concatenates them in specified order, feeds to LLM

### ContextComponent
Components like [`observation.py`](../../../concordia/components/agent/observation.py), [`question_of_recent_memories.py`](../../../concordia/components/agent/question_of_recent_memories.py):
- **Role**: Information providers - each contributes specific context during different phases
- **Key insight**: They don't communicate directly with each other, but can reference other components by name
- **How it works**: Implements `pre_act()` to provide context strings with labels

## Component Communication Pattern

Components communicate through **labeled context sharing**:

```python
# From question_of_recent_memories.py - components can reference other components
person_by_situation = PersonBySituation(
    model=model,
    components=[
        'SelfPerception',      # References another component's output
        'SituationPerception', # References another component's output
    ],
    # This component will see the outputs of those components when generating its context
)
```

**Critical insight**: Components build on each other's outputs without direct coupling. The [`PersonBySituation`](../../../concordia/components/agent/question_of_recent_memories.py) component can use outputs from [`SelfPerception`](../../../concordia/components/agent/question_of_recent_memories.py) and [`SituationPerception`](../../../concordia/components/agent/question_of_recent_memories.py) to generate more sophisticated reasoning.

## Component Ordering Matters

```python
# From basic.py prefab
component_order = list(components_of_agent.keys())
if overarching_goal is not None:
    components_of_agent[goal_key] = overarching_goal
    component_order.insert(1, goal_key)  # Goal goes after instructions, before everything else
```

**Why ordering matters**:
- Components that reference others must come AFTER their dependencies
- The final LLM prompt is built by concatenating contexts in this order
- Goal is strategically placed early to influence all subsequent reasoning

## Memory Integration Pattern

Two-phase memory pattern discovered:
1. **Storage**: [`ObservationToMemory`](../../../concordia/components/agent/observation.py) stores observations during `pre_observe()`
2. **Retrieval**: Other components access memory during `pre_act()` via memory component reference

```python
# Storage component
observation_to_memory = agent_components.observation.ObservationToMemory()

# Retrieval component
relevant_memories = agent_components.all_similar_memories.AllSimilarMemories(
    components=['SituationPerception'],  # Uses situation to query memory
    num_memories_to_retrieve=10,
)
```

**Key insight**: Memory isn't just storage - it's **context-aware retrieval** where components can query memory based on current situation.

## Component Composition Strategy

From analyzing the [`basic prefab`](../../../concordia/prefabs/entity/basic.py), the component composition follows a **cognitive architecture pattern**:

1. **Instructions** - Basic behavioral guidelines
2. **Goal** (optional) - High-level objective
3. **Memory retrieval** - Relevant past experiences
4. **Self-perception** - "What kind of person am I?"
5. **Situation perception** - "What's happening now?"
6. **Person-by-situation** - "What would someone like me do here?" (synthesizes 4+5)
7. **Observations** - Recent events
8. **Memory storage** - Processes observations into memory

This mirrors human decision-making: identity + situation + past experience + current goal → action.

## Component Interaction Patterns

### 1. Context Chaining Pattern ([`concordia/components/agent/question_of_recent_memories.py`](../../../concordia/components/agent/question_of_recent_memories.py))
```python
person_by_situation = PersonBySituation(
    components=['SelfPerception', 'SituationPerception'],  # References other components
)
```
**Pattern**: Components can reference outputs from other components, creating reasoning chains

### 2. Memory Query Pattern ([`concordia/components/agent/all_similar_memories.py`](../../../concordia/components/agent/all_similar_memories.py))
```python
relevant_memories = AllSimilarMemories(
    components=['SituationPerception'],  # Uses situation to query memory
    num_memories_to_retrieve=10,
)
```
**Pattern**: Memory retrieval guided by current context, not just recency

### 3. Component Ordering Strategy ([`concordia/prefabs/entity/basic.py`](../../../concordia/prefabs/entity/basic.py))
```python
component_order.insert(1, goal_key)  # Goal after instructions, before everything else
```
**Pattern**: Strategic positioning affects LLM reasoning quality

### 4. Adaptive Component Pattern ([`concordia/components/agent/plan.py`](../../../concordia/components/agent/plan.py))
**Pattern**: Components that maintain state and make decisions about when to update that state

### 5. Function Reporter Pattern ([`concordia/components/agent/report_function.py`](../../../concordia/components/agent/report_function.py))
**Pattern**: Components that wrap external functions (e.g., time, weather) as context providers

## Game Master Component Patterns

### 1. Switch-Based Architecture ([`concordia/components/game_master/switch_act.py`](../../../concordia/components/game_master/switch_act.py))
**Pattern**: Game masters use different logic paths based on [`OutputType`](../../../concordia/types_concordia/entity.py):
- `MAKE_OBSERVATION` → Generate observations for players
- `NEXT_ACTING` → Decide who acts next
- `RESOLVE` → Process action consequences
- `TERMINATE` → Decide if simulation ends

### 2. Event Queue Pattern ([`concordia/components/game_master/make_observation.py`](../../../concordia/components/game_master/make_observation.py))
**Pattern**: Game masters maintain event queues per player, delivering cached events when appropriate

### 3. Multi-Component Decision Making ([`concordia/components/game_master/`](../../../concordia/components/game_master/))
**Pattern**: Game master components reference multiple other components to make complex decisions

## Key Agent Components Reference

- [`concordia/components/agent/memory.py`](../../../concordia/components/agent/memory.py) - Interface to associative memory
- [`concordia/components/agent/observation.py`](../../../concordia/components/agent/observation.py) - Processes incoming observations
- [`concordia/components/agent/question_of_recent_memories.py`](../../../concordia/components/agent/question_of_recent_memories.py) - Asks questions about recent experiences
- [`concordia/components/agent/concat_act_component.py`](../../../concordia/components/agent/concat_act_component.py) - Combines component outputs for decision making
- [`concordia/components/agent/all_similar_memories.py`](../../../concordia/components/agent/all_similar_memories.py) - Context-aware memory retrieval
- [`concordia/components/agent/plan.py`](../../../concordia/components/agent/plan.py) - Adaptive planning with time horizon reasoning
- [`concordia/components/agent/constant.py`](../../../concordia/components/agent/constant.py) - Static information provider
- [`concordia/components/agent/instructions.py`](../../../concordia/components/agent/instructions.py) - Behavioral guidelines
