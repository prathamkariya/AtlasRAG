"""Weights & Biases wrapper. Falls back to disabled mode if no key is set,
so nothing breaks on a fresh clone."""
from __future__ import annotations
import os


def init_run(cfg: dict, name: str, config: dict | None = None):
    try:
        import wandb
    except ImportError:
        return None
    mode = "online" if os.getenv("WANDB_API_KEY") else "disabled"
    return wandb.init(project=cfg["tracking"]["project"], name=name,
                      config=config or cfg, mode=mode)
