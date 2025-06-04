#!/usr/bin/env python
# coding: utf-8

# # Basic Agent Tutorial in Concordia
#

# This tutorial walks you through how to create your very first agent with
#
# In a full Concordia experiment you'd have a _Game Master_ directing the narrative and deciding what happens in the environment, and some _agents_ interacting with the environment and each other. For this tutorial, we will focus only on the agents, as **you**, the user, will act like the Game Master.
#
# <a href="https://colab.research.google.com/github/google-deepmind/concordia/blob/main/examples/deprecated/tutorials/agent_basic_tutorial.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

#@title Imports and initialization

import sentence_transformers

from typing_custom.deprecated import entity

from associative_memory.deprecated import associative_memory

from language_model import language_model

# The memory will use a sentence embedder for retrievel, so we download one from
# Hugging Face.
_embedder_model = sentence_transformers.SentenceTransformer(
    'sentence-transformers/all-mpnet-base-v2')
embedder = lambda x: _embedder_model.encode(x, show_progress_bar=False)

#@markdown By default this tutorial uses GPT-4, so you must provide an API key.
#@markdown Note that it is also possible to use local models or other API models,
#@markdown simply replace this cell with the correct initialization for the model
#@markdown you want to use.
GPT_API_KEY = '' #@param {type: 'string'}
GPT_MODEL_NAME = 'gpt-4o' #@param {type: 'string'}

if not GPT_API_KEY:
  raise ValueError('GPT_API_KEY is required.')

model = gpt_model.GptLanguageModel(api_key=GPT_API_KEY,
                                   model_name=GPT_MODEL_NAME)

#@markdown This initializes a variable called `model` that handles calls to the
#@markdown language model.
#@markdown
#@markdown We also initialize an `embedder` variable that we will use when we
#@markdown add a memory on the agent.


# # Building a dummy agent
#
# We will start by creating a dummy agent that just always tries to grab an apple.

# In[ ]:


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

agent = DummyAgent()


# In[ ]:


agent.act()


# Alright! We have our first agent... although not a terribly exciting one.
#
# Next let's create a very simple agent backed by the LLM.
#
# # Simple LLM Agent
#
# This agent remembers the last 5 observations, and acts by asking itself `"What should you do next?"`

# In[ ]:


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


agent = SimpleLLMAgent(model)


# In[ ]:


agent.observe("You are in a room.")
agent.observe("The room has only a table in it.")
agent.observe("On the table there is a single apple.")
agent.observe("The apple is shinny red and looks absolutely irresistible!")
agent.act()


# Alright! We have an agent that takes observations and attempts actions.
#
# ## Limitations of the `SimpleLLMAgent`
#
# While useful, the `SimpleLLMAgent` has some severe limitations. An obvious one is that if we push too many observations, we will lose them from context. We can increase the memory, but we are limited to the size of the LLM's context window, which, despite current models increasing this significantly from the times of 8-10k tokens, you can imagine a long running agent to run into this limit.
#
# Here's a toy example:

# In[ ]:


agent = SimpleLLMAgent(model)

agent.observe("You absolutely hate apples and would never willingly eat them.")
agent.observe("You don't particularly like bananas.")
# Only the next 5 observations will be kept, pushing out critical information!
agent.observe("You are in a room.")
agent.observe("The room has only a table in it.")
agent.observe("On the table there are two fruits: an apple and a banana.")
agent.observe("The apple is shinny red and looks absolutely irresistible!")
agent.observe("The banana is slightly past its prime.")
agent.act()


# We can fix this by adding a better memory to the agent. The `AssociativeMemory` saves _all_ observations, and does retrieval of semantically relevant memories on request. So, our agent becomes:

# In[ ]:


import collections

def make_prompt_associative_memory(
    memory: associative_memory.AssociativeMemory) -> str:
  """Makes a string prompt by joining all observations, one per line."""
  recent_memories_list = memory.retrieve_recent(5)
  recent_memories_set = set(recent_memories_list)
  recent_memories = "\n".join(recent_memories_set)

  relevant_memories_list = []
  for recent_memory in recent_memories_list:
    # Retrieve 3 memories that are relevant to the recent memory.
    relevant = memory.retrieve_associative(recent_memory, 3, add_time=False)
    for mem in relevant:
      # Make sure that we only add memories that are _not_ already in the recent
      # ones.
      if mem not in recent_memories_set:
        relevant_memories_list.append(mem)

  relevant_memories = "\n".join(relevant_memories_list)
  return (
      f"Your recent memories are:\n{recent_memories}\n"
      f"Relevant memories from your past:\n{relevant_memories}\n"
  )


class SimpleLLMAgentWithAssociativeMemory(entity.Entity):

  def __init__(self, model: language_model.LanguageModel, embedder):
    self._model = model
    # The associative memory of the agent. It uses a sentence embedder to
    # retrieve on semantically relevant memories.
    self._memory = associative_memory.AssociativeMemory(embedder)

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


agent = SimpleLLMAgentWithAssociativeMemory(model, embedder)

agent.observe("You absolutely hate apples and would never willingly eat them.")
agent.observe("You don't particularly like bananas.")
# Only the next 5 observations will be retrieved as "recent memories"
agent.observe("You are in a room.")
agent.observe("The room has only a table in it.")
agent.observe("On the table there are two fruits: an apple and a banana.")
agent.observe("The apple is shinny red and looks absolutely irresistible!")
agent.observe("The banana is slightly past its prime.")
agent.act()


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

# ```

# ```
