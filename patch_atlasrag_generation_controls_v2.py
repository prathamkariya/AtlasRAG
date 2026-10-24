from pathlib import Path
import sys

PATCHES = {
    "src/atlasrag/llm.py": [
        ("""    def _key(self, model, messages, temperature, max_tokens) -> str:
        blob = json.dumps([model, messages, temperature, max_tokens, self.reasoning_effort], sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()
""", """    def _key(self, model, messages, temperature, max_tokens, reasoning_effort=None, token_headroom=None) -> str:
        blob = json.dumps([model, messages, temperature, max_tokens, reasoning_effort, token_headroom], sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()
"""),
        ("""    def chat(self, messages: list[dict], temperature: float = 0.0,
             max_tokens: int = 700, model: str | None = None) -> str:
        model = model or self.model
        self.stats["calls"] += 1
""", """    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.0,
        max_tokens: int = 700,
        model: str | None = None,
        reasoning_effort: str | None = None,
        token_headroom: int | None = None,
    ) -> str:
        model = model or self.model
        effort = reasoning_effort if reasoning_effort is not None else self.reasoning_effort
        headroom = token_headroom if token_headroom is not None else self.headroom
        self.stats["calls"] += 1
"""),
        ('''            path = self.cache_dir / f"{self._key(model, messages, temperature, max_tokens)}.json"
''', '''            path = self.cache_dir / f"{self._key(model, messages, temperature, max_tokens, effort, headroom)}.json"
'''),
        ('''            if self.reasoning_effort:
                kwargs["extra_body"] = {"reasoning_effort": self.reasoning_effort}
''', '''            if effort:
                kwargs["extra_body"] = {"reasoning_effort": effort}
'''),
        ('''                    max_tokens=max_tokens + self.headroom, **kwargs)
''', '''                    max_tokens=max_tokens + headroom, **kwargs)
'''),
    ],
    "src/atlasrag/bench/generate.py": [
        ('''        out = self.llm.chat([{"role": "system", "content": COMMON + " " + task},
                             {"role": "user", "content": body}],
                            temperature=0.3, max_tokens=300, model=self.model)
''', '''        call_options = {}
        effort = getattr(self, "generation_reasoning_effort", None)
        headroom = getattr(self, "generation_token_headroom", None)
        if effort is not None:
            call_options["reasoning_effort"] = effort
        if headroom is not None:
            call_options["token_headroom"] = headroom
        out = self.llm.chat([{"role": "system", "content": COMMON + " " + task},
                             {"role": "user", "content": body}],
                            temperature=0.3, max_tokens=300, model=self.model,
                            **call_options)
'''),
    ],
    "src/atlasrag/bench/generate_v2.py": [
        ('''                temperature=0.2,
                max_tokens=450,
                model=self.model,
            )
''', '''                temperature=0.2,
                max_tokens=1200,
                model=self.model,
                **({"reasoning_effort": self.generation_reasoning_effort}
                   if getattr(self, "generation_reasoning_effort", None) is not None else {}),
                **({"token_headroom": self.generation_token_headroom}
                   if getattr(self, "generation_token_headroom", None) is not None else {}),
            )
'''),
    ],
    "scripts/gen_questions_v2.py": [
        ('''ap.add_argument("--judge-model", help="support-audit model; use a DIFFERENT one than --model")
ap.add_argument("--max-provider-tokens", type=int, default=0,
''', '''ap.add_argument("--judge-model", help="support-audit model; use a DIFFERENT one than --model")
ap.add_argument("--generation-reasoning-effort", choices=["low", "medium", "high"], default=None,
                help="override reasoning effort for generation calls only")
ap.add_argument("--generation-token-headroom", type=int, default=None,
                help="extra completion-token allowance for generation calls only")
ap.add_argument("--max-provider-tokens", type=int, default=0,
'''),
        ('''gen = ValidatedGenerator(Index.load(resolve(cfg["retrieval"]["index_dir"])), llm,
                          load_meta(resolve(cfg["corpus"]["raw_dir"])), seed=seed_used, model=a.model, judge_model=a.judge_model)

per_type, stopped, t0, error = {}, None, time.time(), None
''', '''gen = ValidatedGenerator(Index.load(resolve(cfg["retrieval"]["index_dir"])), llm,
                          load_meta(resolve(cfg["corpus"]["raw_dir"])), seed=seed_used, model=a.model, judge_model=a.judge_model)
gen.generation_reasoning_effort = a.generation_reasoning_effort
gen.generation_token_headroom = a.generation_token_headroom

per_type, stopped, t0, error = {}, None, time.time(), None
'''),
    ],
}

def patch_llm(text: str) -> str:
    import re

    # Update the cache key, allowing harmless formatting differences.
    key_pattern = re.compile(
        r"    def _key\(self, model, messages, temperature, max_tokens\) -> str:\n"
        r"        blob = json\.dumps\(\[model, messages, temperature, max_tokens, self\.reasoning_effort\], sort_keys=True\)\n"
        r"        return hashlib\.sha256\(blob\.encode\(\)\)\.hexdigest\(\)"
    )
    key_replacement = (
        "    def _key(self, model, messages, temperature, max_tokens, "
        "reasoning_effort=None, token_headroom=None) -> str:\n"
        "        blob = json.dumps([model, messages, temperature, max_tokens, "
        "reasoning_effort, token_headroom], sort_keys=True)\n"
        "        return hashlib.sha256(blob.encode()).hexdigest()"
    )
    text, key_count = key_pattern.subn(key_replacement, text, count=1)
    if key_count != 1:
        raise ValueError("could not uniquely patch _key() in src/atlasrag/llm.py")

    # The local file may already have the expanded chat() signature.
    marker = '        model = model or self.model\n'
    if text.count(marker) != 1:
        raise ValueError("could not uniquely locate chat() model assignment")
    following = text[text.index(marker) + len(marker):]
    effective = (
        "        effort = reasoning_effort if reasoning_effort is not None else self.reasoning_effort\n"
        "        headroom = token_headroom if token_headroom is not None else self.headroom\n"
    )
    if not following.startswith(effective):
        text = text.replace(marker, marker + effective, 1)

    # Cache key must include the effective per-call settings.
    cache_pattern = re.compile(
        r"self\._key\(model, messages, temperature, max_tokens\)"
    )
    text, cache_count = cache_pattern.subn(
        "self._key(model, messages, temperature, max_tokens, effort, headroom)",
        text, count=1
    )
    if cache_count != 1:
        raise ValueError("could not uniquely patch the cache-key call")

    # Apply the effective reasoning effort and headroom to the provider request.
    text, effort_count = re.subn(
        r"if self\.reasoning_effort:\s*\n\s*kwargs\[\"extra_body\"\] = "
        r"\{\"reasoning_effort\": self\.reasoning_effort\}",
        'if effort:\n                kwargs["extra_body"] = {"reasoning_effort": effort}',
        text, count=1
    )
    if effort_count != 1:
        raise ValueError("could not uniquely patch reasoning_effort usage")

    text, headroom_count = re.subn(
        r"max_tokens=max_tokens \+ self\.headroom",
        "max_tokens=max_tokens + headroom",
        text, count=1
    )
    if headroom_count != 1:
        raise ValueError("could not uniquely patch token_headroom usage")
    return text


def main():
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    staged = []

    # Handle llm.py using whitespace-tolerant targeted edits, because local
    # versions may already have the new chat() parameters.
    llm_path = root / "src/atlasrag/llm.py"
    if not llm_path.exists():
        raise SystemExit(f"Missing expected file: {llm_path}")
    llm_original = llm_path.read_text(encoding="utf-8")
    try:
        llm_updated = patch_llm(llm_original)
    except ValueError as exc:
        raise SystemExit(f"{exc}. No files changed.")
    staged.append(("src/atlasrag/llm.py", llm_path, llm_original, llm_updated))

    # Exact, validated changes for the generation pipeline and CLI.
    for rel in (
        "src/atlasrag/bench/generate.py",
        "src/atlasrag/bench/generate_v2.py",
        "scripts/gen_questions_v2.py",
    ):
        path = root / rel
        if not path.exists():
            raise SystemExit(f"Missing expected file: {path}")
        original = path.read_text(encoding="utf-8")
        updated = original
        if rel == "scripts/gen_questions_v2.py":
            import re
            # Insert CLI flags after the existing judge-model argument, regardless
            # of whether adjacent argparse calls share a line.
            if "--generation-reasoning-effort" not in updated:
                pattern = r'(?m)^(?P<indent>\s*)ap\.add_argument\("--judge-model",[^\n]*\n'
                updated, count = re.subn(
                    pattern,
                    lambda m: m.group(0) +
                    'ap.add_argument("--generation-reasoning-effort", choices=["low", "medium", "high"], default=None,\n'
                    '                help="override reasoning effort for generation calls only")\n'
                    'ap.add_argument("--generation-token-headroom", type=int, default=None,\n'
                    '                help="extra completion-token allowance for generation calls only")\n',
                    updated, count=1
                )
                if count != 1:
                    raise SystemExit("Could not locate --judge-model argument in scripts/gen_questions_v2.py. No files changed.")

            # Set generation-only controls immediately after generator creation.
            if "gen.generation_reasoning_effort = a.generation_reasoning_effort" not in updated:
                pattern = r'(?m)^(?P<indent>\s*)gen = ValidatedGenerator\([\s\S]*?^\s*load_meta\(resolve\(cfg\["corpus"\]\["raw_dir"\]\)\),[^\n]*\n?'
                match = re.search(pattern, updated)
                if not match:
                    # Fallback for a single-line or differently wrapped constructor.
                    pattern = r'(?m)^(?P<indent>\s*)gen = ValidatedGenerator\([\s\S]*?judge_model=a\.judge_model\)\s*$'
                    match = re.search(pattern, updated)
                if not match:
                    raise SystemExit("Could not locate ValidatedGenerator construction in scripts/gen_questions_v2.py. No files changed.")
                end = match.end()
                insertion = '\ngen.generation_reasoning_effort = a.generation_reasoning_effort\ngen.generation_token_headroom = a.generation_token_headroom\n'
                updated = updated[:end] + insertion + updated[end:]
        else:
            for old, new in PATCHES[rel]:
                count = updated.count(old)
                if count != 1:
                    raise SystemExit(
                        f"Expected one match in {rel}, found {count}. No files changed."
                    )
                updated = updated.replace(old, new, 1)
        staged.append((rel, path, original, updated))

    # Only write after every file validates successfully.
    for rel, path, original, updated in staged:
        backup = path.with_suffix(path.suffix + ".before_gen_controls.bak")
        if not backup.exists():
            backup.write_text(original, encoding="utf-8")
        path.write_text(updated, encoding="utf-8")
        print(f"Patched {rel}; backup: {backup.name}")
    print("\nGeneration-only flags added: --generation-reasoning-effort and --generation-token-headroom")

if __name__ == "__main__":
    main()
