import pytest
from fastapi import HTTPException

from atlasrag.api import main as api
from atlasrag.llm import LLMEmptyCompletion, LLMRateLimitExceeded


@pytest.fixture
def clean_state():
    old = dict(api._state)
    api._state["pipeline"] = None
    api._state["cfg"] = None
    api._state["llm"] = None
    api._state["notes"] = []
    yield
    api._state.clear()
    api._state.update(old)


def test_health_is_not_healthy_when_pipeline_is_unavailable(clean_state):
    api._state["notes"] = ["index not built yet"]
    with pytest.raises(HTTPException) as exc:
        api.health()
    assert exc.value.status_code == 503
    assert exc.value.detail["pipeline_ready"] is False
    assert exc.value.detail["status"] == "not_ready"


@pytest.mark.parametrize("error", [
    LLMEmptyCompletion("empty completion"),
    LLMRateLimitExceeded("provider rate limit"),
])
def test_api_returns_service_unavailable_for_retryable_provider_failures(clean_state, error):
    class FailedPipeline:
        def answer(self, *args, **kwargs):
            raise error

    api._state["pipeline"] = FailedPipeline()
    api._state["cfg"] = {}
    api._state["llm"] = object()
    with pytest.raises(HTTPException) as exc:
        api.ask(api.AskRequest(question="question", router="static"))
    assert exc.value.status_code == 503
    assert str(error) in exc.value.detail
