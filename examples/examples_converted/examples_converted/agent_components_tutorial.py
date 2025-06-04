#!/usr/bin/env python
# coding: utf-8

# # Components Tutorial in Concordia
#

# This tutorial walks you through how to create your own components to use in Concordia agents.
#
# <a href="https://colab.research.google.com/github/google-deepmind/concordia/blob/main/examples/deprecated/tutorials/agent_components_tutorial.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>
#
# If you want to know the basics of making agents in Concordia, refer to the <a href="https://colab.research.google.com/github/google-deepmind/concordia/blob/main/examples/tutorials/agent_components_tutorial.ipynb" target="_parent">Basic Agent Tutorial</a>. We will assume you are familiar with those concepts from here on.

# In[ ]:


# @title Colab-specific setup (use a CodeSpace to avoid the need for this).
try:
  get_ipython().run_line_magic('pass', ' #env COLAB_RELEASE_TAG')
except:
  pass  # Not running in colab.
else:
  get_ipython().run_line_magic('pass', " #pip install --ignore-requires-python --requirement 'https://raw.githubusercontent.com/google-deepmind/concordia/main/examples/requirements.in' 'git+https://github.com/google-deepmind/git#egg=gdm-concordia'")
  get_ipython().run_line_magic('pass', ' #pip list')


# In[ ]:


#@title Imports and initialization

import sentence_transformers

from typing_custom.deprecated import entity

from agents import entity_agent
from associative_memory import associative_memory

from components.agent.deprecated import action_spec_ignored
from components.agent.deprecated import memory_component
from memory_bank.deprecated import legacy_associative_memory
from typing_custom.deprecated import entity_component


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


# # What is a Component?
#
# Recall that `Entities` have an `act` and an `observe` function they need to implement.
#
# A `Component` is just a modular piece of functionality that helps the agent make decisions to process the observations it receives, and to create action attempts. The [`EntityAgent`](https://github.com/google-deepmind/concordia/blob/main/concordia/agents/entity_agent.py) is in charge of dispatching the action requests to its components, and to inform them once an action attempt has been decided. Likewise, the `EntityAgent` will inform components of observations received, and process any observation processing context from components.
#
# ## The minimal agent
#
# At the very least, an `EntityAgent` needs a special component called an [`ActingComponent`](https://github.com/google-deepmind/concordia/blob/36ba0dbc643cd86a7c3b7769fe2d6beaf4b9c338/concordia/typing/entity_component.py#L192) which decides the action attempts. Let's create an `ActingComponent` that always tries eating an apple. We will then added to a dummy `EntityAgent`.

# In[ ]:


import collections

class AppleEating(entity_component.ActingComponent):

  def get_action_attempt(
      self,
      context,
      action_spec,
  ) -> str:
    return "Eat the apple."


agent = entity_agent.EntityAgent('Alice', act_component=AppleEating())


# In[ ]:


agent.act()


# This is a _very_ simple agent... it just always tries to eat the apple. So, let's make that a bit more interesting.
#
# Like we did in the Basic Tutorial, let's give the agent a memory, and make it decide what to do based on relevant memories to observations. Unlike the previous tutorial where we used an `AssociativeMemory` directly, we will use a memory component instead. This highlights the modularity of the component system.
#
# We will create a `Component` that received observations and pushes them into a memory `Component`. Then, we will create a `Component` that extracts recent memories. Finally, we will define an `ActingComponent` that takes context from all components, and produces an action attempt that is relevant to the situation.

# In[ ]:


class Observe(entity_component.ContextComponent):

  def pre_observe(self, observation: str) -> None:
    self.get_entity().get_component('memory').add(observation, {})


class RecentMemories(entity_component.ContextComponent):

  def pre_act(self, action_spec) -> None:
    recent_memories_list = self.get_entity().get_component('memory').retrieve(
        query='',  # Don't need a query to retrieve recent memories.
        limit=5,
        scoring_fn=legacy_associative_memory.RetrieveRecent(),
    )
    recent_memories = " ".join(memory.text for memory in recent_memories_list)
    print(f"*****\nDEBUG: Recent memories:\n  {recent_memories}\n*****")
    return recent_memories


class SimpleActing(entity_component.ActingComponent):

  def __init__(self, model: language_model.LanguageModel):
    self._model = model

  def get_action_attempt(
      self,
      contexts,
      action_spec,
  ) -> str:
    # Put context from all components into a string, one component per line.
    context_for_action = "\n".join(
        f"{name}: {context}" for name, context in contexts.items()
    )
    print(f"*****\nDEBUG:\n  context_for_action:\n{context_for_action}\n*****")
    # Ask the LLM to suggest an action attempt.
    call_to_action = action_spec.call_to_action.format(
        name=self.get_entity().name, timedelta='2 minutes')
    sampled_text = self._model.sample_text(
        f"{context_for_action}\n\n{call_to_action}\n",
    )
    return sampled_text


raw_memory = legacy_associative_memory.AssociativeMemoryBank(
    associative_memory.AssociativeMemory(embedder))

# Let's create an agent with the above components.
agent = entity_agent.EntityAgent(
    'Alice',
    act_component=SimpleActing(model),
    context_components={
        'observation': Observe(),
        'recent_memories': RecentMemories(),
        'memory': memory_component.MemoryComponent(raw_memory),
    })


# In[ ]:


agent.observe("You absolutely hate apples and would never willingly eat them.")
agent.observe("You don't particularly like bananas.")
# Only the next 5 observations will be kept, pushing out critical information!
agent.observe("You are in a room.")
agent.observe("The room has only a table in it.")
agent.observe("On the table there are two fruits: an apple and a banana.")
agent.observe("The apple is shinny red and looks absolutely irresistible!")
agent.observe("The banana is slightly past its prime.")

agent.act()


# Alright! We have now have an agent that can use a very limited memory to choose actions :)
#
# A few things of notice in the definitions above.
#
# *  Some components are defining `pre_act` while others are defining `pre_observe`
# *  Acting components receive a `contexts` parameter
# *  Some components are finding other components within the agent via `self.get_entity().get_component(component_name)`
#
# ## The `EntityComponent` API
#
# [`EntityComponents`](https://github.com/google-deepmind/concordia/blob/main/concordia/typing/entity_component.py) have the following functions, which you can override in your component implementation:
# *  **`pre_act(action_spec)`**: Returns the information that the component wants to be part of the acting decision
# *  **`post_act(action_attempt)`**: Informs component of the action decided by the `ActingComponent`. Returns any information that might be useful for the agent (usually empty)
# *  **`pre_obeserve(observation)`**: Informs component of the observation received. Returns any information that might be useful for the agent (usually empty)
# *  **`post_observe()`**: Returns any information that might be useful for the agent (usually empty)
# *  **`update()`**: Inform the component that an `act` or `observe` are being finalized. Called after `post_act` or `post_observe` to give the component a chance to update its internal state
#
# These functions correspond to the `Phases` that an `EntityAgent` can be in. We will talk about `Phases` below.
#
# For more detailed information, see the definition of the [`EntityComponent`](https://github.com/google-deepmind/concordia/blob/main/concordia/typing/entity_component.py) and the [`EntityAgent`](https://github.com/google-deepmind/concordia/blob/main/concordia/agents/entity_agent.py)
#
# ## The `ActingComponent` API
#
# [`ActingComponents`](https://github.com/google-deepmind/concordia/blob/36ba0dbc643cd86a7c3b7769fe2d6beaf4b9c338/concordia/typing/entity_component.py#L192) have only one required function:
#
# *  **`get_action_attempt(contexts, action_spec)`**: The contexts are a dictionary of component name to the returned values from all (entity) components' `pre_act`
#
# The `ActingComponent` then uses the contexts from the components and the action spec to decide on the action attempt. This action attempt will then be forwarded by the `EntityAgent` to all components via `post_act`.
#
# ## Accessing other components in the agent
#
# All components have a method `get_entity()` that returns the `EntityAgent` they belong to. The `EntityAgent` has two functions available to the components:
#
# *  **`get_component(component_name)`**: gets the component with the given name. Raises an exception if the entity has no component with that name
# *  **`get_phase()`**: Returns the current [Phase](https://github.com/google-deepmind/concordia/blob/1bc6922689c0a26fb90f4d5ff5f86066937fdb34/concordia/typing/entity_component.py#L32) of the entity. This is one of:
#    * `INIT`: the entity is initialized, and hasn't received any `act` or `observe`
#    * `PRE_ACT`: the entity is asking components for their `pre_act` contexts
#    * `POST_ACT`: the entity is informing components of the action attempt
#    * `PRE_OBSERVE` the entity is informing components of an observation
#    * `POST_OBSERVE` the entity has finished processing the observation and is informing components
#    * `UPDATE` called after `POST_ACT` or `POST_OBSERVE`
#
# **WARNING**:  Accessing other components internals is dangerous!
#
# A component can use the above methods to get another component and call any of its methods. This is very powerful, but dangerous. Recall that we have no guarantees over which order components are getting processed. For instance, what would happen if a component is adding memories in `pre_act` when other components are reading the memory. The component could be in an inconsistent state! Fortunately the [`MemoryComponent`](https://github.com/google-deepmind/concordia/blob/main/concordia/components/agent/memory_component.py) deals with this by buffering the added memories, only committing them during the `UPDATE` phase. If you try to access the memory during this phase, it will raise an error.
#
# # An agent with relevant memories
#
# The problem with our agent above is that critical information is being lost! :(
#
# To fix this, we need a component that takes recent observations (memories), and then searches the memory bank for relevant memories. This creates a dependency of one component's state into another component. But above we just talked about how this is dangerous, so how do we fix it?
#
# When a component's `pre_act` does not take into account the `action_spec` for producing its context, we can derive the component from the [`ActionSpecIgnored`](https://github.com/google-deepmind/concordia/blob/main/concordia/components/agent/action_spec_ignored.py) base class. Then, instead of overriding `pre_act` we override `_make_pre_act_value()` (that doesn't take an `action_spec`) and the base class makes sure everything is handled correctly with concurrency.
#
# It is that simple! :)

# In[ ]:


class RecentMemoriesImproved(action_spec_ignored.ActionSpecIgnored):

  def __init__(self):
    super().__init__('Recent memories')

  def _make_pre_act_value(self) -> str:
    recent_memories_list = self.get_entity().get_component('memory').retrieve(
        query='',  # Don't need a query to retrieve recent memories.
        limit=5,
        scoring_fn=legacy_associative_memory.RetrieveRecent(),
    )
    recent_memories = " ".join(memory.text for memory in recent_memories_list)
    print(f"*****\nDEBUG: Recent memories:\n  {recent_memories}\n*****")
    return recent_memories


# Now we can use this component's pre-act context by calling `get_pre_act_value()` on it. Which is what we will do to implement the relevant memories component.
#
# ## Relevant memories implementation

# In[ ]:


def _recent_memories_str_to_list(recent_memories: str) -> list[str]:
  # Split sentences, strip whitespace and add final period
  return [memory.strip() + '.' for memory in recent_memories.split('.')]


class RelevantMemories(action_spec_ignored.ActionSpecIgnored):

  def __init__(self):
    super().__init__('Relevant memories')

  def _make_pre_act_value(self) -> str:
    recent_memories = self.get_entity().get_component('recent_memories').get_pre_act_value()
    # Each sentence will be used for retrieving new relevant memories.
    recent_memories_list = _recent_memories_str_to_list(recent_memories)
    recent_memories_set = set(recent_memories_list)
    memory = self.get_entity().get_component('memory')
    relevant_memories_list = []
    for recent_memory in recent_memories_list:
      # Retrieve 3 memories that are relevant to the recent memory.
      relevant = memory.retrieve(
          query=recent_memory,
          limit=3,
          scoring_fn=legacy_associative_memory.RetrieveAssociative(add_time=False),
      )
      for mem in relevant:
        # Make sure that we only add memories that are _not_ already in the recent
        # ones.
        if mem.text not in recent_memories_set:
          relevant_memories_list.append(mem.text)
          recent_memories_set.add(mem.text)

    relevant_memories = "\n".join(relevant_memories_list)
    print(f"*****\nDEBUG: Relevant memories:\n{relevant_memories}\n*****")
    return relevant_memories


raw_memory = legacy_associative_memory.AssociativeMemoryBank(
    associative_memory.AssociativeMemory(embedder))

# Let's create an agent with the above components.
agent = entity_agent.EntityAgent(
    'Alice',
    act_component=SimpleActing(model),
    context_components={
        'observation': Observe(),
        'relevant_memories': RelevantMemories(),
        'recent_memories': RecentMemoriesImproved(),
        'memory': memory_component.MemoryComponent(raw_memory),
    })


# In[ ]:


agent.observe("You absolutely hate apples and would never willingly eat them.")
agent.observe("You don't particularly like bananas.")
# The previous memories will be revtrieved associatively, even though they are
# past the recency limit.
agent.observe("You are in a room.")
agent.observe("The room has only a table in it.")
agent.observe("On the table there are two fruits: an apple and a banana.")
agent.observe("The apple is shinny red and looks absolutely irresistible!")
agent.observe("The banana is slightly past its prime.")

agent.act()


# And so, Alice does not eat the apple, because she remembers she _hates_ them! :)
