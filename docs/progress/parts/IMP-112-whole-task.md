# IMP-112 · whole-task part

- Run id: RUN-016
- Owner: Kirtan (kirtan-S111)
- Status: **blocked (hosted steps) by IMP-113, owner Kirtan, 2026-11-02**; the card's local-container path passes
  - Hosted accounts: the Supabase staging project and the Render account do not exist yet, and IMP-113 (draft PR #200) is not merged.
  - Built and run now: steps 1, 4 and 5, plus the local container run.
  - Written as instructions in `docs/guides/deployment.md`, not done: steps 2, 3 and 6.
- Base commit: daeb8e0
- Branch: feat/IMP-112-whole-task
- Reviewer: Junaid (Junaid-Kureshi)
- Traces to: US-002; FR-123; NFR-005, NFR-015, NFR-035; API-01; IMD-38

## Changed files

- `apps/api/Dockerfile` (created, step 1). It builds in two stages on `python:3.12-slim`:
  - **build stage:** builds a wheel of `apps/api`;
  - **runtime stage:** installs the wheel (non-editable, so the templates ship as package data), with no dev extras, tests or migrations, and runs as a non-root user `app` (uid 10001).
  - **Command:** `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`, started through `exec`.
  - **Version:** `BUILD_VERSION` falls back to Render's `RENDER_GIT_COMMIT`, then to `dev`, so `/health` reports the deployed commit for the deploy wait.
  - **Migrations:** none on start (IMD-38).
- `apps/api/.dockerignore` (created). The build context is limited to `pyproject.toml` and `app/`, so `.venv`, tests and env files never reach the image. This file is not in the card's list; it keeps the image and the context small.
- `apps/api/tests/smoke/conftest.py` (created): the `--base-url` and `--web-origin` options and the `base_url`, `web_origin` and `smoke_client` fixtures. Without `--base-url` every smoke test skips.
- `apps/api/tests/smoke/test_deployed.py` (created, step 5; TC-288, TC-351):
  - `GET /health` returns 200 with `status`, `provider` and `environment`;
  - `GET /health/ready` must be 200 when present, and a 404 counts as "not present" (it arrives with IMP-201);
  - a CORS preflight and a simple request from a foreign origin get no `access-control-allow-origin`;
  - with `--web-origin`, the preflight from that origin is allowed.
- `apps/api/tests/smoke/README.md` (modified): how to run the tests locally and against a deployment.
- `.github/workflows/deploy-staging.yml` (created, step 4), job `deploy-staging`:
  - **Trigger:** `workflow_run` of CI, completed on `main`, with the job running only when CI's conclusion is success and its event is push. It never runs on pull requests.
  - **Configuration check:** checks the four `STAGING_*` secrets. If any is missing it prints `staging not configured (blocked by IMP-113)` with the missing names and succeeds.
  - **When configured:** checks out the commit CI tested, then:
    1. `make db-migrate` with the staging `DATABASE_URL`;
    2. the Render deploy hook with `ref=<commit>`;
    3. a wait until `/health` reports the commit;
    4. `make smoke URL=<staging API> ARGS='--web-origin <staging web origin>'`.
- `.github/workflows/deploy-production.yml` (created, step 4), job `deploy-production`:
  - **Trigger:** `workflow_dispatch` with a required `tag` input.
  - **Configuration check:** the same check with the `PRODUCTION_*` secrets.
  - **When configured:** validates the tag format, checks that the tag is on `main`, then runs the same four steps.
- `docs/guides/deployment.md` (created). It covers:
  - the image;
  - the local container run;
  - the deploy secret names and purposes;
  - steps 2 (Render), 3 (Vercel) and the Supabase settings as instructions, each "blocked by IMP-113 (owner Kirtan)";
  - the workflow behaviour and the two unverified Render assumptions;
  - an empty cold-start table for step 6.
- `docs/progress/parts/IMP-112-whole-task.md` (this record).

Not changed:

- app code;
- the `Makefile`: its `smoke` target already runs `pytest tests/smoke --base-url "$(URL)" $(ARGS)` in `apps/api`, as §4.7 says;
- `docker-compose.yml`: the `api` profile and its optional env file from IMP-105 were enough;
- `docs/secrets.md`: draft PR #200 changes it;
- migrations, contracts and CI job names.

## Deploy secret names, for `docs/secrets.md` (to be added by IMP-113's follow-up run)

Store: GitHub Actions secrets store (repository secrets). Owner role: DevOps Engineer and Integration Lead (Kirtan). Purposes are in `docs/guides/deployment.md` section 2.

| Secret | Secret? | Rotation rule to record |
| --- | --- | --- |
| `STAGING_DATABASE_URL` | Yes (database password) | With the staging database password |
| `STAGING_RENDER_DEPLOY_HOOK_URL` | Yes (anyone holding it can trigger a deploy) | Regenerate in Render when exposed |
| `STAGING_API_URL` | No; kept with the others | None |
| `STAGING_WEB_ORIGIN` | No; kept with the others | None |
| `PRODUCTION_DATABASE_URL` | Yes | With the production database password |
| `PRODUCTION_RENDER_DEPLOY_HOOK_URL` | Yes | Regenerate in Render when exposed |
| `PRODUCTION_API_URL` | No | None |
| `PRODUCTION_WEB_ORIGIN` | No | None |

## Commands and results

| Command | Result line |
| --- | --- |
| `git rev-parse --short origin/main` (preflight) | `daeb8e0` |
| `docker info --format '{{.ServerVersion}}'` (preflight) | `29.9.2` |
| `docker build -t group12-api:imp112 apps/api` | `#13 DONE 9.5s` |
| `docker image ls group12-api:imp112` | `image size: 366MB` |
| Inside the image: `id`; `ls <site-packages>/app/ai/prompts/templates/itinerary_generate/v1/`; `pip list` filtered for pytest, ruff, mypy and respx | `uid=10001(app) gid=999(app) groups=999(app)`; `meta.json system.txt user.txt`; `no dev extras`; `no tests or migrations dirs` |
| `make db-up` | ` Container group12-db-1 Healthy ` |
| `docker compose exec -T db psql ... < apps/api/migrations/sql/test_auth_stub.sql` | `auth stub exit 0` |
| `DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/travel_test make db-migrate` | `INFO  [alembic.runtime.migration] Running upgrade 0005 -> 0006, 0006 updated_at triggers; revokes the helper functions and alembic_version from browser roles (Appendix A.7).` |
| `docker compose -f docker-compose.yml -f <scratch override: APP_ENV=local, AI_PROVIDER=MOCK, DATABASE_URL=...@db:5432/travel_test, ALLOWED_ORIGINS=http://localhost:3000> --profile api up -d --build --wait api` | ` Container group12-api-1 Healthy ` (logs: `Uvicorn running on http://0.0.0.0:8000`; no migration on start) |
| `curl -s http://localhost:8000/health` | `{"status":"ok","version":"dev","environment":"local","provider":"MOCK"}` (`/health/ready`: 404, not present yet) |
| `make smoke URL=http://localhost:8000` | `========================= 4 passed, 1 skipped in 0.07s =========================` |
| `make smoke URL=http://localhost:8000 ARGS='--web-origin http://localhost:3000'` | `============================== 5 passed in 0.09s ===============================` |
| Mutation: the image with `ALLOWED_ORIGINS=https://smoke-foreign-origin.invalid` on port 8001, `make smoke URL=http://localhost:8001` | `==================== 2 failed, 2 passed, 1 skipped in 0.11s ====================` (both foreign-origin tests fail, as they should) |
| The image with `PORT=9123` | `Uvicorn running on http://0.0.0.0:9123` |
| The image with `APP_ENV=production` and nothing else | `configuration error: DATABASE_URL is not set; AI_PROVIDER: MOCK is refused when APP_ENV is production` |
| `/health` version with no variable / `RENDER_GIT_COMMIT=abc123` / both `RENDER_GIT_COMMIT=abc123` and `BUILD_VERSION=explicit` | `dev` / `abc123` / `explicit` |
| `docker run --rm -v "$PWD:/repo:ro" -w /repo rhysd/actionlint:latest -no-color` (actionlint 1.7.12; deploy-staging, deploy-production and ci) | no findings, `actionlint exit 0` |
| Skip path (scratch script running each workflow's check step from the YAML with no secrets / one missing / all set) | staging: `exit=0 configured=false` with `staging not configured (blocked by IMP-113)` / `exit=0 configured=false` / `exit=0 configured=true`; production: the same with `production not configured (blocked by IMP-113)`; every later step of both jobs is gated on `configured == 'true'` |
| The staging wait step against the local container with `DEPLOY_SHA=dev` | `staging runs dev (attempt 1)` |
| `pytest tests/smoke -q` without `--base-url` | `5 skipped in 0.02s` |
| `make lint` | `All matched files use Prettier code style!` |
| `make typecheck` | `✓ Types generated successfully` |
| `make imports` | `Contracts: 3 kept, 0 broken.` |
| `make test` | `   Duration  3.97s (environment 63%, tests 15%, setup 12%, import 8%, transform 2%)` (collected 201 unit, 11 contract, 64 api, 9 authz, the same counts as before this card, so no smoke test runs) |
| `make check` | `   Duration  3.85s (environment 54%, tests 17%, setup 17%, import 9%, transform 3%)` (api unit `201 passed`, contract `11 passed`, api `64 passed`, authz `9 passed`, web `48 passed`, `Contracts: 3 kept, 0 broken.`) |
| `docker compose --profile api down`, then `make db-down` | ` Network group12_default Removed ` (no container left) |

## Blocked items (owner Kirtan, 2026-11-02, blocked by IMP-113)

1. **Step 2:** the Render staging web service, with environment variables and auto-deploy off.
2. **Step 3:** the Vercel project for `apps/web`, with the `NEXT_PUBLIC_*` variables.
3. **Secrets:** the staging deploy secrets in the GitHub Actions store.
4. **Step 6:** the cold-start measurements (three) and the wake-up routine.
5. **The first configured deploy-staging run,** with the staging web page and `/health` checked.

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| After a push to main, the staging web page loads and staging GET /health returns 200 (US-002 AC1, TC-288) | not verified | Blocked by IMP-113 (owner Kirtan). `GET /health` 200 is verified on the local container by `make smoke` |
| A browser request from the staging web origin succeeds; one from another origin is refused by CORS (US-002 AC2, NFR-015, TC-351) | verified locally; staging not verified | Local container: the foreign-origin preflight and simple request get no allow header, and `--web-origin http://localhost:3000` is allowed (5 passed); the mutation run shows the tests fail when the foreign origin is allowed. Staging is blocked by IMP-113 |
| The cold-start delay is measured and written in docs/guides/deployment.md (US-002 AC3) | not verified | Blocked by IMP-113; the table in section 7 is empty |
| If IMP-113 accounts are not ready, the task is marked blocked and the local container run (`docker compose up api` + make smoke URL=http://localhost:8000) passes | verified | Marked blocked in this record (the gate writes `docs/progress/sprint-1.md`); `docker compose ... --profile api up api` + `make smoke URL=http://localhost:8000`: `4 passed, 1 skipped` (and `5 passed` with `--web-origin`) |
| Deploy workflows are valid and skip cleanly without secrets (run prompt) | verified locally | actionlint clean; the skip-path simulation ends with exit 0 and the "not configured" message. After merge, the operator confirms that the first deploy-staging run on `main` ends green with that message |

## Blockers

- The hosted steps (2, 3 and 6) and AC1, AC3 and the staging half of AC2 need the IMP-113 accounts (the Supabase staging project and the Render account) and the staging secrets.

## Proposed decisions

- **PD-IMP-112-1, deploy secret names.** The eight names in the table above, `STAGING_*` and `PRODUCTION_*`, held in the GitHub Actions repository secrets. They are to be added to `docs/secrets.md` by IMP-113's follow-up run.
- **PD-IMP-112-2, `BUILD_VERSION` on Render.** Leave `BUILD_VERSION` unset on Render, so the image's start command reports `RENDER_GIT_COMMIT`. This is how "Set by CI (commit SHA)" (§4.5) is met with a deploy hook.

## Open issues

- **Two unverified Render assumptions.** The deploy hook honouring `ref=<commit>`, and `RENDER_GIT_COMMIT` being set in the running container, are checked only on the first configured deploy. If either fails, the wait step times out and the run fails visibly. `docs/guides/deployment.md` section 6 gives the fix.
- **Preview origins.** Vercel preview deployments have their own origins, which the staging API does not allow (exact origins, NFR-015). Previews can show pages, but their API calls are refused.
- **`workflow_run` reads the default branch.** It triggers only from the workflow file on `main`, so `deploy-staging` first runs after this pull request merges. That first run should end green with `staging not configured (blocked by IMP-113)`.
- **Image size.** 366MB, as `docker image ls` reports it uncompressed, most of it the runtime dependencies (`google-genai`, `uvicorn[standard]`, `psycopg[binary]`).
