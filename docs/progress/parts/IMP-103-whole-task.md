# IMP-103 · whole-task part

- Run id: RUN-004
- Owner: Manal (manalPatel2557)
- Status: PR_OPEN
- Base commit: 8c7d8dd
- Branch: feat/IMP-103-whole-task
- Reviewer: Kirtan (kirtan-S111)
- Traces to: US-003; FR-123, FR-124; NFR-013, NFR-015, NFR-035
- Card steps built: 1 to 7

## Changed files

- `apps/api/app/core/config.py` (created): `Settings` (pydantic-settings) with every backend variable of the §4.5 `.env.example` block, `load_settings()`, cached `get_settings()`, `check_settings()` and `ConfigError`.
- `apps/api/app/core/request_id.py` (created): `RequestIdMiddleware` (pure ASGI), `request_id_var` context variable, `X-Request-ID` header.
- `apps/api/app/core/flags.py` (created): `FEATURES_DISABLED` parsed into a `frozenset`; `is_enabled(settings, name)`.
- `apps/api/app/core/errors.py` (created): `DomainError` and its subclasses, the handlers and `register_error_handlers(app)`.
- `apps/api/app/schemas/common.py` (created): `ErrorCode`, `ErrorDetail`, `ErrorBody`, `ErrorEnvelope`.
- `apps/api/app/core/health.py` (created): API-01 `GET /health` and `HealthOut`.
- `apps/api/app/main.py` (created): `create_app(settings=None)` and the `app` that `make api` runs.
- `apps/api/tests/conftest.py` (modified, Het's file): two fixtures added after the socket guard, which is unchanged: `reset_settings_cache` (autouse, clears `get_settings` around each test) and `clean_settings_env` (removes every backend variable and `GOOGLE_API_KEY` and stops reading `.env`, so CI's `APP_ENV`/`AI_PROVIDER`/`DATABASE_URL` or a developer's `.env` cannot change a result).
- `apps/api/tests/unit/core/test_config.py` (created), `apps/api/tests/api/test_health.py` (created).
- `apps/api/tests/unit/core/test_errors.py` (created; not in the card's file list): tests of the §6.3 mapping of every domain exception, 422 `VALIDATION_ERROR` details, 500 `INTERNAL` without a trace, and 405.
- This record (created).

**Makefile not changed.** The run prompt allowed changing the `api` target to the §4.7 command. It already is that command: since IMP-101 the target runs `cd apps/api && .venv/bin/uvicorn app.main:app --reload --port 8000` as soon as `apps/api/app/main.py` exists and only prints the pending message before. `make api` was run in this part (evidence below), so no edit was needed.

## What was built

**Settings (step 1).** One field per backend variable of §4.5, read case-insensitively from the environment and `apps/api/.env` (when present). Defaults are the `.env.example` values for non-secret settings; secrets (`DATABASE_URL`, `TEST_DATABASE_URL`, `SUPABASE_JWT_SECRET`, `ORS_API_KEY`, `GEMINI_API_KEY`, `FINETUNED_API_KEY`) are `SecretStr` with an empty default, and `<placeholder>` values (`GEMINI_MODEL_ID`, `WIKI_USER_AGENT`) default to empty. An empty variable counts as unset (`env_ignore_empty`), so `FEATURES_DISABLED=` and `AI_MAX_INPUT_TOKENS=` work as written in `.env.example`. `APP_ENV`, `AI_PROVIDER`, `MOCK_PROVIDER_SCENARIO` and `LOG_LEVEL` are `Literal` types; `ALLOWED_ORIGINS` is split on commas (trailing `/` dropped). Left out: the `NEXT_PUBLIC_*` names (browser only), `SUPABASE_SERVICE_ROLE_KEY` (used only by the Playwright user fixture, never by the API) and `SEED_DIRS` (a Makefile variable).

**Start-up checks (step 2).** `create_app()` runs `check_settings(settings, os.environ)`; every failed rule is collected into one `ConfigError` whose message names variables only:

| Rule | Environments | Message |
| --- | --- | --- |
| `APP_ENV` in {local, test, staging, production} | all | `APP_ENV: Input should be 'local', 'test', 'staging' or 'production'` |
| `DATABASE_URL` present (not empty or blank) | all | `DATABASE_URL is not set` |
| `AI_PROVIDER` in {GEMINI, MOCK, FINETUNED_MODEL} | all | `AI_PROVIDER: Input should be 'GEMINI', 'MOCK' or 'FINETUNED_MODEL'` |
| `FINETUNED_MODEL` refused | all | `AI_PROVIDER: the FINETUNED_MODEL adapter is not enabled before Stage 2` |
| `MOCK` refused | production | `AI_PROVIDER: MOCK is refused when APP_ENV is production` |
| `GEMINI_API_KEY`, `GEMINI_MODEL_ID` not empty and not starting with `<` | staging, production with GEMINI | `GEMINI_API_KEY is empty or a placeholder` (same for the model ID) |
| `GEMINI_TIMEOUT_S × (GEMINI_MAX_RETRIES + 1) ≤ 70` | staging, production with GEMINI | `GEMINI_TIMEOUT_S x (GEMINI_MAX_RETRIES + 1) exceeds the 70 s generation allowance` |
| `ALLOWED_ORIGINS` has no `*` (step 6) | all | `ALLOWED_ORIGINS must list exact origins; '*' is not allowed` |
| `GOOGLE_API_KEY` set | all | warning only (logged), start-up continues |

A parse error (unknown `APP_ENV` or `AI_PROVIDER`, a non-number) is converted to `ConfigError` with pydantic's message but without the input value, and raised `from None` so the original error (which repeats the value) is not chained. In `local` and `test`, GEMINI without a key starts, as §8.4 says (the provider is reported down by later cards).

**Process exit.** `app.main` builds `app` on first access (module `__getattr__`), which is what uvicorn's `app.main:app` lookup does; a `ConfigError` ends the process with `sys.exit("configuration error: <rules>")`, exit code 1. Importing `app.main` for `create_app` (the tests) reads no settings. Under `make api` the `--reload` supervisor stays up and its worker exits with the message; without `--reload` (Render, `docker compose`) the process exits 1 (evidence below).

**Error envelope (step 3).** Models in `schemas/common.py`; `ErrorCode` has all twelve codes of §6.3. Exceptions in `core/errors.py` with the §6.3 status: `Unauthenticated` 401, `NotFound` 404, `StalePlan`, `GenerationInProgress`, `Conflict` 409, `ValidationFailed` 422 `VALIDATION_ERROR`, `RateLimited` 429 (sets `Retry-After` and `retry_after_s`), `QuotaReached` 429 `AI_QUOTA_REACHED`, `Internal` 500, `ServiceUnavailable` 503, and also `InvalidEdit` 422 `INVALID_EDIT` and `EndpointNotImplemented` 501 `NOT_IMPLEMENTED` so that every §6.3 code has an exception. One handler is registered per class. `RequestValidationError` → 422 `VALIDATION_ERROR` with `details` (`field` from the location without `body`/`query`/`path`, pydantic's message, never the input). Starlette HTTP errors (unknown route) keep their status in the envelope. Any other exception → 500 `INTERNAL`, logged with the request ID, no trace in the body. Every error response carries `X-Request-ID`, and `request_id` in the body equals it.

**Request ID (step 4).** A client `X-Request-ID` that parses as a UUID is kept (lower-case canonical form); otherwise a UUID4 is generated. Stored in `request_id_var` and the request state, echoed on every response, including CORS preflight and 500 responses.

**Health and mount point (step 5).** `GET /health` returns exactly `status` (`ok`), `version` (`BUILD_VERSION`, default `dev`), `environment` (`APP_ENV`) and `provider` (`AI_PROVIDER`); no database or provider call. `/api/v1` is an empty `APIRouter(prefix="/api/v1")` in `create_app`; module cards include their routers there.

**CORS, docs and switches (step 6).** `CORSMiddleware` with `allow_origins=ALLOWED_ORIGINS` (exact), methods GET, POST, PUT, PATCH, DELETE, headers `Authorization`, `Content-Type`, `X-Request-ID`, `allow_credentials=False` (§6.1). `/docs`, `/redoc` and `/openapi.json` are off when `APP_ENV=production`. `core/flags.py` parses `FEATURES_DISABLED` into a set (names trimmed, lower-cased).

## Commands run

| Command | Result line (quoted exactly) |
| --- | --- |
| Preflight: `git fetch origin; git status --porcelain --untracked-files=no` | no output; base `git rev-parse --short origin/main` → `8c7d8dd` |
| `make test-unit ARGS='-k config'` (with `DATABASE_URL`, `APP_ENV`, `AI_PROVIDER` unset in the shell) | `====================== 36 passed, 20 deselected in 1.66s =======================` |
| `make test-api ARGS='-k health'` (with `DATABASE_URL` unset) | `======================== 13 passed, 1 warning in 0.42s =========================` |
| `make lint` | exit 0; last line `All matched files use Prettier code style!` (API part: `All checks passed!`) |
| `make typecheck` | exit 0; last line `✓ Types generated successfully` (API part: `Success: no issues found in 20 source files`) |
| `make imports` | `Contracts: 3 kept, 0 broken.` |
| `make test` | exit 0; unit `======================== 74 passed, 1 warning in 2.37s =========================`, contract `============================ no tests ran in 0.01s =============================` (`pytest: no tests collected (exit 5 treated as success)`), api `======================== 13 passed, 1 warning in 0.43s =========================`, authz no tests ran (exit 5 treated as success), web `No test files found, exiting with code 0` |
| `make check` | exit 0; `openapi-check: not yet implemented (IMP-214)`; unit `======================== 74 passed, 1 warning in 2.36s =========================`; api `======================== 13 passed, 1 warning in 0.36s =========================` |
| `make api` (APP_ENV=local, AI_PROVIDER=MOCK, DATABASE_URL = the §4.5 local default) + the two curls below, then stopped | `INFO:     Application startup complete.`; after stop the port refuses connections |

Not run: `make openapi` (the target still prints `openapi: not yet implemented (IMP-110, IMP-214)`); `make e2e` (no journey touched).

The one warning in the API test runs is `StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.`, raised by the installed Starlette when FastAPI's `TestClient` is imported. It is a dependency matter for whoever owns `pyproject.toml`, not a failure.

## Evidence: `make api` and curl

`curl -s -i http://localhost:8000/health`

```text
HTTP/1.1 200 OK
date: Sat, 31 Oct 2026 18:44:56 GMT
server: uvicorn
content-length: 71
content-type: application/json
vary: Origin
x-request-id: 9a080b47-3e92-4cb1-a0ed-96e998fa9a27

{"status":"ok","version":"dev","environment":"local","provider":"MOCK"}
```

`curl -s -i http://localhost:8000/no-such-route`

```text
HTTP/1.1 404 Not Found
date: Sat, 31 Oct 2026 18:44:56 GMT
server: uvicorn
x-request-id: e8ed2788-b28c-48e9-bd9e-a360ce2efb5a
content-length: 139
content-type: application/json
vary: Origin

{"error":{"code":"NOT_FOUND","message":"Not found.","request_id":"e8ed2788-b28c-48e9-bd9e-a360ce2efb5a","details":[],"retry_after_s":null}}
```

Start-up refusals, `cd apps/api && env -i PATH="$PATH" <variables> .venv/bin/uvicorn app.main:app --port 8001` (no `--reload`, so the exit code is the process's), last line and exit code; the log was also searched for the placeholder text `Gemini API key`:

| Variables | Last line | Exit | Placeholder in output |
| --- | --- | --- | --- |
| `APP_ENV=local AI_PROVIDER=MOCK` (no `DATABASE_URL`) | `configuration error: DATABASE_URL is not set` | 1 | 0 lines |
| `APP_ENV=staging AI_PROVIDER=GEMINI GEMINI_API_KEY='<Gemini API key>' GEMINI_MODEL_ID=test-model-id DATABASE_URL=<local default>` | `configuration error: GEMINI_API_KEY is empty or a placeholder` | 1 | 0 lines |
| `AI_PROVIDER=UNKNOWN DATABASE_URL=<local default>` | `configuration error: AI_PROVIDER: Input should be 'GEMINI', 'MOCK' or 'FINETUNED_MODEL'` | 1 | 0 lines |
| `AI_PROVIDER=FINETUNED_MODEL DATABASE_URL=<local default>` | `configuration error: AI_PROVIDER: the FINETUNED_MODEL adapter is not enabled before Stage 2` | 1 | 0 lines |

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| Starting with DATABASE_URL unset exits non-zero with a message naming DATABASE_URL (US-003 AC1, FR-124 AC1, TC-290) | verified | `test_database_url_missing_is_refused` (unset, empty, blank), `test_start_without_database_url_exits` (fresh interpreter loading `app.main:app`: exit ≠ 0, stderr names `DATABASE_URL`); uvicorn run above, exit 1 |
| APP_ENV=staging, AI_PROVIDER=GEMINI, GEMINI_API_KEY='<Gemini API key>' exits with a configuration error; the key value is not printed (TC-043, TC-291, TC-025) | verified | `test_gemini_key_placeholder_is_refused` (staging and production, empty and placeholder; value absent from the message), `test_gemini_model_id_placeholder_is_refused`, `test_gemini_time_allowance`, `test_start_with_placeholder_gemini_key_exits` (exit ≠ 0, `configuration error` and `GEMINI_API_KEY` in stderr, placeholder absent from stdout and stderr); uvicorn run above |
| AI_PROVIDER=UNKNOWN exits with a clear error (TC-042); AI_PROVIDER=FINETUNED_MODEL is refused (TC-037) | verified | `test_unknown_provider_is_refused` (names `AI_PROVIDER` and the three allowed values; no chained pydantic error), `test_finetuned_model_is_refused` (all four environments); uvicorn runs above |
| GET /health returns 200 with status, version, environment, provider and no secret (FR-123 AC1, TC-288, TC-044) | verified | `test_health_returns_status_version_environment_provider` (exact four-field body; four fake secret values absent from body and headers), `test_health_is_outside_api_v1`, `test_health_docs_are_disabled_in_production`; curl above |
| A request from an origin not in ALLOWED_ORIGINS gets no CORS allow header (TC-351) | verified | `test_health_cors_refuses_other_origins` (three origins, simple request and preflight), `test_health_cors_allows_the_configured_origin` (positive control) |
| Step 7: an unknown route returns the 404 envelope with a request_id | verified | `test_health_unknown_route_returns_not_found_envelope`, `test_health_unknown_api_v1_route_returns_not_found_envelope` (client ID echoed); curl above |

Other start-up rules with unit tests: MOCK refused in production and allowed in local, test and staging; GEMINI without a key starts in local and test; `GOOGLE_API_KEY` only warns and its value is not in the warning; `*` in `ALLOWED_ORIGINS` refused; unknown `APP_ENV` refused; every failed rule listed in one error; `FEATURES_DISABLED` parsed into a set.

## Blockers

None.

## Proposed decisions

- **PD-103-A (API-01 fields).** §6.6.1 API-01 lists the response as `{status: "ok", version, provider}`; the IMP-103 card (task register and Appendix C) and the run prompt require a fourth field, `environment`. Built as the card says (four fields). Proposal: add `environment` to the API-01 entry of §6.6.1 so the catalogue matches the card. Adding an optional response field is allowed within v1 (§6.1).
- **PD-103-B (405 has no §6.3 code).** A known path called with a method it does not serve (for example `DELETE /health`) returns HTTP 405 with its `Allow` header and the envelope code `NOT_FOUND`, because §6.3 has no code for it. Proposal: record this mapping in §6.3, or add a code if the team prefers one.

## Open issues

- The card's step 5 says version comes "from env BUILD_VERSION or git sha"; this part reads only `BUILD_VERSION` (default `dev`), as the §4.5 table says ("Set by CI (commit SHA)"). Running `git` inside the app would add a process call to a route that must stay fast, and the Render container has no `.git`.
- The card asks for the curl output in `docs/progress/sprint-1.md`; it is in this record instead (CLAUDE.md §11 item 5); the SG-1 gate card compiles `sprint-1.md`.
- `ruff`'s N818 rule (exception names end in `Error`) is switched off for `app/core/errors.py` only, with a reason, because the card names the exceptions (`NotFound`, `Conflict`, …) and later cards import them by those names.
- §8.4 also lists start-up checks for `PROMPT_TEMPLATE_VERSION` in the registry, positive caps in staging and production and `supports_structured_output`; the card's step 2 does not include them and their registries and adapters arrive with later cards (IMP-110, IMP-208, IMP-511).
