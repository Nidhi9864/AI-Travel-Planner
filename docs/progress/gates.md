# Gate results

One section per sprint gate (specification §14.1). The gate card of each sprint records the result (pass, pass with listed gaps, or fail), the exit code of each check, open defects and carry-over tasks under its heading.

## SG-1 end of week 1: runnable skeleton and contracts in place (IMP-199)

Status: **pass with listed gaps**

- Run: RUN-017 (IMP-199, Kirtan), 2 November 2026. Part record: [IMP-199-whole-task.md](parts/IMP-199-whole-task.md).
- Commit verified on a clean clone: `4764c5f` (`main` at preflight). `main` then moved to `887e25e` when PR #200 (IMP-113, documentation only) merged at 08:51 UTC; CI and deploy-staging on `887e25e` are recorded below.
- Clean clone: `git clone https://github.com/het-lathiya/Group12.git` into a temporary directory outside the working copy; no `.env` file read or written; the clone was deleted at the end.

### Criteria

| # | Criterion (card IMP-199) | Result | Evidence |
| --- | --- | --- | --- |
| 1 | All commands of step 1 exit 0 on a clean clone | pass | Table "Step 1 on a clean clone" below: six commands, each exit 0 |
| 2 | Local sign-up, sign-in and sign-out work against the Supabase local stack | pass | In the clean clone, local stack keys passed as environment variables only (as RUN-008): `make e2e ARGS='auth'` `  20 passed (32.3s)` (TC-051, TC-052, TC-053 sign-up; TC-054, TC-056 sign-in, reload, sign-out); `make e2e ARGS='smoke'` `  12 passed (11.1s)` (signed-in dashboard and signed-out redirect); `make api` then `curl http://localhost:8000/health`: `{"status":"ok","version":"dev","environment":"local","provider":"MOCK"}` HTTP 200 |
| 3 | CI on main is green (lint, types, imports, unit, guards, audit, api) | pass | [CI run 41416050824](https://github.com/het-lathiya/Group12/actions/runs/41416050824) on `887e25e` (push): lint-types, unit, guards, audit, api success; attribution skipped (it runs on pull requests only). [CI run 41415156650](https://github.com/het-lathiya/Group12/actions/runs/41415156650) on `4764c5f`: the same |
| 4 | Staging `/health` returns 200, or the deployment is recorded as blocked by accounts with an owner | pass (blocked, recorded) | **Deployment blocked by IMP-113, owner Kirtan, 2026-11-02.** IMP-113 merged as templates only (PR #200); no hosted account exists yet. [deploy-staging run 41416325367](https://github.com/het-lathiya/Group12/actions/runs/41416325367) on `887e25e`: success, log line `staging not configured (blocked by IMP-113)` (also [run 41415419222](https://github.com/het-lathiya/Group12/actions/runs/41415419222) on `4764c5f`). Local container smoke (RUN-016 path) in the clean clone: `docker compose ... --profile api up -d --build --wait api` ` Container sg1-clone-api-1 Healthy `; `make smoke URL=http://localhost:8000` `========================= 4 passed, 1 skipped in 0.08s =========================`; with `ARGS='--web-origin http://localhost:3000'` `============================== 5 passed in 0.04s ===============================` |
| 5 | SG-1 entry in docs/progress/gates.md states the result and the evidence links | pass | This entry |

### Step 1 on a clean clone (`4764c5f`)

| Command | Exit | Last line |
| --- | --- | --- |
| `make setup` | 0 | `setup: Playwright browsers skipped (make setup ARGS=--with-browsers installs Chromium)` |
| `make stack-up` | 0 | `  Never paste these values into a tracked file, an issue or a pull request (docs/secrets.md).` |
| `make db-up` | 0 | ` Container sg1-clone-db-1 Healthy ` |
| `make db-migrate DATABASE_URL=postgresql+psycopg://postgres:postgres@127.0.0.1:54322/postgres` | 0 | `INFO  [alembic.runtime.migration] Will assume transactional DDL.` (`alembic current`: `0006 (head)`) |
| `APP_ENV=local DATABASE_URL=<same> make seed` | 0 | `seed sampleton: opening hours replaced for 27 places, unchanged for 3` |
| `make check TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/travel_test` | 0 | `   Duration  6.86s (environment 60%, setup 16%, transform 9%, tests 8%, import 7%)` |

`make check` parts: ruff `All checks passed!`; Prettier `All matched files use Prettier code style!`; mypy `Success: no issues found in 47 source files`; import-linter `Contracts: 3 kept, 0 broken.`; `openapi-check: not yet implemented (IMP-214)`; unit `201 passed, 1 warning in 4.98s`; contract `11 passed in 0.07s`; api `64 passed, 1 warning in 3.57s` (includes the schema-drift test); authz `9 passed in 0.44s`; web `Tests  48 passed (48)`.

Note on `make db-migrate`: the Supabase CLI keeps its database volume across `make stack-down`, so the local stack was already at `0006` from earlier runs and the upgrade had nothing to do. Migration from a blank schema was shown in the same clone on the compose db (`public` dropped, then `make db-migrate`: six `Running upgrade` lines ending `Running upgrade 0005 -> 0006`) and runs on every `api` job in CI (TC-337).

### Contracts on main (step 3)

| Contract | Path | Present |
| --- | --- | --- |
| AI schema gr-1 | `contracts/ai/gr-1.schema.json` | yes |
| AI schema io-1 | `contracts/ai/io-1.schema.json` | yes |
| Error envelope | `apps/api/app/schemas/common.py` (`ErrorCode`, `ErrorDetail`, `ErrorBody`, `ErrorEnvelope`) | yes |
| Migrations 0001-0006, one Alembic head | `apps/api/migrations/sql/0001_helpers.sql` to `0006_updated_at_triggers.sql`; `apps/api/migrations/versions/0001_helpers.py` to `0006_updated_at_triggers.py`; `alembic heads`: `0006 (head)` | yes |
| Environment template | `.env.example` | yes |
| Project instructions | `CLAUDE.md` | yes |

### Working-agreement audit (IMD-68)

Every pull request merged from the start of the project to 2 November 2026 (`gh pr list --state merged`), 14 in all. All were merged by the operator account `het-lathiya`. "Checks green" means all six required checks succeeded on the merged head commit.

| PR | Title | reviewDecision | Approving reviewer | Reviewer owns a part of the card / is the operator | Checks green on merged head | Meets the agreement |
| --- | --- | --- | --- | --- | --- | --- |
| #1 | IMP-101 · repo-tree-makefile part | none | none (Junaid-Kureshi requested) | n/a | n/a (no checks: CI was added by PR #3) | **no**: no approval, no checks |
| #2 | IMP-101 · api-pyproject-guard part | APPROVED | kirtan-S111 | yes, owns repo-tree-makefile of IMP-101 / no | n/a (no checks: CI was added by PR #3) | **no**: no checks; reviewer owns a part of the card |
| #3 | IMP-102 · whole task | none | none (Junaid-Kureshi requested) | n/a | yes (6/6) | **no**: no approval |
| #190 | IMP-103 · whole task | none | none (kirtan-S111 requested) | n/a | yes (6/6) | **no**: no approval |
| #191 | IMP-105 · whole task | none | none (jeelfefar2141 requested) | n/a | yes (6/6) | **no**: no approval |
| #192 | IMP-104 · whole task | none | none (Assassin-byte requested) | n/a | yes (6/6) | **no**: no approval |
| #193 | IMP-106 · sql-migrations and orm-drift-fixture parts | none | none (kirtan-S111 requested) | n/a | yes (6/6) | **no**: no approval |
| #194 | IMP-109 · whole task | none | none (Manasvi1704 requested) | n/a | yes (6/6) | **no**: no approval |
| #195 | IMP-110 · whole task | none | none (kirtan-S111 requested) | n/a | yes (6/6) | **no**: no approval |
| #196 | IMP-108 · whole task | none | none (manalPatel2557 requested) | n/a | yes (6/6) | **no**: no approval |
| #197 | IMP-107 · whole task | none | none (Malhar1112-v requested) | n/a | yes (6/6) | **no**: no approval |
| #198 | IMP-111 · whole task | none | none (Nidhi9864 requested) | n/a | yes (6/6, after a cancelled first run) | **no**: no approval |
| #200 | IMP-113 · accounts-secrets-register, ors-email-sender and gemini-key-terms parts | none | none | n/a | yes (6/6) | **no**: no approval; merged during this gate run while expected to stay a draft |
| #202 | IMP-112 · whole task | none | none (Junaid-Kureshi requested) | n/a | yes (6/6) | **no**: no approval |

Summary: 14 merged; 1 with an approval (#2, from a reviewer who owns another part of the card); 12 with all six checks green on the merged head and 2 that predate CI; **no merged pull request meets the working agreement in full**, because 13 have no approving review. Nothing was changed on these pull requests. Every merged pull request has its part records on `main`.

### Gaps and open defects

- No severity 1 or 2 defect found in the gate's scope.
- Staging not deployed: blocked by IMP-113 (accounts), owner Kirtan, 2026-11-02 (the gate's acceptable known defect).
- Working agreement not met by any merged pull request (audit above); TC-343's "cannot be merged" half stays not verified (IMD-79).
- TC-335 setup walkthrough: about 100 minutes against a 60-minute target (NFR-032 not met; measured by Nidhi on 1 November 2026).
- No screenshot of a local sign-in was taken in this run (the SG-1 evidence column lists one); sign-in is shown by the Playwright auth run above, and the IMP-109 record holds its sign-up screenshot.

### Carry-over

| Item | Owner | Reference |
| --- | --- | --- |
| IMP-113 outcomes: accounts, secrets register, OpenRouteService key, email sender, Gemini key and terms (templates merged, results "TO BE FILLED") | Kirtan, Junaid, Nidhi | PR #200 (merged as templates) |
| IMP-114 stakeholder interviews round 1 | Junaid, Krrish | draft PR #201 |
| IMP-115 seed-data plan and the two demo destinations | Malhar | draft PR #199 |
| IMP-112 hosted half: staging deployment, staging `/health` 200, hosted RLS check | Kirtan | `docs/guides/deployment.md`; after IMP-113 |
| TC-335 over target (100 minutes against 60): shorten `docs/guides/local-setup.md` or the image download step | Malhar (guide owner) | NFR-032 |
| PD-H follow-up: `make setup` upgrades `pip` in the venv so the pip audit can become blocking | Kirtan | IMD-76 |
| AuthGuard loads `['me']` (API-03) once | web, later card (IMP-601, Het) | IMP-108 and IMP-109 records |
| `apps/web/lib/api/client.ts` generated client | Kirtan (IMP-214) | IMD-98 |
| Start-up check that `PROMPT_TEMPLATE_VERSION` exists in the registry | Nidhi (IMP-208) | IMP-111 record |
| `repair.txt` for `itinerary_generate/v1` adds its line to `tests/fixtures/prompt_hashes.json` | Nidhi (IMP-502) | IMP-111 record |
| Working agreement: approvals before merge from now on | Kirtan (integration lead), all reviewers | IMD-68 |

## SG-2 end of week 2: walking skeleton (blueprint Gate 1, IMP-299)

Status: not run

## SG-3 end of week 3: Gemini vertical slice (blueprint Gate 2, IMP-399)

Status: not run

## SG-4 end of week 4: core reliability (blueprint Gate 3, IMP-499)

Status: not run

## SG-5 end of week 5: trip management (IMP-599)

Status: not run

## SG-6 end of week 6: MVP feature freeze (IMP-699)

Status: not run

## SG-7 end of week 7: release candidate and extension freeze (IMP-799)

Status: not run

## SG-8 week 8: release and demo (IMP-899)

Status: not run
