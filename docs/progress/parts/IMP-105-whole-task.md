# IMP-105 · whole-task part

- Run id: RUN-005
- Owner: Malhar (Malhar1112-v)
- Status: PR_OPEN
- Base commit: a54493f
- Branch: feat/IMP-105-whole-task
- Reviewer: Jeel (jeelfefar2141)
- Traces to: US-003; FR-124; NFR-013, NFR-032, NFR-035
- Card steps built: 1 to 6

## Changed files

- `supabase/config.toml` (created by `supabase init`, step 1): default ports kept (API 54321, DB 54322, Studio 54323, Inbucket/Mailpit 54324 under `[local_smtp]` in this CLI version); only two lines changed from the generated file: `site_url = "http://localhost:3000"` and `additional_redirect_urls = ["http://localhost:3000", "http://localhost:3000/auth/callback"]`.
- `supabase/.gitignore` (created by `supabase init`, kept): ignores the CLI's `.branches`, `.temp` and dotenvx files. `supabase init` (CLI 2.122.0, non-interactive by default; IDE settings are only asked with `-i`) created nothing else to delete: no `seed.sql`, no `functions/`, no editor settings. Its `supabase/.temp/` is ignored by both `.gitignore` files.
- `docker-compose.yml` (created, step 2): service `db` (postgres:16, port 5432, `POSTGRES_PASSWORD=postgres`, database `travel_test`, healthcheck `pg_isready -U postgres -d travel_test`, data on `tmpfs` so every start is blank and `make db-down` leaves no volume) and service `api` (build `apps/api/Dockerfile`, `env_file apps/api/.env`, port 8000) for IMP-112.
- `.env.example` (created, step 3): the §4.5 block copied verbatim (extracted from the specification with `awk`, 55 lines, 38 names, same order, placeholders and defaults).
- `apps/web/.env.local.example` (created, step 3): only the four `NEXT_PUBLIC_*` lines of `.env.example`.
- `Makefile` (modified, Kirtan's file, step 4): only the `stack-up`, `stack-down`, `db-up` and `db-down` targets. They ran behind "not yet implemented (IMP-105)" guards until this card; now `stack-up` runs `supabase start` and prints where `JWT_SECRET`, `ANON_KEY` and `SERVICE_ROLE_KEY` from `supabase status -o env` go (it never prints a key), `stack-down` runs `supabase stop`, `db-up` runs `docker compose up -d --wait db` (the §4.7 command plus `--wait`, so it returns once `db` is healthy), and `db-down` runs `docker compose down` (§4.7).
- `.github/workflows/ci.yml` (modified, Kirtan's file, step 5): one step, "Fail if a real env file is tracked", added at the start of the `guards` job. No job renamed or added.
- `docs/guides/local-setup.md` (created, step 6): Linux, macOS and Windows with WSL2 (Ubuntu 24.04, Docker Desktop with WSL integration); timed steps adding up to about 60 minutes (NFR-032); ends with `make api`, the `/health` check and `make web`; troubleshooting; how to record the setup time (TC-335).
- `docs/secrets.md` (created, step 6): variable, secret or not, owner role, where stored, rotation rule; no values. IMP-113 adds the hosted accounts and confirms the owners.
- This record (created).

**`.gitignore` (root) not changed.** Step 5's three entries are already covered by IMP-101's patterns: `.env` matches `.env` and `apps/api/.env` (a pattern without a slash matches at any depth), and `.env.local` matches `apps/web/.env.local`. Checked with `git check-ignore -v --no-index` (`.gitignore:2:.env` for `.env` and `apps/api/.env`).

**`apps/web/.env.local.example` is force-added.** `apps/web/.gitignore:35` (`.env.*`, Kirtan's file, outside this part's file list) ignores the template. Once a file is tracked, ignore rules no longer apply to it, so it was added once with `git add -f` and future edits are tracked normally. See open issues for the one-line follow-up.

## The env-file guard (step 5, note d)

```bash
tracked="$(git ls-files | grep -E '(^|/)(\.env(\..+)?|[^/]+\.env)$' \
  | grep -vxE '\.env\.example|apps/web/\.env\.local\.example' || true)"
```

It fails (exit 1, one `::error` annotation and the file list) when any tracked file is named `.env`, `.env.<anything>` or `<name>.env` at any depth, except the two templates at their exact paths. Local test: the step's `run` text was extracted from `ci.yml` with PyYAML into a scratch file and run with `bash -e`, so the text tested is the text CI runs.

| Tree | Result |
| --- | --- |
| Real repository index (with both templates staged) | `No real env file is tracked.`, exit 0 |
| Scratch clone of this branch outside the repository, clean | `No real env file is tracked.`, exit 0 |
| Same clone with `apps/api/.env` tracked (`git add -f`, placeholder content) | `::error title=Tracked env file::remove these files from git and keep them local:` / `apps/api/.env`, exit 1 |
| … with `.env.local` tracked | lists `.env.local`, exit 1 |
| … with `apps/web/.env.local` tracked | lists `apps/web/.env.local`, exit 1 |
| … with `prod.env` tracked | lists `prod.env`, exit 1 |
| … with `.env.production` tracked | lists `.env.production`, exit 1 |
| Same clone after untracking the file again | `No real env file is tracked.`, exit 0 |

## docker-compose `api` service (note c)

Both safeguards are used: the `api` service sits behind the profile `api`, and its `env_file` is `{path: apps/api/.env, required: false}`. `docker compose config --services` lists only `db` without the profile (`db`, `api` with `--profile api`). So `make db-up` neither builds the missing `apps/api/Dockerfile` nor needs `apps/api/.env` on a fresh clone. IMP-112 starts it by name (`docker compose up --build api`), which turns the profile on. Reaching the stack database from inside that container (`127.0.0.1` is the container itself) is left to IMP-112's smoke.

## Name check: `.env.example` and `Settings` (note b, report only)

Script over `.env.example` and `app.core.config.Settings.model_fields` (apps/api venv):

```text
names in .env.example: 38 | backend names: 34 | Settings fields: 32
in .env.example, not in Settings: ['SEED_DIRS', 'SUPABASE_SERVICE_ROLE_KEY']
in Settings, not in .env.example: []
duplicates: []
```

There is no mismatch against the specification. In §4.5, `SUPABASE_SERVICE_ROLE_KEY` is "E2E user fixture only" and `SEED_DIRS` is "Makefile variable for `make seed`". Neither is read by the API, and the IMP-103 record leaves both out of `Settings` for that reason. Every `Settings` field has its name in `.env.example`. No proposed decision is needed.

## Commands run

Keys are redacted in every block below (`<redacted>`).

| Command | Result line (quoted exactly) |
| --- | --- |
| Preflight: `git fetch origin; git status --porcelain --untracked-files=no` | no output; base `git rev-parse --short origin/main` → `a54493f` |
| Preflight: `docker info --format '{{.ServerVersion}}'`; `supabase --version`; `docker compose version` | `29.9.2`; `2.122.0`; `Docker Compose version v5.6.1` |
| Preflight: ports `ss -ltnp \| grep -E ':(5432\|5432[0-9]\|8000\|3000)\b'` | no output (no port in use; note g) |
| `supabase init < /dev/null` | `Finished supabase init.` |
| `docker compose config --quiet` | exit 0 |
| `make stack-up` (first run, image pulls) | `real	18m52.120s`, exit 0; last lines are the four hint lines, ending `  Never paste these values into a tracked file, an issue or a pull request (docs/secrets.md).` |
| `make db-up` (first run) | ` Container group12-db-1 Healthy `, exit 0 |
| `docker compose exec -T db psql -U postgres -d travel_test -Atc "select current_database(), split_part(version(), ' ', 2)"` | `travel_test\|16.15` |
| psycopg connect to `postgresql://postgres:postgres@localhost:5432/travel_test` from the host | `travel_test via host port 5432` |
| Card command `make stack-up && make db-up && docker compose ps` (images cached) | `group12-db-1   postgres:16   "docker-entrypoint.s…"   db        18 minutes ago   Up 18 minutes (healthy)   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp`; `real	0m2.476s` |
| `supabase status --agent no` | `supabase local development setup is running.` (table below) |
| `supabase status -o env` (names only) | `ANON_KEY`, `JWT_SECRET` and `SERVICE_ROLE_KEY` present; `ANON_KEY` header `{'alg': 'HS256', 'typ': 'JWT'}` (header only decoded), so the local stack issues HS256 tokens as IMD-04 expects |
| Guard test (table above) | real tree exit 0; tracked `apps/api/.env` exit 1 |
| `make lint` | `All matched files use Prettier code style!` (API part: `All checks passed!`) |
| `make typecheck` | `✓ Types generated successfully` (API part: `Success: no issues found in 20 source files`) |
| `make imports` | `Contracts: 3 kept, 0 broken.` |
| `make test` | exit 0; unit `======================== 74 passed, 1 warning in 2.34s =========================`; contract and authz `pytest: no tests collected (exit 5 treated as success)`; api `======================== 13 passed, 1 warning in 0.35s =========================`; web `No test files found, exiting with code 0` |
| `make check` | exit 0; `openapi-check: not yet implemented (IMP-214)`; unit `======================== 74 passed, 1 warning in 2.10s =========================`; api `======================== 13 passed, 1 warning in 0.36s =========================`; web `No test files found, exiting with code 0` |
| `make stack-down` (end of run) | `{"project_id_filter":"Group12","backup":true,"message":"Stopped supabase local development setup."}`, exit 0 |
| `make db-down` (end of run) | ` Network group12_default Removed `, exit 0; `docker ps` lists 0 containers afterwards |

### `supabase status` (keys redacted)

```text
Stopped services: [supabase_imgproxy_Group12 supabase_pooler_Group12]
supabase local development setup is running.

│ Studio  │ http://127.0.0.1:54323     │
│ Mailpit │ http://127.0.0.1:54324     │
│ MCP     │ http://127.0.0.1:54321/mcp │

│ Project URL    │ http://127.0.0.1:54321              │
│ REST           │ http://127.0.0.1:54321/rest/v1      │
│ GraphQL        │ http://127.0.0.1:54321/graphql/v1   │
│ Edge Functions │ http://127.0.0.1:54321/functions/v1 │

│ URL │ postgresql://postgres:postgres@127.0.0.1:54322/postgres │

│ Publishable │ <redacted> │
│ Secret      │ <redacted> │

│ URL        │ http://127.0.0.1:54321/storage/v1/s3 │
│ Access Key │ <redacted> │
│ Secret Key │ <redacted> │
│ Region     │ local      │
```

The two "stopped services" (image proxy, connection pooler) are disabled in the default `config.toml`; the stack does not need them.

### `docker compose ps`

```text
NAME           IMAGE         COMMAND                  SERVICE   CREATED          STATUS                    PORTS
group12-db-1   postgres:16   "docker-entrypoint.s…"   db        18 minutes ago   Up 18 minutes (healthy)   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp
```

## Not run

| Command | Reason |
| --- | --- |
| `gitleaks` locally | Not installed on this machine; the secret scan is the `guards` job on this pull request (pinned gitleaks 8.30.1) |
| `make api` and `make web` following the guide's steps 3 and 7 | Creating or inspecting `apps/api/.env` and `apps/web/.env.local` was not permitted in this run's tool sandbox, so the walkthrough with real env files was not performed here. `GET /health` with the local defaults is shown in the IMP-103 record; the full walkthrough is criterion 4 (human) |
| `make e2e` | No journey touched |
| `make openapi` | No API change; the target is still `not yet implemented (IMP-110, IMP-214)` |

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| `make stack-up` starts the local stack and `supabase status` lists API URL 127.0.0.1:54321 and DB 127.0.0.1:54322 | verified | `make stack-up` exit 0; `supabase status` above: Project URL `http://127.0.0.1:54321`, database `127.0.0.1:54322` |
| `make db-up` starts postgres:16 and `docker compose ps` shows db healthy | verified | `docker compose ps` above (`postgres:16`, `(healthy)`); `travel_test\|16.15` |
| .env.example contains only placeholders and defaults; the secret scan passes (TC-354); a tracked .env file fails CI (NFR-013) | verified locally; CI part pending on this PR | `.env.example` is the §4.5 block verbatim; guard test above (tracked `apps/api/.env` exit 1, real tree exit 0); gitleaks and the guard step run in the `guards` job of this pull request |
| A member outside the platform squad follows docs/guides/local-setup.md to a running API and web app; time taken is recorded (TC-335) | not verified | Human activity; the operator reports the member and the time later |

## Blockers

None.

## Proposed decisions

None. The name check found no mismatch between §4.5 and `core/config.py`.

## Open issues

- **TC-335 pending:** a member outside the platform squad follows the guide and the time is recorded (criterion 4).
- **`apps/web/.gitignore` follow-up (Kirtan's file):** add `!.env.local.example` after line 35 (`.env.*`), so the template does not look ignored to tools that read ignore rules. The file is tracked (force-added), so git itself is unaffected.
- **`docs/guides/contributing.md` §4 (not in this part's files):** the `guards` row says gitleaks only; it should also say "fails when a real env file is tracked". One-line follow-up for the file's owner.
- **The card asks for the outputs in `docs/progress/sprint-1.md`;** they are in this record instead (CLAUDE.md §11 item 5). The SG-1 gate card compiles `sprint-1.md`.
- **The first `make stack-up` took 18m52s** on this machine (image pulls); the guide budgets about 20 minutes for it (step 4) and about 56 minutes in all. Later starts take seconds (2.5 s for the card command with cached images). If many members set up on slow connections, the 60-minute target (NFR-032) depends mostly on this download.
- **The CLI prints `no files matched pattern: supabase/seed.sql` on start.** `[db.seed]` in `config.toml` points at the CLI's default `seed.sql`, which this card does not create (seed data is `make seed`, IMP-107). The warning is harmless. IMP-107 may switch `[db.seed] enabled = false` if it wants a quiet start.
- **The local stack runs Postgres 17** (`[db] major_version = 17`, the CLI default, matching new hosted Supabase projects), while the test database is postgres:16 as the card and §5 say. Both run the same Appendix A SQL. Recorded for IMP-106 in case a version-specific difference appears.
- **New Supabase CLI key names:** `supabase status` now shows Publishable and Secret keys in its table; `supabase status -o env` still gives `JWT_SECRET`, `ANON_KEY` and `SERVICE_ROLE_KEY`, which the guide and the Makefile hints use.
