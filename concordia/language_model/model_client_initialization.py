"""Handles the initialization of the language model and sentence embedder."""

import os
import numpy as np
import sentence_transformers
from dotenv import load_dotenv
import openai

from concordia.language_model import gpt_model
from concordia.language_model import openrouter_model
from concordia.language_model import lm_studio_model
from concordia.language_model import no_language_model
from concordia.language_model import retry_wrapper
from concordia.language_model import fallback_wrapper # Import the new wrapper

class ModelClient:
  """Initializes and holds the language model and sentence embedder."""

  def __init__(self, provider: str | None = None, stream: bool = False):
    """Initializes the ModelClient.

    Args:
      provider: The model provider to use.
      stream: Whether to stream responses.
    """
    load_dotenv()

    if provider is None:
      provider = os.environ.get('MODEL_PROVIDER', 'disabled').lower()

    self.model = None
    self.embedder = None
    self._provider = provider

    if self._provider == 'disabled':
      print("Language model is disabled.")
      self.model = no_language_model.NoLanguageModel()
      self.embedder = lambda x: np.ones(3)
      return

    print(f"Initializing model for provider: {self._provider}")

    # Special handling for OpenRouter to implement the fallback logic
    if self._provider == 'openrouter':
      primary_openrouter_model = openrouter_model.OpenRouterModel()
      fallback_model_name = os.environ.get('OPENROUTER_FALLBACK_MODEL')

      if fallback_model_name:
        print(f"Fallback model configured: {fallback_model_name}")
        fallback_openrouter_model = openrouter_model.OpenRouterModel(
            model_name=fallback_model_name
        )
        self.model = fallback_wrapper.FallbackLanguageModel(
            primary_model=primary_openrouter_model,
            fallback_model=fallback_openrouter_model,
            primary_retry_exceptions=(openai.RateLimitError, openai.APITimeoutError)
        )
      else:
        # If no fallback is specified, use the standard retry wrapper
        self.model = retry_wrapper.RetryLanguageModel(
            model=primary_openrouter_model,
            retry_on_exceptions=(openai.RateLimitError, openai.APITimeoutError),
            retry_tries=2,
            retry_delay=61,
        )

    else:
      # For all other providers, use the standard retry wrapper
      base_model = None
      if self._provider == 'openai':
        model_name = os.environ.get('OPENAI_MODEL_NAME', 'gpt-4')
        base_model = gpt_model.GptLanguageModel(model_name=model_name)
      elif self._provider == 'lmstudio':
        base_model = lm_studio_model.LmStudioModel(stream=stream)
      else:
        raise ValueError(f"Unknown or unsupported provider for standard retry: {self._provider}")

      self.model = retry_wrapper.RetryLanguageModel(
          model=base_model,
          retry_on_exceptions=(openai.RateLimitError, openai.APITimeoutError),
          retry_tries=2,
          retry_delay=61,
      )

    # Initialize the sentence embedder
    st_model = sentence_transformers.SentenceTransformer(
        'sentence-transformers/all-mpnet-base-v2'
    )
    self.embedder = lambda x: st_model.encode(x, show_progress_bar=False)

  def test_model(self, test_prompt: str):
    """Sends a sample prompt to the initialized model to test it."""
    if self._provider != 'disabled':
      print(f"\nTesting model with prompt: '{test_prompt}'")
      try:
        response = self.model.sample_text(test_prompt)
        print(f"Model response: {response}")
      except Exception as e:
        print(f"An error occurred while testing the model: {e}")
    else:
      print("Model is disabled, skipping test.")
