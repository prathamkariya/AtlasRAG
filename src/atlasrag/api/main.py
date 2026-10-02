from __future__ import annotations
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .. import __version__
from ..config import load_config, resolve
from ..pipeline import Pipeline
from ..routers import build_router, AVAILABLE_NOW

_state: dict = {"pipeline": None, "cfg": None, "llm": None, "notes": []}
_lock = threading.Lock()   # answer() diffs shared LLM counters; keep it single-flight


@asynccontextmanager
async def lifespan(app: FastAPI):
    cfg = load_config()
    _state["cfg"] = cfg
    try:
        from ..retrieval.index import Index
        from ..retrieval.embedder import Embedder
        from ..retrieval.reranker import Reranker
        from ..llm import LLMClient
        index = Index.load(resolve(cfg["retrieval"]["index_dir"]))
        llm = LLMClient(cfg["llm"], cache_root=resolve(cfg["llm"]["cache_dir"]))
        _state["llm"] = llm
        _state["pipeline"] = Pipeline(
            cfg, index,
            Embedder(cfg["embedding"]["model"], cfg["embedding"]["query_prefix"]),
            llm, Reranker(cfg["reranker"]["model"]))
    except FileNotFoundError:
        _state["notes"].append("index not built yet: run `make fetch && make index`")
    except RuntimeError as e:
        _state["notes"].append(str(e))
    yield


app = FastAPI(title="AtlasRAG", version=__version__, lifespan=lifespan)


class AskRequest(BaseModel):
    question: str
    router: str = "static"


@app.get("/health")
def health():
    return {"status": "ok", "version": __version__,
            "pipeline_ready": _state["pipeline"] is not None, "notes": _state["notes"]}


@app.get("/routers")
def routers():
    return {"available": AVAILABLE_NOW, "coming": ["compass (week 3)", "oracle (needs gold labels)"]}


@app.post("/ask")
def ask(req: AskRequest):
    if _state["pipeline"] is None:
        raise HTTPException(503, detail=_state["notes"] or "pipeline not ready")
    if req.router not in AVAILABLE_NOW:
        raise HTTPException(400, detail=f"router must be one of {AVAILABLE_NOW}")
    router = build_router(req.router, _state["cfg"], llm=_state["llm"])
    with _lock:
        return _state["pipeline"].answer(req.question, router)
