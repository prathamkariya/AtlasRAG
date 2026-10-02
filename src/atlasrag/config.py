from __future__ import annotations
import os
from pathlib import Path
import yaml
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]


def load_config(path: str | Path | None = None) -> dict:
    path = Path(path or os.getenv("ATLAS_CONFIG") or ROOT / "configs" / "default.yaml")
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if os.getenv("ATLAS_LLM_MODEL"):
        cfg["llm"]["model"] = os.environ["ATLAS_LLM_MODEL"]
    if os.getenv("ATLAS_CACHE_NAMESPACE"):
        cfg["llm"]["cache_namespace"] = os.environ["ATLAS_CACHE_NAMESPACE"]
    return cfg


def resolve(p: str | Path) -> Path:
    p = Path(p)
    return p if p.is_absolute() else ROOT / p
