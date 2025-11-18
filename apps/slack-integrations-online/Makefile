ifeq (,$(wildcard .env))
$(error .env file is missing. Please create one based on .env.example. Run: "cp .env.example .env" and fill in the missing values.)
endif

include .env

export UV_PROJECT_ENVIRONMENT=.venv-online
export PYTHONPATH = .

# --- Utilities ---

help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

# --- Infrastructure --- 

local-docker-infrastructure-up:
	docker compose -f ../infrastructure/docker/docker-compose.yml up --build -d 

local-docker-infrastructure-stop:
	docker compose -f ../infrastructure/docker/docker-compose.yml stop

local-infrastructure-up: local-docker-infrastructure-up

local-infrastructure-stop: local-docker-infrastructure-stop

local-infrastructure-down:
	docker compose -f ../infrastructure/docker/docker-compose.yml down

# --- Run ---

run-agent-cli:
	uv run python ./src/slack_integrations_online/tools/app.py

run-agent-slack:
	uv run python ./src/slack_integrations_online/tools/slack_app.py