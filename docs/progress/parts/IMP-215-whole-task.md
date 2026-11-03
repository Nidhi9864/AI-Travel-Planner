# IMP-215 · whole-task part

- Run id: RUN-031
- Owner: Junaid (Junaid-Kureshi)
- Status: PR_OPEN
- Base commit: 106aa59
- Branch: feat/IMP-215-whole-task
- Reviewer: Kirtan (kirtan-S111)
- Traces to: US-013; FR-005; NFR-012; TC-063, TC-064, TC-065, TC-345, TC-346; IMD-37
- Card steps built: 1 to 5

## Changed files

- `apps/api/tests/authz/route_matrix.py` (created, step 1). `MATRIX` has one `RouteCase` per implemented owned route: API ID, method, path template as FastAPI declares it, access (`foreign` or `scoped`), and how to build a valid body from A's resources (`Owned`). `unlisted_routes(app)` walks `app.routes` and returns every `/api/v1` route that is not in the matrix, not reference data (API-06, 16, 17, §6.2) and not a 501 stub. A route counts as a stub when its handler body is only `raise EndpointNotImplemented()` (IMD-37). This is read from the source, so the check calls no handler.
- `apps/api/tests/authz/test_ownership.py` (created, steps 2 to 4).
  - Fixture: users A and B (rows in `auth.users`; the `CurrentUser` dependency creates their profiles; HS256 test tokens). The SAMPLE destination is seeded. A creates a trip (API-07), saves preferences with one must-visit place (API-14) and starts a generation (API-22) with the MOCK provider (`ok`). The submitted job is captured and run with `jobs.run` on the test's rolled-back session, as in `tests/api/test_generations.py`. The fixture asserts that the generation is `completed` and that `trip_places`, `ai_generations`, `itinerary_days` and `itinerary_items` hold rows for A's trip. The job path could be driven in the test, so no rows were seeded through repositories.
  - `test_tc_063_tc_064_user_b_cannot_read_or_change_user_a`, parametrized over the matrix:
    - B calls each route with A's identifiers. A `foreign` route must answer 404 `NOT_FOUND`. A `scoped` route must answer 200 or 201.
    - No response to B may contain A's user ID, email, trip ID, trip title or generation ID.
    - Before and after each call, A's state is compared. A reads the trip, preferences, generation and trip list through the API. The suite also reads every database row of A's trip: `trips`, A's `profiles` row, `trip_preferences`, `trip_places`, `budget_settings`, `ai_generations`, `itinerary_days`, `itinerary_items`, `itinerary_warnings` and `itinerary_versions`. The two states must be equal.
  - `test_the_same_request_reaches_user_a`: control. A sends the same request to each `foreign` route and gets neither 404 nor 422, so B's 404 comes from the ownership check.
  - `test_tc_063_a_foreign_trip_answers_like_a_missing_one`: A's trip and a random ID give B the same status and the same envelope (request ID aside).
  - `test_tc_065_every_implemented_owned_route_is_in_the_matrix`: `unlisted_routes` is empty, and every matrix entry is a served, built route.
  - `test_tc_065_an_unlisted_route_fails_the_check`: a built probe route is reported and a 501 probe route is skipped. This is a permanent self-check of the walk.
- `docs/guides/authz-suite.md` (created, step 5): what the suite checks and how to add a route.
- Step 5, CI: `.github/workflows/ci.yml` job `api` already runs `make test-authz` (line 231, after `make test-api`). It was not changed.
- This record (created).

No application code, contract, migration, ORM model, env var or error code changed.

## Route matrix

Result of `make test-authz ARGS='-v -p no:cacheprovider -k ownership'` on this branch:

| API | Method | Path | Access | B gets | A unchanged | Control (A) | Result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| API-03 | GET | /api/v1/me | scoped | 200, B's profile | yes | n/a | PASSED |
| API-07 | POST | /api/v1/trips | scoped | 201, B's trip | yes | n/a | PASSED |
| API-08 | GET | /api/v1/trips | scoped | 200, without A's trip | yes | n/a | PASSED |
| API-10 | GET | /api/v1/trips/{trip_id} | foreign | 404 NOT_FOUND | yes | not 404/422 | PASSED |
| API-14 | PUT | /api/v1/trips/{trip_id}/preferences | foreign | 404 NOT_FOUND | yes | not 404/422 | PASSED |
| API-15 | GET | /api/v1/trips/{trip_id}/preferences | foreign | 404 NOT_FOUND | yes | not 404/422 | PASSED |
| API-22 | POST | /api/v1/trips/{trip_id}/generations | foreign | 404 NOT_FOUND | yes, no new `ai_generations` row | not 404/422 | PASSED |
| API-23 | GET | /api/v1/generations/{generation_id} | foreign | 404 NOT_FOUND | yes | not 404/422 | PASSED |

No entry is marked xfail.

- Reference data, outside the matrix: API-06 `GET /api/v1/destinations` and API-16 `GET /api/v1/places`. API-17 `GET /api/v1/places/{place_id}` is a 501 stub.
- Skipped because they answer 501 (IMD-37). The TC-065 test makes each one required as soon as its card replaces the stub:
  - API-04 `PATCH /me`
  - API-11 `PATCH`, API-12 `DELETE`, API-13 `POST …/duplicate` on `/trips/{trip_id}`
  - API-19, API-20, API-21 saved places
  - API-30 and API-31 regenerate
  - API-09, API-24 to API-29, API-32, API-35, API-36 to API-38 (itinerary, items, validate, summary, versions)
  - API-33 and API-34 (costs and budget settings)

## Checks that the tests can fail

- **Unlisted route (TC-065).** An implemented route `GET /api/v1/trips/{trip_id}/temporary-probe` was added to `app/trips/router.py` and reverted afterwards (`git status` clean). `make test-authz ARGS='-q -p no:cacheprovider'` printed `E         Left contains one more item: 'GET /api/v1/trips/{trip_id}/temporary-probe'` and `2 failed, 23 passed in 9.28s`. After the revert it printed `25 passed in 8.72s`.
- **Ownership hole (TC-063, TC-064).** The `Trip.user_id == user_id` filter was removed from `_owned_trips` in `app/trips/repository.py` and reverted afterwards. `make test-authz ARGS='-q -p no:cacheprovider -k ownership'` printed `7 failed, 9 passed, 9 deselected in 7.47s`: the matrix entries API-07, API-08, API-10, API-14, API-15 and API-22, plus the missing-trip comparison.

## Commands run

All commands were run on this branch with `make db-up` first and `make db-down` at the end.

| Command | Result |
| --- | --- |
| `make test-authz ARGS='-q -p no:cacheprovider'` | `25 passed in 8.72s` |
| `make test-authz ARGS='-v -p no:cacheprovider -k ownership'` | `16 passed, 9 deselected in 8.46s` (the per-route lines are in the route matrix above) |
| `make lint` | `All checks passed!`; `All matched files use Prettier code style!` |
| `make typecheck` | `Success: no issues found in 85 source files`; `✓ Types generated successfully` |
| `make imports` | `Contracts: 4 kept, 0 broken.` |
| `make test` | unit `385 passed, 1 warning in 6.87s`; contract `35 passed, 1 warning in 0.77s`; api `223 passed, 1 warning in 43.93s`; authz `25 passed in 8.86s`; web `Test Files  10 passed (10)`, `Tests  54 passed (54)` |
| `make openapi-check` | `openapi-check: contracts/ and apps/web/lib/api/schema.d.ts are up to date` |

## Not run

- `make e2e`: no journey or screen changed.
- The pull-request CI run: see the pull request.

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| B requesting A's trip gets 404 and nothing about the trip (FR-005 AC1, TC-063, TC-345) | verified | The API-10, API-14, API-15 and API-22 matrix entries, plus `test_tc_063_a_foreign_trip_answers_like_a_missing_one`. Table level (TC-345): `test_rls.py` is unchanged and passes |
| Every read and write of A's child resources by B is refused (FR-005 AC2, TC-064, TC-346) | verified for the implemented routes | API-23 (generation) and API-22 (a generation under A's trip) answer 404. The rows of A's trip, including all `itinerary_*` rows, are unchanged after every call. Item and version routes are 501 stubs today (IMD-37) |
| Every implemented owned endpoint is exercised in CI; a new unlisted route fails the suite (FR-005 AC3, TC-065) | verified locally; CI pending | `test_tc_065_*` and the temporary-route check above; the CI `api` job runs `make test-authz` |
| US-013, NFR-012 | verified for the implemented routes | As above |

## Blockers

None. Every implemented owned route returns 404 `NOT_FOUND` to user B and leaves A's data unchanged.

## Proposed decisions

None.

## Open issues

- When IMP-211, IMP-305/IMP-601, IMP-308, IMP-405, IMP-408, IMP-410, IMP-411, IMP-504, IMP-505, IMP-602, IMP-605, IMP-607, IMP-609 and IMP-610 build their routes, each must add a matrix entry in the same pull request, or the TC-065 test fails. The guide `docs/guides/authz-suite.md` lists the steps. Routes with `item_id` or `version_id` will need a new field on `Owned` and in the fixture.
- Stub detection reads the handler source. A built handler that still raises `EndpointNotImplemented` in a branch is counted as built, which is the safe direction.
