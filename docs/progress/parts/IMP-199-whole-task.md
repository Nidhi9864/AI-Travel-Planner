# IMP-199 · whole-task part

- Run id: RUN-017
- Owner: Kirtan (kirtan-S111)
- Status: PR_OPEN
- Base commit: 887e25e (preflight and the clean-clone gate checks ran on 4764c5f; `main` moved to 887e25e when PR #200, IMP-113 documentation only, merged during the run, and the branch was rebased onto it before any commit)
- Branch: feat/IMP-199-gate
- Reviewer: Junaid (Junaid-Kureshi)
- Traces to: NFR-032, NFR-034, NFR-048; IMD-64 to IMD-98
- Gate result: **SG-1 pass with listed gaps** (see `docs/progress/gates.md`, SG-1)

## Changed files

- `docs/progress/sprint-1.md` (modified): compiled from the part records, one line per Sprint 1 part with status, PR, run id, points credited and evidence; IMP-112 hosted half blocked by IMP-113; TC-335 result. No extension parts were listed in the file, so none were added.
- `docs/progress/gates.md` (modified): SG-1 entry with the criteria, step-1 table, contracts, working-agreement audit, gaps and carry-over.
- `docs/spec/DECISION_REGISTER.md` (modified, rows appended after IMD-63 only): IMD-64 to IMD-68 (team decisions D1 to D5) and IMD-69 to IMD-98 (30 implementation decisions accepted as built, D6).
- `docs/guides/contributing.md` (modified): one run, branch and pull request per card (IMD-66) and the working agreement (IMD-68).
- `docs/progress/parts/IMP-199-whole-task.md` (created): this record.

## Commands run

| Command | Result line (quoted exactly) |
| --- | --- |
| `git fetch origin`; `git status --porcelain --untracked-files=no` (preflight) | prints nothing |
| `git rev-parse --short origin/main` (preflight) | `4764c5f` |
| `docker info --format '{{.ServerVersion}}'`; `docker ps` | `29.9.2`; no container running |
| `git config core.hooksPath` | `.githooks` |
| G1 clean clone `git clone https://github.com/het-lathiya/Group12.git <tmp>` | exit 0, head `4764c5f` |
| G1 `make setup` | exit 0; `setup: Playwright browsers skipped (make setup ARGS=--with-browsers installs Chromium)` |
| G1 `make stack-up` | exit 0; `  Never paste these values into a tracked file, an issue or a pull request (docs/secrets.md).` |
| G1 `make db-up` | exit 0; ` Container sg1-clone-db-1 Healthy ` |
| G1 `make db-migrate DATABASE_URL=postgresql+psycopg://postgres:postgres@127.0.0.1:54322/postgres` | exit 0; `INFO  [alembic.runtime.migration] Will assume transactional DDL.` (already at `0006 (head)`, see gates.md) |
| G1 `APP_ENV=local DATABASE_URL=<same> make seed` | exit 0; `seed sampleton: opening hours replaced for 27 places, unchanged for 3` |
| G1 `make check TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/travel_test` | exit 0; `   Duration  6.86s (environment 60%, setup 16%, transform 9%, tests 8%, import 7%)` |
| G2 `make e2e ARGS='auth'` (local keys as environment variables only) | `  20 passed (32.3s)` |
| G2 `make e2e ARGS='smoke'` | `  12 passed (11.1s)` |
| G2 `make api`, then `curl http://localhost:8000/health` | `{"status":"ok","version":"dev","environment":"local","provider":"MOCK"}` HTTP 200 |
| G4 compose db: drop `public`, `make db-migrate` (test URL) | `INFO  [alembic.runtime.migration] Running upgrade 0005 -> 0006, 0006 updated_at triggers; revokes the helper functions and alembic_version from browser roles (Appendix A.7).` |
| G4 `docker compose -f docker-compose.yml -f <scratch override> --profile api up -d --build --wait api` | ` Container sg1-clone-api-1 Healthy ` |
| G4 `make smoke URL=http://localhost:8000` | `========================= 4 passed, 1 skipped in 0.08s =========================` |
| G4 `make smoke URL=http://localhost:8000 ARGS='--web-origin http://localhost:3000'` | `============================== 5 passed in 0.04s ===============================` |
| G4 `gh run list --workflow deploy-staging.yml --branch main -L 5` | latest: run 41416325367 on `887e25e`, success; log `staging not configured (blocked by IMP-113)` |
| G5 `gh run list --workflow ci.yml --branch main -L 1` | run 41416050824 on `887e25e`, success: lint-types, unit, guards, audit, api success; attribution skipped (pull requests only) |
| G6 `gh pr list --state merged`, `gh pr view <n> --json reviews,statusCheckRollup` | 14 merged pull requests audited (table in gates.md) |
| Board: `gh issue close <n> --reason "not planned" --comment "Cut by IMD-65 (team decision, 1 November 2026)"` × 26 | 26 closed as not planned (one call reported an error but the issue, #170, was closed with the comment; confirmed through the API) |
| Cleanup: compose `down`, `make db-down`, `make stack-down`, delete the clone | `Stopped supabase local development setup.`; clone deleted; no container left |
| Branch: `make db-up` | exit 0 |
| Branch: `make lint` | `All matched files use Prettier code style!` |
| Branch: `make check TEST_DATABASE_URL=<test url>` | exit 0; `   Duration  4.92s (environment 63%, setup 16%, tests 12%, import 7%, transform 2%)` (unit 201, contract 11, api 64, authz 9 passed; web 48 passed) |
| Branch: `make db-down` | exit 0 |

## Not run

| Command | Reason |
| --- | --- |
| Manual browser walk-through of step 2 and a sign-in screenshot | Sign-up, sign-in and sign-out were shown by the Playwright auth spec against the local stack; no screenshot was taken in this run (listed as a gap in gates.md) |
| Staging web and `/health` check | Blocked by IMP-113 (no hosted accounts), owner Kirtan, 2026-11-02 |

## Working-agreement audit (G6) summary

14 merged pull requests (#1, #2, #3, #190 to #198, #200, #202), all merged by `het-lathiya`. One has an approving review (#2, by kirtan-S111, who owns the other IMP-101 part). Twelve had all six checks green on the merged head; #1 and #2 predate CI. None meets the working agreement in full. PR #200 (IMP-113) merged during this run while the run prompt expected it to be an open draft. Nothing was changed on any of them.

## Board

26 extension issues closed as not planned (IMP-515, IMP-612, IMP-613, IMP-708 to IMP-713: #112, #113, #138 to #143, #159 to #176). Nothing else was closed. Board after the gate: 141 open, 42 closed.

## Acceptance criteria

| Criterion | Status (pass / fail / not verifiable) | How |
| --- | --- | --- |
| All commands of step 1 exit 0 on a clean clone (G1) | pass | Clean clone of `4764c5f`: six commands, exit 0 each |
| Local sign-up, sign-in and sign-out work against the Supabase local stack (G2) | pass | `make e2e ARGS='auth'` `  20 passed (32.3s)`; `make e2e ARGS='smoke'` `  12 passed (11.1s)` |
| CI on main is green (lint, types, imports, unit, guards, audit, api) (G5) | pass | Run 41416050824 on `887e25e` |
| Staging /health returns 200, or the deployment is recorded as blocked by accounts with an owner (G4) | pass (blocked, recorded) | "deployment blocked by IMP-113, owner Kirtan, 2026-11-02"; deploy-staging run 41416325367; local container smoke passed |
| SG-1 entry in docs/progress/gates.md states the result and the evidence links | pass | SG-1 entry |

## Blockers

- Staging deployment blocked by IMP-113 (accounts), owner Kirtan, 2026-11-02.

## Proposed decisions

None. The decisions of this run were given by the operator (D1 to D6) and are recorded as IMD-64 to IMD-98.

## Open issues

- PR #200 (IMP-113) merged at 08:51 UTC during this run, without an approval; its records are templates with outcomes pending, so the staging block stands. Its part records hold no proposed decisions; nothing from it was added to the register.
- No merged pull request has met the working agreement (IMD-68); approvals are needed from now on.
- The Supabase local stack keeps its database volume across `make stack-down`, so a "clean clone" on a machine that ran the stack before does not start from a blank local database. Blank-schema migration was shown on the compose db and in CI.
- CLAUDE.md §12 still describes one branch per part; IMD-66 overrides it. CLAUDE.md was not changed by this card.
