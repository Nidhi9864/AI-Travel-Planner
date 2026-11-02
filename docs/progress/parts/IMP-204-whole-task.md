# IMP-204 · whole-task part

- Run id: RUN-020
- Owner: Manal (manalPatel2557)
- Status: PR_OPEN
- Base commit: c425fb1
- Branch: feat/IMP-204-whole-task
- Reviewer: Kirtan (kirtan-S111)
- Traces to: US-017, US-018; FR-009, FR-010, FR-005; NFR-016; TC-074, TC-075, TC-076, TC-077, TC-078, TC-079; IMD-25, IMD-29, IMD-40, IMD-45
- Card steps built: 1 to 6
- Prerequisites on main: IMP-203 (`app/trips/service.py`), IMP-205 (`app/places/vocabulary.py`) and its follow-up PR #206 (`app/places/service.py`)

## Changed files

- `apps/api/app/trips/preference_mapping.py` (created, step 4): pure (imports only the standard library), with `MAPPING_VERSION = "pm-1"`.
  - `map_preferences(prefs, trip) -> MappedPreferences(filters, weights, pace_limits, mapping_version)`.
  - **Filters** (`HardFilters`):
    - `step_free_required`;
    - `child_friendly_required` when `children > 0`;
    - `categories_excluded = {stay}`;
    - `must_visit_place_ids`.
    - `HardFilters.keeps(step_free=, child_friendly=)`: when step-free is required, only `step_free is True` passes (unknown excluded, §8.9). When children travel, only `child_friendly is False` is excluded (unknown kept, never read as false).
  - **Weights** (`RankingWeights`, §8.9):
    - interest 0.40, price 0.25, distance 0.15, duration 0.10, `c_signal` 0.10;
    - the signal weight is 0 in the MVP and the rest are renormalised to sum to 1;
    - `budget_priority` `saving` moves 0.10 from interest to price;
    - `long_visit_factor` is relaxed 0.5, balanced 0.2, busy 0, with `duration_component(d) = 1 - min(d/180, 1) * factor`;
    - the interest categories are carried for the interest component.
  - **Pace limits** (§8.9, FR-029): relaxed 3 items / 300 min, balanced 5 / 480, busy 7 / 600.
  - **Effects** (`FIELD_EFFECTS`, FR-009 AC3): interests, pace and budget_priority are `rank`; step_free_required and must_visit_place_ids are `filter`; notes, transport_pref and accommodation_type are `note` (PD-IMP-204-2).
  - Notes are never read by the mapping.
- `apps/api/app/trips/schemas.py` (modified, step 1):
  - `PreferencesIn` (API-14 body, full replacement):
    - `extra="forbid"`;
    - `interests` are `OfferedCategory` from `vocabulary.py` (every category except `stay`, IMD-40), with no duplicates;
    - enums `Pace`, `BudgetPriority`, `TransportPref` and `AccommodationType`, with the defaults of migration 0003;
    - `notes` at most 1,000 characters, with control characters removed (line breaks and tabs kept; §6.5);
    - `must_visit_place_ids` at most 10 (IMD-40), with no duplicates.
  - `PreferencesOut`: the same fields, plus `must_visit_places [{id, name}]`, `effects [{field, effect}]` and `saved`.
- `apps/api/app/trips/repository.py` (modified, step 2): these functions take a `trip_id` the service has just read with the owner-scoped `get_owned` in the same transaction.
  - `get_preferences`.
  - `upsert_preferences`: insert … on conflict update.
  - `must_visit_place_ids`.
  - `replace_must_visit`: deletes must-visit rows no longer listed, then upserts the listed places as `must_visit`, so a saved or rejected row of the same place becomes `must_visit` (one row per place, `unique (trip_id, place_id)`).
  - `mark_preferences_saved`: sets `status ready` from `draft` (IMD-25) and `plan_stale` when an itinerary exists.
  - MOD-B03 stays the only writer of `trip_preferences` and `trip_places`.
- `apps/api/app/trips/service.py` (modified, steps 2, 3 and 5):
  - `save_preferences`, all in the request's one transaction:
    - owned trip, else 404;
    - an archived trip gets 409 `CONFLICT` (§6.2);
    - every must-visit id must be an active place of the trip's destination, otherwise 422 with one detail per id, field `must_visit_place_ids.<index>`, and a message naming the id;
    - then it upserts preferences, replaces the must-visit set and marks the trip;
    - it returns the API-15 shape.
  - `get_preferences`: owned trip, else 404. It returns the stored values or the defaults with `saved: false`, the must-visit ids and active places by name, and the pm-1 effects.
  - Notes are stored as written, minus control characters.
- `apps/api/app/trips/router.py` (modified): API-14 `PUT /api/v1/trips/{trip_id}/preferences` and API-15 `GET` (200 `PreferencesOut`), behind the `/api/v1` CurrentUser guard.
- `apps/api/app/places/repository.py` and `apps/api/app/places/service.py` (modified; Jeel's module): one read-only function each, `repository.active_places_by_ids(session, destination_id, place_ids)` and `service.active_place_names(...) -> {id: name}`.
  - **Reason:** the existing service has only `list_destinations` and `search_places` (paged search by name and category); neither can check a given list of ids against the trip's destination or name them. The trips module reads places only through `places/service.py`.
- `apps/api/tests/unit/trips/test_preference_mapping.py` (created): 15 tests (TC-077, TC-078, TC-079, effects, purity).
- `apps/api/tests/api/test_preferences.py` (created): 27 tests (TC-074, TC-075, TC-076, validation, trip state, archived, ownership, token).

Not changed: `auth/`, `core/`, the db models, migrations, `vocabulary.py`, the IMP-203 routes and the Makefile.

## Checks that the tests can fail

Each mutation was applied to `trips/service.py`, run, and restored:

| Mutation | Result |
| --- | --- |
| Must-visit destination check disabled | `2 failed, 25 passed` (another destination; inactive or unknown) |
| `plan_stale` never set | `1 failed, 26 passed` (existing itinerary marked stale) |

## Commands run

All commands ran with `TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/travel_test` on the command line, after `make db-up` (`Container group12-db-1 Healthy`).

| Command | Result line |
| --- | --- |
| `make test-api ARGS='-k preferences'` | `27 passed, 115 deselected, 1 warning in 9.65s` |
| `make test-unit ARGS='-k preference_mapping'` | `15 passed, 283 deselected, 1 warning in 0.24s` |
| `make test-api ARGS='-k trips'` | `30 passed, 112 deselected, 1 warning in 9.60s` (IMP-203 unchanged) |
| `make test-authz` | `9 passed in 0.86s` (the route inventory walks API-14 and API-15) |
| `make lint` | `All checks passed!` / `102 files already formatted` / `All matched files use Prettier code style!` |
| `make typecheck` | `Success: no issues found in 61 source files` |
| `make imports` | `Contracts: 3 kept, 0 broken.` |
| `make test` | unit `298 passed, 1 warning in 6.02s`; contract `11 passed in 0.07s`; api `142 passed, 1 warning in 27.40s`; authz `9 passed in 0.91s`; web `Tests  48 passed (48)` |
| `make check` | exit 0; unit `298 passed, 1 warning in 5.61s`, api `142 passed, 1 warning in 29.80s`; `openapi-check: not yet implemented (IMP-214)` |

## OpenAPI check (`app.openapi()`, instead of `make openapi-check`)

```text
PUT /api/v1/trips/{trip_id}/preferences API-14 Save my trip's preferences and must-visit places | body: PreferencesIn | 200 PreferencesOut
GET /api/v1/trips/{trip_id}/preferences API-15 Read my trip's preferences | body: - | 200 PreferencesOut
PreferencesIn: ['interests', 'pace', 'budget_priority', 'transport_pref', 'accommodation_type', 'step_free_required', 'notes', 'must_visit_place_ids'] additionalProperties: False
PreferencesOut: ['interests', 'pace', 'budget_priority', 'transport_pref', 'accommodation_type', 'step_free_required', 'notes', 'must_visit_place_ids', 'must_visit_places', 'effects', 'saved']
Pace ['relaxed', 'balanced', 'busy']
BudgetPriority ['saving', 'balanced', 'comfort']
TransportPref ['walking', 'local_transport', 'car']
AccommodationType ['budget', 'mid_range', 'premium', 'any']
Effect ['filter', 'rank', 'note']
```

## Not run

- `make openapi-check`: still the IMP-214 placeholder.
- `make e2e`: no journey screen in this card.

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| Saved preferences are stored per trip and returned unchanged (FR-009 AC1, TC-074) | verified | `test_tc_074_saved_preferences_are_returned_unchanged` (PUT response equals GET; table row checked); `test_api_15_before_saving_returns_the_defaults_with_saved_false` |
| Must-visit places stored as trip_places relation must_visit (FR-009 AC2, TC-075) | verified | `test_tc_075_must_visit_places_are_stored_as_trip_places_must_visit` (stored, replaced, cleared); `test_a_saved_place_becomes_must_visit_and_other_saved_places_stay`; `test_a_must_visit_place_of_another_destination_is_rejected_naming_it`; `test_inactive_or_unknown_must_visit_places_are_rejected` |
| Each field reports filter, rank or note (FR-009 AC3, TC-076) | verified | `test_tc_076_each_field_reports_filter_rank_or_note`; unit `test_every_preference_field_has_exactly_one_effect` |
| step_free_required is a hard filter excluding places whose step_free is not true (FR-010 AC1, TC-077) | verified | unit `test_tc_077_step_free_required_keeps_only_places_marked_step_free` (true kept; false and unknown excluded) |
| Relaxed pace reduces the long-visit weight as §8.9 states (FR-010 AC2, TC-078) | verified | unit `test_tc_078_relaxed_pace_reduces_the_score_of_long_visits` (factors 0.5 / 0.2 / 0; a 240-minute visit scores 0.5 / 0.8 / 1.0) |
| MAPPING_VERSION is available for the generation record (FR-010 AC3, TC-079) | verified | unit `test_tc_079_the_mapping_version_is_pm_1_and_travels_with_the_result`, `test_tc_079_each_preference_changes_a_filter_or_a_weight` |
| Another user's trip returns 404 on both routes | verified | `test_another_users_trip_is_404_on_both_routes` (same message as a missing trip, no data, nothing changed) |
| Notes never a filter or weight; unknown flags never false (card step 6) | verified | unit `test_notes_change_neither_filters_nor_weights`, `test_children_require_child_friendly_but_unknown_is_never_read_as_false` |

## Blockers

none

## Proposed decisions

- PD-IMP-204-1 (where the mapping values come from): the card says "values from §9", but §9 has no preference-mapping section. The values are in §8.9: the score weights, the `saving` shift, the pace factors {0.5, 0.2, 0} and the pace presets. Built from §8.9 exactly. Proposal: point the card to §8.9.
- PD-IMP-204-2 (effects of transport_pref and accommodation_type): §6.5 allows only `filter`, `rank` or `note`. `transport_pref` sets the routing mode (§9.3.5) and `accommodation_type` is model context; neither filters nor ranks places, so both are reported as `note`.
- PD-IMP-204-3 (pace presets in two places): IMD-29 puts the pace presets in `app/generation/presets.py`, which IMP-503 creates. The card asks the mapping to return `pace_limits`, so the §8.9 numbers live in `preference_mapping.PACE_LIMITS` for now. Proposal: IMP-503 makes `presets.py` the single source and the mapping reads it, so there are no duplicated numbers.
- PD-IMP-204-4 (child-friendly filter): the card names a `child_friendly` filter when children travel but gives no rule. Built: exclude only places marked `child_friendly = false`; unknown is kept, because an unknown flag is never read as false.
- PD-IMP-204-5 (must_visit_places): the card asks API-15 for the must-visit places (id, name), while §6.5 lists only `must_visit_place_ids`. `PreferencesOut` has both (an added response field is allowed inside v1, §6.1). Places are ordered by name. A must-visit place that becomes inactive later keeps its id in `must_visit_place_ids`, with no entry in `must_visit_places`.
- PD-IMP-204-6 ("an itinerary exists"): the itinerary module has no service yet. `plan_stale` uses the read-only `exists(itinerary_days)` that the trips repository already has from IMP-203 (`TripOut.has_itinerary`). Proposal: switch it to an itinerary service call when MOD-B08 has one.
- PD-IMP-204-7 (duplicates): duplicate `interests` or `must_visit_place_ids` are rejected with 422 instead of being silently de-duplicated.
- PD-IMP-204-8 (`saving` vs "high budget priority"): IMP-304's card says a "high budget priority" moves 0.10 from interest to price, while §8.9 says `budget_priority = saving`. Built as §8.9.

## Open issues

- Every API-14 save sets `plan_stale` while an itinerary exists, even if nothing changed. IMP-510 narrows this to plan-affecting changes.
- The `reduced_mobility` group need (IMD-40) does not set `step_free_required`; nothing in the specification says it should. The trip wizard (IMP-212) may pre-fill it.
