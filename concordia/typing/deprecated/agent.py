


"""The abstract class that defines simulacrum agent interface.

It has a name and generates actions in response to observations and outcomes of
it's previous actions
Reference: Generative Agents: Interactive Simulacra of Human Behavior
https://arxiv.org/abs/2304.03442
"""

import abc
from typing import Any
from concordia.typing.deprecated import entity

# Forwarding the ActionSpec and the DEFAULT_ACTION_SPEC for backwards
# compatibility.
DEFAULT_ACTION_SPEC = entity.DEFAULT_ACTION_SPEC
ActionSpec = entity.ActionSpec
free_action_spec = entity.free_action_spec
float_action_spec = entity.float_action_spec
choice_action_spec = entity.choice_action_spec

DEFAULT_CALL_TO_SPEECH = (
    'Given the above, what is {name} likely to say next? Respond in'
    ' the format `{name} -- "..."` For example, '
    'Cristina -- "Hello! Mighty fine weather today, right?", '
    'Ichabod -- "I wonder if the alfalfa is ready to harvest", or '
    'Townsfolk -- "Good morning".\n'
)

DEFAULT_SPEECH_ACTION_SPEC = free_action_spec(
    call_to_action=DEFAULT_CALL_TO_SPEECH,
    tag='speech',
)


class GenerativeAgent(entity.Entity):
  """An agent interface for taking actions."""

  @abc.abstractmethod
  def get_last_log(self) -> dict[str, Any]:
    """Returns debugging information in the form of a dictionary."""
    raise NotImplementedError


class SpeakerGenerativeAgent(metaclass=abc.ABCMeta):
  """A simulacrum interface for simple conversation."""

  @abc.abstractmethod
  def say(self, conversation: str) -> str:
    """Returns the agent's response in the conversation."""
    raise NotImplementedError
