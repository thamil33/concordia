# Document System Analysis

The document system provides structured text building and interactive chain-of-thought reasoning with language models. It's a foundational system for building complex prompts and reasoning chains.

## Core Architecture

### Document Base Class ([`concordia/document/document.py`](../../../concordia/document/document.py))

**Purpose**: Structured text document with tagging and filtering capabilities

**Key Features**:
- **Tagged Content**: All content includes metadata tags for categorization
- **Filtered Views**: Create views that include/exclude specific tagged content
- **Immutable Content**: Individual content pieces are frozen dataclasses
- **Editing Context**: Safe editing with commit/rollback semantics

**Core Components**:
```python
@dataclasses.dataclass(frozen=True)
class Content:
    text: str                    # The actual text content
    tags: Set[str] = frozenset() # Metadata tags for filtering

class Document:
    def append(self, text: str, *, tags: Collection[str] = ()) -> None
        # Add content with optional tags

    def view(self, include_tags=(), exclude_tags=()) -> View
        # Create filtered view of document

    def text(self) -> str
        # Get all text as single string
```

**Document Views**:
- **Filtering**: Include only content with specific tags
- **Exclusion**: Remove content with specific tags
- **Dynamic**: Views update automatically as document changes
- **Composable**: Multiple filter criteria can be combined

### InteractiveDocument Class ([`concordia/document/interactive_document.py`](../../../concordia/document/interactive_document.py))

**Purpose**: Chain-of-thought reasoning with language model integration

**Key Innovation**: Enables structured prompting where components can:
1. **Build context** through statements and questions
2. **Query language model** with accumulated context
3. **Process responses** and continue reasoning chain
4. **Maintain conversation flow** with proper formatting

## Interactive Document Features

### 🧠 **Chain-of-Thought Methods**

**Statement Building**:
```python
def statement(self, text: str, *, tags: Collection[str] = ()) -> None
    # Add factual information to reasoning chain

def debug(self, text: str, *, tags: Collection[str] = ()) -> None
    # Add debug information (filtered from model view)
```

**Question-Answer Patterns**:
```python
def open_question(
    self,
    question: str,
    *,
    forced_response: str | None = None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    terminators: Collection[str] = ('\n',),
    question_label: str = 'Question',
    answer_label: str = 'Answer'
) -> str
    # Ask open-ended question and get model response
```

**Structured Choices**:
```python
def multiple_choice_question(
    self,
    question: str,
    answers: Sequence[str],
    randomize_choices: bool = True
) -> int
    # Present multiple choice and get selection

def yes_no_question(self, question: str) -> bool
    # Simple yes/no question
```

### 🎯 **Advanced Reasoning Patterns**

**Diversified Responses**:
```python
def open_question_diversified(
    self,
    question: str,
    *,
    num_samples: int = 10,
    max_tokens: int = DEFAULT_MAX_TOKENS
) -> str
    # Generate multiple responses and randomly select one
    # Increases response diversity and reduces model bias
```

**Forced Responses**:
- All question methods support `forced_response` parameter
- Enables testing, debugging, and deterministic scenarios
- Model is bypassed when forced response provided

### 🏷️ **Tag System**

**Built-in Tags**:
- `DEBUG_TAG`: Debug information (excluded from model view)
- `STATEMENT_TAG`: Factual statements in reasoning chain
- `QUESTION_TAG`: Questions posed to model
- `RESPONSE_TAG`: All responses (model and forced)
- `MODEL_TAG`: Specifically model-generated responses

**Automatic Filtering**:
- Model view excludes debug tags by default
- Enables clean prompts while preserving debug information
- Custom views can include/exclude any tag combinations

## Usage Patterns in Concordia

### 🔧 **Component Integration**

**Game Master Components** ([`concordia/components/game_master/world_state.py`](../../../concordia/components/game_master/world_state.py)):
```python
def update_after_event(self, event_statement: str) -> None:
    chain_of_thought = interactive_document.InteractiveDocument(self._model)

    # Build context with statements
    chain_of_thought.statement(f"Recent event: {event_statement}")
    chain_of_thought.statement(f"Current world state: {self._state}")

    # Ask model to update state
    important_variables_str = chain_of_thought.open_question(
        question="What important variables should be tracked?",
        max_tokens=500
    )

    # Process response and continue reasoning
    self._process_variables(important_variables_str)
```

**Switch Acting** ([`concordia/components/game_master/switch_act.py`](../../../concordia/components/game_master/switch_act.py)):
```python
def get_action_attempt(self, context, action_spec):
    chain_of_thought = interactive_document.InteractiveDocument(self._model)

    # Add all component contexts
    for component_name, component_context in context.items():
        chain_of_thought.statement(f"{component_name}: {component_context}")

    # Generate action decision
    result = chain_of_thought.open_question(
        question=action_spec.call_to_action,
        max_tokens=200,
        terminators=['\n']
    )

    return result
```

### 🎭 **Thought Chains** ([`concordia/thought_chains/thought_chains.py`](../../../concordia/thought_chains/thought_chains.py))

**Action Success Evaluation**:
```python
def determine_success_and_why(
    chain_of_thought: interactive_document.InteractiveDocument,
    action_attempt: str,
    active_player_name: str
):
    # Use structured reasoning to evaluate action success
    success = chain_of_thought.yes_no_question(
        'Does the attempted action succeed? If the attempted action '
        'is easy to accomplish then the attempt should be successful '
        'unless there is a specific reason for it to fail.'
    )

    if success:
        chain_of_thought.statement('The attempt succeeded.')
    else:
        chain_of_thought.statement('The attempt failed.')
        why_failed = chain_of_thought.open_question('Why did the attempt fail?')
```

**Direct Quote Extraction**:
```python
def extract_direct_quote(
    chain_of_thought: interactive_document.InteractiveDocument,
    action_attempt: str,
    active_player_name: str
):
    chain_of_thought.statement(f'{action_attempt}')

    # Multi-step reasoning chain
    proceed = chain_of_thought.yes_no_question(
        f'Did {active_player_name} explicitly say or write anything?'
    )

    if proceed:
        proceed_with_exact = chain_of_thought.yes_no_question(
            f'Does the text state exactly what {active_player_name} said or wrote?'
        )

        if proceed_with_exact:
            direct_quote = chain_of_thought.open_question(
                f'What exactly did {active_player_name} say or write?',
                max_tokens=2500
            )
            chain_of_thought.statement(f'[direct quote] {direct_quote}')
```

## Key Design Principles

### 🔄 **Incremental Context Building**
Interactive documents enable building complex prompts incrementally:
1. **Start with basic context** (statements)
2. **Add specific information** as reasoning progresses
3. **Query model** when decision points are reached
4. **Continue building** on model responses

### 🎯 **Structured Reasoning**
The question-answer pattern creates structured thinking:
- **Clear questions** focus model attention
- **Typed responses** (yes/no, multiple choice, open) constrain output
- **Response processing** enables automated reasoning chains
- **Context accumulation** maintains reasoning history

### 🏷️ **Content Organization**
Tag system enables sophisticated content management:
- **Debug separation**: Debug info doesn't affect model prompts
- **Content filtering**: Different views for different purposes
- **Response tracking**: Distinguish model vs. forced responses
- **Custom categorization**: Add domain-specific tags

### 🔧 **Testing and Debugging**
Forced responses enable comprehensive testing:
- **Deterministic scenarios**: Control exact responses for testing
- **Component isolation**: Test individual reasoning steps
- **Edge case exploration**: Force unusual responses to test robustness
- **Performance analysis**: Measure reasoning without model variability

## Integration with Component System

### **Component Reasoning Pattern**
Many components follow this pattern:
1. **Create InteractiveDocument** with component's language model
2. **Add context statements** from component state and external inputs
3. **Ask structured questions** to make decisions
4. **Process responses** and update component state
5. **Return results** to entity action/observation pipeline

### **Chain-of-Thought as Service**
InteractiveDocument acts as a reasoning service:
- **Stateless**: Each reasoning session creates new document
- **Contextual**: Incorporates all relevant information
- **Structured**: Follows consistent question-answer patterns
- **Traceable**: Full reasoning chain preserved for analysis

### **Model Abstraction**
InteractiveDocument abstracts language model interaction:
- **Consistent interface**: Same methods regardless of underlying model
- **Prompt management**: Handles context building and formatting
- **Response processing**: Manages terminators, token limits, validation
- **Error handling**: Graceful degradation for model issues

The document system enables sophisticated AI reasoning through structured prompt building and interactive dialogue with language models. It's a foundational tool that makes complex cognitive architectures possible while maintaining clean, testable, and debuggable code patterns.
