# IMP-201 · whole-task part

- Run id: RUN-029
- Owner: Kirtan (kirtan-S111)
- Status: PR_OPEN
- Base commit: d2cfbe2
- Branch: feat/IMP-201-whole-task
- Reviewer: Junaid (Junaid-Kureshi)
- Traces to: US-005, US-006; FR-123, FR-125; NFR-013, NFR-047; TC-288, TC-289, TC-292, TC-293, TC-342, TC-358
- Card steps built: 1 to 5
- Prerequisites found:
  - IMP-106 and IMP-103 are merged (their part records exist).
  - API-02 is declared in `contracts/openapi.v1.json` (IMP-214) and answered 501 `NOT_IMPLEMENTED`.
  - The declared `ReadinessOut` is `{status: ready|degraded|not_ready, version, checks: {database: ok|down, migration, provider: {name, model_id, status: ok|degraded|down}}}`. It matches §6 API-02, so it is used unchanged and the contract does not change.

## Changed files

- **Step 1: `apps/api/app/core/health.py` (modified).** API-02 `GET /health/ready`:
  - The database check opens a fresh connection (NullPool) with a 2 s timeout, runs `select 1`, then reads `alembic_version`.
  - The applied revision is compared with `MIGRATION_HEAD` (`"0007"`).
  - The provider status comes from the active provider's `health_check()`, through `app.ai.factory.get_model_provider` (IMP-208). It is cached on the app for 60 s.
  - The database down answers 503 with the same `ReadinessOut` body: `not_ready`, `database: down`, `migration: behind`.
  - A provider that is not `ok`, or a database behind the head, answers 200 `degraded` (PD-12, FR-044 AC2).
  - A failed check logs only the exception class name, never the URL or host.
- **Steps 2 and 3: `apps/api/app/core/logging.py` (created).**
  - `JsonFormatter` writes one JSON object per line: timestamp, level, logger, message and request_id, plus user_hash, method, route, status and latency_ms when present, and the exception text when there is one.
  - `RedactionFilter`, on the handler, so it covers every logger:
    - redacts Authorization and Bearer values;
    - redacts `*key*`, `*secret*`, `*token*` and `*password*` assignments in the text, and the values of extra fields with those names;
    - replaces e-mail addresses with `[redacted]`, also in tracebacks;
    - drops the fields `prompt`, `system_text`, `user_text` and `notes`.
  - `configure_logging(LOG_LEVEL)` installs the handler once on the root logger and routes uvicorn's loggers through it. It switches uvicorn's own access log off, because that log prints the raw path and query string.
- **Step 4: `apps/api/app/core/request_id.py` (modified).**
  - The middleware times every request and writes one `app.access` line: request_id, method, route template (the full `/api/v1/...` template from FastAPI's route contexts, never the raw path), status, latency_ms and user_hash.
  - `user_hash(user_id)` is the first 12 hex characters of the SHA-256 of the ID. It is filled from `request.state.user_id` when that is set.
  - The error envelope already carries `request_id` (IMP-103), unchanged.
- **`apps/api/app/main.py` (modified, 2 lines).** The `app.main:app` entry point (uvicorn, `make api`, the image) calls `configure_logging(settings.log_level)`. `create_app` does not, so tests that build apps do not reconfigure logging.
- **Step 5: `apps/api/tests/api/test_health.py` (modified).** Readiness tests:
  - 200 `ready` with the migrated test database;
  - TC-289: 503 `not_ready` with `database: down` on a closed port, and no password or host in the body;
  - 200 `degraded` with the provider down (GEMINI before IMP-301);
  - 200 `degraded` and `behind` when the head differs;
  - the provider check is called once in three requests (cache);
  - TC-342: a client X-Request-ID is echoed on readiness;
  - `MIGRATION_HEAD` equals the head of `migrations/versions`.
- **Step 5: `apps/api/tests/unit/core/test_logging.py` (created).**
  - TC-292: one access line per request with request_id and latency_ms.
  - The route template, not the path.
  - user_hash.
  - TC-293 and TC-358: requests with an e-mail and a fake key in the query and headers leave neither in the output.
  - The filter on messages, extras and tracebacks.
  - `redact_text` cases.
  - The LOG_LEVEL threshold, and the handler replaced rather than duplicated.
- **Outside the card's Files list (see PD-IMP-201-2): `apps/api/tests/authz/test_route_inventory.py` (4 lines).** The public-route rule is kept: 200, or 501 only with `NOT_IMPLEMENTED`. The one addition is that `/health/ready` may answer the §6 API-02 503 when the test app has no database, and only with `checks.database == "down"`.
- **Outside the card's Files list (see PD-IMP-201-2): `apps/api/tests/contract/test_openapi_contract.py`.** `test_declared_route_answers_501_with_the_envelope` used API-02 as its example of an IMD-37 stub. It now uses API-33 (`GET /trips/{id}/costs`, a stub until IMP-308), with the token dependency overridden.
- This record (created).

Unchanged:
- `contracts/openapi.v1.json` and the web types (`make openapi-check` passes);
- the §6.3 envelope, `X-Request-ID` and `LOG_LEVEL`;
- `core/config.py` and the auth module;
- migrations, `infra/aws/`, the workflows and the Dockerfile.

## Sample access line

From a request to `/health?email=someone@example.test` with an Authorization header; neither appears in the line:

```json
{"timestamp": "2026-11-03T07:00:32.138396+00:00", "level": "INFO", "logger": "app.access", "message": "request", "request_id": "5f0c1d2e-3a4b-4c5d-8e9f-0a1b2c3d4e5f", "user_hash": null, "method": "GET", "route": "/health", "status": 200, "latency_ms": 46.7}
```

The card's completion evidence asks for this line in `docs/progress/sprint-2.md`. The run forbids editing that file, so it is here for the gate card (IMP-299) to copy.

## Checks that the tests can fail

- With the redaction filter removed from the handler, `test_logging.py` failed: `2 failed, 9 passed, 1 warning in 0.54s`.
- With the 503 changed to 200, `test_health.py -k ready` failed: `1 failed, 6 passed, 13 deselected, 1 warning in 1.03s`.
- Both changes were reverted.

## Commands run

| Command | Result |
| --- | --- |
| `make db-up` | `Container group12-db-1 Healthy` |
| `make test-api ARGS='-k health'` | `20 passed, 189 deselected, 1 warning in 2.18s` |
| `make test-unit ARGS='-k logging'` | `11 passed, 374 deselected, 1 warning in 0.84s` |
| `make lint` | `All checks passed!`, `129 files already formatted`, `All matched files use Prettier code style!` |
| `make typecheck` | `Success: no issues found in 79 source files` |
| `make imports` | `Contracts: 4 kept, 0 broken.` |
| `make openapi-check` | `openapi-check: contracts/ and apps/web/lib/api/schema.d.ts are up to date` |
| `make test` | unit `385 passed, 1 warning in 9.28s`; contract `35 passed, 1 warning in 0.98s`; api `209 passed, 1 warning in 49.97s`; authz `9 passed in 1.97s`; web `Tests  54 passed (54)` |
| `make check` | exit 0, with the lines above |
| `make db-down` | run at the end |

## Not run

- `make e2e`: no journey changed.
- Readiness and log output on AWS staging (CloudWatch): not available until IMP-217, IMP-218 and IMP-299.

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| GET /health returns status and version (FR-123 AC1, TC-288) | verified | `test_health_returns_status_version_environment_provider` (unchanged, passes) |
| With the database unreachable, GET /health/ready returns 503 not_ready naming database (FR-123 AC2, TC-289) | verified | `test_health_ready_database_down_is_503_not_ready` |
| Each request produces one log line with request_id and latency_ms (FR-125 AC1, TC-292) | verified | `test_logging_one_access_line_per_request` |
| No log line contains a prompt body, email address, token or key value (FR-125 AC2, TC-293, TC-358) | verified | `test_logging_request_with_email_and_key_leaves_neither_in_the_log`, `test_logging_filter_redacts_messages_extras_and_exceptions` |
| Responses carry X-Request-ID; a client-supplied UUID is echoed (TC-342) | verified | `test_health_echoes_a_client_request_id`, `test_health_ready_echoes_a_client_request_id` |
| NFR-013, NFR-047 (structured logs without secrets; readiness) | verified locally; not verified on staging | The tests above; CloudWatch output after IMP-218 |

## Blockers

None.

## Proposed decisions

- **PD-IMP-201-1 (migration head constant):** the API image ships no `migrations/` folder (Dockerfile, IMD-38), so readiness cannot read the Alembic head at run time. The expected head is `app.core.health.MIGRATION_HEAD`, and `test_health_ready_migration_head_matches_the_migrations` fails until a new migration card updates it. Proposed: name this on the migration cards (each migration updates `MIGRATION_HEAD`).
- **PD-IMP-201-2 (two test files outside the Files list):**
  - The authz inventory test builds its app with an unreachable database. With API-02 built as specified, `/health/ready` answers 503 there, so the test now accepts that answer for this route only, and only with `database: down`.
  - The IMD-37 contract test used API-02 as its stub example; it now uses API-33.
  - Proposed: add both files to the card.
- **PD-IMP-201-3 (migration behind):** §6 does not say what a database behind the head answers. It is reported as 200 `degraded` with `migration: behind`, because only the database down is a 503 in §6.

## Open issues

- **user_hash is not filled yet.** The access line reads `request.state.user_id`, but the `CurrentUser` dependency (auth module) does not set it. The run forbids touching the auth module while PR #229 is open. The fix is one line in `app/auth/deps.py` (`request.state.user_id = claims.user_id`) and belongs to a follow-up once #229 merges.
- **Uvicorn's access log is switched off** by `configure_logging`, because it prints raw query strings. The `app.access` line replaces it.
