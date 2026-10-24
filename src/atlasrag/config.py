from __future__ import annotations
import os
from pathlib import Path
import yaml
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]


def load_config(path: str | Path | None = None) -> dict:
    configured = path or os.getenv("ATLAS_CONFIG") or ROOT / "configs" / "default.yaml"
    config_path = Path(configured)
    if not config_path.is_absolute():
        config_path = ROOT / config_path
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if not isinstance(cfg, dict) or not isinstance(cfg.get("llm"), dict):
        raise ValueError(f"invalid AtlasRAG config structure in {config_path}: expected an 'llm' mapping")
    if os.getenv("ATLAS_LLM_MODEL"):
        cfg["llm"]["model"] = os.environ["ATLAS_LLM_MODEL"]
    if os.getenv("ATLAS_CACHE_NAMESPACE"):
        cfg["llm"]["cache_namespace"] = os.environ["ATLAS_CACHE_NAMESPACE"]
    return cfg


def resolve(p: str | Path) -> Path:
    p = Path(p)
    return p if p.is_absolute() else ROOT / p
