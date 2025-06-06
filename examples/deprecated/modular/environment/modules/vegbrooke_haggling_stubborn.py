
"""World configuration for the Fruitville haggling scenario."""

import random
from examples.deprecated.modular.environment import haggling

YEAR = 1913
MONTH = 9
DAY = 12

FEMALE_NAMES = [
    "Elara Greenleaf",
    "Seraphina Rootwood",
    "Willow Thistlebrook",
    "Ivy Mossheart",
    "Rosalind Nettleford",
    "Anya Pepperbloom",
    "Bryony Trufflewood",
    "Linnea Beetleblossom",
    "Maeve Parsnipvale",
    "Thora Gourdvine",
    "Calla Leekmeadow",
    "Esme Artichokehill",
    "Freya Turniptop",
    "Iris Cucumberford",
    "Lyra Onionbrook",
    "Nova Radishglen",
    "Opal Cabbageheart",
    "Saffron Sproutshade",
    "Verity Celerywood",
    "Wren Garlicgrove",
]

MALE_NAMES = [
    "Cedric Willowbark",
    "Rowan Mossglen",
    "Finnian Thistledew",
    "Asher Nettlewood",
    "Jasper Peppercorn",
    "Silas Trufflebrook",
    "Eamon Beetlebranch",
    "Gareth Parsnipfield",
    "Torin Gourdwhisper",
    "Callum Leekstone",
    "Dorian Artichokevale",
    "Evander Turnipseed",
    "Griffin Cucumberpatch",
    "Lysander Onionglen",
    "Nolan Radishbrook",
    "Oren Cabbagevine",
    "Quentin Sproutmeadow",
    "Tobias Celeryhill",
    "Viggo Garlicstream",
    "Wyatt Willowshade",
]

SCENARIO_PREMISE = (
    "In the enchanted kingdom of Verdant, nestled among rolling hills, lies the"
    " quaint town of Vegbrooke, renowned for its vibrant vegetable market."
    " Merchants and travelers from across the realm journey to Vegbrooke to"
    " trade and acquire the finest produce."
)

VISUAL_SCENE_OPENINGS = [
    (
        "The first rays of dawn paint the sky with hues of orange and gold as"
        " the vegetable market of Vegbrooke awakens. Merchants bustle about,"
        " arranging their colorful displays of crisp cabbages, plump pumpkins,"
        " and fragrant herbs."
    ),
    (
        "A gentle mist blankets the cobblestone streets of Vegbrooke as the"
        " market begins to stir. The air fills with the earthy aroma of freshly"
        " harvested root vegetables and the cheerful chatter of early shoppers."
    ),
    (
        "Sunlight filters through the leaves of the ancient oak tree that"
        " stands sentinel over the market square. Farmers arrive in their"
        " creaking carts, laden with baskets overflowing with vibrant produce,"
        " ready for a day of lively trade."
    ),
    (
        "The sound of cheerful bartering fills the air as the market of"
        " Vegbrooke bursts into life. Shoppers eagerly inspect the mounds of"
        " gleaming peppers, glistening eggplants, and artfully arranged bundles"
        " of asparagus."
    ),
    (
        "A cool breeze carries the scent of blooming flowers from the nearby"
        " meadows as the market of Vegbrooke awakens. Merchants greet each"
        " other with warm smiles, preparing for another day of bustling"
        " activity and the joy of sharing the bounty of the land."
    ),
]


def sample_parameters(seed: int | None = None):
  """Samples a set of parameters for the world configuration."""
  seed = seed if seed is not None else random.getrandbits(63)

  config = haggling.WorldConfig(
      year=YEAR,
      location="Fruitville",
      premise=SCENARIO_PREMISE,
      scene_visuals=VISUAL_SCENE_OPENINGS,
      buyer_base_reward_min=2,
      seller_base_reward_max=5,
      supporting_player_parameters={
          "fixed_response_by_call_to_action": {
              "proposed 1 coin": "reject",
              "proposed 2 coins": "reject",
              "proposed 3 coins": "reject",
              "proposed 4 coins": "accept",
              "proposed 5 coins": "reject",
              "What price would {name} propose?:": "4 coins",
          },
          "specific_memories": [
              "{name} is a stubborn merchant. {name} will sell his items"
              " exactly for 4 coins no more and no less. He is very vocal"
              " about it."
          ],
          "explicit_preference_component": (
              "{name} is a stubborn merchant. {name} will sell his items"
              " exactly for 4 coins no more and no less. He is very vocal"
              " about it."
          ),
      },
      num_supporting_players=1,
      num_main_players=1,
      num_games=5,
      random_seed=seed,
      only_match_with_support=True,
  )
  rng = random.Random(config.random_seed)

  all_names = list(MALE_NAMES) + list(FEMALE_NAMES)

  rng.shuffle(all_names)
  config.people = all_names

  for _, name in enumerate(MALE_NAMES):
    config.person_data[name] = {"gender": "male"}
  for _, name in enumerate(FEMALE_NAMES):
    config.person_data[name] = {"gender": "female"}

  return config
