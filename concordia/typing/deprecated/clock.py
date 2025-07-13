


"""An abstract class of a clock for synchronising the simulation."""

import abc
import datetime


class GameClock(metaclass=abc.ABCMeta):
  """An abstract clock for synchronising simulation."""

  @abc.abstractmethod
  def advance(self):
    """Advances the clock."""
    raise NotImplementedError

  def set(self, time: datetime.datetime):
    """Sets the clock to a specific time."""
    raise NotImplementedError

  def now(self) -> datetime.datetime:
    """Returns the current time."""
    raise NotImplementedError

  def get_step_size(self) -> datetime.timedelta:
    """Returns the step size."""
    raise NotImplementedError

  def get_step(self) -> int:
    """Returns the current step."""
    raise NotImplementedError

  def current_time_interval_str(self) -> str:
    """Returns the current time interval."""
    raise NotImplementedError
