"""Language Model that uses a local LM Studio server."""

import os
from concordia.language_model import language_model
from concordia.language_model.base_oai_compatible import BaseOAICompatibleModel
from concordia.utils.deprecated import measurements as measurements_lib
import openai


class LmStudioModel(BaseOAICompatibleModel):
  """Language Model that uses a local model served by LM Studio."""

  def __init__(
      self,
      model_name: str | None = None,
      *,
      base_url: str | None = None,
      timeout: float | None = None,
      measurements: measurements_lib.Measurements | None = None,
      channel: str = language_model.DEFAULT_STATS_CHANNEL,
  ):
    """Initializes the instance.

    Args:
      model_name: The model identifier. If None, will use the LM_STUDIO_MODEL
        environment variable. Note: For LM Studio, this can often be a
        placeholder as the model is pre-loaded in the UI.
      base_url: The base URL of the LM Studio server. If None, will use the
        LM_STUDIO_URL environment variable, falling back to
        "http://127.0.0.1:1234/v1".
      timeout: The timeout for API requests in seconds. If None, will use the
        LM_STUDIO_TIMEOUT environment variable, falling back to 600.0 (10
        minutes).
      measurements: The measurements object to log usage statistics to.
      channel: The channel to write the statistics to.
    """
    if base_url is None:
      base_url = os.environ.get('LM_STUDIO_URL', 'http://127.0.0.1:1234/v1')
    if model_name is None:
      model_name = os.environ.get('LM_STUDIO_MODEL')
    if timeout is None:
        timeout_str = os.environ.get('LM_STUDIO_TIMEOUT', '600.0')
        timeout = float(timeout_str)

    if not model_name:
      raise ValueError(
          'LM Studio model name must be provided either as the `model_name`'
          + ' argument or through the `LM_STUDIO_MODEL` environment variable.'
      )

    # LM Studio's local server does not require an API key.
    client = openai.OpenAI(
        api_key="lm-studio",
        base_url=base_url,
        timeout=timeout,
    )

    super().__init__(
        model_name=model_name,
        client=client,
        measurements=measurements,
        channel=channel
    )
