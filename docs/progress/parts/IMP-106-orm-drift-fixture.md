# IMP-106 · orm-drift-fixture part

- Run id: RUN-007
- Owner: Jeel (jeelfefar2141)
- Status: PR_OPEN
- Base commit: db02416
- Branch: feat/IMP-106-migrations-orm (one branch and pull request for both IMP-106 parts, as the run prompt directs; this part is built on top of the sql-migrations part)
- Reviewer: Kirtan (kirtan-S111)
- Traces to: US-008; NFR-012; TC-337, TC-345; IMD-01
- Card steps built: 3, 4, 5 and 6

## Changed files

- `apps/api/app/db/__init__.py` (created): package docstring.
- `apps/api/app/db/session.py` (created, step 3): this is the only module that creates an engine. `create_engine(url, **options)` returns an async engine (`postgresql+psycopg`, `pool_pre_ping`). `get_engine()` and `get_sessionmaker()` are built once, from `DATABASE_URL` in the settings. `transaction()` is the async context manager the services use (`async with transaction() as session:`). It commits at the end of the block and rolls back on an error (§5.8). `psycopg_url()` makes sure the URL uses the psycopg 3 driver. The URL is never logged.
- `apps/api/app/db/models/` (created, step 4): `base.py` (`Base(DeclarativeBase)`); `profiles.py` (Profile); `trips.py` (Trip, TripPreferences); `places.py` (Destination, DataSource, Place, PlaceOpeningHours, TripPlace); `generation.py` (AiGeneration); `itinerary.py` (ItineraryDay, ItineraryItem, ItineraryWarning, ItineraryVersion); `budget.py` (BudgetSettings); `routing.py` (RouteCache). `__init__.py` imports them all and exposes `metadata = Base.metadata`.
  - Each file belongs to the module that writes the table (§5.2). `trip_places` sits in `places.py` because MOD-B04 writes it.
  - The models use exactly the SQL's column names, types, nullability and server defaults. They also declare the primary keys and the foreign keys inside schema public, including the composite `(day_id, trip_id)` key of `itinerary_items`.
  - `trips.num_days` is `Computed("end_date - start_date + 1", persisted=True)`, so the ORM never writes it.
  - CHECK constraints, indexes and policies stay in the SQL only.
  - `profiles.id → auth.users(id)` is not declared, because the auth schema belongs to Supabase and is not in this metadata (a comment in `profiles.py` says so).
- `apps/api/tests/fixtures/db.py` (created, step 5):
  - `migrated_database_url` (session scope) reads `TEST_DATABASE_URL` from the settings, falling back to the §4.7 default. It creates the database when it is missing, applies `test_auth_stub.sql` only when schema `auth` is absent, and runs `alembic upgrade head`. Alembic gets the fixture's own connection through `config.attributes["connection"]`, which the sql-migrations part's `env.py` accepts.
  - `db_session` gives each test an `AsyncSession` inside one outer transaction, which is rolled back at the end (`join_transaction_mode="create_savepoint"`, so a commit in the code under test only releases a savepoint).
  - `insert_auth_user(session, user_id=None, email=None)` inserts the `auth.users` row for a test user.
- `apps/api/tests/api/test_schema_drift.py` (created, step 6, TC-337): it reflects the migrated test database. The table set must be exactly the 15 MVP tables (`alembic_version` aside), in both the ORM and the database. Then, for each of the 15 tables, two parametrised tests compare:
  - columns, both ways: missing or extra;
  - per column: compiled PostgreSQL type, nullability, server default (casts, brackets and spaces normalised) and generated expression;
  - primary key columns, and foreign keys inside schema public with their `ondelete`.

  §5.5 asks for the server default as well as the card's tables, columns, types and nullability, so it is compared too. 31 tests in all.
- `apps/api/tests/authz/test_rls.py` (created, step 6, TC-345): it writes one row into each of the 15 tables through the ORM models, which also shows that the models can write: 15 inserts accepted by every CHECK and foreign key. It then checks that the privileged connection sees at least one row in every public table. For roles `anon` and `authenticated` it reads every public table, `alembic_version` included (16 tables, 32 reads). Each read runs in a savepoint with `set local role` and `request.jwt.claim.sub` set to the row owner, so `authenticated` reads as the owner of the rows. It asserts that every read gives zero rows. A read refused with `InsufficientPrivilege` counts as zero; any other error fails.
- `apps/api/tests/conftest.py` (modified, Het's file): one import line only, `from fixtures.db import db_session, migrated_database_url  # noqa: F401  # registers the DB fixtures`. **Reason:** pytest registers fixtures from a module only when a conftest imports them, and the run prompt allows exactly this line. The socket guard and the settings fixtures are unchanged.
- `apps/api/pyproject.toml` (modified, Het's file, one token): `sqlalchemy>=2.1,<3` became `sqlalchemy[asyncio]>=2.1,<3`. **Reason:** SQLAlchemy 2.1 no longer installs `greenlet` by default, and without it `sqlalchemy.ext.asyncio` fails on import ("requires that the Python 'greenlet' library is installed"). §5.5 requires the async engine. The extra adds `greenlet` (3.5.6 installed), and no new top-level dependency. The change is in the session commit, the first one that needs it.
- This record (created).

## Checks that the tests can fail

The tests were run against deliberately broken inputs, and each change was undone after it was checked (the files are byte-identical again, checked with `diff`).

| Change | Result |
| --- | --- |
| `trips.title` made nullable in the model | `trips.title: nullable True != False (database)`, 1 failed |
| `trips.budget_amount` as `Numeric(10, 2)` | `trips.budget_amount: type NUMERIC(10, 2) != NUMERIC(12, 2) (database)`, 1 failed |
| `trips.status` default `'ready'` | `trips.status: server default 'ready' != 'draft'`, 1 failed |
| `trips.plan_stale` removed from the model | `columns in the database, not in the model: ['plan_stale']`, 1 failed |
| `trips.num_days` without `Computed` | `trips.num_days: generated None != ('end_date-start_date+1', True)`, 1 failed |
| `trips.user_id` foreign key without `ondelete` | the foreign-key set assertion failed, 1 failed |
| `grant select on public.destinations, public.trips to authenticated` (then revoked) | `{('authenticated', 'destinations'): 1, ('authenticated', 'trips'): 1}`, 1 failed |
| `grant select on public.route_cache to anon` and RLS disabled on it (then restored) | `{('anon', 'route_cache'): 1}`, 1 failed |

## Commands run

Local, non-secret URLs only, passed on the command line. `apps/api/.env` does not exist and was neither read nor written.

| Command | Result line (quoted exactly) |
| --- | --- |
| `.venv/bin/python -m pip install -e ".[dev]"` (after the `sqlalchemy[asyncio]` change) | `greenlet 3.5.6` importable |
| `make db-down`, `make db-up` (fresh compose db) | ` Container group12-db-1 Healthy ` |
| `TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/travel_test make test-api ARGS='-k schema_drift'` (TC-337; the fixture applied the stub and migrated the blank db) | `================= 31 passed, 13 deselected, 1 warning in 1.64s =================` |
| `TEST_DATABASE_URL=… make test-authz ARGS='-k rls'` (TC-345) | `============================== 1 passed in 0.52s ===============================` |
| Fixture on a database that does not exist yet (`TEST_DATABASE_URL=…/travel_fixture_check`, drift and RLS tests), then `psql` checks, then `drop database` | `32 passed, 13 deselected, 1 warning in 2.07s`; `auth.users`, `0006`, 16 public tables, 0 rows left in `trips` |
| Same two tests against the Supabase local stack (`TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@127.0.0.1:54322/postgres`; stub skipped because `auth` exists) | `32 passed, 13 deselected, 1 warning in 2.00s` |
| `alembic heads` (from `apps/api`) | `0006 (head)` |
| `make lint` | `All checks passed!` / `54 files already formatted` / `All matched files use Prettier code style!`, exit 0 |
| `make typecheck` | `Success: no issues found in 31 source files` / `✓ Types generated successfully`, exit 0 |
| `make imports` | `Contracts: 3 kept, 0 broken.` |
| `make test` | test-unit `74 passed`, test-api `======================== 44 passed, 1 warning in 1.58s =========================`, test-authz `1 passed`, test-web `      Tests  12 passed (12)`; last line `   Duration  2.01s (environment 63%, tests 13%, setup 13%, import 8%, transform 3%)`, exit 0 |
| `make check` | exit 0; last line `   Duration  1.77s (environment 61%, tests 15%, setup 13%, import 9%, transform 2%)` |

## Not run

| Command | Reason |
| --- | --- |
| CI api job on GitHub | Runs on the pull request; its result is reported in the SYNC REPORT (this record is committed before the push). |

## Acceptance criteria

| Criterion | Status (verified / not verified) | How |
| --- | --- | --- |
| test_schema_drift passes: the ORM metadata equals the migrated schema (TC-337) | verified | `make test-api ARGS='-k schema_drift'`: 31 passed on a blank compose db; also passes on the Supabase local stack; the six model changes above each make it fail |
| Roles anon and authenticated read zero rows from every table (US-008 AC2, NFR-012, TC-345) | verified | `make test-authz ARGS='-k rls'`: 1 passed (32 reads over 16 public tables, each with a row present); also passes on the Supabase stack; the two grants above make it fail |
| The CI api job runs the migrations on a blank database and is green | not verified | Shown on the pull request |

## Blockers

None.

## Proposed decisions

None. The `sqlalchemy[asyncio]` extra puts in place the async engine that §1.4 and §5.5 already require, so no decision is needed. The pull request states the reason, as CLAUDE.md §2 asks for any added dependency.

## Open issues

- The ORM models declare no `relationship()`. Without relationships, SQLAlchemy's unit of work does not order inserts by foreign key, so code that adds parent and child rows in one flush must flush the parent first (the RLS test does this). Module cards may add relationships when they need them; the drift test does not compare them.
- `make test`, `make check`, `make test-api` and `make test-authz` now need the compose db (`make db-up`), as §4.7 says. Without it, the database tests fail with a connection error; they are not skipped.
- Fixed test UUIDs and the `insert_auth_user` helper are the base for `tests/fixtures/factories.py` (§5.6), which a later card adds.
