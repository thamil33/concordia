# 0.0.1 - My Concordia Fork (PyScrAI)

## Changed

## Added

### New API Integrations

#### - **OpenRouter API Implementation**
  - Added `concordia\language_model\openrouter_model.py` for direct integration
     with the OpenRouter API.
  - Supports both free-form text and multiple choice via HTTP requests.
  - Reads API key and endpoint from environment variables or arguments.
  - Handles timeouts, error reporting, and response parsing.

#### - **LMStudio API Implementation**
  - Added `concordia\language_model\lmstudio_model.py` for integration with
    the LMStudio local API.
  - Communicates with LMStudio via HTTP (default: `http://localhost:1234/v1`).
  - Supports both text and multiple choice via prompt formatting.
  - Reads API key and base URL from environment variables if not provided.
  - Handles timeouts and error reporting.

#### - **_llm_interface.py Implementation**

  - Added `_llm_interface.py` to provide a unified interface for setting up and
  testing multiple LLM backends (OpenRouter, LMStudio, and SentenceTransformer
  embedder) with robust error handling and environment variable support.



## Fixed
