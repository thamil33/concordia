# A simple test of the sentence-transformers package and embedding model
from sentence_transformers import SentenceTransformer
import numpy as np
import os 
import dotenv

dotenv.load_dotenv()

DISABLE_LANGUAGE_MODEL = os.environ.get("DISABLE_LANGUAGE_MODEL", None)
embedder = os.environ.get("EMBEDDER", None)

def test_embedding():
    model = SentenceTransformer(embedder)
    sentences = ["This is a test sentence."]
    embeddings = model.encode(sentences)
    print("Embedding shape:", embeddings.shape)
    # Optionally, check the shape
    assert embeddings.shape in [(1, 384), (1, 768)], f"Unexpected embedding shape: {embeddings.shape}"


if __name__ == "__main__":
    test_embedding()
