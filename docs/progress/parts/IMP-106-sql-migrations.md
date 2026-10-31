# IMP-106 · sql-migrations part

- Run id: RUN-007
- Owner: Malhar (Malhar1112-v)
- Status: PR_OPEN
- Base commit: db02416
- Branch: feat/IMP-106-migrations-orm (one branch and pull request for both IMP-106 parts, as the run prompt directs; this part's commits come first)
- Reviewer: Kirtan (kirtan-S111)
- Traces to: US-008; NFR-034; TC-337; IMD-01, IMD-02
- Card steps built: 1, 2 and 7

## Changed files

- `apps/api/migrations/sql/test_auth_stub.sql`, `0001_helpers.sql`, `0002_reference_data.sql`, `0003_accounts_trips.sql`, `0004_ai_and_plan.sql`, `0005_mvp_security.sql`, `0006_updated_at_triggers.sql` (created, step 1): copied with `cp` from `docs/spec/sql/`.
- `apps/api/migrations/sql/down/0001_helpers.down.sql` … `0006_updated_at_triggers.down.sql` (created, step 1): copied with `cp` from `docs/spec/sql/down/`.
- `apps/api/alembic.ini` (created, step 2): `script_location = %(here)s/migrations`, `prepend_sys_path = %(here)s`, no `sqlalchemy.url`, `file_template = %%(rev)s_%%(slug)s`, standard logging sections.
- `apps/api/migrations/env.py` (created, step 2): synchronous engine (`create_engine`, `NullPool`) with the psycopg driver. The URL is `DATABASE_URL` read through `app.core.config.get_settings()` and is never printed; a plain `postgresql://` URL is switched to `postgresql+psycopg`. There is no target metadata and no autogenerate. A caller that already holds a connection (the test fixture of the orm-drift-fixture part) passes it as `config.attributes["connection"]`. Offline mode (`--sql`) is supported.
- `apps/api/migrations/script.py.mako` (created, step 2): the template for `alembic revision --rev-id 000N -m "<name>"` (§5.5). New revisions execute their SQL file in the same way as 0001 to 0006.
- `apps/api/migrations/versions/0001_helpers.py` … `0006_updated_at_triggers.py` (created, step 2): `revision = "000N"`, `down_revision = "000(N-1)"` (None for 0001). `upgrade()` runs `op.execute(<sql/000N_name.sql text>)` and `downgrade()` runs `op.execute(<sql/down/000N_name.down.sql text>)`.
- `Makefile` (modified, Kirtan's file, step 7): `db-migrate` now runs `cd apps/api && .venv/bin/alembic upgrade head` without the "not yet implemented (IMP-106)" guard, because `alembic.ini` exists. A two-line comment says that plain PostgreSQL needs the stub first. `db-reset` now names IMP-107 in its pending message, because the §5.7 reset ends with `make seed`. No target was renamed or added.
- `.github/workflows/ci.yml` (modified, Kirtan's file, step 7, `api` job only): after `make setup`, the job applies `test_auth_stub.sql` with `psql -v ON_ERROR_STOP=1` to the blank `postgres:16` service, then runs `make db-migrate`. A new step checks that `alembic heads` prints exactly one line (§5.5 "CI fails on more"). Another runs `alembic downgrade base && alembic upgrade head` (the §5.5 CI round trip). `make test-api` and `make test-authz` follow. No job was renamed or added. **Reason:** the card's step 7 and the §4 CI row of the api job. Until now the job ran `make db-migrate` as a no-op.
- This record (created).

Extension migrations 0007 to 0010 were not copied, because the extensions were cut at SG-1 on 1 November 2026.

## Byte-for-byte copy (step 1)

Every fenced `sql` block of Appendix A in `docs/spec/IMPLEMENTATION_SPEC.md` (lines 6151 to 6886, 21 blocks) was compared by script with the matching `docs/spec/sql/` file. All 21 were identical. The 13 MVP files were then copied with `cp`. `sha256sum` in both directories, compared with `diff` (no output):

```text
92aeb1e65f3ff1f94edf81fa36207c1255bddd0bfe6bd33e8b4bffa0bdb682fe  test_auth_stub.sql
6d14efa2b70e21b443149b81055112bb4550fd90f6f184c1d0b2259c05d2f271  0001_helpers.sql
e76798b1c03100d1603eb6099d7e70fa068293606bb676ef742e960bcbfe932d  0002_reference_data.sql
1893e869e280d58c7eec8c30c229126b963747b8a0337ffdf28f5bf6d23eea54  0003_accounts_trips.sql
a88e05b342303b48da891b37494cdf36847179a761027b50e24627ca395ec043  0004_ai_and_plan.sql
df735490d013f953a6bb1ea9a9d00904451ae54bb6e49fc1680062388a59745b  0005_mvp_security.sql
ab547475cb25d524811855572a0f8dd522a1cfdc01f578c9924cbb6926a9e2ff  0006_updated_at_triggers.sql
7afa5c26da9426b1b65525ee4e9ba82b00c93fb7b3775e0f4b733e0cb18d7953  down/0001_helpers.down.sql
ad564cc969116e368d469294967b03ddb661e601b937513048061eb5ac680976  down/0002_reference_data.down.sql
d35a79e9b00bfa52eb6bc0228876b419767604d1c79fbda14f596f3c7386424b  down/0003_accounts_trips.down.sql
849a107fdbc85c22b3cbdfc6c747206b57958528d2cd5d7e102ab8eb873caf8a  down/0004_ai_and_plan.down.sql
57fc30bae0dcc997cc5d7493871732a53ace190cd9addca5944a6bb1000a3a47  down/0005_mvp_security.down.sql
f28abf2da3b51d39048b12db281a8d30cf4387951771f8a403eb6ee8f5a3bb23  down/0006_updated_at_triggers.down.sql
```

`op.execute` receives each file as one string. Two things were checked. First, no file contains a `:name` pattern that SQLAlchemy's `text()` would read as a bind parameter. Second, psycopg 3 runs the multi-statement files, including the `$$` bodies and the `%1$s` format string of 0001, unchanged. The 9 triggers that 0001's function creates confirm this.

## Commands run

Local, non-secret URLs only, passed on the command line. `apps/api/.env` does not exist and was neither read nor written. Tools: Alembic 1.20.1, SQLAlchemy 2.1.6, psycopg 3.3.6, Docker 29.9.2.

| Command | Result line (quoted exactly) |
| --- | --- |
| `make db-up` | ` Container group12-db-1 Healthy ` |
| `docker compose exec -T db psql -U postgres -d travel_test -v ON_ERROR_STOP=1 -f - < apps/api/migrations/sql/test_auth_stub.sql` (no `psql` on the host) | `COMMIT` |
| `DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/travel_test make db-migrate` (compose db, PostgreSQL 16) | `INFO  [alembic.runtime.migration] Running upgrade 0005 -> 0006, 0006 updated_at triggers; revokes the helper functions and alembic_version from browser roles (Appendix A.7).` |
| `psql` checks after upgrade (compose db): tables in public except `alembic_version`; `trg_%_updated_at` triggers; tables with RLS; public policies; `alembic_version`; grants to anon/authenticated | `15`, `9`, `15`, `16`, `0006`, `0` |
| `cd apps/api && alembic heads` | `0006 (head)` |
| `alembic downgrade base` (compose db) | `INFO  [alembic.runtime.migration] Running downgrade 0001 -> , 0001 helpers: the updated_at trigger functions (Appendix A.2).`; afterwards `1` table left in public (`alembic_version`) |
| `alembic upgrade head` (compose db) | `INFO  [alembic.runtime.migration] Running upgrade 0005 -> 0006, 0006 updated_at triggers; revokes the helper functions and alembic_version from browser roles (Appendix A.7).` |
| `alembic current` | `0006 (head)` |
| `alembic history` | `<base> -> 0001, 0001 helpers: the updated_at trigger functions (Appendix A.2).` (first line printed last; six linear lines, 0001 to 0006) |
| CI api job steps replayed on a fresh compose db (`make db-down`, `make db-up`, stub, `make db-migrate`, then the "one head" and "round trip" step texts extracted from `ci.yml` with PyYAML and run with `bash -e` in `apps/api`) | `heads step exit 0`; `round trip exit 0` |
| `make stack-up` | `Starting database from backup...`, exit 0 (PostgreSQL 17.11; `auth.users` present; 0 public tables before) |
| `DATABASE_URL=postgresql+psycopg://postgres:postgres@127.0.0.1:54322/postgres make db-migrate` (Supabase local stack) | `INFO  [alembic.runtime.migration] Running upgrade 0005 -> 0006, 0006 updated_at triggers; revokes the helper functions and alembic_version from browser roles (Appendix A.7).`, exit 0 |
| `alembic heads` / `alembic downgrade base` / `alembic upgrade head` / `alembic current` (Supabase local stack) | `0006 (head)` / exit 0 / exit 0 / `0006 (head)` |
| `psql` checks on the Supabase stack after the round trip: tables, triggers, RLS tables, browser grants | `15`, `9`, `15`, `0` |
| `make lint` | `All checks passed!` (ruff) … `All matched files use Prettier code style!`, exit 0 |
| `make typecheck` | `Success: no issues found in 20 source files` … `✓ Types generated successfully`, exit 0 |
| `make imports` | `Contracts: 3 kept, 0 broken.` |
| `make test` (`TEST_DATABASE_URL` = the §4.7 default) | `======================== 13 passed, 1 warning in 0.41s =========================` (test-api); last line `      Tests  12 passed (12)` (test-web), exit 0 |
| `make check` | exit 0; last line `   Duration  2.04s (environment 58%, setup 14%, tests 14%, import 9%, transform 5%)` |

## Not run

| Command | Reason |
| --- | --- |
| CI api job on GitHub | Runs on the pull request; its result is reported in the SYNC REPORT, not here (this record is committed before the push). |

## Acceptance criteria

| Criterion | Status (verified / not verified) | How |
| --- | --- | --- |
| On an empty PostgreSQL 16 (make db-up, stub first) and on the Supabase local stack, `make db-migrate` applies 0001 to 0006 without error and `alembic heads` prints one head (US-008 AC1, NFR-034, TC-337) | verified | Commands above: both databases reach `0006 (head)` with 15 tables, 9 triggers, RLS on 15 tables and no browser grants; `alembic heads` prints the single line `0006 (head)` |
| `alembic downgrade base` followed by `alembic upgrade head` succeeds locally | verified | Round trip on the compose db (twice, once as the CI step text) and on the Supabase stack, each exit 0 |
| The CI api job runs the migrations on a blank database and is green | not verified | Shown on the pull request (stub, `make db-migrate`, one head, round trip, then the suites) |

## Blockers

None.

## Proposed decisions

None.

## Open issues

- The Supabase local stack runs PostgreSQL 17.11, while CI and the compose db run 16. Migrations 0001 to 0006 behave the same on both. This was the first Supabase run that §5 asks to record, and it showed no difference to fix. The hosted projects are checked in IMP-112.
- The card's "Owners and parts" row asks for one branch and pull request per part. The run prompt puts both parts on `feat/IMP-106-migrations-orm`, with this part's commits first, so this part still merges before the ORM part it supports.
- The host running this part has no `psql`, so the stub was applied through `docker compose exec`. The CI runner image ships `psql`, and the CI step uses it.
