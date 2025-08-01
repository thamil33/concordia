import datetime
from absl.testing import absltest
from absl.testing import parameterized
from concordia.clocks import game_clock


class GameClockTest(parameterized.TestCase):

  def test_advance(self):
    times = []
    clock = game_clock.MultiIntervalClock(
        start=datetime.datetime(hour=8, year=2024, month=9, day=1),
        step_sizes=[
            datetime.timedelta(hours=1),
            datetime.timedelta(minutes=10),
        ],
    )
    clock.advance()
    times.append(clock.now())

    with clock.higher_gear():
      for _ in range(7):
        clock.advance()
      times.append(clock.now())
    times.append(clock.now())

    clock.advance()
    times.append(clock.now())

    expected = [
        datetime.datetime(hour=9, year=2024, month=9, day=1),
        datetime.datetime(minute=10, hour=10, year=2024, month=9, day=1),
        datetime.datetime(minute=10, hour=10, year=2024, month=9, day=1),
        datetime.datetime(minute=0, hour=11, year=2024, month=9, day=1),
    ]
    self.assertEqual(times, expected)


if __name__ == '__main__':
  absltest.main()
