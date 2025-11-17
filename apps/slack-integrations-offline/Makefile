ifeq (,$(wildcard .env))
$(error .env file is missing. Please create one based on .env.example. Run: "cp .env.example .env" and fill in the missing values.)
endif

include .env

export UV_PROJECT_ENVIRONMENT=.venv-offline
export PYTHONPATH = .

# --- Utilities ---

help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done


# --- Infrastructure --- 

local-docker-infrastructure-up:
	docker compose -f ../infrastructure/docker/docker-compose.yml up --build -d 

local-docker-infrastructure-stop:
	docker compose -f ../infrastructure/docker/docker-compose.yml stop

local-infrastructure-down:
	docker compose -f ../infrastructure/docker/docker-compose.yml down

local-zenml-server-up:
ifeq ($(shell uname), Darwin)
	OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES uv run zenml login --local
else
	uv run zenml login --local
endif

local-zenml-server-stop:
	uv run zenml logout --local

local-infrastructure-up: local-docker-infrastructure-up local-zenml-server-stop local-zenml-server-up

local-infrastructure-stop: local-docker-infrastructure-stop local-zenml-server-stop


# --- Offline Pipelines ---

collect-crawl-data:
	uv run python -m tools.run --run-collect-crawl-data-pipeline

etl-pipeline:
	uv run python -m tools.run --run-etl-pipeline

compute-rag-pipeline:
	uv run python -m tools.run --run-compute-rag-pipeline