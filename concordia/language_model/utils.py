"""Utilities for loading language models."""

import os
from concordia.language_model import language_model
from concordia.language_model import lmstudio_model
from concordia.language_model import no_language_model
from concordia.language_model import ollama_model
from concordia.language_model import openrouter_model
from concordia.language_model import pytorch_gemma_model


def language_model_setup(
    *,
    api_type: str,
    model_name: str | None = None,
    api_key: str | None = None,
    api_base: str | None = None,  # Added to allow explicit api_base override
    device: str | None = None,
    disable_language_model: bool = False,
) -> language_model.LanguageModel:
  """Get the wrapped language model.

  Args:
    api_type: The type of API to use.
    model_name: The name of the specific model to use. If None, will be retrieved
      from environment variables based on api_type.
    api_key: The API key to use (if supported). If None, will be retrieved
      from environment variables based on api_type.
    api_base: The base URL for the API (if supported). Allows explicit override
      of the default or environment variable-based URL.
    device: The device to use for model processing (if supported).
    disable_language_model: If True then disable the language model.
      This uses a model that returns an empty string whenever asked for a free
      text response and a randome option when asked for a choice.

  Returns:
    The wrapped language model.
  """
  if disable_language_model:
    return no_language_model.NoLanguageModel()

  # Get model_name from environment variables if not provided
  if model_name is None:
    if api_type == 'openrouter':
      model_name = os.getenv("OPENROUTER_MODEL_NAME")
      if not model_name:
        raise ValueError("OPENROUTER_MODEL_NAME environment variable not set")
    elif api_type == 'openrouter_secondary':  # Renamed from openrouter_orchestrator
      model_name = os.getenv("OPENROUTER_SECONDARY_MODEL_NAME")  # Renamed from OPENROUTER_ORCHESTRATOR_MODEL_NAME
      if not model_name:
        raise ValueError("OPENROUTER_SECONDARY_MODEL_NAME environment variable not set")
    elif api_type == 'lmstudio':
      model_name = os.getenv("LMSTUDIO_MODEL_NAME")
      if not model_name:
        raise ValueError("LMSTUDIO_MODEL_NAME environment variable not set")
    elif api_type == 'lmstudio_secondary':  # Renamed from lmstudio_orchestrator
      model_name = os.getenv("LMSTUDIO_SECONDARY_MODEL_NAME")  # Renamed from LMSTUDIO_ORCHESTRATOR_MODEL_NAME
      if not model_name:
        raise ValueError("LMSTUDIO_SECONDARY_MODEL_NAME environment variable not set")
    else:
      env_var = f"{api_type.upper()}_MODEL_NAME"
      model_name = os.getenv(env_var)
      if not model_name:
        raise ValueError(f"{env_var} environment variable not set")

  # Get API key from environment variables if not provided
  if api_key is None:
    if api_type in ('openrouter', 'openrouter_secondary'):  # Renamed from openrouter_orchestrator
      api_key = os.getenv("OPENROUTER_API_KEY")
      if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")
    elif api_type in ('lmstudio', 'lmstudio_secondary'):  # Renamed from lmstudio_orchestrator
      api_key = os.getenv("LMSTUDIO_API_KEY", "")
    # Add similar logic for other providers that need API keys

  kwargs = {'model_name': model_name}
  if api_key is not None:
    kwargs['api_key'] = api_key

  # Handle api_base explicitly if provided, otherwise let model constructors handle defaults/env vars
  if api_base is not None:
    kwargs['api_base'] = api_base
  else:  # If api_base is not directly passed to this function, check for orchestrator-specific env var
    if api_type == 'lmstudio_secondary':  # Renamed from lmstudio_orchestrator
      secondary_api_base = os.getenv("LMSTUDIO_SECONDARY_API_BASE")  # Renamed from LMSTUDIO_ORCHESTRATOR_API_BASE
      if secondary_api_base:
        kwargs['api_base'] = secondary_api_base
    elif api_type == 'openrouter_secondary':  # Added for consistency, though OpenRouter model handles its own base URL env var
        secondary_api_base = os.getenv("OPENROUTER_SECONDARY_API_BASE")  # New optional env var if needed
        if secondary_api_base:
            kwargs['api_base'] = secondary_api_base

  if device is not None:
    kwargs['device'] = device

  if api_type == 'lmstudio' or api_type == 'lmstudio_secondary':  # Renamed
    cls = lmstudio_model.LMStudioLanguageModel
  elif api_type == 'ollama':
    cls = ollama_model.OllamaLanguageModel
  elif api_type == 'openrouter' or api_type == 'openrouter_secondary':  # Renamed
    cls = openrouter_model.OpenRouterLanguageModel
  elif api_type == 'pytorch_gemma':
    cls = pytorch_gemma_model.PyTorchGemmaLanguageModel
  else:
    raise ValueError(f'Unrecognized api type: {api_type}')

  return cls(**kwargs)  # pytype: disable=wrong-keyword-args
