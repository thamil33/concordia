# Thought Chains Analysis

The thought chains module provides **pre-built reasoning patterns** that define how InteractiveDocument conversations should flow for complex decision-making scenarios. These are **higher-order abstractions** that combine multiple interactive document operations into sophisticated reasoning workflows.

## Core Concept

**Thought Chains** = **Composable Reasoning Pipelines** that use InteractiveDocument to implement complex decision-making patterns. They're functions that take a reasoning document, candidate event, and active player, then process them through structured AI conversations.

### Pattern Signature
```python
def thought_chain_function(
    chain_of_thought: interactive_document.InteractiveDocument,
    candidate_event: str,
    active_player_name: str,
) -> str:
    # Structured reasoning using chain_of_thought
    # Returns processed/modified event
```

## 🧠 **Basic Reasoning Patterns**

### **Identity Chain** - Pass-Through
```python
def identity(chain_of_thought, premise, active_player_name):
    """Outputs the premise unchanged. Use for pass-through chains."""
    return premise  # No processing
```
**Usage**: Skip reasoning when simple pass-through is needed

### **Extract Direct Quote** - Speech Processing
```python
def extract_direct_quote(chain_of_thought, action_attempt, active_player_name):
    """Extract and preserve exact quotes from player actions."""

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
**Usage**: Preserve exact dialogue in narrative events

### **Determine Success and Why** - Action Resolution
```python
def determine_success_and_why(chain_of_thought, action_attempt, active_player_name):
    """Evaluate action success with reasoning."""

    success = chain_of_thought.yes_no_question(
        'Does the attempted action succeed? If easy to accomplish, '
        'should be successful unless specific reason to fail.'
    )

    if success:
        chain_of_thought.statement('The attempt succeeded.')
    else:
        chain_of_thought.statement('The attempt failed.')
        why_failed = chain_of_thought.open_question('Why did the attempt fail?')

    # Format result with success/failure reasoning
    return formatted_result
```
**Usage**: Standard action resolution with AI-determined outcomes

## 🎯 **Advanced Event Processing**

### **Result to Causal Statement** - Narrative Causality
```python
def result_to_causal_statement(chain_of_thought, event, active_player_name):
    """Transform events into clear cause-effect statements."""

    effect = chain_of_thought.open_question(
        'Because of that, what happens as a result?',
        max_tokens=1200
    )

    # Rewrite for clarity and causality
    causal_statement = chain_of_thought.open_question(
        'Rewrite to better highlight cause and effect. '
        'Do not express uncertainty (say "Francis released the demon" '
        'not "Francis could release the demon")',
        max_tokens=1500
    )
```
**Usage**: Create clear narrative causality chains

### **Attempt to Most Likely Outcome** - Probabilistic Resolution
```python
def attempt_to_most_likely_outcome(chain_of_thought, action_attempt, active_player_name):
    """Determine most probable outcome through structured analysis."""

    # Build context with questions
    chain_of_thought.open_question(f'Where is {active_player_name}?')
    chain_of_thought.open_question(f'What is {active_player_name} trying to do?')

    # Generate multiple possibilities
    chain_of_thought.open_question(
        f'List at least 3 possible direct consequences. '
        'Never assume voluntary actions by others. Be specific - '
        'say "Alex finds a teddy bear" not "Alex finds something".',
        max_tokens=3000
    )

    # Select most likely
    result = chain_of_thought.open_question('Which outcome is most likely?')
```
**Usage**: Realistic outcome prediction with multiple scenario consideration

### **Result to Who What Where** - Event Clarification
```python
def result_to_who_what_where(chain_of_thought, event, active_player_name):
    """Clarify events by emphasizing who did what where."""

    causal_statement = chain_of_thought.open_question(
        'Rewrite to better highlight the main person, where and what they did, '
        'and what happened as a result. Include exact quotes if anyone spoke.',
        max_tokens=1500
    )
```
**Usage**: Standardize event descriptions for clarity

## 🎭 **Complex Interactive Patterns**

### **AccountForAgencyOfOthers Class** - Player Agency Protection
```python
class AccountForAgencyOfOthers:
    """Prevents NPCs from taking voluntary actions without player consent."""

    def __call__(self, chain_of_thought, candidate_event, active_player_name):
        # Check if event implies others took voluntary actions
        voluntary_act_of_inactive_player = chain_of_thought.yes_no_question(
            f'Does event indicate anyone besides {active_player_name} '
            'took voluntary action?'
        )

        if voluntary_act_of_inactive_player:
            # Identify who acted
            inactive_players_who_acted = chain_of_thought.open_question(
                f'Which individuals besides {active_player_name} took action?'
            )

            # Ask each player if they would actually do that
            for player in inactive_players_who_acted:
                would_they = self._player_by_name[player].act(
                    choice_action_spec(
                        call_to_action=f'Would {player} do: {action}?',
                        options=['Yes', 'No']
                    )
                )

                if would_they == 'No':
                    # Generate alternative outcome
                    alternative = chain_of_thought.open_question(
                        'What happened instead, accounting for their refusal?'
                    )
```
**Usage**: Maintain player agency by checking consent for character actions

### **Conversation Class** - Multi-Agent Dialogue
```python
class Conversation:
    """Resolve conversation events into structured dialogues."""

    def __call__(self, chain_of_thought, candidate_event, active_player_name):
        conversation_occurred = chain_of_thought.yes_no_question(
            'Does the event suggest a conversation?'
        )

        if conversation_occurred:
            # Get participants
            participants = chain_of_thought.open_question(
                'Who participated? Comma-separated list.'
            )

            # Get contribution from each participant
            for participant in participants:
                if participant in self._player_names:
                    # Ask actual player what they'd say
                    contribution = self._player_by_name[participant].act(
                        free_action_spec(
                            call_to_action='What would {name} say?'
                        )
                    )
                else:
                    # AI generates NPC dialogue
                    contribution = chain_of_thought.open_question(
                        f'What would {participant} say?'
                    )

            # Generate full conversation
            conversation = chain_of_thought.open_question(
                'Generate conversation consistent with all contributions.',
                max_tokens=2200
            )
```
**Usage**: Transform conversation suggestions into full dialogues with player input

## 🎲 **Narrative Enhancement Patterns**

### **Action Categorization** - RPG-Style Action types_concordia
```python
def get_action_category_and_player_capability(chain_of_thought, event, active_player_name):
    """Categorize actions using tabletop RPG framework."""

    categories = (
        'Confess', 'Forgive', 'Perceive', 'Express', 'Defy',
        'Empathize', 'Conceal', 'Flow', 'Analyze'
    )

    # Each category has detailed description
    chain_of_thought.statement('Action types_concordia:\n1. Confess -- expose inner thoughts...')

    category_idx = chain_of_thought.multiple_choice_question(
        f'What category does {active_player_name}\'s action fall into?',
        answers=categories
    )

    # Assess capability
    chain_of_thought.open_question(
        f'Is {active_player_name} proficient in {category} actions? Why?'
    )
```
**Usage**: Add RPG-style action assessment and capability checking

### **Narrative Push Injection** - Story Momentum
```python
def maybe_inject_narrative_push(chain_of_thought, putative_event, active_player_name):
    """Add complications to prevent repetitive storylines."""

    if chain_of_thought.yes_no_question('Is the story repetitive?'):
        # Generate complications
        plausible_events = chain_of_thought.open_question(
            'Suggest five plausible events to move narrative forward. '
            'Only suggest things game master can decide. '
            'Never assume player character voluntary actions.',
            max_tokens=1500
        )

        # Randomly select complication
        additional_event = random.choice(plausible_events.split('\n'))

        # Combine with original event
        composite_event = chain_of_thought.open_question(
            f'How does complication modify original event? '
            'Answer as single composite event.'
        )
```
**Usage**: Prevent boring, repetitive storylines by injecting narrative complications

### **Scene Transition Detection** - Dramatic Pacing
```python
def maybe_cut_to_next_scene(chain_of_thought, event, active_player_name):
    """Determine if story needs scene transition."""

    chain_of_thought.open_question('What is current scene about?')

    cut_to_next_scene = chain_of_thought.yes_no_question(
        'Does latest event constitute good place to end scene? '
        'Valid reasons: conflict resolution, pacing, key revelation, '
        'catalyst for future action, character establishment, '
        'theme emphasis, natural break points.'
    )

    if cut_to_next_scene:
        next_scene = chain_of_thought.open_question(
            'What duration should pass? What will drive next scene? '
            'Include time duration on its own line at end.'
        )
        event += f'\\n\\n[CUT TO NEXT SCENE]\\n\\nSetting: {duration}\\n'
```
**Usage**: Automatic scene transitions based on narrative structure

## 🔧 **Chain Composition System**

### **Run Chain of Thought** - Pipeline Executor
```python
def run_chain_of_thought(
    thoughts: Sequence[Callable],
    premise: str,
    document: interactive_document.InteractiveDocument,
    active_player_name: str,
):
    """Execute sequence of thought chain functions."""

    conclusion = premise
    for thought_function in thoughts:
        conclusion = thought_function(document, conclusion, active_player_name)
        premise = conclusion  # Output becomes input for next step

    return document, conclusion
```

### **Usage in Game Master Prefabs**

**Situated Game Master** ([`concordia/prefabs/game_master/situated.py`](../../../concordia/prefabs/game_master/situated.py)):
```python
# Define event resolution pipeline
account_for_agency = thought_chains_lib.AccountForAgencyOfOthers(
    model=model, players=entities
)

event_resolution_steps = [
    account_for_agency,                           # Check player agency
    thought_chains_lib.result_to_who_what_where,  # Clarify event
    # Additional steps from configuration
]

# Used in EventResolution component
event_resolution = EventResolution(
    model=model,
    event_resolution_steps=event_resolution_steps,  # Thought chain pipeline
    components=context_components
)
```

**Psychology Experiment** ([`concordia/prefabs/game_master/psychology_experiment.py`](../../../concordia/prefabs/game_master/psychology_experiment.py)):
```python
# Simple pass-through for controlled experiments
event_resolution_steps = [thought_chains_lib.identity]
```

**Generic Game Master** ([`concordia/prefabs/game_master/generic.py`](../../../concordia/prefabs/game_master/generic.py)):
```python
# Full narrative enhancement pipeline
event_resolution_steps = [
    account_for_agency_of_others,
    thought_chains_lib.maybe_inject_narrative_push,  # Add complications
    thought_chains_lib.maybe_cut_to_next_scene,      # Scene transitions
    # Additional steps...
]
```

## Key Design Insights

### 🧩 **Composable Reasoning**
Thought chains are **building blocks for complex reasoning**:
- **Single responsibility**: Each function handles one reasoning aspect
- **Composable**: Chain functions together for complex workflows
- **Reusable**: Same functions used across different game master types_concordia
- **Configurable**: Game masters can specify custom chain combinations

### 🎭 **Narrative Intelligence**
Advanced patterns show sophisticated understanding of storytelling:
- **Player agency protection**: Prevents NPCs from acting without consent
- **Causal clarity**: Ensures events have clear cause-effect relationships
- **Dramatic pacing**: Automatic scene transitions based on narrative structure
- **Story momentum**: Injects complications to prevent repetitive storylines

### 🔧 **Integration with Framework**
Thought chains integrate seamlessly with component system:
- **EventResolution components** use thought chain pipelines
- **Game master prefabs** configure different chain combinations
- **InteractiveDocument** provides the reasoning engine
- **Player entities** participate in agency checking

### 🎯 **Sophisticated AI Direction**
Shows advanced prompt engineering patterns:
- **Multi-step reasoning**: Break complex decisions into simple questions
- **Uncertainty elimination**: Force definitive statements ("Francis opened door" not "Francis could open door")
- **Context building**: Accumulate information before major decisions
- **Constraint enforcement**: Prevent invalid narrative choices

The thought chains module reveals Concordia's sophisticated approach to **AI-driven narrative generation** with **formal guarantees around player agency** and **structured approaches to complex storytelling decisions**. It's a **higher-order abstraction** that makes InteractiveDocument reasoning patterns reusable and composable.
