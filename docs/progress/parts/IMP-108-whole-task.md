# IMP-108 · whole-task part

- Run id: RUN-010
- Owner: Het (het-lathiya)
- Status: PR_OPEN
- Base commit: 7c9f5f4
- Branch: feat/IMP-108-whole-task
- Reviewer: Manal (manalPatel2557)
- Traces to: US-012; FR-003; NFR-012, NFR-013; TC-057, TC-058, TC-059, TC-344, TC-347, TC-348; IMD-04, IMD-14, IMD-45
- Card steps built: 1 to 7

## Changed files

- `apps/api/app/auth/tokens.py` (created, step 1): `TokenVerifier.verify(token) -> TokenClaims(user_id, email)`.
  - With `SUPABASE_JWKS_URL` set, it uses `jwt.PyJWKClient`, one per URL for the process: keys cached, key set cached 10 minutes, 5 s fetch timeout. Accepted algorithms are ES256, RS256 and EdDSA; the blocking fetch runs off the event loop.
  - Otherwise it uses HS256 with `SUPABASE_JWT_SECRET`.
  - Required claims are `exp`, `sub` and `aud`; the audience must be `authenticated` and `sub` must be a UUID.
  - Every failure raises the same `Unauthenticated` with the default message, so the reason is never revealed. Only the failure class is logged, never the token or a claim.
  - A JWKS key set that cannot be fetched gives `ServiceUnavailable` (IMD-04), and so does a missing secret without a JWKS URL (see PD-IMP-108-2).
- `apps/api/app/auth/deps.py` (created, step 2):
  - `verified_claims` reads `Authorization: Bearer` (`HTTPBearer(auto_error=False)`, so a missing header gets our 401 envelope).
  - `db_session` gives one `transaction()` per request; tests override it.
  - `current_user` resolves the token first, so no database session opens for an invalid token. It then calls `service.get_or_create_profile` and returns the claims.
  - `CurrentUser` and `DbSession` are the `Annotated` aliases handlers use.
- `apps/api/app/auth/repository.py` (created): `insert_if_absent` runs `insert … on conflict do nothing` inside a savepoint and returns False when `auth.users` has no such user (foreign-key violation). `get` reads the row. This module is the only writer of `profiles` (MOD-B02, §5.2).
- `apps/api/app/auth/service.py` (created): `get_or_create_profile`, where a token for an account missing from `auth.users` gives 401, and `get_profile`.
- `apps/api/app/auth/schemas.py` (created): `Profile` per §6.5 (`id`, `email` from the token, `display_name`, `home_country`, `preferred_currency`, `default_preferences`, `ai_notice_ack_at`). Every field maps to a `profiles` column of migration 0003 except `email`, which §6.5 says comes from the token. No contract conflict.
- `apps/api/app/auth/router.py` (created, step 6): API-03 `GET /api/v1/me` returns the caller's `Profile`.
- `apps/api/app/main.py` (modified, Manal's file, three lines and a comment): the `/api/v1` router is created with `dependencies=[Depends(current_user)]` and includes the auth router. **Reason:** card step 3, so every route a later card mounts under `/api/v1` is protected by default. `/health` and the docs stay outside it. Nothing in `app/core/` changed.
- `apps/api/tests/fixtures/auth.py` (created, step 4):
  - `make_token(user_id, expired=, wrong_aud=, secret=, email=, omit=, algorithm=)` mints HS256 tokens.
  - `TEST_JWT_SECRET` is derived at import from a fixed test phrase, so no secret-like literal is in the repository and no real key is used.
  - `auth_test_settings()`, `bearer()` and `client_for()` are helpers.
  - The fixtures are `api_app` and `api_client` (the real app, with `db_session` overridden to the rolled-back test session) and `auth_user` (inserts the `auth.users` row).
- `apps/api/tests/conftest.py` (modified, Het's own file): one import line registers the auth fixtures. The socket guard is unchanged.
- `apps/api/tests/unit/auth/test_tokens.py` (created; TC-057, TC-347; no database, no network):
  - a valid token gives `sub` and `email`;
  - 11 bad tokens give the same `Unauthenticated` message: expired, tampered signature, another secret, wrong audience, no `aud`, no `exp`, no `sub`, `sub` not a UUID, `alg: none`, garbage, empty;
  - no secret gives 503;
  - the JWKS path with a locally generated RSA key and a fake key source: a valid RS256 token; an HS256 token or wrong audience rejected; an unknown key 401; an unreachable key set 503; `verifier_for` picks JWKS when the URL is set;
  - six header cases each return the 401 envelope without reaching the database.
- `apps/api/tests/authz/test_route_inventory.py` (created; TC-344, TC-059, TC-058, TC-348):
  - It walks every effective route with `fastapi.routing.iter_route_contexts`; FastAPI 0.162 keeps included routers unflattened in `app.routes`.
  - Every route outside the public allow-list must return 401 `UNAUTHENTICATED` with no token, an expired one, a wrong-audience one and a tampered one, without reaching the database.
  - Public routes answer without a token.
  - The two FastAPI documentation companions are checked separately (PD-IMP-108-1) and are absent in production.
  - TC-348 (static): every request body model of the app forbids extra fields and declares no `user_id`.
  - TC-058: a probe route behind the same router-level `CurrentUser` rejects `{"title", "user_id": <other>}` with 422 `VALIDATION_ERROR` and `details` field `user_id`, and its handler sees the token's user (TC-057).
- `apps/api/tests/api/test_me.py` (created; TC-057, IMD-14):
  - the first call creates exactly one `profiles` row, and the second creates none;
  - the response has exactly the Profile fields, with `id` equal to the token's `sub` and `email` from the token;
  - two users each get their own profile;
  - no token gives 401 and creates nothing;
  - a valid token for an account missing from `auth.users` gives 401 and creates nothing.
- This record (created).

## Checks that the tests can fail (scratch copy outside the repository)

`apps/api` was copied to a scratch folder, and the copy was imported via `PYTHONPATH`; `app.main.__file__` pointed into the copy. The repository was not changed.

| Planted change | Result |
| --- | --- |
| `@app.get("/api/v1/planted-unprotected")` added outside the protected router | `pytest tests/authz -k inventory`: `4 failed, 4 passed`, each failure `GET /api/v1/planted-unprotected -> 200` (TC-344, acceptance 4) |
| A POST route under `/api/v1` whose body model `LooseIn` does not forbid extra fields | `pytest tests/authz -k "tc_348 or tc_344"`: `1 failed, 4 passed`, `/api/v1/planted-loose-body: LooseIn` (TC-348). TC-344 still passes, because the route is protected. |

## Commands run

| Command | Result line (quoted exactly) |
| --- | --- |
| `make db-up` | ` Container group12-db-1 Healthy ` |
| `make test-unit ARGS='-k tokens'` | `================= 25 passed, 74 deselected, 1 warning in 0.16s =================` |
| `TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/travel_test make test-authz ARGS='-k inventory'` | `======================= 8 passed, 1 deselected in 0.24s ========================` |
| `TEST_DATABASE_URL=… make test-api ARGS='-k me'` | `================= 39 passed, 10 deselected, 1 warning in 1.51s =================` (`-k me` also matches other test names; the 5 tests of `test_me.py` are among them) |
| `make lint` | `All checks passed!` (ruff) … `All matched files use Prettier code style!` |
| `make typecheck` | `Success: no issues found in 37 source files` … `✓ Types generated successfully` |
| `make imports` | `Contracts: 3 kept, 0 broken.` |
| `make test` | test-unit `======================== 99 passed, 1 warning in 4.76s ========================`, test-contract `no tests ran` (exit 5 treated as success), test-api `49 passed`, test-authz `9 passed`, test-web `      Tests  48 passed (48)`; last line `   Duration  3.61s (environment 58%, tests 17%, setup 13%, import 7%, transform 5%)` |
| `make check` | exit 0; last line `   Duration  3.66s (environment 59%, tests 18%, setup 12%, import 8%, transform 2%, worker 1%)` |
| `make db-down` | see the SYNC REPORT (run after this record was committed) |

## Not run

| Command | Reason |
| --- | --- |
| `make openapi-check` (as a real check) | Still a placeholder (`openapi-check: not yet implemented (IMP-214)`); the OpenAPI export arrives with IMP-214. API-03 appears in the app's OpenAPI with the `HTTPBearer` scheme. |
| Token verification against a real Supabase project | No hosted project in this run. The local stack issues HS256 tokens, which is the tested mode; JWKS is covered with a local RSA key and a fake key source (no network). |

## Acceptance criteria

| Criterion | Status (verified / not verified) | How |
| --- | --- | --- |
| A valid token reaches the handler with user_id equal to the token sub (FR-003 AC1, TC-057) | verified | `test_tc_057_a_valid_token_yields_the_sub_as_user_id`; probe handler in `test_tc_058_…` returns the token's user; `test_tc_057_me_returns_the_token_users_profile` |
| A body field user_id naming another user is rejected with 422 VALIDATION_ERROR (FR-003 AC2, TC-058, TC-348, IMD-45) | verified | `test_tc_058_a_body_naming_another_user_is_rejected` (422, `details` field `user_id`); `test_tc_348_no_request_body_can_name_a_user` over every route; fails for a planted loose body model |
| No token, or an expired, tampered or wrong-audience token, returns 401 UNAUTHENTICATED in the envelope (FR-003 AC3, TC-059, TC-347) | verified | 11 token cases in `test_tc_347_…`; 6 header cases and the 4 inventory cases return the envelope with code `UNAUTHENTICATED` and one message |
| The route-inventory test fails if any non-public route is reachable without a token (TC-344) | verified | Scratch copy with an unprotected route: `4 failed`, `GET /api/v1/planted-unprotected -> 200` |
| A first authenticated call creates exactly one profiles row for the user | verified | `test_me_creates_exactly_one_profile_on_the_first_call` (0 → 1 → 1) |
| GET /api/v1/me returns the caller's profile, creating it on the first call; without a token it returns 401 (IMD-14) | verified | `test_me.py` (5 tests) |

## Blockers

None.

## Proposed decisions

- **PD-IMP-108-1 (documentation routes in the allow-list):** the card's public allow-list is `/health`, `/health/ready`, `/docs` and `/openapi.json`. Outside production, FastAPI (as configured by IMP-103) also serves `/redoc` and `/docs/oauth2-redirect`, two static documentation pages with no data. The test keeps the four-path allow-list as written and lists the two pages separately as `DOCS_COMPANION_PATHS`. It asserts they are FastAPI's built-in HTML routes and absent in production. Proposed: add them to the allow-list in §6.2 and the card, or turn ReDoc off in `create_app` (IMP-103's file).
- **PD-IMP-108-2 (verification not configured):** IMD-04 does not say what happens when neither `SUPABASE_JWKS_URL` nor `SUPABASE_JWT_SECRET` is set. Built: 503 `SERVICE_UNAVAILABLE` with an error log line, because the fault is the server's and not the caller's; a missing header is still 401. Proposed: record this in IMD-04, or add a start-up check in `app/core/config.py` (IMP-103's area, not changed here).

## Open issues

- **Web:** AuthGuard can now load `['me']` from API-03; IMP-109 left this open, and IMP-601 owns it.
- **`default_preferences`** is returned as a JSON object, `{}` for a new profile. Its keys and types are defined and validated with API-04 (IMP-601), together with the `PreferencesIn` vocabularies.
- **Profile check on every request:** each authenticated request runs one `insert … on conflict do nothing` on `profiles`, in a savepoint of the request's transaction. There is no in-process "seen" cache, so a profile removed by the account-deletion procedure (NFR-022) is recreated on the next call rather than hidden by a stale cache.
- **Access classes:** §3.4 rule 1 also names `tests/authz/test_ownership.py`, an access-class table over the OpenAPI routes with two-user tests. That belongs to the cards that add owned routes (IMP-215). The inventory here covers the token half for every route now.
- **Token for a deleted account:** a validly signed token whose user is missing from `auth.users` gets 401 (`test_a_valid_token_for_a_deleted_account_is_401`), never a 500 from the foreign key.
