from concordia.language_model import utils
import numpy as np
import sentence_transformers
import os # Added for os.getenv in fallback for model names

# For local development, you might need to load environment variables from a .env file.
# If so, install python-dotenv (pip install python-dotenv) and uncomment:
from dotenv import load_dotenv
load_dotenv()

# To debug without spending money on API calls, set DISABLE_LANGUAGE_MODEL=True
# Set to False to attempt to use real LLMs and SentenceTransformer
DISABLE_LANGUAGE_MODEL = False

# Individual setup functions for each model client
def setup_openrouter_primary():
    global openrouter_llm
    # OpenRouter LLM (Primary)
    try:
        print("\nInstantiating OpenRouter LLM (Primary)...")
        openrouter_llm = utils.language_model_setup(
            api_type='openrouter',
            disable_language_model=DISABLE_LANGUAGE_MODEL
        )
        model_name_or = getattr(openrouter_llm, '_model_name', 'NoLanguageModel (or model name not set)')
        if isinstance(openrouter_llm, utils.no_language_model.NoLanguageModel):
            print(f"OpenRouter LLM (Primary) is NoLanguageModel (DISABLE_LANGUAGE_MODEL: {DISABLE_LANGUAGE_MODEL}).")
        else:
            print(f"Successfully instantiated OpenRouter model (Primary): {model_name_or}")
    except ValueError as e:
        print(f"Configuration error for OpenRouter LLM (Primary): {e}")
        print("  Falling back to NoLanguageModel for OpenRouter LLM (Primary).")
        openrouter_llm = utils.language_model_setup(api_type='openrouter', disable_language_model=True)
    except Exception as e:
        print(f"An unexpected error occurred with OpenRouter LLM (Primary) setup: {e}")
        print("  Falling back to NoLanguageModel for OpenRouter LLM (Primary).")
        openrouter_llm = utils.language_model_setup(api_type='openrouter', disable_language_model=True)
    return openrouter_llm

def setup_openrouter_secondary():
    global openrouter_secondary_llm
    # OpenRouter_Secondary LLM
    try:
        print("\nInstantiating OpenRouter LLM (Secondary)...")
        openrouter_secondary_llm = utils.language_model_setup(
            api_type='openrouter_secondary', # Renamed from openrouter_orchestrator
            disable_language_model=DISABLE_LANGUAGE_MODEL
        )
        model_secondary_name_or = getattr(openrouter_secondary_llm, '_model_name', 'NoLanguageModel (or model name not set)')
        if isinstance(openrouter_secondary_llm, utils.no_language_model.NoLanguageModel):
            print(f"OpenRouter LLM (Secondary) is NoLanguageModel (DISABLE_LANGUAGE_MODEL: {DISABLE_LANGUAGE_MODEL}).")
        else:
            print(f"Successfully instantiated OpenRouter model (Secondary): {model_secondary_name_or}")
    except ValueError as e:
        print(f"Configuration error for OpenRouter LLM (Secondary): {e}")
        print("  Falling back to NoLanguageModel for OpenRouter LLM (Secondary).")
        openrouter_secondary_llm = utils.language_model_setup(api_type='openrouter_secondary', disable_language_model=True)
    except Exception as e:
        print(f"An unexpected error occurred with OpenRouter LLM (Secondary) setup: {e}")
        print("  Falling back to NoLanguageModel for OpenRouter LLM (Secondary).")
        openrouter_secondary_llm = utils.language_model_setup(api_type='openrouter_secondary', disable_language_model=True)
    return openrouter_secondary_llm

def setup_lmstudio_primary():
    global lmstudio_llm
    # LMStudio LLM (Primary)
    try:
        print("\nInstantiating LMStudio LLM (Primary)...")
        lmstudio_llm = utils.language_model_setup(
            api_type='lmstudio',
            disable_language_model=DISABLE_LANGUAGE_MODEL
        )
        model_name_lms = getattr(lmstudio_llm, '_model_name', 'NoLanguageModel (or model name not set)')
        if isinstance(lmstudio_llm, utils.no_language_model.NoLanguageModel):
            print(f"LMStudio LLM (Primary) is NoLanguageModel (DISABLE_LANGUAGE_MODEL: {DISABLE_LANGUAGE_MODEL}).")
        else:
            print(f"Successfully instantiated LMStudio model (Primary): {model_name_lms}")
    except ValueError as e:
        print(f"Configuration error for LMStudio LLM (Primary): {e}")
        print("  Falling back to NoLanguageModel for LMStudio LLM (Primary).")
        lmstudio_llm = utils.language_model_setup(api_type='lmstudio', disable_language_model=True)
    except Exception as e:
        print(f"An unexpected error occurred with LMStudio LLM (Primary) setup: {e}")
        print("  Falling back to NoLanguageModel for LMStudio LLM (Primary).")
        lmstudio_llm = utils.language_model_setup(api_type='lmstudio', disable_language_model=True)
    return lmstudio_llm

def setup_lmstudio_secondary():
    global lmstudio_secondary_llm
    # LMStudio_Secondary LLM
    try:
        print("\nInstantiating LMStudio LLM (Secondary)...")
        lmstudio_secondary_llm = utils.language_model_setup(
            api_type='lmstudio_secondary', # Renamed from lmstudio_orchestrator
            disable_language_model=DISABLE_LANGUAGE_MODEL
        )
        model_name_lms_secondary = getattr(lmstudio_secondary_llm, '_model_name', 'NoLanguageModel (or model name not set)')
        if isinstance(lmstudio_secondary_llm, utils.no_language_model.NoLanguageModel):
            print(f"LMStudio LLM (Secondary) is NoLanguageModel (DISABLE_LANGUAGE_MODEL: {DISABLE_LANGUAGE_MODEL}).")
        else:
            print(f"Successfully instantiated LMStudio model (Secondary): {model_name_lms_secondary}")
    except ValueError as e:
        print(f"Configuration error for LMStudio LLM (Secondary): {e}")
        print("  Falling back to NoLanguageModel for LMStudio LLM (Secondary).")
        lmstudio_secondary_llm = utils.language_model_setup(api_type='lmstudio_secondary', disable_language_model=True)
    except Exception as e:
        print(f"An unexpected error occurred with LMStudio LLM (Secondary) setup: {e}")
        print("  Falling back to NoLanguageModel for LMStudio LLM (Secondary).")
        lmstudio_secondary_llm = utils.language_model_setup(api_type='lmstudio_secondary', disable_language_model=True)
    return lmstudio_secondary_llm

def setup_embedder():
    global embedder
    # Embedder Setup
    if DISABLE_LANGUAGE_MODEL:
        print("\nUsing dummy embedder as DISABLE_LANGUAGE_MODEL is True.")
        embedder = lambda _: np.ones(3) # Dummy embedder
    else:
        print("\nInstantiating SentenceTransformer model...")
        try:
            # Consider making the model name an environment variable too for flexibility
            st_model_name = os.getenv("SENTENCE_TRANSFORMER_MODEL", 'sentence-transformers/all-mpnet-base-v2')
            st_model = sentence_transformers.SentenceTransformer(st_model_name)
            embedder = lambda x: st_model.encode(x, show_progress_bar=False) # Disabled progress bar for cleaner output
            print(f"Successfully instantiated SentenceTransformer model: {st_model_name}")
        except Exception as e:
            print(f"Error instantiating SentenceTransformer: {e}. Using dummy embedder as fallback.")
            embedder = lambda _: np.ones(3)
    return embedder

def run_group_llm():
    print(f"DISABLE_LANGUAGE_MODEL is set to: {DISABLE_LANGUAGE_MODEL}")

    # Setup each model individually
    embedder = setup_embedder()
    openrouter_llm = setup_openrouter_primary()
    openrouter_secondary_llm = setup_openrouter_secondary()
    lmstudio_llm = setup_lmstudio_primary()
    lmstudio_secondary_llm = setup_lmstudio_secondary()

    # Example usage for each model
    print("\n--- Testing OpenRouter LLM (Primary) ---")
    try:
        prompt_or = "Tell me your funniest short joke about AI."
        print(f"Sending prompt to OpenRouter (Primary): '{prompt_or}'")
        or_response = openrouter_llm.sample_text(prompt_or)
        print(f"OpenRouter Response (Primary): '{or_response}'")
    except Exception as e:
        print(f"Error sampling from OpenRouter LLM (Primary): {e}")

    print("\n--- Testing OpenRouter LLM (Secondary) ---")
    try:
        prompt_or_secondary = "Who or what are you?"
        print(f"Sending prompt to OpenRouter (Secondary): '{prompt_or_secondary}'")
        or_secondary_response = openrouter_secondary_llm.sample_text(prompt_or_secondary)
        print(f"OpenRouter Response (Secondary): '{or_secondary_response}'")
    except Exception as e:
        print(f"Error sampling from OpenRouter LLM (Secondary): {e}")

    print("\n--- Testing LMStudio LLM (Primary) ---")
    try:
        prompt_lms = "What is the largest mammal in the world?"
        print(f"Sending prompt to LMStudio (Primary): '{prompt_lms}'")
        lms_response = lmstudio_llm.sample_text(prompt_lms)
        print(f"LMStudio Response (Primary): '{lms_response}'")
    except Exception as e:
        print(f"Error sampling from LMStudio LLM (Primary): {e}")

    print("\n--- Testing LMStudio LLM (Secondary) ---")
    try:
        prompt_lms_secondary = "What is the capital of New Mexico?"
        print(f"Sending prompt to LMStudio (Secondary): '{prompt_lms_secondary}'")
        lms_secondary_response = lmstudio_secondary_llm.sample_text(prompt_lms_secondary)
        print(f"LMStudio Response (Secondary): '{lms_secondary_response}'")
    except Exception as e:
        print(f"Error sampling from LMStudio LLM (Secondary): {e}")

    print("\n--- Testing Embedder ---")
    try:
        sample_text_for_embedding = "This is a test sentence for the embedder."
        print(f"Getting embedding for: '{sample_text_for_embedding}'")
        embedding_vector = embedder(sample_text_for_embedding)
        # Check if it's a numpy array and print shape or first few dims
        if hasattr(embedding_vector, 'shape'):
            print(f"Embedding vector shape: {embedding_vector.shape}. First 5 dims: {embedding_vector[:5]}")
        else:
            print(f"Embedding vector: {embedding_vector}") # Fallback for non-numpy
        if DISABLE_LANGUAGE_MODEL:
            # Basic check for the dummy embedder
            if np.array_equal(embedding_vector, np.ones(3)):
                print("Dummy embedder produced expected output.")
            else:
                print("Warning: Dummy embedder output mismatch.")

    except Exception as e:
        print(f"Error using embedder: {e}")

    print("\nFinished LLM instantiation and testing attempts.")

if __name__ == "__main__":
    run_group_llm()
    print("\nFinished LLM instantiation and testing attempts.")
