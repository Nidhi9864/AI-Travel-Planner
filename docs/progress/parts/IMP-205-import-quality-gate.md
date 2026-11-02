# IMP-205 · import-quality-gate part

- Run id: RUN-019b (retry of RUN-019, which stopped with no commits on the Sampleton retrieved-date conflict)
- Owner: Malhar (Malhar1112-v)
- Status: PR_OPEN
- Base commit: cc6a900
- Branch: feat/IMP-205-places-import-api (one branch and pull request for the card, IMD-66; Jeel's places-api-search part is built on top)
- Reviewer: Kirtan (kirtan-S111)
- Traces to: US-024, US-025, US-028; FR-019, FR-022, FR-023; NFR-040; TC-101, TC-102, TC-108, TC-109, TC-110, TC-111, TC-112, TC-113; IMD-09, IMD-15, IMD-40, IMD-86
- Card steps built: 1 to 4, and the gate unit tests and seed integration tests of step 7

## Changed files

- `apps/api/app/places/vocabulary.py` (created, step 1): the single source of the place vocabulary.
  - `Category`, with all nine categories, `stay` included. The values equal the migration 0002 CHECK.
  - `OfferedCategory`: every category except `stay`, for API filters (not offered in the MVP).
  - `Tag`: the tag vocabulary, PD-IMP-205-2.
  - `SuitabilityFlag`: `step_free`, `child_friendly`, `indoor`.
  - `SourceLabel` (`curated`, `estimate`, `unavailable`) and `VerificationStatus`.
  - Frozen sets of the same values, for the gate.
- `apps/api/app/places/quality_gate.py` (created, step 2): `check(row, destination) -> GateResult(values, hours, rejects, flags)`. It is pure; the row carries its resolved `SourceRecord` and its hours lines.
  - Rejected, as in step 2 and §5.6:
    - no `external_ref`;
    - unknown source, or a source without licence or without retrieved date;
    - verification status missing or unknown;
    - coordinates outside the bounding box (inclusive edges);
    - category or tag not in the vocabulary;
    - a negative price, max below min, a price without currency, or a price with label `unavailable`;
    - duration outside 15 to 480 minutes.
  - Also rejected, because migration 0002 would refuse the row and abort the whole directory:
    - name missing or over 160 characters, description over 600;
    - a priced label without `price_min`;
    - an unknown label, or `hours_label curated` without `hours_checked_on`;
    - malformed numbers or dates;
    - a suitability value other than `true`, `false` or empty.
  - Flagged and kept: hours that do not parse into weekday intervals (bad time or weekday, missing close time, close before open without `closes_next_day`, a closed day with times, the same slot twice). The place is stored with `hours_label unavailable` and no hour rows.
  - Unknown suitability stays `None` (NULL), never `False`.
- `apps/api/app/places/import_pipeline.py` (created, step 3): the loading core moved here from `seed.py`.
  - `prepare(dir)` reads the four files and applies the gate. A second row with the same `external_ref` is rejected.
  - `load(session, prepared)` works in the caller's transaction:
    - it upserts sources by name, the destination by slug, and accepted places by (`source_id`, `external_ref`);
    - it replaces hours as a set when they differ;
    - it deactivates places of the same destination and sources that are missing from the file or rejected, never deleting them;
    - a source without a licence is not stored (licence is NOT NULL); a copy stored earlier is kept, so its places can still be deactivated.
  - `render_report` and `write_report` write `<dir>/quality_report.md`. It holds rows read, loaded, rejected with reasons, flagged, usable places by category, and the usable count against `min_usable_places`, with a shortfall line when short.
    - The report holds only what the gate decided, so `--check` and a load write the same file and an unchanged import leaves it unchanged.
    - Database counts (inserted, updated, deactivated) go to stdout.
  - `run(dirs, check=, strict=)` is the CLI core:
    - format errors and SAMPLE refusals (when loading) exit 1;
    - `--check` writes the report and nothing to the database, and needs no `DATABASE_URL`;
    - `--strict` exits 1 on a shortfall before anything is written;
    - without `--strict`, a shortfall still exits 0 (§5.6).
- `apps/api/app/places/seed.py` (modified; Jeel's IMP-107 file, card step 3): now only the argument parser, with the new `--check` and `--strict` flags, which calls `import_pipeline.run`. It re-exports the IMP-107 names `read_fixture`, `load_fixture`, `Fixture`, `SeedReport`, `SeedFormatError` and `check_allowed`. `tests/api/test_trips.py` (IMP-203) loads Sampleton through them and is unchanged. The command `python -m app.places.seed <dir> [<dir> ...]` and `make seed` are unchanged.
- `data/fixtures/sampleton/sources.csv` (modified; Jeel's IMP-107 file, PD-IMP-205-1): `retrieved_on` set to `2026-10-31`, the date of commit 9b86b0b (IMP-107), which created the fixture. **Reason:** the retrieved-date rule of card step 2 stays strict, with no exemption for SAMPLE sources.
- `data/fixtures/sampleton/destination.json` (modified; Jeel's IMP-107 file, PD-IMP-205-3): adds `"min_usable_places": 30`, the §5.6 fixture minimum.
- `data/fixtures/README.md` (modified): records the source's retrieved date, the minimum and the generated report, and notes that every source, SAMPLE ones included, carries a licence and a retrieved date.
- `data/fixtures/sampleton/quality_report.md` (created, generated by the seed): 30 read, 30 loaded, 0 rejected, 0 flagged, minimum met (30 of 30).
- `.github/workflows/ci.yml` (modified; Kirtan's file, card step 4): one step, "Place quality gate in check mode (no database)", in the existing `unit` job after `make setup`. It runs `python -m app.places.seed --check` over every `data/fixtures/*/` and `data/places/*/` that has a `destination.json`, prints `skipped …` for the others (`data/places/` holds only a README today), and adds no job. **Reason:** card step 4; the job names that branch protection requires are unchanged.
- `apps/api/tests/unit/places/test_quality_gate.py` (created): 47 tests, one or more per gate rule (TC-102, TC-108, TC-111, TC-112, TC-113), including a source without a retrieved date.
- `apps/api/tests/api/test_seed.py` (modified; IMP-107 file, card step 7):
  - The format-error cases for an unknown source, a non-numeric latitude and a bad time are now gate outcomes (rejected or flagged), tested in new tests.
  - New format-error cases: a bad `min_usable_places`, hours for an unknown place, and a malformed source date.
  - New tests for TC-108, TC-109 (with TC-111 through the pipeline), TC-110 (deactivated when rejected, reactivated when fixed), TC-112, TC-113 (shortfall, and `--strict` exit 1), check mode in any `APP_ENV`, TC-101/TC-102 storage, and a test that the committed `quality_report.md` is current.

## Commands run

All commands ran with `TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/travel_test` on the command line, after `make db-up` (`Container group12-db-1 Healthy`).

| Command | Result line |
| --- | --- |
| `make test-unit ARGS='-k quality_gate'` | `47 passed, 236 deselected, 1 warning in 0.36s` |
| `make test-api ARGS='-k seed'` | `23 passed, 77 deselected, 1 warning in 2.60s` |
| `make test-authz` | `9 passed in 0.69s` |
| `make lint` | `All checks passed!` / `94 files already formatted` / `All matched files use Prettier code style!` |
| `make typecheck` | `Success: no issues found in 56 source files` |
| `make imports` | `Contracts: 3 kept, 0 broken.` |
| `make test` | unit `283 passed, 1 warning in 5.68s`; contract `11 passed in 0.08s`; api `100 passed, 1 warning in 11.79s` (`test_trips.py` included); authz `9 passed in 0.68s`; web `Tests  48 passed (48)` |
| `make seed` on a freshly migrated compose database (`travel_seed`: auth stub, `make db-migrate`, `APP_ENV=test`) | `seed sampleton: places inserted 30, updated 0, unchanged 0, deactivated 0`; the second run gives `places inserted 0, updated 0, unchanged 30, deactivated 0`; `select count(*), count(*) filter (where is_active) from places` gives `30\|30`. `quality_report.md` was regenerated unchanged |
| CI gate step run locally (with a temporary notes-only `data/places/demo-notes/`, removed afterwards) | `skipped data/places/demo-notes (no destination.json)` … `seed: --check: nothing was written to the database` (exit 0) |
| `python -m app.places.seed data/fixtures/sampleton --check --strict` | `seed sampleton: gate loaded 30, rejected 0, flagged 0` (exit 0) |

`make check` is run once both parts are in; its result is in the places-api-search part record and the pull request.

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| Rows without source or verification status are rejected and listed (FR-022 AC1, TC-108) | verified | `test_tc_108_rows_without_source_or_verification_status_are_rejected_and_listed` (lines 3 and 4 listed with their reasons, in the report too; 28 loaded); unit `test_tc_108_*`, `test_a_source_without_a_licence_is_rejected`, `test_a_source_without_a_retrieved_date_is_rejected` |
| The report states rows read, loaded and rejected (FR-022 AC2, TC-109) | verified | `test_tc_109_the_report_states_rows_read_loaded_and_rejected`; `test_the_committed_sampleton_report_is_current` |
| Importing twice creates no duplicates (FR-022 AC3, TC-110) | verified | `test_tc_110_seed_twice_gives_identical_rows`; second `make seed` on `travel_seed` `unchanged 30`; `test_tc_110_a_place_that_now_fails_the_gate_is_deactivated_not_deleted` |
| Coordinates outside the destination are rejected (FR-023 AC1, TC-111) | verified | unit `test_tc_111_coordinates_outside_the_bounding_box_are_rejected` (4 edges); through the pipeline in `test_tc_109_*` |
| Unknown hours format stores hours as unavailable and flags the row (FR-023 AC2, TC-112) | verified | unit `test_tc_112_*` (7 cases); `test_tc_112_unparseable_hours_store_unavailable_and_flag_the_row` (stored `unavailable`, no hour rows) |
| A shortfall against the minimum is stated (FR-023 AC3, TC-113) | verified | unit `test_tc_113_a_shortfall_is_stated_in_the_report`; `test_tc_113_a_shortfall_is_stated_and_strict_exits_non_zero` (exit 0 without `--strict`, 1 with it) |
| Tags under the vocabulary; unknown suitability NULL, never false (FR-019 AC1-AC2, TC-101, TC-102), storage half | verified | `test_tc_101_tags_come_from_the_vocabulary_and_unknown_suitability_is_null`; unit `test_tc_102_unknown_suitability_is_none_never_false`, `test_an_unknown_tag_is_rejected` |
| Sampleton loads all 30 places with no shortfall | verified | `make seed` on `travel_seed`; committed `quality_report.md` |

## Blockers

none

## Proposed decisions

- PD-IMP-205-1 (retrieved date, planner decision for SG-2): the retrieved-date rule of card step 2 stays as strict as written, with no exemption for SAMPLE sources. The Sampleton source got `retrieved_on` 2026-10-31, the date of the IMP-107 commit 9b86b0b that created the fixture, and `data/fixtures/README.md` notes that every source carries a retrieved date. §5.6 lists `retrieved_on` only as a column; proposal: add "the source has a licence and a retrieved date" to the §5.6 gate table.
- PD-IMP-205-2 (tag vocabulary, planner decision): the 32 tags Sampleton uses plus the budget tags of §9.3.1, all three of which the specification names (`child_half` and `child_free` in BF-01, `price_per_group` in BF-02). Final set, 35 tags: architecture, art, books, breakfast, cafe, child_free, child_half, crafts, cycling, dinner, evening, family, games, garden, history, indoor, late, local, lunch, maritime, market, music, outdoor, price_per_group, quiet, seafood, sport, street-food, tea, theatre, vegetarian, views, walking, water, wildlife. Curated destinations (IMP-206, IMP-603) add tags through `vocabulary.py`.
- PD-IMP-205-3 (minimum key, planner decision): the minimum usable count is the `destination.json` key `min_usable_places`. Sampleton is 30 (§5.6 "fixture 30"); an absent key means no minimum, and the report says so. Proposal: add the key to the §5.6 `destination.json` row.
- PD-IMP-205-4 (report location): §5.6 says the report is written beside `data/places/<slug>/`, while the card says `<dir>/quality_report.md` for every directory. Built as the card says, for fixtures too, and the report is the same in `--check` and load mode.
- PD-IMP-205-5 (SAMPLE refusal in check mode): `--check` writes nothing, so it reads SAMPLE data in any `APP_ENV`, which the CI gate step needs; loading still refuses SAMPLE data outside local and test (IMD-15).
- PD-IMP-205-6 (extra rejections): rows that migration 0002 would refuse (name and description length, a priced label without a price, `hours_label curated` without a date, malformed values) are rejected by the gate and listed, instead of aborting the directory with a database error.

## Open issues

- The CI step checks that the gate runs without error, but not that a committed `quality_report.md` is current. `test_the_committed_sampleton_report_is_current` covers Sampleton; IMP-206 may add a `git diff --exit-code` for curated reports.
- `--strict` loads nothing on a shortfall. The card only says it "exits non-zero"; refusing before writing seemed the safer reading.
