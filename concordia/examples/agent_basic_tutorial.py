# # Basic Agent Tutorial in Concordia

# This tutorial walks you through how to create your very first agent with Concordia.

# In a full Concordia experiment you'd have a _Game Master_ directing the narrative and deciding what happens in the environment, and some _agents_ interacting with the environment and each other. For this tutorial, we will focus only on the agents, as **you**, the user, will act like the Game Master.

#@title Imports and initialization
from concordia.embedding.sentence_transformer import get_embedder
from concordia.language_model.openrouter_model import OpenRouterLanguageModel as getmodel
from concordia.typing import entity

from concordia.associative_memory import  basic_associative_memory
from concordia.language_model import language_model

# Set up the embedder 
embedder = get_embedder 
# Test the embedder functionality
test_sentence = "This is a test sentence for the embedder."
embedding = embedder(test_sentence)
print("===== Concordia Agent Tutorial =====")
print(f"Embedding for test sentence: {embedding}")

#Again, we simply pass our model from concordia.language_model.openrouter_model import OpenRouterLanguageModel as model
model = getmodel()

# # Building a dummy agent
# 
# We will start by creating a dummy agent that just always tries to grab an apple

class DummyAgent(entity.Entity):

  @property
  def name(self) -> str:
    return 'Dummy'

  def act(self, action_spec=entity.DEFAULT_ACTION_SPEC) -> str:
    return "Dummy attempts to grab an apple."

  def observe(
      self,
      observation: str,
  ) -> None:
    pass


print("\n===== Example 1: DummyAgent =====")
agent = DummyAgent()
print(f"Created agent: {agent.name}")
action = agent.act()
print(f"Action: {action}")
print("===== End Example 1 =====\n")

# Alright! We have our first agent... although not a terribly exciting one.
# Next let's create a very simple agent backed by the LLM.
# # Simple LLM Agent
# remembers the last 5 observations, and acts by asking itself `"What should you do next?"`

import collections

def make_prompt(deque: collections.deque[str]) -> str:
  """Makes a string prompt by joining all observations, one per line."""
  return "\n".join(deque)


class SimpleLLMAgent(entity.Entity):

  def __init__(self, model: language_model.LanguageModel):
    self._model = model
    # Container (circular queue) for observations.
    self._memory = collections.deque(maxlen=5)

  @property
  def name(self) -> str:
    return 'Alice'

  def act(self, action_spec=entity.DEFAULT_ACTION_SPEC) -> str:
    prompt = make_prompt(self._memory)
    print(f"*****\nDEBUG: {prompt}\n*****")
    return self._model.sample_text(
        "You are a person.\n"
        f"Your name is {self.name} and your recent observations are:\n"
        f"{prompt}\nWhat should you do next?")

  def observe(
      self,
      observation: str,
  ) -> None:
    # Push a new observation into the memory, if there are too many, the oldest
    # one will be automatically dropped.
    self._memory.append(observation)



print("===== Example 2: SimpleLLMAgent =====")
agent = SimpleLLMAgent(model)
print(f"Created agent: {agent.name}")
observations = [
    "You are in a room.",
    "The room has only a table in it.",
    "On the table there is a single apple.",
    "The apple is shinny red and looks absolutely irresistible!"
]
for obs in observations:
    print(f"Observation: {obs}")
    agent.observe(obs)
print("-- Agent acts:")
prompt = make_prompt(agent._memory)
print(f"Prompt to LLM:\n{prompt}")
action = agent.act()
print(f"Action: {action}")
print("===== End Example 2 =====\n")


# Alright! We have an agent that takes observations and attempts actions.
# 
# ## Limitations of the `SimpleLLMAgent`
# 
# While useful, the `SimpleLLMAgent` has some severe limitations. An obvious one is that if we push too many observations, we will lose them from context. We can increase the memory, but we are limited to the size of the LLM's context window, which, despite current models increasing this significantly from the times of 8-10k tokens, you can imagine a long running agent to run into this limit.
# 
# Here's a toy example:

# In[ ]:



print("===== Example 3: SimpleLLMAgent with memory overflow =====")
agent = SimpleLLMAgent(model)
print(f"Created agent: {agent.name}")
observations = [
    "You absolutely hate apples and would never willingly eat them.",
    "You don't particularly like bananas.",
    "You are in a room.",
    "The room has only a table in it.",
    "On the table there are two fruits: an apple and a banana.",
    "The apple is shinny red and looks absolutely irresistible!",
    "The banana is slightly past its prime."
]
for obs in observations:
    print(f"Observation: {obs}")
    agent.observe(obs)
print("-- Agent acts:")
prompt = make_prompt(agent._memory)
print(f"Prompt to LLM:\n{prompt}")
action = agent.act()
print(f"Action: {action}")
print("===== End Example 3 =====\n")


# We can fix this by adding a better memory to the agent. The `AssociativeMemory` saves _all_ observations, and does retrieval of semantically relevant memories on request. So, our agent becomes:

# In[ ]:


import collections

def make_prompt_associative_memory(
    memory: basic_associative_memory.AssociativeMemoryBank) -> str:
  """Makes a string prompt by joining all observations, one per line."""
  recent_memories_list = memory.retrieve_recent(5)
  recent_memories_set = set(recent_memories_list)
  recent_memories = "\n".join(recent_memories_set)

  relevant_memories_list = []
  for recent_memory in recent_memories_list:
    # Retrieve 3 memories that are relevant to the recent memory.
    relevant = memory.retrieve_associative(recent_memory, 3)
    for mem in relevant:
      # Make sure that we only add memories that are _not_ already in the recent ones.
      if mem not in recent_memories_set:
        relevant_memories_list.append(mem)

  relevant_memories = "\n".join(relevant_memories_list)
  return (
      f"Your recent memories are:\n{recent_memories}\n"
      f"Relevant memories from your past:\n{relevant_memories}\n"
  )


class SimpleLLMAgentWithAssociativeMemory(entity.Entity):
  """An agent that uses an associative memory to retrieve relevant memories."""
  def __init__(self, model: language_model.LanguageModel, embedder):
    self._model = model
    # The associative memory of the agent. It uses a sentence embedder to
    # retrieve on semantically relevant memories.
    self._memory = basic_associative_memory.AssociativeMemoryBank(embedder)

  @property
  def name(self) -> str:
    return 'Alice'

  def act(self, action_spec=entity.DEFAULT_ACTION_SPEC) -> str:
    prompt = make_prompt_associative_memory(self._memory)
    print(f"*****\nDEBUG: {prompt}\n*****")
    return self._model.sample_text(
        "You are a person.\n"
        f"Your name is {self.name}.\n"
        f"{prompt}\n"
        "What should you do next?")

  def observe(
      self,
      observation: str,
  ) -> None:
    # Push a new observation into the memory, if there are too many, the oldest
    # one will be automatically dropped.
    self._memory.add(observation)


# In[ ]:



print("===== Example 4: SimpleLLMAgentWithAssociativeMemory =====")
agent = SimpleLLMAgentWithAssociativeMemory(model, embedder)
print(f"Created agent: {agent.name}")
observations = [
    "You absolutely hate apples and would never willingly eat them.",
    "You don't particularly like bananas.",
    "You are in a room.",
    "The room has only a table in it.",
    "On the table there are two fruits: an apple and a banana.",
    "The apple is shinny red and looks absolutely irresistible!",
    "The banana is slightly past its prime."
]
for obs in observations:
    print(f"Observation: {obs}")
    agent.observe(obs)
print("-- Agent acts:")
prompt = make_prompt_associative_memory(agent._memory)
print(f"Prompt to LLM (with associative memory):\n{prompt}")
action = agent.act()
print(f"Action: {action}")
print("===== End Example 4 =====\n")


# With a better memory, Alice should not eat the apple. She'll be able to remember she hates apples, and isn't super keen on bananas either. So she might choose to eat the banana, or just leave the room, or whatever else.
# 
# # The Entity-Component system
# 
# In the example above we are using an `AssociativeMemory` that we didn't have to implement, that's good. But now imagine we want to add some functionality for our agent to reason about how it is feeling at the moment. Maybe they are hungy because it hasn't eaten in a while, so they would eat the banana. We can easily do that by extending the class above, but it gets cumbersome and leads to a lot of forking code!
# 
# Instead of forking, we will be building agents using components. The idea is that an `Entity` is something that exist (explicitly, we'll talk about that later on) in the environment, but its functionality is controlled by adding components to it. This is a pattern used in many game engines called an [Entity-Component-System](https://en.wikipedia.org/wiki/Entity_component_system).
# 
# You can think of components as a piece of the thought process of the agent. All components, together, provide the full information that is used for the agent to act in a situation.
# 
# In this way, any modular piece of functionality in the entity can be easily reused in other agents without having to fork. So, for example, a component that retrieves relevant memories given recent observations should be useful in our example above, and in many other agents. So we create a component to handle this.
# 
# Now you are ready for the next tutorial: [Agent tutorial](https://colab.research.google.com/github/google-deepmind/concordia/blob/main/examples/tutorials/agent_components_tutorial.ipynb)
