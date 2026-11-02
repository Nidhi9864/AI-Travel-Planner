# IMP-209 · whole-task part

- Run id: RUN-024
- Owner: Junaid (Junaid-Kureshi)
- Status: PR_OPEN
- Base commit: d552fe0
- Branch: feat/IMP-209-whole-task
- Reviewer: Kirtan (kirtan-S111)
- Traces to: US-088; FR-079; TC-236, TC-237; IMD-30
- Card steps built: 1 to 4

## Changed files

- `apps/api/app/routing/estimate.py` (created, pure; steps 1 and 2):
  - **Types:** `TravelMode` (walking, local_transport, car: the `itinerary_items.travel_mode` CHECK list) and `TravelSource` (`routing_api` or `fallback_estimate`).
  - **`TravelEstimate(minutes, distance_m, mode, travel_source="fallback_estimate")`:**
    - It is frozen.
    - Its `label` is "Estimate" for a fallback value (FR-079 AC1), and also for `local_transport` routing values, which have no transit timetables (§9.3.5). It is `None` for walking or car routing values.
  - **`haversine_m`:** distance on a sphere with a radius of 6,371 km.
  - **`estimate(from_lat, from_lon, to_lat, to_lon, mode)`:** `distance_m` is the haversine distance rounded to whole metres, and `minutes = ceil(1.3 · distance_m / v)`, computed exactly. Identical points give 0 minutes and 0 m. An unknown mode raises `ValueError`.
  - **`buffer_minutes(travel_source)`:** 5 after `routing_api` and 15 after `fallback_estimate`. An unknown source raises `ValueError`.
  - **Imports:** only `math`, `dataclasses`, `enum`, `fractions` and `typing`.
- `apps/api/app/routing/service.py` (created; step 3): `async travel_time(place_a, place_b, mode) -> TravelEstimate`.
  - The places are anything with `lat` and `lon` (`Located` protocol; a `places` row qualifies, with Decimal coordinates). For now it returns the estimate.
  - It is async so that IMP-307 can put the route cache and OpenRouteService in front without changing the signature. Nothing here touches the database.
- `apps/api/.importlinter` (Het's file, appended only): new contract `pure-domain` (§4.4 "Pure domain").
  - `app.routing.estimate` may not import `fastapi`, `sqlalchemy`, `httpx`, `google`, `app.db`, `app.core` or any `app.*.router`, `app.*.service` or `app.*.repository`.
  - **Reason:** as agreed in RUN-002, each card that creates a pure module listed in §4.4 adds it to this contract's `source_modules`, and this card creates the first one.
  - The three existing contracts are unchanged. The routing-isolation contract is not added; it comes with `app.routing.client` (IMP-307).
- `apps/api/tests/unit/routing/test_estimate.py` (created, 24 tests; step 4): the §9.3.5 constants; known distance pairs (one degree of latitude, a ~4 km city pair, symmetry); the formula for each mode; a 1 km walk and drive; rounding up; exact multiples (750, 1500 and 3000 m) not inflated; identical points give 0 in every mode; label and source (TC-236); buffers (TC-237); unknown mode or source; determinism; standard-library imports only; the service using place coordinates; the stable service signature.

## Constants (all Proposed, §9.3.5)

| Constant | Value | §9.3.5 source |
| --- | --- | --- |
| `DETOUR_FACTOR` | 1.3 | "minutes = ceil(1.3 · d / v)" |
| `SPEED_M_PER_MIN[walking]` | 75 | "v = 75 m/min walking" |
| `SPEED_M_PER_MIN[car]` | 400 | "400 m/min driving modes" |
| `SPEED_M_PER_MIN[local_transport]` | 400 | Mode row: "`local_transport` → ORS `driving-car`", so it is a driving mode at 400 m/min |
| `BUFFER_MIN[routing_api]` | 5 | "5 min after `routing_api`" |
| `BUFFER_MIN[fallback_estimate]` | 15 | "15 min after `fallback_estimate`" (FR-079 AC2) |
| `EARTH_RADIUS_M` | 6,371,000 | mean Earth radius for the haversine formula (§9.3.5 names haversine without a radius) |

## Commands and results

| Command | Result line |
| --- | --- |
| `make test-unit ARGS='-k estimate'` | `24 passed, 330 deselected, 1 warning in 0.24s` |
| Scratch copy of `app/` and `.importlinter` in the session scratchpad (outside the repository) with `import sqlalchemy` and `from app.core import config` planted in `app/routing/estimate.py`, `lint-imports --config .importlinter` | `Contracts: 3 kept, 1 broken.` (`app.routing.estimate -> app.core.config (l.18)`, `app.routing.estimate -> sqlalchemy (l.17)`); copy deleted |
| `make imports` (real code) | `Contracts: 4 kept, 0 broken.` |
| `make lint` | `All matched files use Prettier code style!` (ruff `All checks passed!`) |
| `make typecheck` | `Success: no issues found in 66 source files` |
| `make db-up` | `Container group12-db-1 Healthy` |
| `make test` | unit `354 passed, 1 warning in 4.84s`; contract `28 passed in 0.08s`; api `183 passed, 1 warning in 35.53s`; authz `9 passed in 0.91s`; web `Tests  48 passed (48)` |
| `make check` | exit 0 (unit `354 passed, 1 warning in 4.93s`; `Contracts: 4 kept, 0 broken.`; `openapi-check: not yet implemented (IMP-214)`) |
| `make db-down` | `Network group12_default Removed` |

Mutation check, reverted: with the fallback buffer set to 5, `make test-unit ARGS='-k estimate'` failed.

Not run: `make e2e` (no journey in this card). `make openapi-check` is still the IMP-214 placeholder.

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| With no routing data the fallback value is returned with source fallback_estimate, shown as Estimate (FR-079 AC1, TC-236) | verified | `test_tc_236_the_fallback_value_is_labelled_fallback_estimate_shown_as_estimate`; `test_the_service_returns_the_estimate_from_place_coordinates` |
| Fallback values carry the 15-minute buffer, routing values the 5-minute buffer (FR-079 AC2, TC-237) | verified | `test_tc_237_fallback_values_carry_15_minutes_and_routing_values_5` |
| estimate() is pure (no I/O) and deterministic | verified | `pure-domain` import contract (kept on the real code, broken by a planted import in the scratch copy); `test_the_estimate_module_imports_only_the_standard_library`; `test_estimate_is_deterministic` |

## Blockers

None.

## Proposed decisions

- **PD-IMP-209-1: local_transport speed.** It is 400 m/min, read from §9.3.5: local_transport is routed as `driving-car`, and the formula gives 400 m/min for "driving modes". No new value was introduced.
- **PD-IMP-209-2: exact minutes.** Minutes are computed from the whole-metre distance with exact rational arithmetic. With floats, `ceil(1.3 · 1500 / 75)` gave 27 instead of 26, because the haversine result was 1500.0000000000002 m. The rounded distance is also the value stored in `travel_from_prev_m`, so minutes and metres agree.
- **PD-IMP-209-3: label for routing values.** `TravelEstimate.label` is "Estimate" for `local_transport` routing values as well as all fallback values (§9.3.5 Mode row), and `None` for walking or car routing values. The display text for routing values is decided by the screens that show travel times.
- **PD-IMP-209-4: scope of the pure-domain contract.** Besides the §4.4 list (fastapi, sqlalchemy, httpx, google.genai, any repository or service), it also forbids `app.db`, `app.core` and `app.*.router`, as the run asked. Later pure modules (validation, budget, ranking, …) join by adding themselves to `source_modules`.

## Open issues

- The constants are Proposed and are to be calibrated against routing results in Sprint 3 (§9.3.5).
- The 1-day cache of fallback estimates (IMD-30) and the lookup order cache → OpenRouteService → estimate belong to IMP-307.

## Fix runs RUN-024b to RUN-024d

- A stray commit (b17e1e4, a local tool set-up made with another identity that added a `graphify-out/` cache) was removed from the branch before review. The branch was reset to 92bba70, the last of the part's own commits, and pushed with a lease pinned to b17e1e4.
- Reason: the guards secret scan reported 9 gitleaks findings in `graphify-out/cache/stat-index.json` at b17e1e4, and the files were outside the part's scope. Because the guards push job on `main` scans every fetched branch, it also failed main's CI run 41506367439.
- `make check` on 92bba70 (with `make db-up`): passed (`All checks passed!`, `Success: no issues found in 66 source files`, `Contracts: 4 kept, 0 broken.`, `354 passed, 1 warning`, `28 passed`, `183 passed, 1 warning`, `9 passed`, `Tests  48 passed (48)`).
- Re-run of the failed guards job on `main` (run 41506367439): see the run's SYNC REPORT.
