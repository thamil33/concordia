"""Language Model that uses OpenRouter's OpenAI-compatible API (Optimized)."""

import os
from collections.abc import Sequence
from typing import Optional

from dotenv import load_dotenv, find_dotenv
import openai

from concordia.language_model import language_model
from concordia.language_model.base_openai_compatible_model import BaseOpenAICompatibleModel
from concordia.utils import measurements as measurements_lib


# --- Environment Setup ---
# Load from .env anywhere in project
load_dotenv(find_dotenv(), override=False)

# Centralized env config with defaults
ENV = {
    "MODEL": os.getenv("OPENROUTER_MODEL"),
    "API_URL": os.getenv("OPENROUTER_API_URL"),
    "API_KEY": os.getenv("OPENROUTER_API_KEY"),
    "XTRA_URL": os.getenv("OPENROUTER_XTRA_URL"),
    "XTRA_TITLE": os.getenv("OPENROUTER_XTRA_TITLE"),
}


def _validate_env():
    """Ensure required environment variables are set."""
    missing = [k for k, v in {"MODEL": ENV["MODEL"], "API_KEY": ENV["API_KEY"]}.items() if not v]
    if missing:
        raise EnvironmentError(
            f"Missing required OpenRouter settings in .env: {', '.join(missing)}"
        )


class OpenRouterLanguageModel(BaseOpenAICompatibleModel):
    """Language Model that uses OpenRouter's OpenAI-compatible models."""

    def __init__(
        self,
        model_name: Optional[str] = ENV["MODEL"],
        api_key: Optional[str] = ENV["API_KEY"],
        base_url: Optional[str] = ENV["API_URL"],
        http_referer: Optional[str] = ENV["XTRA_URL"],
        x_title: Optional[str] = ENV["XTRA_TITLE"],
        measurements: Optional[measurements_lib.Measurements] = None,
        channel: str = language_model.DEFAULT_STATS_CHANNEL,
        system_prompt: Optional[str] = None,
        max_tokens: int = language_model.DEFAULT_MAX_TOKENS,
    ):
        """Initializes the instance."""
        _validate_env()

        custom_headers = {
            k: v for k, v in {
                "HTTP-Referer": http_referer,
                "X-Title": x_title
            }.items() if v
        }

        try:
            client = openai.OpenAI(
                api_key=api_key,
                base_url=base_url,
                default_headers=custom_headers,
            )
        except Exception as e:
            raise ConnectionError(f"Failed to initialize OpenRouter client: {e}") from e

        super().__init__(
            model_name=model_name,
            client=client,
            measurements=measurements,
            channel=channel,
            system_prompt=system_prompt,

            max_tokens=max_tokens,
        )
