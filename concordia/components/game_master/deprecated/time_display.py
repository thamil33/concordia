


"""This component shows current time interval."""


from concordia.typing.deprecated import clock
from concordia.typing.deprecated import component


class TimeDisplay(component.Component):
  """Tracks the status of players."""

  def __init__(
      self,
      game_clock: clock.GameClock,
      name: str = 'Current time interval',
  ):
    self._clock = game_clock
    self._name = name

  def name(self) -> str:
    return self._name

  def state(self) -> str:
    return self._clock.current_time_interval_str()
