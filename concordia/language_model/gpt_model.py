"""Language Model that uses OpenRouter's OpenAI-compatible API."""

import os

from concordia.language_model import language_model
from concordia.language_model.base_gpt_model import BaseGPTModel
from concordia.utils.deprecated import measurements as measurements_lib
import dotenv
import openai

dotenv.load_dotenv()

class GptLanguageModel(BaseGPTModel):
  """Language Model that uses OpenRouter's OpenAI-compatible models."""

  def __init__(
      self,
      model_name: str,
      *,
      api_key: str | None = None,
      base_url: str | None = None,
      http_referer: str | None = None,
      x_title: str | None = None,
      measurements: measurements_lib.Measurements | None = None,
      channel: str = language_model.DEFAULT_STATS_CHANNEL,
  ):
    """Initializes the instance.

    Args:
      model_name: The language model to use from OpenRouter.
      api_key: The API key to use when accessing the OpenRouter API. If None,
        will use the OPENROUTER_API_KEY environment variable.
      base_url: The base URL for the OpenRouter API. If None, will use the
        OPENROUTER_API_URL environment variable.
      http_referer: Optional. Site URL for rankings on openrouter.ai.
      x_title: Optional. Site title for rankings on openrouter.ai.
      measurements: The measurements object to log usage statistics to.
      channel: The channel to write the statistics to.
    """
    # Use the OPENROUTER_API_KEY from environment variables if not provided.
    if api_key is None:
      api_key = os.environ.get("OPENROUTER_API_KEY")
      if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set.")
    self._api_key = api_key

    # Use the OPENROUTER_API_URL from environment variables if not provided.
    if base_url is None:
      base_url = os.environ.get("OPENROUTER_API_URL")
      if not base_url:
        raise ValueError("OPENROUTER_API_URL environment variable not set.")
    self._base_url = base_url

    # Prepare the custom headers for OpenRouter.
    custom_headers = {}
    if http_referer:
      custom_headers["HTTP-Referer"] = http_referer
    if x_title:
      custom_headers["X-Title"] = x_title

    # Instantiate the OpenAI client, pointing it to the OpenRouter API endpoint
    # and including the custom headers.
    client = openai.OpenAI(
        api_key=self._api_key,
        base_url=self._base_url,
        default_headers=custom_headers,
    )

    super().__init__(model_name=model_name,
                     client=client,
                     measurements=measurements,
                     channel=channel)
