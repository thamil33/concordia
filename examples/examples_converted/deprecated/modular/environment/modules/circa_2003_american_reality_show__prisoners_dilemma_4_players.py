

"""Settings for an early 2000s american reality show for the prisoners_dilemma.
"""

from examples.deprecated.modular.environment.modules import circa_2003_american_reality_show as parent_module


def sample_parameters(seed: int | None = None):
  """Sample parameters of the setting and the backstory for each player."""
  return parent_module.sample_parameters(
      minigame_name='prisoners_dilemma',
      num_players=4,
      seed=seed,
  )
