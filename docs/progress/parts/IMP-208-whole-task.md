# IMP-208 · whole-task part

- Run id: RUN-023
- Owner: Nidhi (Nidhi9864)
- Status: PR_OPEN
- Base commit: bbaa573
- Branch: feat/IMP-208-whole-task
- Reviewer: Manya (manyarana)
- Traces to: US-036; FR-043; NFR-013; TC-013, TC-037, TC-042, TC-043, TC-164, TC-165, TC-166; IMD-27, IMD-72, IMD-80, IMD-91, IMD-92
- Card steps built: 1 to 4

## Changed files

- `apps/api/app/ai/factory.py` (created; steps 1 to 3):
  - **`get_provider(settings=None) -> ModelProvider`:** cached for the process (`functools.cache` on the provider name, `APP_ENV`, the scenario and the model id); `reset_provider_cache()` is for tests. Each adapter is imported inside its own branch:
    - MOCK gives `MockProvider(MOCK_PROVIDER_SCENARIO, app_env=APP_ENV)`.
    - GEMINI gives `GeminiPendingProvider` until IMP-301 (see the reconciliation below).
    - FINETUNED_MODEL builds the IMD-92 stub, whose `ProviderBadRequest("FINETUNED_MODEL not enabled in Stage 1")` is re-raised as `ProviderBadRequest("AI_PROVIDER: the FINETUNED_MODEL adapter is not enabled before Stage 2")`, with the stub's error kept as the cause. The wording matches `core/config.py`.
    - Any other value (only reachable when Settings validation is bypassed) raises `ProviderConfigError("AI_PROVIDER must be one of GEMINI, MOCK, FINETUNED_MODEL")`, without echoing the value.
  - **`startup_provider(settings)`:** the §8.4 start-up step.
    - `registry.load("itinerary_generate", PROMPT_TEMPLATE_VERSION)`. A missing template raises `ConfigError(["PROMPT_TEMPLATE_VERSION: no itinerary_generate template for version 'v999' in app/ai/prompts/templates"])`.
    - It then calls `get_provider`; a `ProviderConfigError` becomes `ConfigError`.
    - It calls `health_check()` once and logs provider, model, adapter version and health. There are no secrets in that log, and a provider that is not `ok` logs a warning without stopping the app.
  - **`get_model_provider(request)` and `ModelProviderDep`:** the FastAPI dependency for generation code (IMP-210). It returns `app.state.model_provider` from start-up, or builds it when the lifespan did not run (tests with a plain `TestClient`). It can be overridden with `app.dependency_overrides`.
  - **Keys:** read only through `Settings`. The module imports no `os`, `pathlib`, `dotenv` or `json` and opens no file.
- `apps/api/app/main.py` (modified, Manal's file; step 2): `create_app` now passes a `lifespan` that runs `startup_provider(settings)` and stores the result in `app.state.model_provider`. A `ConfigError` is logged as `configuration error: …` and stops start-up.
  - The existing `check_settings` call still runs first in `create_app`, unchanged.
  - `/health` (API-01, IMD-80), the error envelope and the routers are unchanged.
  - **Reason:** card step 2 (resolve the provider at start-up and expose it through a dependency) and §8.4 (the template check).
- `apps/api/tests/unit/ai/test_factory.py` (created, 20 tests; step 4): each `AI_PROVIDER` value and its message; caching; GEMINI in staging and production compared with local and test; the GEMINI config error on generate; an unknown value at load and in the factory; FINETUNED_MODEL at `create_app`, in the factory and at start-up; key source and no key in logs (TC-013); `.env` git-ignored; missing prompt template; MOCK start-up with an unchanged `/health`; the existing checks still first; the dependency, with start-up and override and without start-up; only the factory imports concrete adapters (AST scan of `app/`).

`core/config.py` is unchanged. It already stops start-up for an unknown `AI_PROVIDER` (Literal, `ConfigError` without the value), for FINETUNED_MODEL ("not enabled before Stage 2"), for MOCK in production, and for GEMINI with an empty or placeholder key or model id in staging and production. The factory relies on those checks and does not repeat them.

## Reconciling card step 1 with the objective

Card step 1 says "until IMP-301 the GEMINI branch raises ProviderConfigError 'Gemini adapter not implemented yet'". The objective says that in local and test, GEMINI without a key "starts with provider status down and generations end failed with config_error". If `get_provider` raised at start-up, the second could not hold. Built:

- **Staging and production, no key:** start-up stops in `create_app` through the existing `check_settings` (TC-043). The message names `GEMINI_API_KEY`, never a value.
- **Every environment that gets past `check_settings`:** the GEMINI branch returns `GeminiPendingProvider`.
  - Its `health_check` is `down` ("Gemini adapter not implemented yet"), and start-up logs that warning.
  - `generate_itinerary` raises `ProviderConfigError("Gemini adapter not implemented yet")`, a `config_error`, so IMP-210's pipeline ends the generation `failed` and offers `rule_based`.
  - The step-1 error and message are kept, raised on use rather than at construction, in line with §8.4 ("A `down` provider never stops the app").
- **IMP-301** replaces the stand-in with `from app.ai.providers.gemini import GeminiProvider` inside the GEMINI branch only.

## Commands and results

| Command | Result line |
| --- | --- |
| `make test-unit ARGS='-k factory'` | `20 passed, 330 deselected, 1 warning in 0.71s` |
| `make test-contract` | `28 passed in 0.07s` |
| `make lint` | `All matched files use Prettier code style!` (ruff `All checks passed!`) |
| `make typecheck` | `Success: no issues found in 65 source files` |
| `make imports` | `Contracts: 3 kept, 0 broken.` |
| `make db-up` | `Container group12-db-1 Healthy` |
| `make test` | unit `350 passed, 1 warning in 6.28s`; contract `28 passed in 0.08s`; api `183 passed, 1 warning in 39.21s`; authz `9 passed in 0.86s`; web `Tests  48 passed (48)` |
| `make check` | exit 0 (api `183 passed, 1 warning in 39.39s`; `openapi-check: not yet implemented (IMP-214)`) |
| `APP_ENV=local AI_PROVIDER=MOCK DATABASE_URL=<local test URL> make api` (background), `curl localhost:8000/health`, then stopped | `INFO:     Application startup complete.`; `{"status":"ok","version":"dev","environment":"local","provider":"MOCK"}` |
| `make db-down` | `Network group12_default Removed` |

Mutation checks, both reverted:
- With the `registry.load` start-up check replaced by `pass`, `make test-unit ARGS='-k factory'` failed.
- With the GEMINI stand-in reporting `ok`, the same command failed.

Not run: `make e2e` (no journey in this card). `make openapi-check` is still the IMP-214 placeholder.

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| Staging and production: GEMINI without a key stops start-up with a clear error; local and test: starts with provider down (FR-043 AC1, TC-043, TC-164) | verified | `test_tc_043_gemini_without_a_key_stops_start_up_in_staging_and_production[staging/production]`; `test_tc_164_gemini_without_a_key_starts_with_provider_down_in_local_and_test[local/test]` (lifespan runs, `/health` 200, health `down` logged); `test_gemini_generations_end_with_a_config_error_until_the_adapter_exists` |
| An unknown value stops start-up with a clear error (FR-043 AC2, TC-042, TC-165) | verified | `test_tc_042_an_unknown_ai_provider_stops_start_up_naming_the_variable`; `test_tc_165_the_factory_refuses_an_unknown_value_without_echoing_it` |
| FINETUNED_MODEL is refused with "not enabled before Stage 2" (FR-043 AC3, TC-037, TC-166) | verified | `test_tc_037_finetuned_model_stops_start_up_not_enabled_before_stage_2`; `test_tc_166_the_factory_refuses_finetuned_model_with_the_imd_92_error` |
| The key is read from the environment only (TC-013) | verified | `test_tc_013_the_factory_reads_nothing_but_settings`; `test_tc_013_the_key_comes_from_the_environment_and_is_never_logged`; `test_the_local_env_file_is_not_tracked` |
| §8.4: a PROMPT_TEMPLATE_VERSION with no template stops start-up with a clear error | verified | `test_a_missing_prompt_template_version_stops_start_up` (message names `PROMPT_TEMPLATE_VERSION` and `'v999'`; logged as a configuration error) |
| Only app.ai.factory imports concrete adapters | verified | `test_only_the_factory_imports_concrete_adapters`; `make imports` (`Contracts: 3 kept, 0 broken.`) |

## Blockers

None.

## Proposed decisions

- **PD-IMP-208-1:** GEMINI before IMP-301 is a stand-in provider (health `down`, `ProviderConfigError("Gemini adapter not implemented yet")` on generate) in every environment that passes `check_settings`, rather than an error at construction. This follows the reconciliation above and §8.4.
  - With a key set in staging, start-up succeeds and generations end `failed` with `config_error` until IMP-301.
- **PD-IMP-208-2: FINETUNED_MODEL message.** The factory uses the card's wording ("AI_PROVIDER: the FINETUNED_MODEL adapter is not enabled before Stage 2", the same as `core/config.py`) on a `ProviderBadRequest`, with the IMD-92 stub message kept as the chained cause.
- **PD-IMP-208-3: where the template check runs.** It runs in the lifespan, as the card says, not in `create_app`. Under uvicorn a lifespan `ConfigError` is logged as `configuration error: …`, and uvicorn reports "Application startup failed" and exits non-zero. A plain `TestClient(app)` without `with` does not run the lifespan, so `get_model_provider` builds the provider on first use.

## Open issues

- §8.4 also lists "metadata `supports_structured_output` is false → exit". Every current adapter reports true; IMP-301 should add that check to `startup_provider` when the real Gemini metadata exists.
- The provider's health is logged at start-up but not exposed: API-01 keeps its four fields (IMD-80). `/health/ready` (breaker state, §8.4) belongs to a later card.
