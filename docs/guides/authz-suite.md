# The two-user authorization suite

The suite checks that no signed-in traveller can read or change another traveller's trip or any resource under it (US-013, FR-005, NFR-012; IMP-215). It runs in CI as part of the `api` job, through `make test-authz`.

## What it checks

`apps/api/tests/authz/test_ownership.py` builds user A's data through the API with the MOCK provider: a trip, its preferences with one must-visit place, a completed generation and the saved itinerary. Then user B calls every route in the matrix with A's identifiers:

- A **foreign** route (its path names A's trip or a resource under it) must answer `404 NOT_FOUND`, the same answer as for an ID that does not exist (§6.2, CLAUDE.md §4 rule 4).
- A **scoped** route (no resource in the path, such as `GET /api/v1/trips`) must answer B with B's own data only.
- No response to B may contain A's user ID, email, trip ID, trip title or generation ID.
- After every call, A's trip, preferences and generation (read by A through the API) and every database row of A's trip (`trip_preferences`, `trip_places`, `budget_settings`, `ai_generations` and the `itinerary_*` tables) must be unchanged.

A control test sends the same request as A and expects neither 404 nor 422. This proves that B's 404 comes from the ownership check, not from a malformed request.

## The route matrix

`apps/api/tests/authz/route_matrix.py` holds `MATRIX`, one `RouteCase` per implemented owned route. The test `test_tc_065_every_implemented_owned_route_is_in_the_matrix` walks the app's routes and fails when an `/api/v1` route is missing from the matrix, unless the route is:

- reference data (`REFERENCE`: API-06, API-16, API-17, §6.2), or
- a declared stub whose handler is only `raise EndpointNotImplemented()`, which answers 501 (IMD-37).

The same test also fails if a matrix entry names a route that does not exist or is still a stub.

## Adding a route

When your card turns a 501 stub into a real handler, or adds a new owned route, the suite fails until you add the route to the matrix. In the same pull request:

1. Add a `RouteCase` to `MATRIX` with the API ID, the method, and the path exactly as FastAPI declares it (for example `/api/v1/itinerary/items/{item_id}`).
2. Set `access="foreign"` if the path names a resource; otherwise use `"scoped"`.
3. If the route takes a body, add a function that returns a valid body built from `Owned`; use `params` for query parameters. The body must be valid for A, or the control test fails.
4. If the path uses an identifier the suite does not have yet (for example `item_id` or `version_id`), add the field to `Owned`, fill it in the `owned` fixture from A's data, and pass it in `RouteCase.url`.
5. If the route writes to a table that is not listed yet, add the table to `TRIP_TABLES` in `test_ownership.py`, so a change by B is detected.
6. Run `make test-authz`.

If a route answers B with anything other than 404, do not weaken the test. Fix the route in the owning module, or mark that case `xfail` in the test's parametrization (`pytest.param(case, marks=pytest.mark.xfail(reason=...))`) with the observed status and a reason, and report it as a blocker on the owning card.

## Running it

```sh
make db-up
make test-authz                       # the whole authorization suite
make test-authz ARGS='-v -k ownership' # one result line per route
```
