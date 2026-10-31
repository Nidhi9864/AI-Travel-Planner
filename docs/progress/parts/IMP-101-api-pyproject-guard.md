# IMP-101 · api-pyproject-guard part

- Run id: RUN-002
- Owner: Het (het-lathiya)
- Status: PR_OPEN
- Base commit: 61a3e64
- Branch: feat/IMP-101-api-pyproject-guard
- Reviewer: Kirtan (kirtan-S111)
- Traces to: US-001; NFR-031, NFR-032, NFR-033
- Card steps built: 3, 6 and 9. Steps 1, 2, 4, 5, 7, 8 and 10 were Kirtan's repo-tree-makefile part.

## Changed files

- `apps/api/pyproject.toml` (created): Python 3.12 (`>=3.12,<3.13`); the runtime dependencies and dev extra of step 3, nothing else; setuptools build backend (needed by `pip install -e`, not a runtime dependency); ruff, mypy (strict on `app/`) and pytest configuration with the markers `live` and `slow`.
- `apps/api/.importlinter` (created): the §4.4 Layers contract and the §4.4 Vendor isolation row (two import-linter sections, one per half of the row).
- `apps/api/tests/conftest.py` (created): the provider socket guard.
- `apps/api/tests/unit/test_socket_guard.py` (created): the test for card criterion 6.
- This record (created).

The Makefile was not changed: its API lines ran as soon as `pyproject.toml` and `.importlinter` existed.

## What the files contain

**pyproject.toml.** Runtime: fastapi, uvicorn[standard], pydantic>=2, pydantic-settings, sqlalchemy>=2, psycopg[binary] 3, alembic, httpx, PyJWT[crypto], google-genai. Dev: pytest, pytest-asyncio, respx, ruff, mypy, import-linter, pip-audit. Libraries have a lower bound at the version installed today and a cap at the next major version (next minor for 0.x packages). ruff, mypy and import-linter are pinned exactly so that local runs and CI report the same findings. ruff: target py312, rule sets E, W, F, I, B, UP, N, S, C4, SIM, PT, ASYNC, RUF; `S101` (assert) allowed under `tests/`. mypy: `strict = true`, `files = ["app"]`, `warn_unreachable`, pydantic plugin. pytest: `testpaths = ["tests"]`, `--strict-markers --strict-config -ra`, markers `live` and `slow`, pytest-asyncio strict mode with function loop scope.

**.importlinter.** Root package `app`, `include_external_packages = True`.

| Contract | Rule | import-linter options used so it passes on the empty skeleton and binds later |
| --- | --- | --- |
| Layers (`layers`) | In every module: `router` > `service` > `domain` : `repository` > `client` : `providers`. A lower layer never imports a higher one: domain and repository never import service or router; service never imports router; clients and adapters import none of them. | Container `app.*` (every module, including the extension modules once created). Every layer is optional (in parentheses), because a module creates only the files it needs (§4.3); a layer that exists is checked. `:` makes domain/repository and client/providers non-independent siblings, as §4.4 does not forbid imports between them. |
| Vendor isolation, SDK (`forbidden`) | `google` (and so `google.genai`) is imported by no module of `app` except `app.ai.providers.gemini`. | import-linter models an external package only by its top-level name and rejects `google.genai` as a forbidden module ("subpackages of external packages are not valid"), so the rule names the `google` namespace. The allowed import is `ignore_imports = app.ai.providers.gemini -> google` with `unmatched_ignore_imports_alerting = none`, because gemini.py does not exist yet (IMP-207). |
| Vendor isolation, adapters (`protected`) | `app.ai.providers.gemini`, `.mock` and `.finetuned` are imported only by `app.ai.factory`. | A protected module named plainly must already exist, so each adapter is written as `app.*.providers.<name>`, which only `app.ai.providers.<name>` matches. `as_packages = False`, because otherwise import-linter looks up descendants of the not-yet-existing `app.ai.factory`; factory and the adapters are single modules (§4.1). |

Nothing was dropped or weakened. The SDK rule is stricter than the §4.4 wording (it covers every `google.*` package). Both contracts were checked against a scratch copy of `app/` (commands below): a graph with only allowed imports passed all three, and a graph with planted violations broke all three.

**Socket guard (tests/conftest.py).** An autouse fixture `provider_socket_guard` wraps `socket.getaddrinfo` (the resolution step used by `socket.create_connection`, httpx/httpcore and asyncio) and `socket.socket.connect` / `connect_ex` (a host name passed straight to connect). For a test that is not marked `live`, any host that matches `PROVIDER_HOSTS` raises `ProviderNetworkBlockedError` with the message `socket guard: <test id> tried to reach provider host '<host>' (matches '<pattern>'). Use the MOCK provider, recorded responses or respx, or mark the test 'live' (run only by make live-smoke).` The error is a `RuntimeError`, not an `OSError`, so a client's network-error fallback cannot swallow it. Matching ignores case and a trailing dot; a pattern `*.example.org` matches the domain and all its subdomains, ready for the extension hosts of §13.1. The fixture yields a small handle (active flag, host list, error class, matcher) so tests inspect the guard without importing conftest.

Hosts in `PROVIDER_HOSTS` (the one list later cards add to):

- `generativelanguage.googleapis.com` (Gemini API, used by google-genai with an API key)
- `api.openrouteservice.org` (OpenRouteService)

**test_socket_guard.py (20 tests).** Unmarked: each provider host is refused through `getaddrinfo`, `create_connection`, `socket.connect`, `socket.connect_ex`, sync httpx and async httpx, with the host named in the error; upper case and trailing-dot variants are refused; `localhost` still resolves; a respx-mocked call to the ORS host works; the wildcard matcher. Marked `live`: the guard is inactive and `socket.create_connection` to each provider host succeeds. No test touches the network: `_socket.getaddrinfo` is stubbed to answer with a loopback listener, and the blocked tests assert that the stub was never called. `make test-unit` runs the live-marked case offline; `make live-smoke` selects `tests/contract -m live` only, so it never picks these tests up.

## Commands run

| Command | Result line (quoted exactly) |
| --- | --- |
| `rm -rf apps/api/.venv apps/web/node_modules`, then `make setup && make lint && make typecheck && make imports` (TC-335) | `Contracts: 3 kept, 0 broken.`; exit 0; both directories present afterwards. Inside the run: `All checks passed!`, `23 files already formatted` (ruff), `All matched files use Prettier code style!`, `Success: no issues found in 13 source files` (mypy) |
| `make test-unit` | `============================== 20 passed in 0.19s ==============================` |
| `make test` | `No test files found, exiting with code 0` (vitest); exit 0. API suites: `20 passed in 0.16s` (unit), `pytest: no tests collected (exit 5 treated as success)` (contract, api, authz) |
| `make check` | `No test files found, exiting with code 0`; exit 0. Inside: `All checks passed!`, `20 passed in 0.22s`, `Contracts: 3 kept, 0 broken.` |
| `for t in <26 targets of §4.7>; do make -n $t >/dev/null 2>&1 \|\| echo "FAIL $t"; done` | no `FAIL` line printed (26 targets) |
| `lint-imports --config .importlinter` on a scratch copy of `app/` with allowed imports only (gemini → google, factory → gemini and mock, router → service → domain, repository, generation.service → ai.factory and providers.base, routing.service → client) | `Contracts: 3 kept, 0 broken.` |
| The same on a scratch copy with planted violations (service → router, repository → service, domain → service, client → service, `app.weather.service` → router, `itinerary.domain` → google.genai, `generation.service` → providers.mock, `ai.prompts` → providers.finetuned) | `Contracts: 0 kept, 3 broken.`; every planted import listed, including the not-yet-existing extension module `app.weather` |
| `pytest tests/unit -k "not socket.connect"` on a scratch copy whose guard is forced off (mutation check) | `11 failed, 5 passed, 4 deselected in 2.61s`; the 11 blocked-host tests fail when the guard is off |

Installed versions (pip, 2026-10-31): fastapi 0.162.0, uvicorn 0.54.0, pydantic 2.14.2, pydantic-settings 2.16.2, SQLAlchemy 2.1.6, psycopg 3.3.6 (psycopg-binary 3.3.6), alembic 1.20.1, httpx 0.28.1, PyJWT 2.15.1, cryptography 50.0.2, google-genai 2.34.0, pytest 9.2.0, pytest-asyncio 1.4.1, respx 0.23.1, ruff 0.17.3, mypy 2.4.1, import-linter 2.15 (grimp 3.18), pip-audit 2.10.1.

## Not run

| Command | Reason |
| --- | --- |
| `make live-smoke` | Needs a real provider key and is never run in a part or PR CI (CLAUDE.md §8); `tests/contract` holds no live test yet |
| `make stack-up`, `make stack-down`, `make db-up`, `make db-down` | `not yet implemented (IMP-105)` |
| `make db-migrate`, `make db-reset` | `not yet implemented (IMP-106)` |
| `make seed` | `not yet implemented (IMP-107)` |
| `make api` | `not yet implemented (IMP-103)` |
| `make e2e` | `not yet implemented (IMP-216)` |
| `make openapi` / `make openapi-check` | `not yet implemented (IMP-110, IMP-214)` / `not yet implemented (IMP-214)` |
| `make eval` | `not yet implemented (IMP-413)` |
| `make smoke` | `not yet implemented (IMP-112)` |
| `pip-audit` | Installed by this part; the audit job and its threshold belong to IMP-102 |

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| Card 1: `make setup` exits 0 on a clean clone and creates apps/api/.venv and apps/web/node_modules | verified | TC-335 run after deleting both directories; exit 0; both present afterwards |
| Card 2: `make lint`, `make typecheck`, `make imports` exit 0, running ruff, mypy and lint-imports | verified | TC-335 output shows ruff check and format, mypy strict and lint-imports with 3 contracts kept; no pending message printed |
| Card 3 (re-run): every §4.7 target exists | verified | `make -n` loop over the 26 targets printed no `FAIL` line |
| Card 6: a test that opens a connection to a provider host fails unless it is marked `live` | verified | `tests/unit/test_socket_guard.py`, 20 passed under `make test-unit`; mutation check shows the tests fail without the guard |
| NFR-031: vendor SDK and adapter imports isolated | verified (for the skeleton) | Contracts kept on the skeleton, and broken by planted violations in a scratch copy |

## Blockers

None.

## Proposed decisions

- PD-D (SDK contract scope): import-linter can forbid an external package only by its top-level name, so the §4.4 rule "google.genai only in app.ai.providers.gemini" is enforced as "no `google.*` import outside app.ai.providers.gemini". No current or planned module needs another `google` package; if one ever does, the contract needs an `ignore_imports` line for it.
- PD-E (ruff line limits): the formatter wraps at 100 characters and E501 flags only lines over 120 (docstrings and comments the formatter cannot wrap). The existing docstring of `app/generation/__init__.py` is 101 characters; it was left untouched.
- PD-F (tool pins): ruff, mypy and import-linter are pinned exactly; libraries use lower bounds with a major-version cap. There is no Python lock file, because adding one (pip-tools, uv) is a new tool and needs a decision.

## Open issues

- §4.7 says `live` tests are "skipped otherwise" (without a key). This part adds the marker and the guard only; the skip-without-key rule needs `GEMINI_API_KEY` from settings and comes with the first real live test (IMP-207). The marker description does not claim the skip.
- `docs/decisions/versions.md` (Kirtan's file) says Python package versions are recorded when this part lands; the versions are listed above for whoever updates that file.
- A new adapter under `app/ai/providers/` must be added to the `vendor-adapters` contract by the card that creates it; a new provider host must be added to `PROVIDER_HOSTS` by its card (§13.1 names `api.open-meteo.com`, `*.wikipedia.org`, `*.wikivoyage.org` for the extensions).
- Only the Gemini API host is guarded. A Vertex AI endpoint (`*-aiplatform.googleapis.com`) is not used by the spec (the key is `GEMINI_API_KEY`); add it if that ever changes.
- The PR is opened from the operator's GitHub account (`het-lathiya`), which is also the part owner's account; the reviewer is Kirtan.
