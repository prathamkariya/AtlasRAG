import types
import pytest

pytest.importorskip("openai")
from atlasrag.llm import LLMClient


def _resp(text, finish="stop"):
    return types.SimpleNamespace(
        choices=[types.SimpleNamespace(message=types.SimpleNamespace(content=text), finish_reason=finish)],
        usage=types.SimpleNamespace(prompt_tokens=7, completion_tokens=3))


class FakeAPI:
    def __init__(self, text="hello", finish="stop"):
        self.calls, self.text, self.finish = [], text, finish
        self.chat = types.SimpleNamespace(completions=types.SimpleNamespace(create=self.create))

    def create(self, **kw):
        self.calls.append(kw)
        return _resp(self.text, self.finish)


def make(tmp_path, monkeypatch, **cfg_over):
    monkeypatch.setenv("GROQ_API_KEY", "x")
    cfg = {"base_url": "http://x", "model": "m", "reasoning_effort": "low", "token_headroom": 400,
           "cache_namespace": "t"}
    cfg.update(cfg_over)
    llm = LLMClient(cfg, cache_root=tmp_path)
    llm.client = FakeAPI()
    return llm


def test_headroom_and_reasoning_effort_sent(tmp_path, monkeypatch):
    llm = make(tmp_path, monkeypatch)
    assert llm.chat([{"role": "user", "content": "hi"}], max_tokens=40) == "hello"
    kw = llm.client.calls[0]
    assert kw["max_tokens"] == 440 and kw["extra_body"] == {"reasoning_effort": "low"}


def test_no_reasoning_params_for_plain_models(tmp_path, monkeypatch):
    llm = make(tmp_path, monkeypatch, reasoning_effort=None)
    llm.chat([{"role": "user", "content": "hi"}], max_tokens=40)
    kw = llm.client.calls[0]
    assert kw["max_tokens"] == 40 and "extra_body" not in kw


def test_cache_hit_counts_logical_calls_but_not_api_calls(tmp_path, monkeypatch):
    llm = make(tmp_path, monkeypatch)
    m = [{"role": "user", "content": "hi"}]
    llm.chat(m); llm.chat(m)
    assert len(llm.client.calls) == 1
    assert llm.stats["calls"] == 2 and llm.stats["cache_hits"] == 1
    assert llm.stats["prompt_tokens"] == 14


def test_empty_completion_raises_helpful_error_and_is_not_cached(tmp_path, monkeypatch):
    llm = make(tmp_path, monkeypatch)
    llm.client = FakeAPI(text="", finish="length")
    with pytest.raises(RuntimeError, match="token_headroom"):
        llm.chat([{"role": "user", "content": "hi"}])
    assert not list((tmp_path / "t").glob("*.json"))
