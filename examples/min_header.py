#
from concordia.embedding.embedd import Embedder, DummyEmbedder

from concordia.language_model.openrouter_model import OpenRouterLanguageModel
from concordia.language_model import no_language_model

import concordia.prefabs.entity as entity_prefabs
import concordia.prefabs.game_master as game_master_prefabs
from concordia.utils import helper_functions

# Language Model & Embedder
# To debug without spending money on API calls, set DISABLE_LANGUAGE_MODEL=True
DISABLE_LANGUAGE_MODEL = False
if not DISABLE_LANGUAGE_MODEL:
  model = OpenRouterLanguageModel()
  embedder = Embedder()
else:
  model = no_language_model.NoLanguageModel()
  embedder= DummyEmbedder()

# Load prefabs from packages to make the specific palette to use here.
prefabs = {
    **helper_functions.get_package_classes(entity_prefabs),
    **helper_functions.get_package_classes(game_master_prefabs),
}
# Print menu of prefabs
print((helper_functions.print_pretty_prefabs(prefabs)))
