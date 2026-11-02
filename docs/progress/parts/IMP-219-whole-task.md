# IMP-219 · whole-task part

- Run id: RUN-028
- Owner: Het (het-lathiya)
- Status: PR_OPEN
- Base commit: 2053abf
- Branch: feat/IMP-219-whole-task
- Reviewer: Manal (manalPatel2557)
- Traces to: US-012, US-163; FR-003; NFR-012, NFR-020, NFR-022; TC-439, TC-440; IMD-03, IMD-14, IMD-101 (Amendment A1 §5.1, §7.2, §7.3)
- Card steps built: 1 to 6
- Prerequisites found:
  - the auth stub SQL is `apps/api/migrations/sql/test_auth_stub.sql` (IMP-106);
  - `get_or_create_profile` is in `apps/api/app/auth/service.py` (IMP-108), with signature `(session, user_id) -> None`, as IMD-14 describes.

## Changed files

- **Step 1: `apps/api/app/db/auth_stub.py` (created).** `python -m app.db.auth_stub --if-missing`:
  - reads `DATABASE_URL`, removes the `+psycopg` suffix (`libpq_url`) and connects with synchronous psycopg;
  - when schema `auth` exists, prints `auth schema present; nothing to do` and exits 0;
  - otherwise runs the committed stub file unchanged (path `AUTH_STUB_SQL`, reused from `app/db/reset.py`) and prints `auth stub: applied`. The connection is in autocommit mode, so the file's own `begin; … commit;` is the single transaction;
  - on any error it exits 1 and prints only the exception class name, never the URL, host or credentials.
- **Step 2: `apps/api/app/core/config.py` (modified).** Adds `db_auth_stub: bool = False` (`DB_AUTH_STUB`).
- **Step 3: mirroring.** These are the auth module's profile creation code: the service holds `get_or_create_profile`, the repository holds the SQL, and the `CurrentUser` dependency passes the setting.
  - `apps/api/app/auth/service.py` (modified): `get_or_create_profile(session, user_id, *, mirror_auth_user=False)`. When true, it first calls `repository.mirror_auth_user`, in the request's transaction and before the profile insert.
  - `apps/api/app/auth/repository.py` (modified): `mirror_auth_user` runs `insert into auth.users (id) values (:user_id) on conflict (id) do nothing`. It stores the ID only; the e-mail claim is never written (NFR-020).
  - `apps/api/app/auth/deps.py` (modified): `current_user` reads `request.app.state.settings.db_auth_stub` (the same settings object `verified_claims` uses) and passes it on. When the setting is false nothing touches `auth.users`, and a token for an unknown user still gets 401, as IMP-108 does.
- **Step 4: `Makefile` (modified).** `make db-bootstrap` runs `cd apps/api && .venv/bin/python -m app.db.auth_stub --if-missing && .venv/bin/alembic upgrade head`, exactly as A1 §7.3. It is listed in `.PHONY` and in `make help`.
- **Step 2: `.env.example` (modified).** The A1 §7.2 comment line and `DB_AUTH_STUB=false` are added under the existing "database and authentication" section. That section already has a header, so the A1 header line was not repeated. `GEMINI_EMBEDDING_MODEL_ID` is not added (IMP-312).
- **Step 6: `apps/api/app/db/admin.py` (created).** `python -m app.db.admin delete-user --user-id <uuid>`:
  - refuses with exit 1 unless `DB_AUTH_STUB` is true;
  - deletes the `auth.users` row in one transaction, which cascades to the profile and its trips and plans;
  - prints only `delete-user: N row(s) deleted`.
- **Step 5: `apps/api/tests/api/test_auth_stub_mirror.py` (created; TC-439, TC-440).** It holds 8 tests:
  - TC-439, first call: an unknown user's first `GET /me` with the setting on creates `auth.users` with a null `email` and the profile; a second call creates nothing.
  - An existing `auth.users` row is kept unchanged.
  - With the setting false, an unknown user gets 401 and no `auth.users` or profile row is written.
  - TC-440, blank database: on a scratch database without schema `auth`, created and dropped by the test, the command applies the stub (`auth.users` and `auth.uid()` exist), and a second run is a no-op.
  - TC-440, existing schema: on the migrated test database, which has schema `auth`, the command is a no-op.
  - An unreachable URL exits 1, and neither the password nor the host is printed.
  - `delete-user` refuses when the setting is false.
  - `delete-user` with the setting true deletes 1 row, and the profile and trip are gone by cascade. These rows are committed and cleaned up in `finally`.
- This record (created).

Unchanged: the API-03 shape and its first-call profile creation (IMD-14), token verification, migrations 0001 to 0007, `contracts/`, the authz suites, `infra/aws/`, the deploy workflows and the Dockerfiles. `apps/api/.env` and `apps/web/.env.local` were neither read nor written.

## Checks that the tests can fail

- With the mirroring call disabled in the service, `test_auth_stub_first_call_mirrors_the_user_then_creates_nothing` failed (`1 failed, 7 passed, 194 deselected, 1 warning in 0.86s`). The change was reverted.

## Commands run

| Command | Result |
| --- | --- |
| `make db-up && make test-api ARGS='-k auth_stub'` | `8 passed, 194 deselected, 1 warning in 1.08s` |
| `make db-down`, `make db-up` (blank compose db), `make db-bootstrap` (`DATABASE_URL` = compose test database) | `auth stub: applied`, then `Running upgrade  -> 0001` … `Running upgrade 0006 -> 0007` |
| `make db-bootstrap` (second run) | `auth schema present; nothing to do`; alembic ran no upgrade |
| `make lint` | `All checks passed!`, `127 files already formatted`, `All matched files use Prettier code style!` |
| `make typecheck` | `Success: no issues found in 78 source files`; `✓ Types generated successfully` |
| `make imports` | `Contracts: 4 kept, 0 broken.` |
| `make openapi-check` | `openapi-check: contracts/ and apps/web/lib/api/schema.d.ts are up to date` |
| `make test` | unit `374 passed, 1 warning in 7.35s`; contract `35 passed, 1 warning in 0.73s`; api `202 passed, 1 warning in 44.13s`; authz `9 passed in 1.54s` (unchanged suite); web `Tests  54 passed (54)` |
| `make check` | exit 0, with the lines above |

## Not run

- `make e2e`: no journey changed.
- Anything on AWS RDS or hosted Supabase Auth: there is no access in this run, and they are not available until IMP-217, IMP-218 and IMP-299.

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| The first call of a new hosted-Auth user on a stub database creates `auth.users(id)` and the profile; repeat calls create nothing; no e-mail is stored (TC-439, FR-003) | verified on the compose stub database; not verified on RDS with hosted Supabase Auth (IMP-217, IMP-299) | `test_auth_stub_first_call_mirrors_the_user_then_creates_nothing` |
| `auth_stub --if-missing` applies the stub once, is a no-op afterwards, and is a no-op on a database with schema `auth` (TC-440) | verified on PostgreSQL 16 (compose); not verified on RDS | Two TC-440 tests; `make db-bootstrap` twice on a blank compose database |
| `app.db.admin delete-user` removes the `auth.users` row and, by cascade, the profile and trips, and refuses when `DB_AUTH_STUB` is false (NFR-022) | verified on the compose database; the one-off ECS run is not verified (IMP-217, IMP-218) | The two delete-user tests |
| Existing auth and authorization suites pass unchanged (`make test-authz`) | verified | `9 passed in 1.54s`; `tests/api/test_me.py` passes inside `make test-api` |
| NFR-012, NFR-020: no e-mail stored and no URL or credential printed | verified | Null `email` assertion; the failure-output test |

## Blockers

None.

## Proposed decisions

- **PD-IMP-219-1 (files touched for step 3):** the card lists "the auth module's profile creation code that holds `get_or_create_profile`". The SQL went to `auth/repository.py`, because services hold no SQL (CLAUDE.md §4). The setting reaches the service through `auth/deps.py` (`current_user`), which already holds the app's settings. Both files belong to the auth module. Proposed: name them on the card.
- **PD-IMP-219-2 (stub file name and header):** the stub file is still named `test_auth_stub.sql`, and its header says it is applied "ONLY" by the test fixture. Under A1 it is also applied by `make db-bootstrap` and the release task on RDS. The file was run unchanged, as the run requires. Proposed: amend the header comment (and possibly the name) in a later card owned by the migrations owner.

## Open issues

- **A local `apps/api/.env` with `DB_AUTH_STUB=true`:** pydantic-settings would read it in tests that do not use `clean_settings_env`. `test_me.py`'s "deleted account answers 401" case would then mirror instead of refusing. CI has no `.env` file, and the A1 §7.2 value for the Supabase local stack is `false`. The new tests set the value explicitly.
- **On RDS, the release task must have `DB_AUTH_STUB=true` set before `delete-user` is used.** The setting is read per process, and the command refuses otherwise. This belongs to IMP-217 and IMP-218 (task definition).
