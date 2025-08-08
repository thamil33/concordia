"""Handles the initialization of the language model and sentence embedder."""

import os
import numpy as np
import sentence_transformers
from dotenv import load_dotenv

from concordia.language_model import gpt_model
from concordia.language_model import openrouter_model
from concordia.language_model import lm_studio_model
from concordia.language_model import no_language_model


class ModelClient:
  """Initializes and holds the language model and sentence embedder."""

  def __init__(self, provider: str | None = None):
    """Initializes the ModelClient.

    This class reads environment variables to configure the correct language
    model provider (e.g., 'openai', 'openrouter', 'lmstudio'). It also
    initializes a sentence embedder unless the language model is disabled.

    Args:
      provider: The model provider to use. If None, it will be read from the
        'MODEL_PROVIDER' environment variable. Valid options are 'openai',
        'openrouter', 'lmstudio', or 'disabled'.

    Raises:
      ValueError: If an unknown provider is specified.
    """
    # Load environment variables from a .env file if it exists.
    load_dotenv()

    if provider is None:
      provider = os.environ.get('MODEL_PROVIDER', 'disabled').lower()

    self.model = None
    self.embedder = None
    self._provider = provider

    if self._provider == 'disabled':
      print("Language model is disabled.")
      self.model = no_language_model.NoLanguageModel()
      # Use a dummy embedder when the model is disabled.
      self.embedder = lambda x: np.ones(3)
      return

    print(f"Initializing model for provider: {self._provider}")

    if self._provider == 'openai':
      model_name = os.environ.get('OPENAI_MODEL_NAME', 'gpt-4')
      self.model = gpt_model.GptLanguageModel(model_name=model_name)
    elif self._provider == 'openrouter':
      self.model = openrouter_model.OpenRouterModel()
    elif self._provider == 'lmstudio':
      self.model = lm_studio_model.LmStudioModel()
    else:
      raise ValueError(f"Unknown model provider: {self._provider}")

    # Initialize the sentence embedder for any active model.
    st_model = sentence_transformers.SentenceTransformer(
        'sentence-transformers/all-mpnet-base-v2'
    )
    self.embedder = lambda x: st_model.encode(x, show_progress_bar=False)


  def test_model(self, test_prompt: str):
    """
    Sends a sample prompt to the initialized model to test it.

    Args:
      test_prompt: The string prompt to send to the model.
    """
    if self._provider != 'disabled':
      print(f"\nTesting model with prompt: '{test_prompt}'")
      try:
        response = self.model.sample_text(test_prompt)
        print(f"Model response: {response}")
      except Exception as e:
        print(f"An error occurred while testing the model: {e}")
    else:
      print("Model is disabled, skipping test.")
