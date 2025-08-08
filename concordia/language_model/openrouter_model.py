"""Language Model that uses OpenRouter."""
import os

from concordia.language_model import language_model
from concordia.language_model.base_oai_compatible import BaseOAICompatibleModel
from concordia.utils import measurements as measurements_lib
import openai


class OpenRouterModel(BaseOAICompatibleModel):
  """Language Model that uses a model from OpenRouter."""

  def __init__(
      self,
      model_name: str | None = None,
      *,
      api_key: str | None = None,
      base_url: str | None = None,
      measurements: measurements_lib.Measurements | None = None,
      channel: str = language_model.DEFAULT_STATS_CHANNEL,
  ):
    """Initializes the instance.

    Args:
      model_name: The model name to use, e.g., "mistralai/mistral-7b-instruct".
        If None, will use the OPENROUTER_MODEL environment variable.
        See https://openrouter.ai/docs#models for a list of models.
      api_key: The OpenRouter API key. If None, will use the
        OPENROUTER_API_KEY environment variable.
      base_url: The base URL of the OpenRouter API. If None, will use the
        OPENROUTER_API_URL environment variable, falling back to
        "https://openrouter.ai/api/v1".
      measurements: The measurements object to log usage statistics to.
      channel: The channel to write the statistics to.
    """
    api_key = api_key or os.environ.get('OPENROUTER_API_KEY')
    if not api_key:
      raise ValueError(
          'OpenRouter API key must be provided either as the `api_key`'
          + ' argument or through the `OPENROUTER_API_KEY` environment'
          + ' variable.'
      )

    base_url = base_url or os.environ.get(
        'OPENROUTER_API_URL', 'https://openrouter.ai/api/v1'
    )
    model_name = model_name or os.environ.get('OPENROUTER_MODEL')
    if not model_name:
      raise ValueError(
          'OpenRouter model name must be provided either as the `model_name`'
          + ' argument or through the `OPENROUTER_MODEL` environment variable.'
      )

    client = openai.OpenAI(api_key=api_key, base_url=base_url)

    super().__init__(
        model_name=model_name,
        client=client,
        measurements=measurements,
        channel=channel,
    )
