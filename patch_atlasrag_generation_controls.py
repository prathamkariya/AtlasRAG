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

def main():
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    staged = []
    for rel, replacements in PATCHES.items():
        path = root / rel
        if not path.exists():
            raise SystemExit(f"Missing expected file: {path}")
        original = path.read_text(encoding="utf-8")
        updated = original
        for old, new in replacements:
            count = updated.count(old)
            if count == 1:
                updated = updated.replace(old, new, 1)
                continue
            # The uploaded llm.py may already have the expanded chat() signature
            # from the earlier manual step; add effective settings in that case.
            if rel == "src/atlasrag/llm.py" and "def chat(" in old and count == 0:
                partial = """    ) -> str:
        model = model or self.model
        self.stats[\"calls\"] += 1
"""
                full = """    ) -> str:
        model = model or self.model
        effort = reasoning_effort if reasoning_effort is not None else self.reasoning_effort
        headroom = token_headroom if token_headroom is not None else self.headroom
        self.stats[\"calls\"] += 1
"""
                if updated.count(partial) == 1:
                    updated = updated.replace(partial, full, 1)
                    continue
            raise SystemExit(f"Expected one match in {rel}, found {count}. No files changed; local source differs from expected version.")
        staged.append((rel, path, original, updated))
    for rel, path, original, updated in staged:
        backup = path.with_suffix(path.suffix + ".before_gen_controls.bak")
        if not backup.exists():
            backup.write_text(original, encoding="utf-8")
        path.write_text(updated, encoding="utf-8")
        print(f"Patched {rel}; backup: {backup.name}")
    print("\nGeneration-only flags added: --generation-reasoning-effort and --generation-token-headroom")

if __name__ == "__main__":
    main()
