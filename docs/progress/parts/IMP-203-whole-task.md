# IMP-203 · whole-task part

- Run id: RUN-018
- Owner: Manal (manalPatel2557)
- Status: PR_OPEN
- Base commit: eb44ee3
- Branch: feat/IMP-203-whole-task
- Reviewer: Kirtan (kirtan-S111)
- Traces to: US-016; FR-005, FR-007, FR-008; NFR-012, NFR-014; TC-063, TC-068, TC-069, TC-070, TC-071, TC-072, TC-073; IMD-05, IMD-25, IMD-40, IMD-45
- Card steps built: 1 to 6
- Prerequisites on main: IMP-106 (`app/db/models/trips.py`), IMP-107 (`app/places/seed.py`, `data/fixtures/sampleton/`), IMP-108 (`app/auth/deps.py`, `tests/authz/test_route_inventory.py`), SG-1 entry in `docs/progress/gates.md`

## Changed files

- `apps/api/app/schemas/common.py` (modified; Manal's file from IMP-103): adds the §6.5 shared types next to the error envelope.
  - `MoneyAmount`: a Decimal with at most 12 digits and 2 decimals, serialised as a two-decimal string (IMD-05).
  - `Money {amount, currency}`, which forbids extra fields.
  - `Page[T] {items, total, limit, offset}`.
  - `UtcTimestamp`, which normalises a timestamp to UTC so it serialises with `Z` (§6.1).
- `apps/api/app/trips/schemas.py` (created, step 1):
  - `TripIn` (API-07 body): `extra="forbid"`, trims strings, and gives `adults` 1, `children` 0, `group_needs` `[]` and `budget` null as defaults.
  - `TripOut`: every §6.5 field, including `num_days`, `has_itinerary` and `destination {id, name, timezone, currency, is_sample}`.
  - `TripStatus`.
  - Name mapping: `title` -> `trips.title`, `adults`/`children` -> same columns, `budget {amount, currency}` -> `budget_amount`/`budget_currency`.
- `apps/api/app/trips/domain.py` (created, step 2): pure rules that return `FieldError(field, message)`; no I/O and no framework imports.
  - Title 1 to 120 characters after trimming.
  - `end_date >= start_date`, else the error names `end_date`.
  - Trip length 1 to `MAX_TRIP_DAYS` = 14. The maximum can be lowered per call but never raised above the database CHECK, and the message states the limit.
  - Adults 1 to 20, children 0 to 20.
  - `group_needs` from the IMD-40 vocabulary (`GroupNeed`), with no duplicates.
  - Budget amount > 0 when given, with the currency as three upper-case letters (amount and currency come together, DR-16/17).
  - `validate_destination` rejects an id that is not among the active destinations. Its message lists every supported destination as `name (id)`.
- `apps/api/app/trips/repository.py` (created, step 3): every trip query filters by the caller's `user_id` and `deleted_at IS NULL`.
  - `insert_trip` writes `status 'draft'` and `plan_revision 0`.
  - `get_owned` returns the trip, its destination and `has_itinerary` (an `exists` over `itinerary_days`).
  - `list_owned` returns one page ordered by `updated_at desc` (ties broken by `created_at desc`, then `id`) and the total. Archived trips are excluded unless `include_archived`.
  - `active_destinations`. `destinations` and `itinerary_days` are only read here.
- `apps/api/app/budget/repository.py` (created, step 5; MOD-B09 owns `budget_settings`): `upsert_settings(session, trip_id, *, transport_allowance_per_day, stay_budget_per_night, contingency_pct)`.
  - With no values it inserts the table defaults and leaves an existing row alone (on conflict do nothing).
  - With values it upserts them and sets `updated_at`.
- `apps/api/app/trips/service.py` (created, step 4):
  - `create_trip` runs every domain rule and the destination check. Any error raises `ValidationFailed` with one detail per field.
  - It then inserts the trip and calls `budget_repository.upsert_settings` in the same request transaction, and creates no `trip_preferences` row (IMD-25).
  - `get_trip` raises `NotFound` for a missing, soft-deleted or foreign trip; all three give the same 404.
  - `list_trips`.
- `apps/api/app/trips/router.py` (created, step 4), with prefix `/trips`:
  - API-07 `POST` returns 201 `TripOut`.
  - API-08 `GET` takes `limit` (1 to 50, default 20), `offset` (≥ 0) and `include_archived` (default false), and returns `Page[TripOut]`.
  - API-10 `GET /{trip_id}` returns `TripOut`.
  - Handlers use `CurrentUser` and `DbSession` from `app.auth.deps` (imported, not changed).
- `apps/api/app/main.py` (modified; Manal's file from IMP-103): one import and one `api_v1.include_router(trips_router)` line. The routes sit behind the existing `/api/v1` CurrentUser guard.
- `apps/api/tests/api/test_health.py` (modified; Manal's IMP-103 test): `test_health_unknown_api_v1_route_returns_not_found_envelope` used `/api/v1/trips` as its example of an unknown route. That route now exists (and answers 401 without a token), so the test now uses `/api/v1/no-such-route`. Its assertions are unchanged.
- `apps/api/tests/unit/trips/test_trip_validation.py` (created): 31 tests covering every rule (TC-071, TC-072, TC-073).
- `apps/api/tests/api/test_trips.py` (created): 29 tests against the migrated PostgreSQL, using Sampleton loaded through `seed.load_fixture` and an inactive destination row inserted by the test (TC-063, TC-068 to TC-073, API-08 paging and scoping).

Not changed: `app/auth/` (Het), `app/db/models/` (Jeel), migrations, `contracts/`, the Makefile, env names.

## Checks that the tests can fail

Each mutation was applied in the working tree, run, and reverted with `git checkout`:

| Mutation | Result |
| --- | --- |
| Owner filter removed from `_owned_trips` | `2 failed, 27 passed` (TC-063 and the list scoping test) |
| `end_date < start_date` rule disabled | `1 failed, 28 passed` (TC-071) |
| Budget rule changed to `amount < 0` | `3 failed, 28 passed` in the unit tests (TC-073) |

## Commands run

All commands ran with `TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/travel_test` on the command line, after `make db-up`.

| Command | Result line |
| --- | --- |
| `make db-up` | `Container group12-db-1 Healthy` |
| `make test-api ARGS='-k trips'` | `29 passed, 62 deselected, 1 warning in 7.38s` |
| `make test-unit ARGS='-k trip_validation'` | `31 passed, 201 deselected, 1 warning in 0.17s` |
| `make test-authz` | `9 passed in 0.57s` |
| `make lint` | `All checks passed!` / `90 files already formatted` / `All matched files use Prettier code style!` |
| `make typecheck` | `Success: no issues found in 53 source files` (web: `✓ Types generated successfully`) |
| `make imports` | `Contracts: 3 kept, 0 broken.` |
| `make test` | unit `232 passed, 1 warning in 5.24s`; contract `11 passed in 0.08s`; api `91 passed, 1 warning in 11.06s`; authz `9 passed in 0.58s`; web `Tests  48 passed (48)` |
| `make check` | exit 0; includes `openapi-check: not yet implemented (IMP-214)` |

The one warning is the existing `StarletteDeprecationWarning` from `fastapi/testclient.py`; it is not from this change.

## OpenAPI check (`app.openapi()`, instead of `make openapi-check`)

```text
POST /api/v1/trips API-07 Create a draft trip | body: TripIn | 201 TripOut | params: []
GET /api/v1/trips API-08 List my trips | body: - | 200 Page_TripOut_ | params: ['limit', 'offset', 'include_archived']
GET /api/v1/trips/{trip_id} API-10 Read one of my trips | body: - | 200 TripOut | params: ['trip_id']
TripIn: ['title', 'destination_id', 'start_date', 'end_date', 'adults', 'children', 'group_needs', 'budget'] additionalProperties: False
TripOut: ['id', 'title', 'destination_id', 'start_date', 'end_date', 'num_days', 'adults', 'children', 'group_needs', 'budget', 'status', 'plan_revision', 'plan_stale', 'has_itinerary', 'destination', 'created_at', 'updated_at']
Page_TripOut_: ['items', 'total', 'limit', 'offset']
Money-Output amount: {'type': 'string', 'title': 'Amount'}
```

`contracts/openapi.v1.json` and the web types are not generated yet; that is IMP-214.

## Not run

- `make openapi-check`: still the IMP-214 placeholder; the `app.openapi()` check above stands in for it.
- `make e2e`: this card touches no journey screen.

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| Valid input creates a draft trip, 201, visible in API-08 (FR-007 AC1, TC-068) | verified | `test_tc_068_valid_input_creates_a_draft_trip_visible_in_the_list`; `test_api_07_writes_default_budget_settings_and_no_preferences` |
| Unknown or inactive destination rejected with the supported list (FR-007 AC2, TC-069) | verified | `test_tc_069_an_unknown_destination_is_rejected_with_the_supported_list` (unknown id and inactive row; message holds Sampleton's id and name, not the inactive one; no row written) |
| Group needs are stored (FR-007 AC3, TC-070) | verified | `test_tc_070_group_needs_are_stored` (response, table row and API-10) |
| End before start: 422 naming `end_date` (FR-008 AC1, TC-071) | verified | `test_tc_071_end_before_start_returns_422_naming_end_date`; unit `test_tc_071_*` |
| Longer than 14 days rejected with the limit (FR-008 AC2, TC-072) | verified | `test_tc_072_a_trip_longer_than_14_days_is_rejected_with_the_limit` (15 days rejected with "14 days", 14 days accepted); unit `test_tc_072_*` |
| Budget <= 0 rejected (FR-008 AC3, TC-073) | verified | `test_tc_073_a_budget_of_zero_or_less_is_rejected` (`0.00`, `0`, `-5.00` -> field `budget.amount`); unit `test_tc_073_*` |
| User B reading user A's trip gets 404 with no trip data (FR-005 AC1, TC-063) | verified | `test_tc_063_another_users_trip_is_404_with_no_trip_data` (same envelope as a missing id apart from `request_id`; no id or title in the body) |
| API-08 returns only the caller's non-deleted trips, limit <= 50 | verified | `test_api_08_lists_only_my_trips_newest_first`, `test_a_soft_deleted_trip_is_404_and_not_listed`, `test_api_08_limit_is_1_to_50_and_offset_not_negative`, `test_api_08_accepts_the_maximum_limit`, `test_api_08_pages_with_limit_and_offset` |
| New routes answer 401 without a token (IMP-108 inventory) | verified | `make test-authz` (TC-344 walks the new routes); `test_trip_routes_need_a_token` |
| A body naming a user gets 422 (IMD-45) | verified | `test_a_body_naming_a_user_is_rejected`; TC-348 in `make test-authz` |

## RUN-018b · currency rule fix (same PR #204)

- Base commit: eb44ee3 (origin/main had not moved, so no rebase was needed)
- Change: `app/trips/domain.py` gains `SupportedDestination.currency` and `validate_budget_currency(budget_currency, destination)`, which is pure. When a well-formed budget currency differs from the destination's currency, it returns a `budget.currency` error, for example "Budget currency must be GBP, the currency of Sampleton (sample)." A malformed code is still reported once, by the three-letter ISO 4217 check, and a trip without a budget is unaffected. `app/trips/service.py` passes the chosen active destination (with the currency already read by `active_destinations`) into the rule. No contract, table or envelope changed.
- Tests added:
  - unit (`test_trip_validation.py`): `test_a_budget_in_the_destination_currency_passes`, `test_a_budget_in_another_valid_currency_names_budget_currency`, `test_no_budget_needs_no_currency_match`, `test_a_malformed_currency_is_reported_once_by_the_format_rule`;
  - API (`test_trips.py`): `test_the_budget_currency_must_be_the_destination_currency` (Sampleton: INR gives 422 on `budget.currency` and writes no row; GBP gives 201).
- Existing tests and fixtures: none used a budget currency other than its destination's. Every API test budget is GBP with Sampleton (GBP), and the unit fixture is GBP; the unit test destinations gained a `currency` value (`GBP`, `EUR`). `test_traveller_counts_and_currency_are_checked` sends `gb`, which is malformed, so it still gets only the format error.

All commands ran with `TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/travel_test` on the command line.

| Command | Result line |
| --- | --- |
| `make db-up` | `Container group12-db-1 Healthy` |
| `make test-unit ARGS='-k trip_validation'` | `35 passed, 201 deselected, 1 warning in 0.22s` |
| `make test-api ARGS='-k trips'` | `30 passed, 62 deselected, 1 warning in 8.36s` |
| `make test-authz` | `9 passed in 0.69s` |
| `make lint` | `All checks passed!` / `90 files already formatted` / `All matched files use Prettier code style!` |
| `make typecheck` | `Success: no issues found in 53 source files` |
| `make imports` | `Contracts: 3 kept, 0 broken.` |
| `make check` | exit 0; unit `236 passed, 1 warning in 4.40s`, contract `11 passed in 0.04s`, api `92 passed, 1 warning in 11.00s`, authz `9 passed in 0.54s`, web `Tests  48 passed (48)`; `openapi-check: not yet implemented (IMP-214)` |

Acceptance (RUN-018b): the budget currency must equal the destination currency (§9.3.2): verified by the unit and API tests above.

## Blockers

none

## Proposed decisions

- PD-IMP-203-1 (schema names): the card names the models `TripCreate`, `TripOut` and `TripPage`, while §6.5/§6.6.2 name them `TripIn`, `TripOut` and `Page<TripOut>`. The specification wins (CLAUDE.md), so the code uses `TripIn` and the generic `Page[TripOut]`, which OpenAPI shows as `Page_TripOut_`. Proposal: amend the card wording to the specification names.
- PD-IMP-203-2 (supported-destination list in the 422): the §6.3 `details` entry has only `field` and `message`, so the supported destinations are listed in the message of the `destination_id` detail as `name (id)` pairs separated by `; `. The envelope shape is unchanged. Proposal: record this format so IMP-212 can show it.
- PD-IMP-203-4 (currency rule and the §6.7 example, RUN-018b): the §6.7 worked example for API-07 creates a Sampleton trip with an INR budget, which contradicts §9.3.2 ("a known currency (ISO 4217, destination currency in the MVP)") and §9.3.1 (no currency conversion). The code follows §9.3.2: when a budget is given, `budget.currency` must equal the destination's currency, else 422 on `budget.currency`. Proposal: change the §6.7 example to a GBP budget for Sampleton, or to a destination whose currency is INR.
- PD-IMP-203-3 (TC-073 field name): the §13 TC-073 row says `budget_total`; §6.5 has `budget {amount, currency}`. The error names `budget.amount`. Proposal: correct the TC-073 row.

## Open issues

- Resolved in RUN-018b: the budget currency must equal the destination currency (§9.3.2); see the RUN-018b section and PD-IMP-203-4.
- API-08 already accepts `include_archived` (§6.6.2). Nothing can archive a trip until IMP-602, so the test sets `status` directly.
- Every trip created in one transaction gets the same `now()`, so newest-first order is tested with rows inserted with explicit timestamps; the `updated_at` trigger runs only on update.
