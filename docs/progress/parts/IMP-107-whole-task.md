# IMP-107 · whole-task part

- Run id: RUN-011
- Owner: Jeel (jeelfefar2141)
- Status: PR_OPEN
- Base commit: 19d7239 (rebased from 7c9f5f4 after IMP-110 and IMP-108 merged; the seed, reset and test runs below were taken on 7c9f5f4, and `make test-api ARGS='-k seed'`, `make check` and `make seed` were repeated after the rebase)
- Branch: feat/IMP-107-whole-task
- Reviewer: Malhar (Malhar1112-v)
- Traces to: NFR-032; TC-110; IMD-09
- Card steps built: 1 to 5

## Changed files

- `data/fixtures/sampleton/destination.json`, `sources.csv`, `places.csv`, `opening_hours.csv` (created, steps 1 and 2): the §5.6 column format.
  - **Destination:** slug `sampleton`, name "Sampleton (sample)", region "Sample region (synthetic)". The centre (53.9, 2.2) and bounding box are invented, out at sea east of England, with no town. The rest is `GB`, `Europe/London`, `GBP`, `is_sample: true`.
  - **Source:** one data source, "SAMPLE fixture (synthetic)", with `source_type` `other`, licence "synthetic test data" and notes `synthetic`.
  - **Places:** 30, `sample-001` to `sample-030`. Every name starts with "Sample" or "Fixture" and ends with "(sample)", so no name is a real business. Addresses, URLs and phone numbers are empty, and descriptions say "Synthetic … place for tests (sample)". All places are `verification_status` `estimated` and inside the bounding box.
- `data/fixtures/README.md` (updated): what each file holds, and the fixture counts below with the `external_ref` of each special place.
- `apps/api/app/places/seed.py` (created, step 3): `python -m app.places.seed <dir> [<dir> ...]`.
  - **Reading:** every directory is read and type-checked before anything is written. A format error names the file, line and column and exits 1: a missing or unknown column, a bad number, date, `HH:MM` time or boolean, a duplicate `external_ref`, an unknown `source_name`, hours for an unknown place, invalid JSON, or a time zone that is not IANA (`zoneinfo`).
  - **SAMPLE refusal:** a `destination.json` with `is_sample: true` is refused (exit 1) unless `APP_ENV` is `local` or `test` (§5.6).
  - **Writing:** one transaction per directory, in the order data_sources (by `name`), destinations (by `slug`), places (by (`source_id`, `external_ref`)), opening hours (replaced as a set per place).
  - **No-op on unchanged files:** rows are compared before writing. A row is inserted, updated only when a value differs, or left untouched, and opening hours are replaced only when the set differs. A second run with unchanged files writes nothing; ids and `updated_at` stay the same, as §5.6 asks.
  - **Loader rules from §5.6:** a place without opening-hours rows gets `hours_label` `unavailable`. Places of the same source and destination missing from the file are set `is_active = false`, never deleted.
  - **Report:** counts read, then inserted, updated and unchanged per table, deactivated places, and opening hours replaced or unchanged.
  - **Database rejection:** a row the database rejects (CHECK or foreign key) exits 1 with the constraint name, and that directory's transaction is rolled back.
  - **Scope:** the quality gate and provenance report (IMP-205) are not built; IMP-205 replaces this loading core behind the same command.
- `apps/api/app/db/reset.py` (created; **not in the card's file list**): the first step of `make db-reset`.
  - It refuses unless `APP_ENV` is `local` or `test` (§4.7) and the `DATABASE_URL` host is `localhost` or `127.0.0.1` (§5.7). It also refuses when `DATABASE_URL` is empty.
  - It drops and recreates schema `public`, restores the default `usage` grant, and applies `test_auth_stub.sql` when schema `auth` is absent (a plain PostgreSQL; §5.7 compose case).
  - **Reason it exists:** these steps need code, which does not belong in a Makefile recipe. It lives in `app/db/`, the database package of IMP-106's orm-drift-fixture part (Jeel), and it never prints the URL.
- `Makefile` (modified, Kirtan's file, the `seed` and `db-reset` targets only). **Reason:** card step 4, and the run prompt, which assigns `db-reset` to this card (RUN-007 moved its pending message to IMP-107). No target was renamed or added.
  - `seed` now runs `python -m app.places.seed <repo>/data/fixtures/sampleton $(SEED_DIRS)` unconditionally; the "not yet implemented" guard is gone.
  - `db-reset` runs `python -m app.db.reset`, then `make db-migrate` and `make seed`. A refusal stops `make` with exit 2.
- `apps/api/tests/api/test_seed.py` (created, step 5; TC-110):
  - loading twice gives identical row counts and an identical snapshot of every Sampleton row (ids and `updated_at` included);
  - 1 sample destination, 1 SAMPLE source, 30 places, each with `(sample)` in the name, the SAMPLE source, `verification_status` and `is_active`;
  - the step 2 counts;
  - a changed file updates 1 place and deactivates 1, without deleting it;
  - five format errors exit 1 with a message naming the file and line;
  - SAMPLE data refused when `APP_ENV` is staging;
  - the `db-reset` guard refuses staging, production, a remote host and an empty URL, and allows local and test databases.

  The tests run in the rolled-back session of `tests/fixtures/db.py`, so they hold whether or not the test database was seeded before.
- This record (created).

## Fixture counts (note b)

| Property | Count | Places |
| --- | --- | --- |
| Places | 30 | `sample-001` to `sample-030` |
| Per category | sight 4, museum 4, nature 4, food 6, shopping 3, entertainment 3, religious 3, activity 3; no `stay` | |
| Food (at least 6) | 6 | `sample-013` to `sample-018` |
| `closes_next_day` (18:00 to 02:00, every day) | 3 | `sample-015`, `sample-023`, `sample-024` |
| `is_closed` on one weekday (Monday) | 3 | `sample-005`, `sample-007`, `sample-016` |
| `hours_label` `unavailable` and no hours rows | 3 | `sample-003`, `sample-009`, `sample-026` |
| `step_free` true | 2 | `sample-001`, `sample-005` (others false or unknown) |
| `price_label` `unavailable` (no price) | 2 | `sample-007`, `sample-017` |
| `price_label` `estimate`, `GBP` | 28 | the rest (free places as 0.00 to 0.00) |
| Opening-hours rows | 189 | 27 places × 7 weekdays |

## Commands run

Local, non-secret URLs on the command line; `apps/api/.env` was neither read nor written.

| Command | Result line (quoted exactly) |
| --- | --- |
| `make db-up` (blank) | ` Container group12-db-1 Healthy ` |
| `docker compose exec -T db psql … -f - < apps/api/migrations/sql/test_auth_stub.sql` | `COMMIT` |
| `DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/travel_test make db-migrate` | `INFO  [alembic.runtime.migration] Running upgrade 0005 -> 0006, 0006 updated_at triggers; revokes the helper functions and alembic_version from browser roles (Appendix A.7).` |
| `APP_ENV=test DATABASE_URL=… make seed` (first) | see output 1 below; exit 0 |
| row counts after the first seed | `destinations=1 data_sources=1 places=30 place_opening_hours=189` |
| `APP_ENV=test DATABASE_URL=… make seed` (second) | see output 2 below; exit 0 |
| row counts after the second seed | `destinations=1 data_sources=1 places=30 place_opening_hours=189` |
| `APP_ENV=test DATABASE_URL=… make db-reset` | `db-reset: schema public dropped and recreated`, migrations 0001 to 0006 (`Running upgrade 0005 -> 0006 …`), then the first-seed output again; exit 0; counts `destinations=1 data_sources=1 places=30 place_opening_hours=189` |
| `APP_ENV=test make db-reset` on a blank database without schema auth (`make db-down`, `make db-up`) | `db-reset: schema public dropped and recreated; auth test stub applied`, then `seed sampleton: places inserted 30, updated 0, unchanged 0, deactivated 0`; exit 0 |
| `APP_ENV=staging DATABASE_URL=… make db-reset` | `db-reset: refused: APP_ENV is staging; db-reset runs only when it is local or test` / `make: *** [Makefile:85: db-reset] Error 1` (exit 2) |
| `APP_ENV=test DATABASE_URL=postgresql+psycopg://u:p@db.example.test:5432/x make db-reset` | `db-reset: refused: the DATABASE_URL host is not localhost or 127.0.0.1` (exit 2) |
| `TEST_DATABASE_URL=… make test-api ARGS='-k seed'` | `================= 15 passed, 44 deselected, 1 warning in 1.27s =================` |
| Mutation: opening hours always replaced (`if False and current == wanted`), then restored | TC-110: `1 failed` (the snapshot differs), so the test detects a non-idempotent load |
| `make lint` | `All checks passed!` (ruff) … `All matched files use Prettier code style!` |
| `make typecheck` | `Success: no issues found in 33 source files` … `✓ Types generated successfully` |
| `make imports` | `Contracts: 3 kept, 0 broken.` |
| `make test` | test-unit `74 passed`, test-api `======================== 59 passed, 1 warning in 2.46s =========================`, test-authz `1 passed`, test-web `48 passed`; last line `   Duration  3.62s (environment 58%, tests 17%, setup 13%, import 9%, transform 2%)` |
| `make check` | exit 0; last line `   Duration  3.65s (environment 58%, tests 18%, setup 13%, import 8%, transform 2%)` |
| After the rebase on 19d7239: `make test-api ARGS='-k seed'` | `================= 15 passed, 49 deselected, 1 warning in 0.81s =================` |
| After the rebase: `make check` | exit 0; test-unit `178 passed`, test-contract `11 passed`, test-api `64 passed`, test-authz `9 passed`, test-web `48 passed`; last line `   Duration  3.75s (environment 58%, tests 19%, setup 12%, import 8%, transform 2%)` |
| After the rebase: `make seed` (third run on the same database) | `seed sampleton: places inserted 0, updated 0, unchanged 30, deactivated 0` |
| `make db-down` | see the SYNC REPORT (run after this record was committed) |

**Output 1 (first `make seed`):**

```text
seed sampleton: read 1 destination, 1 source(s), 30 places, 189 opening-hours rows
seed sampleton: data_sources inserted 1, updated 0, unchanged 0
seed sampleton: destinations inserted 1, updated 0, unchanged 0
seed sampleton: places inserted 30, updated 0, unchanged 0, deactivated 0
seed sampleton: opening hours replaced for 27 places, unchanged for 3
```

**Output 2 (second `make seed`):**

```text
seed sampleton: read 1 destination, 1 source(s), 30 places, 189 opening-hours rows
seed sampleton: data_sources inserted 0, updated 0, unchanged 1
seed sampleton: destinations inserted 0, updated 0, unchanged 1
seed sampleton: places inserted 0, updated 0, unchanged 30, deactivated 0
seed sampleton: opening hours replaced for 0 places, unchanged for 30
```

The "unchanged for 3" of the first run are the three places without hours rows, which have nothing to replace.

## Not run

| Command | Reason |
| --- | --- |
| `make seed` / `make db-reset` on the Supabase local stack | Not asked in this run. `db-reset` there drops and recreates `public` and skips the stub, because `auth` exists. §5.7 suggests `supabase db reset` for that stack instead (see Open issues). |
| CI api job | Runs on the pull request; reported in the SYNC REPORT. |

## Acceptance criteria

| Criterion | Status (verified / not verified) | How |
| --- | --- | --- |
| `make seed` on a freshly migrated database loads 1 destination and about 30 places and prints the counts | verified | Output 1 on a blank, migrated compose db; counts `destinations=1 … places=30 … place_opening_hours=189` |
| Running `make seed` twice leaves identical row counts | verified | Output 2 and the identical counts; TC-110 also compares every row, ids and `updated_at` included |
| Every fixture place name contains "(sample)" and its source is the SAMPLE data source | verified | `test_seed_loads_one_sample_destination_with_30_places` |
| test_seed passes in CI | not verified | Shown by the api job on the pull request |

## Blockers

None.

## Proposed decisions

- **PD-IMP-107-1 (sample source name):** §5.6 calls the fixture source "SAMPLE fixture data" (notes `synthetic`). The IMP-107 card and the run prompt call it "SAMPLE fixture (synthetic)". Built: the card's name, with notes `synthetic`. Proposed: align §5.6 with the card.
- **PD-IMP-107-2 (`db-reset` on the Supabase local stack):** §4.7 says to drop and recreate schema `public`; §5.7 says to run `supabase db reset` on the local stack. Built: §4.7 for both databases, plus the §5.7 host check and the stub on plain PostgreSQL. On the local stack this keeps Supabase's own schemas and restores the default `usage` grant on `public`, but not Supabase's extra default privileges for its API roles. The browser roles hold no table privileges anyway (migration 0005). Proposed: keep this, or add a `supabase db reset` branch for port 54322.

## Open issues

- **`app/db/reset.py` is outside the card's file list.** See Changed files for the reason.
- **Deactivation is scoped to the same source and destination.** §5.6 says "same source". Scoping it to the destination too keeps a multi-destination source, such as an OSM import, from deactivating another destination's places. IMP-205 may revisit this.
- **Downstream use:** the fixture gives IMP-203 (Trips API) a destination to create trips for, and IMP-205 (the provenance import and quality gate) replaces the loading core behind the same command.
