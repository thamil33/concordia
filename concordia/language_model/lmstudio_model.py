"""LMStudio language model client implementation."""

import os
import requests
from collections.abc import Collection, Mapping, Sequence
from typing import Any

from language_model import language_model

class LMStudioLanguageModel(language_model.LanguageModel):
  """Language model implementation that uses the LMStudio local API."""

  def __init__(
    self,
    model_name: str = "default",
    api_key: str | None = None,
    api_base: str | None = None,
  ):
    """Initialize the LMStudio language model client.

    Args:
      model_name: Name of the model loaded in LMStudio, used for logging.
      api_key: API key for LMStudio if required.
      api_base: Base URL for LMStudio API. Defaults to http://localhost:1234/v1
    """
    self._model_name = model_name
    self._api_key = api_key or os.environ.get("LMSTUDIO_API_KEY", "")
    self._api_base = api_base or os.environ.get(
      "LMSTUDIO_API_BASE", "http://localhost:1234/v1"
    )

  def sample_text(
    self,
    prompt: str,
    *,
    max_tokens: int = language_model.DEFAULT_MAX_TOKENS,
    terminators: Collection[str] = language_model.DEFAULT_TERMINATORS,
    temperature: float = language_model.DEFAULT_TEMPERATURE,
    timeout: float = language_model.DEFAULT_TIMEOUT_SECONDS,
    seed: int | None = None,
  ) -> str:
    """Samples text from the LMStudio API.

    Args:
      prompt: The prompt to send to the model.
      max_tokens: Maximum number of tokens to generate.
      terminators: Collection of strings that will terminate generation.
      temperature: Temperature for sampling.
      timeout: Timeout in seconds for the API call.
      seed: Random seed for deterministic sampling.

    Returns:
      Generated text.

    Raises:
      TimeoutError: If the request times out.
    """
    chat_endpoint = f"{self._api_base}/chat/completions"

    headers = {
      "Content-Type": "application/json",
    }

    # Add API key to headers if it exists and is not empty
    if self._api_key:
      headers["Authorization"] = f"Bearer {self._api_key}"

    stop_sequences = list(terminators) if terminators else None

    payload = {
      "model": self._model_name,
      "messages": [{"role": "user", "content": prompt}],
      "temperature": temperature,
      "max_tokens": max_tokens,
    }

    if stop_sequences:
      payload["stop"] = stop_sequences
    if seed is not None:
      payload["seed"] = seed

    try:
      response = requests.post(
        chat_endpoint,
        headers=headers,
        json=payload,
        timeout=timeout
      )
      response.raise_for_status()

      completion = response.json()
      if "choices" in completion and completion["choices"]:
        message = completion["choices"][0].get("message")
        if message and "content" in message:
          return message["content"].strip()

      error_msg = f"Unexpected response format from LMStudio: {completion}"
      raise RuntimeError(error_msg)

    except requests.exceptions.Timeout as e:
      raise TimeoutError(f"LMStudio API request timed out: {e}") from e
    except requests.exceptions.RequestException as e:
      detail = ""
      if hasattr(e, "response") and e.response:
        detail = f" (Status: {e.response.status_code}, Response: {e.response.text})"
      raise RuntimeError(f"Error calling LMStudio API: {e}{detail}") from e

  def sample_choice(
    self,
    prompt: str,
    responses: Sequence[str],
    *,
    seed: int | None = None,
  ) -> tuple[int, str, Mapping[str, Any]]:
    """Samples a response from the available options.

    Args:
      prompt: The prompt to condition on.
      responses: The responses to choose from.
      seed: Random seed for deterministic sampling.

    Returns:
      A tuple of (index, response, info).

    Raises:
      InvalidResponseError: If unable to produce a valid choice.
    """
    if not responses:
      raise language_model.InvalidResponseError("No responses provided")

    # Create a formatted prompt with labeled options
    formatted_prompt = f"{prompt}\n\nChoose one of the following options:\n"
    for i, response in enumerate(responses):
      formatted_prompt += f"{i+1}. {response}\n"
    formatted_prompt += "\nRespond with the number of your choice only."

    try:
      # Lower temperature for more deterministic choice
      result = self.sample_text(
        formatted_prompt,
        max_tokens=10,  # Should be enough for a number
        temperature=0.2,  # Lower temperature for more deterministic choice
        seed=seed
      ).strip()

      # Extract the number from the result
      for i, _ in enumerate(responses):
        if str(i+1) in result:
          return i, responses[i], {"raw_choice_output": result}

      # If we couldn't extract a number, try again with direct matching
      for i, response in enumerate(responses):
        if response.lower() in result.lower():
          return i, response, {"raw_choice_output": result}

      raise language_model.InvalidResponseError(
        f"Could not extract a valid choice from model output: '{result}'"
      )

    except Exception as e:
      raise language_model.InvalidResponseError(
        f"Error while sampling choice: {e}"
      )
