
"""A set of pub names and reasons to like them."""

import random
from examples.deprecated.modular.environment import pub_coordination
from examples.deprecated.modular.environment.modules import pub_coordination_london

YEAR = pub_coordination_london.YEAR
MONTH = pub_coordination_london.MONTH
DAY = pub_coordination_london.DAY

NUM_PUBS = pub_coordination_london.NUM_PUBS


def sample_parameters(seed: int | None = None):
  """Samples a set of parameters for the world configuration."""
  seed = seed if seed is not None else random.getrandbits(63)
  rng = random.Random(seed)

  pubs = rng.sample(
      list(pub_coordination_london.PUB_PREFERENCES.keys()),
      pub_coordination_london.NUM_PUBS,
  )
  pub_preferences = {
      k: pub_coordination_london.PUB_PREFERENCES[k] for k in pubs
  }

  config = pub_coordination.WorldConfig(
      year=pub_coordination_london.YEAR,
      location="London",
      event="European football cup",
      game_countries=pub_coordination_london.EURO_CUP_COUNTRIES,
      venues=pubs,
      venue_preferences=pub_preferences,
      social_context=pub_coordination_london.SOCIAL_CONTEXT,
      random_seed=seed,
      pub_closed_probability=0.7
  )

  all_names = list(pub_coordination_london.MALE_NAMES) + list(
      pub_coordination_london.FEMALE_NAMES
  )

  rng.shuffle(all_names)
  config.people = all_names

  for _, name in enumerate(pub_coordination_london.MALE_NAMES):
    config.person_data[name] = {"gender": "male"}
  for _, name in enumerate(pub_coordination_london.FEMALE_NAMES):
    config.person_data[name] = {"gender": "female"}
  config.player_who_knows_closed_pub = all_names[0]

  return config
