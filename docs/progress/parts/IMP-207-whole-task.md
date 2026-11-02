# IMP-207 · whole-task part

- Run id: RUN-021
- Owner: Manya (manyarana)
- Status: PR_OPEN
- Base commit: c425fb1
- Branch: feat/IMP-207-whole-task
- Reviewer: Nidhi (Nidhi9864)
- Traces to: US-035; FR-042; NFR-043; TC-003, TC-033, TC-034, TC-035, TC-036, TC-162, TC-163; IMD-27, IMD-28, IMD-91
- Card steps built: 1 to 5

## Changed files

- `apps/api/app/ai/providers/mock.py` (created, steps 1 to 4): `MockProvider`, with name `MOCK`, model `mock-v1` and adapter version `mock-1`.
  - **Plan built from the gr-1 request only:**
    - Candidates are the `shortlist`, in its given order. They go over the requested days: `trip.num_days`, or the one day of a `day` scope.
    - Each day holds at most `limits.max_items_per_day` items (the pace item limit), and the first days fill first. Candidates that do not fit are left out.
    - The first item of a day starts at 09:00. Each next item starts at the previous start + `typical_duration_min` + 30 minutes (§8.4). `duration_min` is the candidate's typical duration, which is 15 to 480 in gr-1, so IMD-28 holds.
    - `slot_type` is `meal` for category `food`, otherwise `activity`.
    - The theme, the notes, `summary` and `assumptions` are io-1's model-text fields, and each starts with `SAMPLE`.
    - The same request gives an identical output.
    - An empty shortlist cannot give a valid io-1, so it raises `ProviderInvalidOutput("empty")`.
  - **Scenarios (IMD-27):**
    - `timeout`, `rate_limited` (`retry_after_s=1`), `quota` and `invalid_json` (`malformed_json`) raise their shared error at once.
    - `flawed` leaves out the first must-visit ID that is a candidate. It also moves the second item of day 1 to start halfway through the first item, giving exactly one overlap. Both flaws come from the request, and no Sampleton ID is in the code.
    - `unknown_place` replaces the last item's `place_id` with a deterministic UUID5 of the request ID that is not among the candidates.
    - `raise_error=<ProviderError>` takes precedence and covers the other error kinds.
  - **Settings:**
    - `scenario` and `app_env` come from the constructor, or default to `MOCK_PROVIDER_SCENARIO` and `APP_ENV` through `app.core.config.get_settings()`.
    - The scenario is honoured in local, test and staging, and treated as `ok` in production (the `scenario` property).
  - **Result and other operations:**
    - The result has `UsageMetadata()` with every count null, `latency_ms` measured with `perf_counter`, `finish_reason` `"stop"` and `provider_request_id` null.
    - `health_check` returns `ok`. `modify_itinerary` raises `ProviderBadRequest` (R2).
    - A `TYPE_CHECKING` conformance function makes `make typecheck` fail if the mock stops matching `ModelProvider`.
  - **Imports:** nothing from `trips/`, `generation/` or `places/`, and no httpx or `google.genai`. `.importlinter` already protects `app.*.providers.mock`, so only `app.ai.factory` (IMP-208) may import it.
- `apps/api/tests/contract/test_provider_contract.py` (modified, step 5):
  - Registers the `mock` adapter: `MockProvider("ok", app_env="test")`, and `raise_error=` for the failing build. The double stays registered.
  - Adds `test_tc_162_generate_itinerary_makes_no_network_call`, run for every adapter, which patches `socket.connect`, `connect_ex` and `getaddrinfo` to raise.
  - Adds `test_tc_163_mock_failure_scenarios_raise_the_shared_error` for the four failure scenarios.
  - The docstring now says the MOCK adapter is registered. No existing test was changed.
- `apps/api/tests/unit/ai/test_mock_provider.py` (created, 32 tests):
  - Determinism (TC-033).
  - io-1 model and committed `contracts/ai/io-1.schema.json` validity (TC-036), using a small in-test checker for the keywords that schema uses. jsonschema is not installed, and no dependency was added; a test shows the checker rejects an invalid output.
  - Candidate order and the timing rule, the pace item limit and day count, day scope, slot types and SAMPLE text, null usage, latency and finish reason, health and metadata.
  - Each failure scenario (TC-034), `raise_error` kinds, `flawed`, `unknown_place`.
  - The seven scenario values, an unknown value refused, scenarios honoured in local, test and staging and ignored in production, `ok` as the default.
  - No network with `socket.connect` patched to raise (TC-035), and no forbidden imports.

## Commands and results

| Command | Result line |
| --- | --- |
| `make test-unit ARGS='-k mock_provider'` | `32 passed, 283 deselected, 1 warning in 0.35s` |
| `make test-contract` | `28 passed in 0.11s` |
| `make openapi && git diff --exit-code contracts/ai` | `openapi: OpenAPI export and web types not yet implemented (IMP-214)`; no diff in `contracts/ai` (exit 0) |
| `make lint` | `All matched files use Prettier code style!` (ruff `All checks passed!`) |
| `make typecheck` | `Success: no issues found in 61 source files` |
| `make imports` | `Contracts: 3 kept, 0 broken.` |
| `make db-up` | `Container group12-db-1 Healthy` |
| `make test` | unit `315 passed, 1 warning in 5.00s`; contract `28 passed in 0.08s`; api `118 passed, 1 warning in 19.93s`; authz `9 passed in 0.71s`; web `Tests  48 passed (48)` |
| `make check` | exit 0 (unit `315 passed, 1 warning in 4.79s`; api `118 passed, 1 warning in 18.02s`; `openapi-check: not yet implemented (IMP-214)`) |
| `make db-down` | `Network group12_default Removed` |

Mutation checks (reverted): with the production rule removed, the scenario is always honoured and `make test-unit ARGS='-k mock_provider'` failed. With the `flawed` overlap moved out of range, the same command failed.

Not run: `make e2e` (this card adds no journey). `make openapi-check` is still the IMP-214 placeholder.

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| With AI_PROVIDER=MOCK no network call is made (FR-042 AC1, TC-035, TC-162) | verified | `test_tc_035_generate_runs_with_socket_connect_patched_to_raise` (ok, flawed, unknown_place, health); `test_tc_162_generate_itinerary_makes_no_network_call[mock]`; `test_the_mock_imports_no_http_client_vendor_sdk_or_planning_module` |
| Each failure scenario raises the matching shared error (FR-042 AC2, TC-034, TC-163) | verified | `test_tc_034_each_failure_scenario_raises_the_shared_error` (type and `failure_reason`); `test_tc_163_mock_failure_scenarios_raise_the_shared_error`; `test_failures_surface_as_the_shared_error_types[mock-*]` (raise_error, seven kinds) |
| Output is deterministic and passes the io-1 schema (TC-033, TC-036, TC-003) | verified | `test_tc_033_the_same_request_gives_an_identical_output`; `test_tc_036_the_output_passes_the_io_1_model_and_the_committed_schema`; `test_tc_158_generate_itinerary_returns_a_valid_io_1_result[mock]`; flawed and unknown_place outputs are also checked against the schema |
| MOCK_PROVIDER_SCENARIO accepts exactly the seven IMD-27 values, is honoured in local, test and staging and ignored in production | verified | `test_the_scenario_values_are_exactly_the_seven_of_imd_27`; `test_an_unknown_scenario_is_refused_by_the_settings`; `test_scenarios_are_honoured_in_local_test_and_staging[local/test/staging]`; `test_scenarios_are_ignored_in_production` |

## Blockers

None.

## Proposed decisions

- **PD-IMP-207-1: plan source and start time.**
  - The card (step 1) and the run's narrowing note build the plan from the shortlist candidates in order, limited by the pace item limit, from 09:00.
  - §8.4 says "builds io-1 from `day_hints` … items start at `limits.day_start`".
  - The card's rule is built. Proposal: align the §8.4 sentence with the card. In the SAMPLE request `day_start` is 09:00, so the two rules agree there.
- **PD-IMP-207-2: unknown scenario values.**
  - `MOCK_PROVIDER_SCENARIO` is already validated by `app.core.config` (`MockScenario` Literal; start-up fails with a `ConfigError` that names the variable, not the value). The mock relies on that and does not repeat the list.
  - A scenario passed straight to the constructor is checked against the same Literal and raises `ProviderConfigError` (IMD-91).
- **PD-IMP-207-3: "usage None".** The card says "usage None", but `ProviderResult.usage` is a required `UsageMetadata` (§8.3, IMP-110). The mock returns `UsageMetadata()` with every count null, which keeps the token columns NULL as the card intends.
- **PD-IMP-207-4: `flawed` and `unknown_place` on other requests.**
  - `flawed` applies only the flaws a request allows. With no shortlisted must-visit place, nothing is left out. When day 1 has a single item, there is no overlap.
  - `unknown_place` replaces the last item rather than adding one, so the pace item limit still holds.
- **PD-IMP-207-5: `raise_error` and production.** `raise_error` is honoured in every environment, because only tests use it. The production rule applies to `MOCK_PROVIDER_SCENARIO` and to the constructor's `scenario`.

## Open issues

- IMP-208 (factory) should build `MockProvider()` with no arguments, or pass `settings.mock_provider_scenario` and `settings.app_env` explicitly.
- Items whose start is at or before 23:59 may end after midnight when long candidates fill a busy day. The validator reports this as `DAY_TOO_LONG`; the mock does not fix times.
