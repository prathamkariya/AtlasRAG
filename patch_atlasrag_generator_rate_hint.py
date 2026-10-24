from pathlib import Path
import re

path = Path("src/atlasrag/bench/generate_v2.py")
if not path.is_file():
    raise SystemExit("ERROR: Run this from the AtlasRAG repository root.")

source = path.read_text(encoding="utf-8")
backup = path.with_name("generate_v2.py.before_rate_limit_hint_log.bak")
if not backup.exists():
    backup.write_text(source, encoding="utf-8")

# Expose the preserved exception text to the parent automation process.
# The generator intentionally handles the exception and returns None, so without
# this message the outer runner cannot see a provider retry hint.
pattern = re.compile(r"except LLMRateLimitExceeded:\s*\n(\s*)self\.vstats\[\"rate_limited\"\] \+= 1")
source_new, count = pattern.subn(
    'except LLMRateLimitExceeded as exc:\n\\1print(f"[rate limit detail] {exc}")\n\\1self.vstats["rate_limited"] += 1',
    source,
)

if count == 0:
    raise SystemExit(
        "ERROR: No matching LLMRateLimitExceeded handlers found. No changes made; "
        "inspect generate_v2.py because its structure differs."
    )

path.write_text(source_new, encoding="utf-8")
print(f"Patched {count} rate-limit handlers in {path}.")
print(f"Backup: {backup}")
print("Run tests: pytest tests/test_bench_v2.py tests/test_gen_script.py -q")
