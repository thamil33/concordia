import sentence_transformers
import numpy as np
import os
import dotenv

dotenv.load_dotenv()

def get_embedder():
    embedder_env = os.environ.get("EMBEDDER", None) or 'sentence-transformers/all-MiniLM-L6-v2'
    dummy_embedder = os.environ.get("DUMMY_EMBEDDER", None) or False  
    if dummy_embedder:
        # Return a dummy embedder function
        return lambda x: np.ones((1, 3))
    else:
        # You can use embedder_env to select model if desired
        model_name = embedder_env or 'sentence-transformers/all-mpnet-base-v2'
        st_model = sentence_transformers.SentenceTransformer(model_name)
        return lambda x: st_model.encode(x, show_progress_bar=False)

# Optional: provide a module-level embedder for convenience
embedder = get_embedder()