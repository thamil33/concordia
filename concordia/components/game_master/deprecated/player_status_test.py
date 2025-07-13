


import datetime
from unittest import mock

from absl.testing import absltest
from absl.testing import parameterized
from concordia.associative_memory.deprecated import associative_memory
from concordia.components.game_master.deprecated import player_status
from concordia.language_model import language_model


def _clock_now() -> datetime.datetime:
  return datetime.datetime(2023, 1, 1, 0, 0, 0)


class PlayerStatusTest(parameterized.TestCase):
  """Tests for the PlayerStatus component."""

  @parameterized.named_parameters(
      dict(testcase_name="library", location="at the library"),
      dict(testcase_name="memory", location="at the pub"),
  )
  def test_output_in_right_format(self, location):
    """Tests that the output of the component is in the correct format.

    Args:
      location: The location to be returned by the language model.
    """
    model = mock.create_autospec(
        language_model.LanguageModel, instance=True, spec_set=True)
    model.sample_text.return_value = location
    memory = mock.create_autospec(associative_memory.AssociativeMemory,
                                  instance=True)
    memory.__len__.return_value = 1
    memory.retrieve_associative.return_value = "gibberish"
    player_names = ["Alice", "Bob"]
    component = player_status.PlayerStatus(
        clock_now=_clock_now,
        model=model,
        memory=memory,
        player_names=player_names)
    component.update()
    expected = "\n".join([f"  {name} is {location}" for name in player_names])
    self.assertEqual(component.state(), expected + "\n")


if __name__ == "__main__":
  absltest.main()
