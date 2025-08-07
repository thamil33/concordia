"""Utilities for loading language models."""

from concordia.language_model import amazon_bedrock_model
from concordia.language_model import google_aistudio_model
from concordia.language_model import google_cloud_custom_model
from concordia.language_model import gpt_model
from concordia.language_model import langchain_ollama_model
from concordia.language_model import language_model
from concordia.language_model import mistral_model
from concordia.language_model import no_language_model
from concordia.language_model import ollama_model
from concordia.language_model import \
    openrouter_model  # Added OpenRouter import
from concordia.language_model import pytorch_gemma_model
from concordia.language_model import together_ai


def language_model_setup(
    *,
    api_type: str,
    model_name: str,
    api_key: str | None = None,
    base_url: str | None = None,
    http_referer: str | None = None,
    x_title: str | None = None,
    device: str | None = None,
    disable_language_model: bool = False,
) -> language_model.LanguageModel:
  """Get the wrapped language model.

  Args:
    api_type: The type of API to use.
    model_name: The name of the specific model to use.
    api_key: The API key to use (if supported).
    base_url: The base URL for the API (if supported).
    http_referer: The HTTP referer for OpenRouter (if supported).
    x_title: The X-Title for OpenRouter (if supported).
    device: The device to use for model processing (if supported).
    disable_language_model: If True then disable the language model.

  Returns:
    The wrapped language model.
  """
  if disable_language_model:
    return no_language_model.NoLanguageModel()

  # A dictionary to hold the arguments for the model class
  kwargs = {'model_name': model_name}

  # A mapping from api_type to the corresponding model class
  api_to_class = {
      'amazon_bedrock': amazon_bedrock_model.AmazonBedrockLanguageModel,
      'google_aistudio_model': google_aistudio_model.GoogleAIStudioLanguageModel,
      'google_cloud_custom_model': google_cloud_custom_model.VertexAI,
      'langchain_ollama': langchain_ollama_model.LangchainOllamaLanguageModel,
      'mistral': mistral_model.MistralLanguageModel,
      'ollama': ollama_model.OllamaLanguageModel,
      'openai': gpt_model.GptLanguageModel,
      'openrouter': openrouter_model.OpenRouterLanguageModel,  # Added OpenRouter
      'pytorch_gemma': pytorch_gemma_model.PyTorchGemmaLanguageModel,
      'together_ai': together_ai.Gemma2,
  }

  if api_type not in api_to_class:
    raise ValueError(f'Unrecognized api type: {api_type}')

  cls = api_to_class[api_type]

  # Add arguments based on the selected API type
  if api_key is not None:
    kwargs['api_key'] = api_key
  if device is not None and api_type in ['pytorch_gemma']:
    kwargs['device'] = device
  if base_url is not None and api_type == 'openrouter':
      kwargs['base_url'] = base_url
  if http_referer is not None and api_type == 'openrouter':
      kwargs['http_referer'] = http_referer
  if x_title is not None and api_type == 'openrouter':
      kwargs['x_title'] = x_title

  return cls(**kwargs)
