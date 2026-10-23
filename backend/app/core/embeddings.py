from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


@lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    """Carga el modelo una sola vez por proceso (la primera vez descarga ~120MB)."""
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
