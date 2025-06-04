

"""Language Model that uses OpenAI's GPT models."""

import os

from concordia.language_model import language_model
from concordia.language_model.base_gpt_model import BaseGPTModel
from concordia.utils.deprecated import measurements as measurements_lib
import openai


class GptLanguageModel(BaseGPTModel):
  """Language Model that uses OpenAI GPT models."""

  def __init__(
      self,
      model_name: str,
      *,
      api_key: str | None = None,
      measurements: measurements_lib.Measurements | None = None,
      channel: str = language_model.DEFAULT_STATS_CHANNEL,
  ):
    """Initializes the instance.

    Args:
      model_name: The language model to use. For more details, see
        https://platform.openai.com/docs/guides/text-generation/which-model-should-i-use.
      api_key: The API key to use when accessing the OpenAI API. If None, will
        use the OPENAI_API_KEY environment variable.
      measurements: The measurements object to log usage statistics to.
      channel: The channel to write the statistics to.
    """
    if api_key is None:
      api_key = os.environ['OPENAI_API_KEY']
    self._api_key = api_key
    client = openai.OpenAI(api_key=self._api_key)
    super().__init__(model_name=model_name,
                     client=client,
                     measurements=measurements,
                     channel=channel)
