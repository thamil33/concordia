"""Language Model that uses OpenRouter's OpenAI-compatible API (Hardened)."""

import os
from collections.abc import Sequence
from typing import Optional

from dotenv import load_dotenv, find_dotenv
import openai

from concordia.language_model import language_model
from concordia.utils import measurements as measurements_lib


# --- Environment Setup ---
# Automatically find and load the closest .env file
load_dotenv(find_dotenv(), override=False)

# Centralized env config
ENV = {
    "MODEL": os.getenv("OPENROUTER_MODEL"),
    "API_URL": os.getenv("OPENROUTER_API_URL"),
    "API_KEY": os.getenv("OPENROUTER_API_KEY"),
    "XTRA_URL": os.getenv("OPENROUTER_XTRA_URL"),
    "XTRA_TITLE": os.getenv("OPENROUTER_XTRA_TITLE"),
}


def _validate_env():
    """Ensure required environment variables are set before continuing."""
    missing = [
        name for name in ("MODEL", "API_KEY")
        if not ENV.get(name)
    ]
    if missing:
        raise EnvironmentError(
            f"Missing required OpenRouter settings in .env: {', '.join(missing)}"
        )
class BaseOpenAICompatibleModel:
    """Language Model that uses OpenRouter's OpenAI-compatible models, with safer initialization."""

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
        """Initializes the instance with hardened configuration checks."""
        _validate_env()

        # Allow runtime overrides without mutating ENV
        self._model_name = model_name or ENV["MODEL"]
        self._api_key = api_key or ENV["API_KEY"]
        self._base_url = base_url or ENV["API_URL"]

        custom_headers = {
            k: v for k, v in {
                "HTTP-Referer": http_referer or ENV["XTRA_URL"],
                "X-Title": x_title or ENV["XTRA_TITLE"]
            }.items() if v
        }

        try:
            client = openai.OpenAI(
                api_key=self._api_key,
                base_url=self._base_url,
                default_headers=custom_headers,
            )
        except Exception as e:
            raise ConnectionError(f"Failed to initialize OpenRouter client: {e}") from e

        super().__init__(
            model_name=self._model_name,
            client=client,
            measurements=measurements,
            channel=channel,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
        )

    # Optional: Provider-specific override for sample_text to add extra logging
    def sample_text(self, *args, **kwargs) -> str:
        try:
            return super().sample_text(*args, **kwargs)
        except Exception as e:
            if self._measurements is not None:
                self._measurements.publish_datum(
                    self._channel,
                    {"provider": "openrouter", "error": str(e)}
                )
            return ""  # Fail quietly to avoid breaking simulation loop

    # Optional: Provider-specific override for sample_choice
    def sample_choice(self, *args, **kwargs):
        try:
            return super().sample_choice(*args, **kwargs)
        except Exception as e:
            if self._measurements is not None:
                self._measurements.publish_datum(
                    self._channel,
                    {"provider": "openrouter", "choice_error": str(e)}
                )
            # Return a safe default instead of raising if needed
            return -1, "", {}
