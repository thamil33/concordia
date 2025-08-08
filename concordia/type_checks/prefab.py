

"""prefab base class."""

import abc
from collections.abc import Mapping, Sequence
import dataclasses
import enum
from typing import ClassVar

from concordia.associative_memory import basic_associative_memory
from concordia.language_model import language_model
from concordia.type_checks import entity_component


class Role(enum.StrEnum):
  ENTITY = 'entity'
  GAME_MASTER = 'game_master'
  INITIALIZER = 'initializer'


@dataclasses.dataclass
class Prefab(abc.ABC):
  """Base class for a prefab entity."""

  description: ClassVar[str]
  params: Mapping[str, str] = dataclasses.field(default_factory=dict)
  entities: (
      Sequence[entity_component.EntityWithComponents] | None
  ) = None

  @abc.abstractmethod
  def build(
      self,
      model: language_model.LanguageModel,
      memory_bank: basic_associative_memory.AssociativeMemoryBank,
  ) -> entity_component.EntityWithComponents:
    """Builds a prefab entity."""
    raise NotImplementedError

  def __init_subclass__(cls, **kwargs):
    """Called when a class inherits from Prefab. We use it to perform checks.
    """
    super().__init_subclass__(**kwargs)
    if not hasattr(cls, 'description'):
      raise TypeError(
          f"Class {cls.__name__} must define the 'description' class attribute."
      )


@dataclasses.dataclass
class InstanceConfig:
  prefab: str
  role: Role
  params: Mapping[str, str]


@dataclasses.dataclass
class Config:
  prefabs: Mapping[str, Prefab]
  instances: Sequence[InstanceConfig]
  default_premise: str = ''
  default_max_steps: int = 100
