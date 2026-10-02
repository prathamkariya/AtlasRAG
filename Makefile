PY ?= python
.PHONY: install check fetch index serve test docker-build docker-up

install:        ## install deps (use a venv)
	$(PY) -m pip install -r requirements.txt
check:          ## verify env vars, imports, optional LLM ping
	$(PY) scripts/check_env.py
fetch:          ## download arXiv metadata + PDFs
	$(PY) scripts/fetch_arxiv.py
index:          ## parse -> chunk -> embed -> index
	$(PY) scripts/build_index.py
serve:          ## run the API locally
	PYTHONPATH=src uvicorn atlasrag.api.main:app --reload --port 8000
test:
	$(PY) -m pytest -q
docker-build:
	docker compose build
docker-up:
	docker compose up

# ---- Week 2: benchmark ----
questions:      ## generate candidate test questions
	$(PY) scripts/gen_questions.py --split test --per-type 30
review:
	$(PY) scripts/review_questions.py
oracle:
	$(PY) scripts/label_oracle.py
