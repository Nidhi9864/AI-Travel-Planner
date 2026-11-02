# IMP-205 · places-api-search part

- Run id: RUN-019b
- Owner: Jeel (jeelfefar2141)
- Status: PR_OPEN
- Base commit: cc6a900
- Branch: feat/IMP-205-places-import-api (one branch and pull request for the card, IMD-66), built on Malhar's import-quality-gate part and its `vocabulary.py`
- Reviewer: Kirtan (kirtan-S111)
- Traces to: US-024, US-028; FR-007, FR-016, FR-019; TC-069, TC-101, TC-102
- Card steps built: 5 and 6, and the API tests of step 7

## Changed files

- `apps/api/app/places/schemas.py` (created): response shapes from §6.5.
  - `Destination`: id, slug, name, region, country_code, timezone, currency, is_sample, center `{lat, lon}`, bbox `{min_lat, max_lat, min_lon, max_lon}`. The card lists fewer fields; §6.5 wins, so `region` and `is_sample` are included.
  - `PlaceSummary`: id, name, category, tags, lat, lon (numbers, 6 decimals), typical_duration_min, price `{min, max, currency, label}` or null, price_label, hours_label, verification_status, suitability `{step_free, child_friendly, indoor}` (each true, false or null).
  - `category`, `tags`, labels and verification status use the enums of `vocabulary.py`, so the OpenAPI contract lists the allowed values. Prices are IMD-05 money strings (`MoneyAmount`).
  - Each model has `from_row`, which maps an ORM row to the response.
  - The §6.5 fields `distance_m` (with `near_*`) and `saved`/`must_visit` (with `trip_id`) belong to the filters IMP-509 and IMP-604 add, so they are not built.
- `apps/api/app/places/repository.py` (created): read-only queries, active rows only, with no user filter (shared reference data).
  - `active_destinations` returns active destinations ordered by name, then id.
  - `search_places(destination_id, q, categories, limit, offset)` returns active places of an active destination ordered by name, then id, and the total. `q` matches anywhere in the name, case-insensitively, with LIKE wildcards escaped; `categories` matches any of them.
- `apps/api/app/places/router.py` (created):
  - API-06 `GET /api/v1/destinations` returns 200 `Destination[]`.
  - API-16 `GET /api/v1/places` takes `destination_id` (required), `q` (1 to 80 characters), `category` (repeatable, `OfferedCategory`: every category except `stay`), `limit` (1 to 50, default 20) and `offset` (≥ 0), and returns 200 `Page<PlaceSummary>`. It uses `DbSession` from `app.auth.deps` (imported, not changed).
  - There is no categories endpoint; the categories are the OpenAPI enums.
- `apps/api/app/main.py` (modified; Manal's file): one import and one `api_v1.include_router(places_router)` line, so both routes sit behind the existing `/api/v1` CurrentUser guard (401 without a token).
- `apps/api/tests/api/test_places.py` (created): 18 test functions (25 cases with parameters).

## Commands run

All commands ran with `TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/travel_test` on the command line, after `make db-up`.

| Command | Result line |
| --- | --- |
| `make test-api ARGS='-k destinations'` | `7 passed, 111 deselected, 1 warning in 1.76s` |
| `make test-api ARGS='-k places'` (API-16 tests) | `25 passed, 93 deselected, 1 warning in 6.27s` |
| `make test-unit ARGS='-k quality_gate'` | `47 passed, 236 deselected, 1 warning in 0.28s` |
| `make test-api ARGS='-k seed'` | `23 passed, 95 deselected, 1 warning in 3.24s` |
| `make test-authz` | `9 passed in 0.81s` (the route inventory walks API-06 and API-16) |
| `make lint` | `All checks passed!` / `98 files already formatted` / `All matched files use Prettier code style!` |
| `make typecheck` | `Success: no issues found in 59 source files` |
| `make imports` | `Contracts: 3 kept, 0 broken.` |
| `make check` | exit 0; unit `283 passed, 1 warning in 5.61s`, contract `11 passed in 0.08s`, api `118 passed, 1 warning in 20.21s` (`test_trips.py` included), authz `9 passed in 0.87s`, web `Tests  48 passed (48)`; `openapi-check: not yet implemented (IMP-214)` |

## OpenAPI check (`app.openapi()`, instead of `make openapi-check`)

```text
GET /api/v1/destinations API-06 List the supported destinations | array of Destination | params: []
GET /api/v1/places API-16 Search places | Page_PlaceSummary_ | params: [('destination_id', True), ('q', False), ('category', False), ('limit', False), ('offset', False)]
Destination: ['id', 'slug', 'name', 'region', 'country_code', 'timezone', 'currency', 'is_sample', 'center', 'bbox']
PlaceSummary: ['id', 'name', 'category', 'tags', 'lat', 'lon', 'typical_duration_min', 'price', 'price_label', 'hours_label', 'verification_status', 'suitability']
Category enum: ['sight', 'museum', 'nature', 'food', 'shopping', 'entertainment', 'religious', 'activity', 'stay']
OfferedCategory enum: ['sight', 'museum', 'nature', 'food', 'shopping', 'entertainment', 'religious', 'activity']
Tag enum count: 35
```

## Not run

- `make openapi-check`: still the IMP-214 placeholder; the `app.openapi()` check above stands in for it.
- `make e2e`: no journey screen in this part.

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| API-06 returns only active destinations to a signed-in user, and 401 without a token | verified | `test_destinations_lists_only_active_destinations_ordered_by_name`, `test_tc_069_destinations_return_the_section_6_5_shape`, `test_destinations_and_places_need_a_token`; `make test-authz` (TC-344) |
| API-16 returns active places of the requested destination, filtered by name and category, paged | verified | `test_places_returns_a_page_of_the_destinations_active_places_by_name`, `test_places_pages_with_limit_and_offset`, `test_places_filters_by_name_case_insensitively`, `test_places_filters_by_one_or_more_categories`, `test_places_hides_inactive_places_and_other_destinations`, `test_places_of_an_inactive_or_unknown_destination_are_an_empty_page`, `test_places_rejects_bad_query_values` |
| Tags under the vocabulary; unknown suitability exposed as unknown (FR-019 AC1-AC2, TC-101, TC-102), exposure half | verified | `test_tc_101_tc_102_tags_from_the_vocabulary_and_unknown_suitability_as_null` (sample-002 `step_free` is `null`, never `false`) |

## RUN-019c · service layer fix (follow-up pull request; PR #205 was already merged)

- Base commit: 02d216f
- Branch: fix/IMP-205-places-service
- Change:
  - `apps/api/app/places/service.py` (created): `list_destinations(session)` and `search_places(session, destination_id, *, q, categories, limit, offset)`. The session is the request's transaction from `DbSession`, as in `trips/service.py`. The service calls `places/repository.py`, maps rows with the schemas' `from_row`, and trims `q`.
  - `apps/api/app/places/router.py` (modified): imports `places.service` instead of `places.repository`; the handlers only validate the query and call the service.
  - No behaviour change: responses, status codes, ordering, paging, the empty page for an unknown or inactive destination (PD-IMP-205-7) and the `stay` rejection (PD-IMP-205-8) are unchanged. No test file changed.
- Router check: `grep -n "repository\|select(\|sqlalchemy" apps/api/app/places/router.py` prints nothing (exit 1).

All commands ran with `TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/travel_test` on the command line, after `make db-up` (`Container group12-db-1 Healthy`).

| Command | Result line |
| --- | --- |
| `make test-api ARGS='-k destinations'` | `7 passed, 111 deselected, 1 warning in 1.88s` |
| `make test-api ARGS='-k places'` | `25 passed, 93 deselected, 1 warning in 7.19s` |
| `make test-authz` | `9 passed in 0.94s` |
| `make lint` | `All checks passed!` / `99 files already formatted` / `All matched files use Prettier code style!` |
| `make typecheck` | `Success: no issues found in 60 source files` |
| `make imports` | `Contracts: 3 kept, 0 broken.` |
| `make check` | exit 0; unit `283 passed, 1 warning in 6.21s`, contract `11 passed in 0.05s`, api `118 passed, 1 warning in 18.09s`, authz `9 passed in 0.85s`, web `Tests  48 passed (48)`; `openapi-check: not yet implemented (IMP-214)` |

## Blockers

none

## Proposed decisions

- PD-IMP-205-7 (API-16 for an inactive or unknown destination): §6.2 says inactive destinations are invisible, and §6.6.3 says an empty page is valid. API-16 returns an empty page (200) for an inactive or unknown `destination_id` rather than 404, so a list request never reveals whether a destination exists.
- PD-IMP-205-8 (`stay` in API-16): the `category` filter accepts only the offered categories (no `stay`, 422 otherwise), while `PlaceSummary.category` uses the full vocabulary so any stored row can be returned. No `stay` places exist yet.
- PD-IMP-205-9 (no service layer): **withdrawn.** Resolved in RUN-019c (follow-up pull request): the router now calls only `places/service.py`, which calls `places/repository.py` (CLAUDE.md §4 rule 1, §4.3).

## Open issues

- `contracts/openapi.v1.json` and the generated web types arrive with IMP-214.
