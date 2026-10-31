# Root command runner (IMD-08). Target names and commands follow specification §4.7.
# ARGS passes extra arguments to the wrapped tool, for example make test-api ARGS='-k trips'.
# A target whose code arrives with a later card prints "not yet implemented (IMP-xxx)" and exits 0;
# it starts running the real command as soon as the file that card adds is present.

SHELL := /bin/bash
.DEFAULT_GOAL := help

API_DIR := apps/api
WEB_DIR := apps/web
VENV := $(API_DIR)/.venv
PY312 := python3.12

ARGS ?=
URL ?=
PROVIDER ?= MOCK
DATASET ?= trips/v1
SEED_DIRS ?=

# The API toolchain (ruff, mypy, pytest, import-linter) arrives with the IMP-101 api-pyproject-guard part.
API_READY := [ -f $(API_DIR)/pyproject.toml ]
API_PENDING := not yet implemented (IMP-101 api-pyproject-guard part)
# pytest exits 5 when it collects no tests; an empty suite counts as success.
PYTEST_EXIT := rc=$$?; if [ $$rc -eq 5 ]; then echo "pytest: no tests collected (exit 5 treated as success)"; exit 0; fi; exit $$rc

.PHONY: help setup stack-up stack-down db-up db-down db-migrate db-reset seed api web \
	lint typecheck imports test-unit test-contract test-api test-authz test-web test e2e \
	openapi openapi-check eval check smoke live-smoke

help:
	@echo "Targets (specification §4.7):"
	@echo "  setup [ARGS=--with-browsers]  install API venv, web packages, git hooks (and Playwright Chromium)"
	@echo "  stack-up | stack-down         Supabase CLI local stack"
	@echo "  db-up | db-down               docker compose test Postgres"
	@echo "  db-migrate | db-reset | seed  migrations, local/test reset, seed data (SEED_DIRS=...)"
	@echo "  api | web                     run the API (port 8000) or the web app (port 3000)"
	@echo "  lint | typecheck | imports    quality checks"
	@echo "  test-unit | test-contract | test-api | test-authz | test-web | test"
	@echo "  e2e                           Playwright journeys (BASE_URL=... runs against a deployment)"
	@echo "  openapi | openapi-check       export or verify the API contract and AI schemas"
	@echo "  eval PROVIDER=MOCK DATASET=trips/v1"
	@echo "  check                         everything a pull request needs"
	@echo "  smoke URL=<base url> | live-smoke"

setup:
	@if $(API_READY); then \
	  [ -d $(VENV) ] || $(PY312) -m venv $(VENV); \
	  $(VENV)/bin/python -m pip install -e "$(API_DIR)[dev]"; \
	else echo "setup (api): $(API_PENDING)"; fi
	npm ci --prefix $(WEB_DIR)
	@if [ -d .githooks ]; then git config core.hooksPath .githooks && echo "setup: core.hooksPath set to .githooks"; \
	else echo "setup: .githooks not present yet (IMP-102); core.hooksPath unchanged"; fi
	@case " $(ARGS) " in *" --with-browsers "*) cd $(WEB_DIR) && npx playwright install --with-deps chromium;; \
	*) echo "setup: Playwright browsers skipped (make setup ARGS=--with-browsers installs Chromium)";; esac

# The hints name where each local key goes; they never print a key (copy them from your own terminal).
stack-up:
	supabase start
	@echo ""
	@echo "stack-up: run 'supabase status -o env' and copy these values into your untracked env files:"
	@echo "  JWT_SECRET       -> SUPABASE_JWT_SECRET in apps/api/.env"
	@echo "  ANON_KEY         -> NEXT_PUBLIC_SUPABASE_ANON_KEY in apps/web/.env.local"
	@echo "  SERVICE_ROLE_KEY -> SUPABASE_SERVICE_ROLE_KEY in apps/api/.env (local E2E only)"
	@echo "  Never paste these values into a tracked file, an issue or a pull request (docs/secrets.md)."

stack-down:
	supabase stop

# --wait returns once the healthcheck passes, so make test-api can follow straight away.
db-up:
	docker compose up -d --wait db

db-down:
	docker compose down

# Applies migrations 0001 onwards to DATABASE_URL (§5.5). On plain PostgreSQL (compose db, CI), apply
# apps/api/migrations/sql/test_auth_stub.sql first; the Supabase stack already has the auth schema.
db-migrate:
	cd $(API_DIR) && .venv/bin/alembic upgrade head

# §5.7: the reset reloads the seed, so it arrives with make seed.
db-reset:
	@echo "db-reset: not yet implemented (IMP-107)"

seed:
	@if [ -e $(API_DIR)/app/places/seed.py ] || [ -d $(API_DIR)/app/places/seed ]; then \
	  cd $(API_DIR) && .venv/bin/python -m app.places.seed $(CURDIR)/data/fixtures/sampleton $(foreach d,$(SEED_DIRS),$(abspath $(d))) $(ARGS); \
	else echo "seed: not yet implemented (IMP-107)"; fi

api:
	@if [ -f $(API_DIR)/app/main.py ]; then cd $(API_DIR) && .venv/bin/uvicorn app.main:app --reload --port 8000; \
	else echo "api: not yet implemented (IMP-103)"; fi

web:
	npm run dev --prefix $(WEB_DIR)

lint:
	@if $(API_READY); then cd $(API_DIR) && .venv/bin/ruff check . && .venv/bin/ruff format --check .; \
	else echo "lint (api): $(API_PENDING)"; fi
	npm run lint --prefix $(WEB_DIR)
	npm run format:check --prefix $(WEB_DIR)

typecheck:
	@if $(API_READY); then cd $(API_DIR) && .venv/bin/mypy app; \
	else echo "typecheck (api): $(API_PENDING)"; fi
	npm run typecheck --prefix $(WEB_DIR)

imports:
	@if [ -f $(API_DIR)/.importlinter ]; then cd $(API_DIR) && .venv/bin/lint-imports --config .importlinter; \
	else echo "imports: $(API_PENDING)"; fi

test-unit:
	@if $(API_READY); then cd $(API_DIR) && .venv/bin/pytest tests/unit $(ARGS); $(PYTEST_EXIT); \
	else echo "test-unit: $(API_PENDING)"; fi

test-contract:
	@if $(API_READY); then cd $(API_DIR) && .venv/bin/pytest tests/contract -m "not live" $(ARGS); $(PYTEST_EXIT); \
	else echo "test-contract: $(API_PENDING)"; fi

test-api:
	@if $(API_READY); then cd $(API_DIR) && .venv/bin/pytest tests/api $(ARGS); $(PYTEST_EXIT); \
	else echo "test-api: $(API_PENDING)"; fi

test-authz:
	@if $(API_READY); then cd $(API_DIR) && .venv/bin/pytest tests/authz $(ARGS); $(PYTEST_EXIT); \
	else echo "test-authz: $(API_PENDING)"; fi

test-web:
	npm run test --prefix $(WEB_DIR) -- --passWithNoTests $(ARGS)

test: test-unit test-contract test-api test-authz test-web

e2e:
	@if [ -f $(WEB_DIR)/playwright.config.ts ]; then cd $(WEB_DIR) && npx playwright test --pass-with-no-tests $(ARGS); \
	else echo "e2e: not yet implemented (IMP-216)"; fi

# The AI JSON Schemas (gr-1, io-1) are exported here (IMP-110); the OpenAPI export and the web types
# arrive with IMP-214.
openapi:
	@if $(API_READY); then cd $(API_DIR) && .venv/bin/python -m app.schemas.ai_export --out $(CURDIR)/contracts/ai; \
	else echo "openapi (ai schemas): $(API_PENDING)"; fi
	@echo "openapi: OpenAPI export and web types not yet implemented (IMP-214)"

openapi-check:
	@echo "openapi-check: not yet implemented (IMP-214)"

eval:
	@if [ -e $(API_DIR)/app/evaluation/run.py ] || [ -d $(API_DIR)/app/evaluation/run ]; then \
	  cd $(API_DIR) && .venv/bin/python -m app.evaluation.run --dataset $(DATASET) --provider $(PROVIDER) $(ARGS); \
	else echo "eval: not yet implemented (IMP-413)"; fi

check: lint typecheck imports openapi-check test

smoke:
	@if [ -f $(API_DIR)/tests/smoke/test_deployed.py ]; then \
	  if [ -z "$(URL)" ]; then echo "smoke: URL is required (make smoke URL=<base url>)"; exit 1; fi; \
	  cd $(API_DIR) && .venv/bin/pytest tests/smoke --base-url "$(URL)" $(ARGS); \
	else echo "smoke: not yet implemented (IMP-112)"; fi

live-smoke:
	@if $(API_READY); then cd $(API_DIR) && .venv/bin/pytest tests/contract -m live $(ARGS); $(PYTEST_EXIT); \
	else echo "live-smoke: $(API_PENDING)"; fi
