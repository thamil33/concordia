## Simulation Flow (Simplified)

### Initialization

1. Choose a prefab (e.g., `basic.Entity`) and call its `build()` method with a language model and memory bank.
2. This creates an `EntityAgentWithLogging`, initializing all specified components and calling each component's `set_entity()`.

### Observe

1. The simulation calls `agent.observe(observation_text)`.
2. Agent enters `PRE_OBSERVE`: calls `pre_observe(observation_text)` on all context components in parallel (e.g., `ObservationToMemory` buffers the observation).
3. Enters `POST_OBSERVE`: calls `post_observe()` on components.
4. Enters `UPDATE`: calls `update()` on components (e.g., `Memory` commits buffered observations).
5. Returns to `READY` phase.

### Act

1. The simulation calls `agent.act(action_spec)`.
2. Agent enters `PRE_ACT`: calls `pre_act(action_spec)` on all context components in parallel to gather context/state.
3. The `context_processor` processes these contexts.
4. The `act_component` (e.g., `ConcatActComponent`) constructs a prompt and generates an `action_attempt`.
5. Enters `POST_ACT`: calls `post_act(action_attempt)` on components.
6. Enters `UPDATE`: calls `update()` on components (e.g., clears cached values).
7. Returns to `READY` and returns the `action_attempt`.

---

This modular, component-based architecture enables flexible and complex agent behaviors by combining and configuring different functional pieces.
