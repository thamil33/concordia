# Agent Architecture Analysis

The agent system implements entities that participate in simulations, using component-based cognitive architectures.

## Core Agent Implementation

### EntityAgent Class ([`concordia/agents/entity_agent.py`](../../../concordia/agents/entity_agent.py))

**Purpose**: Base agent implementation using Entity-Component-System architecture

**Key Features**:
- **Component composition**: Agents built from reusable component library
- **Lifecycle management**: Structured interaction phases for all components
- **Memory integration**: Built-in associative memory system
- **State tracking**: Maintains component states across simulation time

**Core Methods**:
```python
def act(self) -> str
    # Returns agent's action for current timestep
    # Calls all components in PRE_ACT → POST_ACT phases

def observe(self, observation: str) -> None
    # Processes environmental observation
    # Calls all components in PRE_OBSERVE → POST_OBSERVE phases

def update(self) -> None
    # Updates internal state
    # Calls all components in UPDATE phase
```

### EntityAgentWithLogging ([`concordia/agents/entity_agent_with_logging.py`](../../../concordia/agents/entity_agent_with_logging.py))

**Purpose**: Enhanced agent with detailed logging for debugging and analysis

**Additional Features**:
- **Component output logging**: Records each component's contribution
- **Timestep tracking**: Logs state changes over simulation time
- **Performance analysis**: Enables understanding of component interactions
- **Debug capabilities**: Detailed trace of agent reasoning process

## Agent Construction Patterns

### Component-Based Assembly
Agents are assembled from components in specific orders:

```python
# From basic.py prefab
components = [
    Instructions,           # Behavioral guidelines
    Constant,              # Goal/objective
    AllSimilarMemories,    # Experience retrieval
    SelfPerception,        # Identity reasoning
    SituationPerception,   # Context understanding
    PersonBySituation,     # Behavioral synthesis
    LastNObservations,     # Recent events
    ObservationToMemory,   # Learning mechanism
    AssociativeMemory      # Memory interface
]
```

### Component Ordering Strategy
Strategic ordering affects reasoning quality:
1. **Foundation first**: Instructions and goals set behavioral base
2. **Information gathering**: Memory retrieval and perception
3. **Reasoning synthesis**: High-level decision components
4. **Memory processing**: Learning and storage components last

### Lifecycle Integration
Components participate in agent lifecycle phases:
- **READY**: Initial setup and configuration
- **PRE_ACT**: Reasoning before action generation
- **POST_ACT**: Processing after action selection
- **PRE_OBSERVE**: Preparation for new observations
- **POST_OBSERVE**: Processing observations
- **UPDATE**: State updates and maintenance

## Agent types_concordia and Patterns

### Player Agents
Represent individual participants in simulations:
- Use complex cognitive architectures (Basic, Planning patterns)
- Have personalities, goals, and memory
- Make autonomous decisions based on reasoning

### Assistant Agents
Simulate AI assistants or simple reactive entities:
- Use simplified architectures (Assistant pattern)
- Focus on response generation rather than complex reasoning
- Minimal memory and no planning

### Meta Agents
Handle simulation setup and configuration:
- Use Configurator pattern
- Design other agents and simulation parameters
- Specialized reasoning for simulation design

## Memory-Agent Integration

### Automatic Learning
All agents automatically learn through:
- [`ObservationToMemory`](../../../concordia/components/agent/observation.py) component
- Stores all experiences for future reference
- Builds experience base over simulation time

### Context-Aware Reasoning
Agents access memory contextually:
- [`AllSimilarMemories`](../../../concordia/components/agent/all_similar_memories.py) retrieves relevant experiences
- Memory informs identity, situation assessment, and action choice
- Creates consistency in agent behavior over time

### Formative Memory Seeding
Agents can be initialized with background memories:
- Personality traits and characteristics
- Past experiences and relationships
- Knowledge and beliefs specific to agent role

## Agent Configuration

### Parameter Customization
Agents configured via parameter dictionaries:
```python
params = {
    'name': 'Alice',
    'goal': 'Be helpful and honest',
    'personality': 'Friendly and analytical',
    'extra_components': [CustomComponent],
    'component_order': ['Instructions', 'Goal', 'Memory', ...]
}
```

### Memory Configuration
```python
# Formative memories for personality
formative_memories = [
    f"{name} is a {personality} person",
    f"{name} values {core_values}",
    f"{name} has experience with {background}"
]

# Memory initialization
mem = basic_associative_memory.AssociativeMemory(
    sentence_embedder=embedder,
    formative_memories=formative_memories
)
```

### Component Customization
Agents can use:
- **Standard components**: From component library
- **Custom components**: Domain-specific implementations
- **Parameter overrides**: Modify component behavior
- **Extra components**: Add specialized functionality

## Usage Patterns

### Basic Agent Creation
```python
# Using prefab factory
agent = basic.build_agent(
    config=agent_config,
    model=language_model,
    memory=memory,
    clock=game_clock,
    update_time_interval=update_interval
)
```

### Custom Agent Assembly
```python
# Manual component assembly
agent = entity_agent.EntityAgent(
    agent_name=name,
    act_component=act_component,
    observe_component=observe_component,
    update_component=update_component,
    config=config
)
```

### Multi-Agent Coordination
Agents coordinate through:
- **Shared environment**: Common observation space
- **Game master mediation**: Centralized coordination
- **Direct communication**: Agent-to-agent messaging (if enabled)

The agent system provides flexible, configurable entities that can simulate complex human-like reasoning while maintaining consistency and learning from experience.
