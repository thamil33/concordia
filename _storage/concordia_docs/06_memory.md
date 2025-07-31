# Memory System Analysis

The associative memory system is a core component providing context-aware memory storage and retrieval using semantic similarity.

## Core Implementation

### AssociativeMemory Class ([`concordia/associative_memory/basic_associative_memory.py`](../../../concordia/associative_memory/basic_associative_memory.py))

**Purpose**: Semantic memory storage with vector-based similarity retrieval

**Key Features**:
- **Vector embeddings**: Uses sentence transformers for semantic encoding
- **DataFrame storage**: Pandas DataFrame with columns for memory data
- **Similarity search**: Cosine similarity for memory retrieval
- **Automatic timestamping**: Tracks when memories are stored

**Core Methods**:
```python
def add(self, memory_text: str, metadata: dict = None) -> None
    # Stores memory with embedding and timestamp

def retrieve(self, query: str, k: int = 5) -> List[str]
    # Returns k most similar memories to query

def extend(self, memory_texts: List[str]) -> None
    # Batch memory storage
```

### Storage Schema
Memories stored as DataFrame rows with:
- `text`: The memory content
- `embedding`: Vector representation
- `time_added`: Timestamp
- Additional metadata columns as needed

### Formative Memories ([`concordia/associative_memory/formative_memories.py`](../../../concordia/associative_memory/formative_memories.py))

**Purpose**: Initial memory seeding for agent personalities and backgrounds

**Implementation**:
- Pre-populates memory with character background
- Establishes personality foundation before simulation starts
- Can include relationships, experiences, knowledge

## Component Integration

### Memory Component ([`concordia/components/agent/memory.py`](../../../concordia/components/agent/memory.py))

**Purpose**: Component interface to associative memory system

**Functionality**:
- Exposes memory operations to other components
- Provides consistent memory access across agent architecture
- Integrates with component lifecycle

### ObservationToMemory ([`concordia/components/agent/observation.py`](../../../concordia/components/agent/observation.py))

**Purpose**: Automatically stores observations as memories during `pre_observe()` phase

**Key Insights**:
- Creates memory traces of all agent experiences
- Enables learning from past interactions
- Provides experience base for future reasoning

### AllSimilarMemories ([`concordia/components/agent/all_similar_memories.py`](../../../concordia/components/agent/all_similar_memories.py))

**Purpose**: Context-aware memory retrieval for current situation

**Implementation**:
- Uses current situation as retrieval query
- Returns relevant past experiences
- Informs decision-making with historical context

## Memory Retrieval Patterns

### Context-Driven Retrieval
Components like [`QuestionOfRecentMemories`](../../../concordia/components/agent/question_of_recent_memories.py) use contextual queries:
- Self-perception queries: "What kind of person am I?"
- Situation queries: "What's happening now?"
- Behavioral queries: "What would someone like me do?"

### Time-Based Filtering
Components can access:
- Recent observations via [`LastNObservations`](../../../concordia/components/agent/observation.py)
- Historical experiences via [`AllSimilarMemories`](../../../concordia/components/agent/all_similar_memories.py)
- Complete memory via direct [`AssociativeMemory`](../../../concordia/components/agent/memory.py) access

### Strategic Memory Access
Different components use memory strategically:
- **Planning**: Retrieves goal-relevant experiences
- **Perception**: Compares current to past situations
- **Action**: Recalls successful behavioral patterns

## Memory Configuration

### Embedding Models
Configurable embedding backend:
- Default: Sentence transformers
- Custom: Via embedding interface in [`concordia/embedding/`](../../../concordia/embedding/)

### Retrieval Parameters
- `k`: Number of memories to retrieve
- `threshold`: Minimum similarity score
- `time_window`: Temporal filtering options

### Memory Initialization
```python
# Via formative memories
mem = basic_associative_memory.AssociativeMemory(
    sentence_embedder=embedder,
    formative_memories=formative_memories_list
)

# Runtime seeding
mem.extend([
    "I am a helpful assistant",
    "I value honesty and accuracy",
    "I care about being understood"
])
```

## Usage Patterns

### Agent Construction Pattern
1. **Initialize memory** with formative memories
2. **Add memory component** to agent architecture
3. **Include ObservationToMemory** for automatic learning
4. **Add retrieval components** for context access

### Memory-Driven Reasoning
Components reference memory outputs to build reasoning chains:
```
AllSimilarMemories → PersonBySituation
SelfPerception (from memory) → PersonBySituation
SituationPerception → memory retrieval → action planning
```

### Learning Integration
Memory enables agent learning through:
- **Experience accumulation**: All interactions stored
- **Pattern recognition**: Similar situations retrieved
- **Behavioral consistency**: Past actions inform future choices
- **Adaptive responses**: Learning from consequences

This memory system provides the foundation for believable, consistent agent behavior that improves over time through accumulated experience.
