"""A streamlined and configurable factory for generating formative memories."""

from collections.abc import Callable, Collection, Sequence
import dataclasses
import datetime
import logging
import os
import re
from typing import Any

from concordia.associative_memory import basic_associative_memory as associative_memory
from concordia.document import interactive_document
from concordia.language_model import language_model
from dateutil.relativedelta import relativedelta
import numpy as np

from concordia.associative_memory.formative_memories import AgentConfig, MemoryFactory

logger = logging.getLogger(__name__)


class SlimFormativeMemoryFactory:
  """A streamlined generator of formative memories."""

  def __init__(
      self,
      *,
      model: language_model.LanguageModel,
      embedder: Callable[[str], np.ndarray],
      shared_memories: Sequence[str] = (),
      delimiter_symbol: str = '***',
      current_date: datetime.datetime | None = None,
  ):
    """Initializes the memory factory, loading parameters from environment variables.

    Args:
      model: The language model to use for generating memories.
      embedder: The text embedder to use.
      shared_memories: Memories to be added to all agents.
      delimiter_symbol: The delimiter to split generated episodes.
      current_date: The date of the simulation.
    """
    self._model = model
    self._delimiter_symbol = delimiter_symbol
    self._blank_memory_factory_call = MemoryFactory(
        embedder=embedder).make_blank_memory
    self._shared_memories = shared_memories
    self._current_date = current_date

    # Load configurable parameters from environment variables with defaults
    self._sentences_per_episode = int(os.environ.get(
        'FORMATIVE_MEMORY_SENTENCE_LENGTH', '3'))
    self._backstory_max_tokens = int(os.environ.get(
        'BACKSTORY_MAX_TOKENS', '4500'))
    self._episodes_max_tokens = int(os.environ.get(
        'EPISODES_MAX_TOKENS', '6000'))

  def make_backstory(self, agent_config: AgentConfig) -> str:
    """Creates a backstory for an agent."""
    prompt = interactive_document.InteractiveDocument(self._model)
    prompt.statement('**Instructions:** Write a concise life story.')
    prompt.statement(f'\n**Name:** {agent_config.name}')
    if agent_config.gender:
      prompt.statement(f'\n**Gender:** {agent_config.gender}')
    if agent_config.date_of_birth:
      prompt.statement(f'\n**Born:** {agent_config.date_of_birth.year}')
    if agent_config.traits:
      prompt.statement(f'\n**Traits:** {agent_config.traits}')
    if agent_config.context:
      prompt.statement(f'\n**Context:** {agent_config.context}')

    question = (
        f'\nWrite a complete but concise life story for {agent_config.name}, '
        'from youth to old age, in no more than four paragraphs. '
        'The story should establish a clear personality consistent with the '
        'provided traits and context.'
    )
    result = prompt.open_question(
        question,
        max_tokens=self._backstory_max_tokens,
        terminators=['\nQuestion', '-----'],
    )
    return result

  def _generate_episodes(
      self,
      agent_config: AgentConfig,
      description: str,
  ) -> list[str]:
    """Generates formative memory episodes based on the agent's backstory."""
    prompt = interactive_document.InteractiveDocument(self._model)
    prompt.statement(f'**Character Backstory:**\n{description}')

    question = (
        f'\n**Task:** Invent formative episodes for {agent_config.name} at ages '
        f'{agent_config.formative_ages}. These events are critical to their '
        'personality. Describe each from a third-person limited perspective. '
        f'Each episode must be no more than {self._sentences_per_episode} '
        'sentences and start with "When [name] was [age] years old...". '
        f'Separate episodes with "{self._delimiter_symbol}".'
    )
    if agent_config.traits:
      question += f'\nThe episodes should explain these traits: "{agent_config.traits}".'
    if agent_config.context:
      question += f'\nSome episodes must relate to this context: "{agent_config.context}".'

    aggregated_result = prompt.open_question(
        question=question,
        max_tokens=self._episodes_max_tokens,
    )
    return list(aggregated_result.split(self._delimiter_symbol))

  def add_memories(
      self,
      memory: associative_memory.AssociativeMemoryBank,
      agent_config: AgentConfig,
  ) -> None:
    """Creates and adds formative memories to an agent's memory bank."""
    description = self.make_backstory(agent_config)
    episodes = self._generate_episodes(agent_config, description)

    if len(episodes) != len(agent_config.formative_ages):
      logger.warning(
          f'Warning: Mismatch between generated episodes ({len(episodes)}) and '
          f'required ages ({len(agent_config.formative_ages)}).'
      )

    for episode_age, episode in zip(agent_config.formative_ages, episodes):
      timestamp = None
      if agent_config.date_of_birth:
        timestamp = agent_config.date_of_birth + relativedelta(years=episode_age)

      memory_text = f'[{timestamp}] {episode.strip()}' if timestamp else episode.strip()
      memory.add(memory_text)

    if self._current_date and agent_config.date_of_birth:
      age = relativedelta(self._current_date, agent_config.date_of_birth).years
      memory.add(f'[{self._current_date}] {agent_config.name} is {age} years old.')

  def make_memories(
      self,
      agent_config: AgentConfig,
  ) -> associative_memory.AssociativeMemoryBank:
    """Creates a complete agent memory bank from the agent config."""
    mem = self._blank_memory_factory_call()
    for item in self._shared_memories:
      mem.add(item)

    context = agent_config.context
    if agent_config.goal:
      context += f"\n{agent_config.name}'s goal is: {agent_config.goal}"

    self.add_memories(memory=mem, agent_config=agent_config)

    if context:
      for item in context.split('\n'):
        if item:
          mem.add(item)

    if agent_config.specific_memories:
      for item in agent_config.specific_memories.split('\n'):
        if item:
          mem.add(item)

    return mem
