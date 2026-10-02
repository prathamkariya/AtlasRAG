"""Run `python scripts/check_env.py` (add --ping for a 1-token LLM call)."""
import importlib, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

ok = True
def line(good, msg):
    global ok
    ok &= good
    print(("[ok]   " if good else "[FAIL] ") + msg)

line(sys.version_info >= (3, 10), f"python {sys.version.split()[0]} (need >= 3.10)")
for mod in ["numpy", "yaml", "rank_bm25", "sentence_transformers", "pymupdf", "arxiv",
            "openai", "fastapi", "wandb"]:
    try:
        importlib.import_module(mod); line(True, f"import {mod}")
    except Exception as e:
        line(False, f"import {mod}: {e}")
line(bool(os.getenv("GROQ_API_KEY")), "GROQ_API_KEY set")
print("[info] WANDB_API_KEY", "set" if os.getenv("WANDB_API_KEY") else "not set (tracking will run disabled)")

if "--ping" in sys.argv and os.getenv("GROQ_API_KEY"):
    from atlasrag.config import load_config
    from atlasrag.llm import LLMClient
    cfg = load_config()
    try:
        out = LLMClient(cfg["llm"]).chat([{"role": "user", "content": "Reply with the word ready."}], max_tokens=5)
        line(True, f"LLM ping ({cfg['llm']['model']}): {out.strip()!r}")
    except Exception as e:
        line(False, f"LLM ping failed: {e}")
        if "model_not_found" in str(e) or "404" in str(e):
            print("       -> run: python scripts/list_models.py   (then set llm.model or ATLAS_LLM_MODEL)")
sys.exit(0 if ok else 1)
