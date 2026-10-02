"""Print the model IDs YOUR key can call. Run this when you get model_not_found."""
import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass
from openai import OpenAI
from atlasrag.config import load_config

cfg = load_config()["llm"]
client = OpenAI(base_url=cfg["base_url"], api_key=os.environ[cfg["api_key_env"]])
ids = sorted(m.id for m in client.models.list().data)
print(f"{len(ids)} models available to this key:")
for i in ids:
    print("  ", i)
print("\nPut your choice in configs/default.yaml (llm.model) or ATLAS_LLM_MODEL in .env.")
print("Skip whisper-*, *-guard*, *-safeguard*, tts/audio models: they are not chat models.")
