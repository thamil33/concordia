import sentence_transformers
import numpy as np
import os
import dotenv

dotenv.load_dotenv()

def set_embedder():
    embedder_env = os.environ.get("EMBEDDER", None) or 'sentence-transformers/all-MiniLM-L6-v2'
    dummy_embedder = os.environ.get("DUMMY_EMBEDDER", None) or False  
    if dummy_embedder:
        # Return a dummy embedder function that always returns 1D
        return lambda x, *args, **kwargs: np.ones((1, 3)).flatten()
    else:
        # You can use embedder_env to select model if desired
        model_name = embedder_env or 'sentence-transformers/all-mpnet-base-v2'
        st_model = sentence_transformers.SentenceTransformer(model_name)
        return lambda x, *args, **kwargs: st_model.encode(x, show_progress_bar=False).flatten()

# Optional: provide a module-level embedder for convenience
get_embedder = set_embedder()