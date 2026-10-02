from __future__ import annotations


class Reranker:
    def __init__(self, model_name: str):
        self.model_name, self._model = model_name, None

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder(self.model_name)
        return self._model

    def rerank(self, query: str, chunks: list[dict], top_k: int) -> list[dict]:
        if not chunks:
            return []
        pairs = [(query, f'{c["title"]}\n{c["text"]}') for c in chunks]
        scores = self.model.predict(pairs)
        order = sorted(range(len(chunks)), key=lambda i: -float(scores[i]))
        return [chunks[i] for i in order[:top_k]]
