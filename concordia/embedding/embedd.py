import sentence_transformers
import numpy as np
import os
import dotenv

dotenv.load_dotenv()

class Embedder:
    def __init__(self, model_name=None):
        if model_name is None:
            model_name = os.getenv('EMBEDDER_MODEL', 'sentence-transformers/all-mpnet-base-v2')
        self.st_model = sentence_transformers.SentenceTransformer(model_name)

    def encode(self, x, *args, **kwargs):
        return self.st_model.encode(x, show_progress_bar=False).flatten()

class DummyEmbedder:
    def encode(self, x, *args, **kwargs):
        return np.ones((1, 3)).flatten()

# Optional: provide a module-level embedder for convenience
get_embedder = Embedder().encode
