# IMP-211 · whole-task part

- Run id: RUN-034
- Owner: Het (het-lathiya)
- Status: PR_OPEN
- Base commit: 42ed3fa
- Branch: feat/IMP-211-whole-task
- Reviewer: Manal (manalPatel2557)
- Traces to: US-153; FR-059; FR-005 AC2 (TC-064); NFR-012; Amendment A1 §7.1 (IMD-116)
- Card steps built: 1 to 5 (step 1's shapes were already declared by IMP-214 and were kept unchanged)

## Changed files

- `apps/api/app/itinerary/repository.py` (modified). New read functions:
  - `plan_days`: one query, ordered by `day_number`.
  - `plan_items`: one query that joins `places`, and reads the must-visit flag from `trip_places` with an `EXISTS`, ordered by `day_number`, `position`.
  - `latest_version_id`.
  - `latest_completed_generation`.
  - `latest_itinerary_for_user`: the caller's non-deleted trips joined to `itinerary_versions`, taking the latest `created_at`, as §6 API-09 says.

  `places`, `trip_places` and `ai_generations` are only read, as `budget_settings` already was.
- `apps/api/app/itinerary/service.py` (modified).
  - `get_itinerary` (API-24):
    - Ownership goes through `trips_service.get_trip`, so another user's, a missing or a deleted trip gives the same 404 `NOT_FOUND`.
    - A trip with no days gives 404 `NOT_FOUND` "No itinerary yet."
    - `version_id` answers 501 `NOT_IMPLEMENTED`, because reading a stored version is IMP-610 (IMD-37).
    - Items are grouped per day in memory. Days and items take two queries in total, never one per day.
    - The response is built with `model_validate`, so stored text columns are checked against the response vocabularies.
  - `latest_itinerary` (API-09).
- `apps/api/app/itinerary/router.py` (modified): the API-24 and API-09 placeholders call the service; the other stubs are unchanged.
- `apps/api/tests/authz/route_matrix.py` (modified, an IMP-215 file): API-09 (`scoped`) and API-24 (`foreign`) added. `docs/guides/authz-suite.md` requires a built 501 route to be added to the matrix in the same pull request. Without the entries, `test_tc_065_every_implemented_owned_route_is_in_the_matrix` fails (see the checks below).
- `apps/api/tests/api/test_itinerary.py` (created): 7 tests.
- This record (created).

### What API-24 returns today

The declared `ItineraryOut` (§6.5, IMP-214) is unchanged. These fields hold placeholder values until later cards fill them:

- `findings`: `[]` until IMP-405.
- Each item's `sources`: `[]` until IMP-316 (A1 §7.1).
- `cost` and `travel_from_previous`: null, because their columns are null until IMP-308 and routing fill them. When a column is set, its value is returned.
- `day_cost` and `totals`:
  - They sum the stored item costs; following BF-04, a missing cost counts as 0 and makes the sum incomplete. Today no item has a cost, so every amount is `0.00`, `complete` is false and `incomplete_count` is the number of items.
  - `planning_total` equals `estimate.max`. The transport, stay and contingency lines (BF-05 to BF-09) belong to the budget engine of IMP-308. This is marked in the code with a `shortcut:` comment.
- `theme_origin` is `ai` when the day has a theme and the latest completed generation's outcome is `model` or `model_repaired`; otherwise it is `none`.
- `end_time` is `start_time` plus `duration_min`.
- `must_visit` comes from `trip_places`.

No contract, migration, ORM model, environment variable or error code changed. `MIGRATION_HEAD` is unchanged.

## Checks that the tests can fail

- **Item order.** `plan_items` was changed to order by `position desc`, then reverted. `make test-api` printed `FAILED tests/api/test_itinerary.py::test_us_153_the_saved_plan_is_returned_in_order` and `1 failed, 229 passed, 1 warning in 55.48s`. After the revert: `17 passed, 213 deselected, 1 warning in 4.92s` (`-k itinerary`).
- **Matrix completeness.** With the matrix as it is on main, `make test-authz ARGS='-k tc_065_every'` printed `E         Left contains 2 more items, first extra item: 'GET /api/v1/itineraries/latest'` and `1 failed, 24 deselected in 0.21s`.
- **No N+1.** The ordering test counts the SELECT statements that read `itinerary_items` while API-24 is served: exactly 1 for a three-day plan.

## Commands run

`make db-up` was run first and `make db-down` at the end.

| Command | Result |
| --- | --- |
| `make test-api ARGS='-k itinerary'` | `17 passed, 213 deselected, 1 warning in 4.92s` (the 7 tests of `test_itinerary.py` and the `test_generations.py` tests whose names contain "itinerary") |
| `make test-authz ARGS='-v'` | `28 passed in 12.21s`, including `[API-09 GET /api/v1/itineraries/latest] PASSED`, `[API-24 GET /api/v1/trips/{trip_id}/itinerary] PASSED` and the API-24 control `PASSED` |
| `make openapi-check` | `openapi-check: contracts/ and apps/web/lib/api/schema.d.ts are up to date` |
| `make check` | exit 0. Lint: `All checks passed!`, `139 files already formatted`, `✖ 1 problem (0 errors, 1 warning)` (the existing web warning in `lib/api/client.ts`), `All matched files use Prettier code style!`. Types: `Success: no issues found in 85 source files`, `✓ Types generated successfully`. Imports: `Contracts: 4 kept, 0 broken.`. Contract: `openapi-check: … up to date`. Tests: unit `385 passed, 1 warning in 8.03s`, contract `35 passed, 1 warning in 0.70s`, api `230 passed, 1 warning in 55.28s`, authz `28 passed in 12.16s`, web `Test Files  11 passed (11)`, `Tests  64 passed (64)` |

## Not run

- `make e2e`: no journey or screen changed.

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| After a MOCK generation, API-24 returns the saved days and items in order with plan_revision (US-153 AC1) | verified | `test_us_153_the_saved_plan_is_returned_in_order`: days 1 to 3 with their dates; items in stored (day, position) order; positions 1..n; `plan_revision` 1; `version_id` and `source` match the generation; `sources` `[]` on every item; one items query |
| A trip without itinerary returns 404 with the envelope; a foreign trip returns 404 (FR-005 AC2, TC-064) | verified | `test_tc_064_a_trip_without_an_itinerary_answers_404_no_itinerary_yet` (code, message, details, request_id). `test_tc_064_another_users_itinerary_answers_like_a_missing_trip`: the same envelope as a random ID, "Not found.", so it does not reveal whether a plan exists |
| API-09 returns the caller's most recent itinerary reference only | verified | `test_latest_returns_the_callers_most_recently_changed_itinerary_only`: of the caller's two plans the newer is returned, and another user's even newer plan is ignored. `test_latest_is_null_when_the_caller_has_no_itinerary` |
| Both routes pass the IMP-215 two-user suite | verified | `make test-authz`: user B gets 404 on A's itinerary, and only B's own (null) reference from API-09; A's rows are unchanged; A's control request succeeds |
| Must-visit flag (§6.5 Item) | verified | `test_a_must_visit_place_in_the_plan_is_flagged` |

## Blockers

None.

## Proposed decisions

- **PD-IMP-211-1 (API-09 shape):** card step 3 says `{trip_id, trip_name, plan_revision, updated_at}`, or 404 when there is none. §6 API-09 and the declared `LatestItineraryOut` say `{trip_id, plan_revision, updated_at}`, with `{trip_id: null}` and 200 when there is none (FR-014 AC2). The specification and the contract were followed: no `trip_name`, and 200 with nulls. Proposed: align the card.
- **PD-IMP-211-2 (API-24 field names):** card step 1 names `warnings[]`, `travel_from_prev`, `outcome and provider`, and `theme (with origin ai)`. The declared `ItineraryOut` (§6.5) has `findings[]`, `travel_from_previous`, `source {generation_id, provider, outcome}`, `theme` with `theme_origin`, and also `version_id`, `is_current`, `day_cost`, `end_time`, `origin`, `must_visit` and `totals`. The declared shape was built. Proposed: align the card's step 1 with §6.5.
- **PD-IMP-211-3 (`version_id` before IMP-610):** a request with `version_id` answers 501 `NOT_IMPLEMENTED` rather than silently returning the current plan. Proposed: record this as the IMD-37 behaviour for a reserved query parameter.

## Open issues

- **Placeholder totals.** `totals` and `day_cost` are placeholder sums until IMP-308. With no stored costs they read `0.00` with `complete: false`; the web must show them as incomplete, not as a price. IMP-308 replaces `_cost_sum` and `planning_total` with the budget engine.
- **Message text.** The "no itinerary yet" message is written "No itinerary yet.", in the sentence style of the other envelope messages ("Not found.").
- **Tie-breaking in API-09.** `now()` is fixed within one transaction, so two versions saved in the same transaction get the same `created_at`. API-09 then breaks the tie by trip id.
