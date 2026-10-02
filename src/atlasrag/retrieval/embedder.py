from __future__ import annotations
import numpy as np


class Embedder:
    def __init__(self, model_name: str, query_prefix: str = ""):
        self.model_name, self.query_prefix, self._model = model_name, query_prefix, None

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def encode_docs(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        return self.model.encode(texts, batch_size=batch_size, normalize_embeddings=True,
                                 show_progress_bar=True).astype("float32")

    def encode_query(self, q: str) -> np.ndarray:
        return self.model.encode([self.query_prefix + q],
                                 normalize_embeddings=True)[0].astype("float32")
