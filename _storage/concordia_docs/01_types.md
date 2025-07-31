# Types System Analysis

The types module defines the fundamental abstractions and interfaces that enable Concordia's modular, component-based architecture. This is the foundational layer that everything else builds upon.

## Core Architectural Insights

### 🏗️ **Entity-Component-System Foundation**
The types system reveals Concordia's true architectural pattern:
- **Entities**: Independent actors (agents, game masters) that can observe and act
- **Components**: Modular building blocks that provide specific functionality
- **System**: Coordination framework managing entity lifecycles and interactions

### 🔄 **Component Lifecycle State Machine**
Components follow a strict state machine pattern with defined transitions:

```
READY → (PRE_ACT | PRE_OBSERVE)
PRE_ACT → POST_ACT → UPDATE → READY
PRE_OBSERVE → POST_OBSERVE → UPDATE → READY
```

This enables predictable, coordinated reasoning across multiple components.

## Core Type Definitions

### Component Interface ([`concordia/types/component.py`](../../../concordia/types/component.py))

**Purpose**: Base abstraction for all cognitive and coordination components

**Key Methods**:
```python
@abc.abstractmethod
def name(self) -> str
    # Component identifier

def state(self) -> str | None
    # Current component context for action generation

def partial_state(self, player_name: str) -> str | None
    # Player-specific view of component state

def observe(self, observation: str) -> None
    # Process environmental observations

def update(self) -> None
    # Update internal state after action/observation cycle
```

**Critical Insights**:
- **Context Generation**: `state()` provides component's contribution to action context
- **Perspective Filtering**: `partial_state()` enables player-specific information filtering
- **Memory Integration**: Components can maintain internal state across simulation time
- **Observational Learning**: `observe()` enables components to learn from environment

### Entity System ([`concordia/types/entity.py`](../../../concordia/types/entity.py))

**Purpose**: Defines actors that participate in simulations with configurable action types

**Action Type System**:
```python
class OutputType(str, enum.Enum):
    FREE = 'free'           # Open-ended text responses
    CHOICE = 'choice'       # Multiple choice selections
    FLOAT = 'float'        # Numerical responses

    # Game Master specific
    MAKE_OBSERVATION = 'make_observation'
    NEXT_ACTING = 'next_acting'
    RESOLVE = 'resolve'
    TERMINATE = 'terminate'
```

**ActionSpec System**:
- **Call to Action**: Template for prompting entity responses
- **Output Validation**: Ensures responses conform to expected types
- **Option Constraints**: Enforces valid choices for multiple choice actions
- **Tagging System**: Categorizes actions for memory storage (e.g., 'action', 'speech')

**Entity Lifecycle**:
```python
@abc.abstractmethod
def act(self, action_spec: ActionSpec) -> str
    # Generate action based on specification

@abc.abstractmethod
def observe(self, observation: str) -> None
    # Process environmental feedback
```

### Advanced Component Architecture ([`concordia/types/entity_component.py`](../../../concordia/types/entity_component.py))

**Purpose**: Sophisticated component system with lifecycle management and state persistence

#### Phase Management System
```python
class Phase(enum.Enum):
    READY = "Ready for action or observation"
    PRE_ACT = "Gathering context before action"
    POST_ACT = "Processing action attempt"
    PRE_OBSERVE = "Receiving observation"
    POST_OBSERVE = "Processing observation"
    UPDATE = "Updating internal state"
```

**Phase Transition Rules**:
- **READY** → **PRE_ACT** | **PRE_OBSERVE** (external triggers)
- **PRE_ACT** → **POST_ACT** (action generation)
- **POST_ACT** → **UPDATE** (action processing)
- **PRE_OBSERVE** → **POST_OBSERVE** (observation processing)
- **POST_OBSERVE** → **UPDATE** (observation integration)
- **UPDATE** → **READY** (state synchronization)

#### Component Types

**ContextComponent**: Standard cognitive components
```python
def pre_act(self, action_spec: ActionSpec) -> str
    # Provide context for action generation

def post_act(self, action_attempt: str) -> str
    # Process action attempt and return feedback

def pre_observe(self, observation: str) -> str
    # Prepare for observation processing

def post_observe(self) -> str
    # Finalize observation processing

def update(self) -> None
    # Update component state
```

**ActingComponent**: Privileged decision-making component
```python
@abc.abstractmethod
def get_action_attempt(
    self,
    context: ComponentContextMapping,
    action_spec: ActionSpec
) -> str
    # Central action decision using all component contexts
```

**ContextProcessorComponent**: Meta-component for processing other components' outputs
- Monitors and processes context from other components
- Enables meta-reasoning and coordination patterns
- Supports debugging and analysis of component interactions

#### State Management System
**Component State Persistence**:
```python
@abc.abstractmethod
def get_state(self) -> ComponentState
    # Return serializable component state

@abc.abstractmethod
def set_state(self, state: ComponentState) -> None
    # Restore component from saved state
```

**Entity State Management**:
```python
EntityState = Mapping[str, ComponentState | Mapping[str, ComponentState]]
```
- Hierarchical state structure supporting complex component compositions
- Enables simulation checkpointing and rollback
- Supports analysis and debugging of agent behavior over time

## Scene System ([`concordia/types/scene.py`](../../../concordia/types/scene.py))

**Purpose**: Structured interaction frameworks for organizing simulations

### Scene Type Specifications
```python
@dataclasses.dataclass(frozen=True)
class SceneTypeSpec:
    name: str                           # Scene type identifier
    game_master_name: str | None        # Designated coordinator
    default_premise: Mapping[...] | None # Player initialization messages
    action_spec: ActionSpec | None      # Custom action constraints
    possible_participants: Sequence[str] | None # Eligible actors
```

### Scene Instances
```python
@dataclasses.dataclass(frozen=True)
class SceneSpec:
    scene_type: SceneTypeSpec           # Scene template
    participants: Sequence[str]         # Actual participants
    num_rounds: int                     # Duration in rounds
    start_time: datetime.datetime | None # Schedule coordination
    premise: Mapping[...] | None        # Override default premise
```

**Key Insights**:
- **Template System**: Scene types define reusable interaction patterns
- **Instance Customization**: Scene specs customize templates for specific scenarios
- **Time Coordination**: Scenes can advance simulation time automatically
- **Participant Filtering**: Flexible participant selection from eligible pools

## Configuration System ([`concordia/types/prefab.py`](../../../concordia/types/prefab.py))

**Purpose**: Factory pattern for assembling entities with consistent configurations

### Role System
```python
class Role(enum.StrEnum):
    ENTITY = 'entity'         # Player agents
    GAME_MASTER = 'game_master' # Coordination agents
    INITIALIZER = 'initializer' # Setup agents
```

### Prefab Pattern
```python
@dataclasses.dataclass
class Prefab(abc.ABC):
    description: ClassVar[str]  # Documentation requirement
    params: Mapping[str, str]   # Configuration parameters
    entities: Sequence[...] | None # Entity references

    @abc.abstractmethod
    def build(
        self,
        model: LanguageModel,
        memory_bank: AssociativeMemoryBank,
    ) -> EntityWithComponents
```

### Configuration Structure
```python
@dataclasses.dataclass
class Config:
    prefabs: Mapping[str, Prefab]      # Available entity templates
    instances: Sequence[InstanceConfig] # Instantiation specifications
    default_premise: str               # Simulation premise
    default_max_steps: int             # Runtime limits
```

**Key Insights**:
- **Factory Pattern**: Prefabs encapsulate entity assembly logic
- **Role-Based Organization**: Clear separation of entity types and responsibilities
- **Parameter Injection**: Flexible customization through parameter mapping
- **Dependency Injection**: Prefabs receive required resources (model, memory)

## Supporting Systems

### Simulation Interface ([`concordia/types/simulation.py`](../../../concordia/types/simulation.py))
- **Entity Management**: Add/retrieve game masters and entities
- **Execution Framework**: `play()` method for running simulations
- **Resource Configuration**: Language models and embedders

### Clock System ([`concordia/types/clock.py`](../../../concordia/types/clock.py))
- **Time Progression**: Advance simulation through discrete timesteps
- **Scheduling**: Set specific times for scene transitions
- **Step Tracking**: Monitor simulation progress

### Logging System ([`concordia/types/logging.py`](../../../concordia/types/logging.py))
- **Metric Definitions**: Structured evaluation criteria
- **Channel Pattern**: Flexible logging output destinations
- **Component Integration**: Built-in logging support for components

## Architectural Patterns Revealed

### 🧠 **Cognitive Architecture Pattern**
Components build reasoning chains through:
1. **Context Gathering** (PRE_ACT): Each component contributes perspective
2. **Central Decision** (ActingComponent): Synthesizes all contexts into action
3. **Feedback Processing** (POST_ACT): Components process action outcomes
4. **Learning Integration** (UPDATE): Update state based on experience

### 🎭 **Role-Based Coordination Pattern**
Clear separation of concerns:
- **Entities**: Autonomous reasoning and action
- **Game Masters**: Rule enforcement and world state management
- **Initializers**: Setup and configuration
- **Components**: Modular cognitive capabilities

### 🔄 **State Management Pattern**
Hierarchical state with lifecycle guarantees:
- **Component States**: Individual component persistence
- **Entity States**: Composed component state collections
- **Phase Transitions**: Guaranteed state consistency across lifecycle
- **Checkpointing**: Simulation rollback and analysis support

### 🎯 **Action Specification Pattern**
Flexible action generation:
- **Type Safety**: Validated action formats
- **Context Templating**: Dynamic prompt generation
- **Constraint Enforcement**: Option validation for choice actions
- **Tagging System**: Categorized action storage

The types system reveals Concordia as a sophisticated cognitive architecture framework with formal guarantees around component interaction, state management, and entity coordination. This foundation enables the complex emergent behaviors seen in the component and prefab systems.
