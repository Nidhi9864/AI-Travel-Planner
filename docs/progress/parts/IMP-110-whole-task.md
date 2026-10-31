# IMP-110 · whole-task part

- Run id: RUN-009
- Owner: Nidhi (Nidhi9864)
- Status: PR_OPEN
- Base commit: 7c9f5f4 (rebased from 99c7510 after IMP-109 merged; the results below were taken on 99c7510, and `make check` and `make openapi` were repeated after the rebase)
- Branch: feat/IMP-110-whole-task
- Reviewer: Kirtan (kirtan-S111)
- Traces to: US-034; FR-040; NFR-031, NFR-043; TC-001, TC-002, TC-005, TC-156, TC-157, TC-158; IMD-06
- Card steps built: 1 to 6

## Changed files

- `apps/api/app/schemas/ai.py` (created, step 1):
  - **gr-1** `GenerationRequest` follows the §8.6 table field for field: `trip` (dates, `num_days` 1 to 14 and consistent with the dates, travellers 1 to 20 and 0 to 20, `group_needs`, budget or null, `contingency_pct` 0 to 50), `preferences`, `must_visit_place_ids` (at most 10, IMD-40), `shortlist[]`, `day_hints[]`, `limits`, `locked_items[]`, `scope` (`day_number` set exactly for `day`, mirroring the `ai_generations` CHECK), `repair_context` (with the `PlanFinding` shape of the §8.18 repair example), `prompt_template_id` and `prompt_version`. Amounts are two-decimal strings (IMD-05).
  - **io-1** `ItineraryOutput` follows the §8.7 table:
    - `days[]` has 1 to 14 entries, each with `day_number` 1 to 14, `theme` of at most 80 characters, and 1 to 12 `items[]`;
    - each item has `place_id`, `start_time` as 24-hour `HH:MM`, `duration_min` 15 to 480, `slot_type` (`activity`, `meal` or `rest`) and `note` of at most 200 characters;
    - `summary` is optional and at most 500 characters; `assumptions` is required, with 0 to 20 entries;
    - the field order is days, summary, assumptions;
    - there is no price, hour, travel-time or total field.
  - Every model forbids extra fields. `unknown_place_ids(request)` lists the IDs outside the request's shortlist, so step 8 can produce `UNKNOWN_PLACE` (§8.11); parsing itself does not reject them.
  - Vocabularies are `Literal`s copied from the CHECK lists of migrations 0002 to 0004 and IMD-40.
  - The provider result types of §8.3: `ProviderResult[T]`, `UsageMetadata` (four optional counts, never estimated), `HealthStatus` and `ModelMetadata`. `ModificationRequest` and `EditOperations` are empty R2 placeholders, so the interface is complete.
- `apps/api/app/ai/errors.py` (created, step 3):
  - `ProviderError` is the base (`internal`). Below it are `ProviderTimeout`, `ProviderRateLimited(retry_after_s)` and `ProviderUnavailable` (retryable), and `ProviderQuotaExhausted`, `ProviderInvalidOutput(kind)` and `ProviderConfigError` (not retryable).
  - `ProviderConfigError` has two subclasses, `ProviderAuthError` and `ProviderBadRequest` (§8.3). See PD-IMP-110-1.
  - `retryable` and `failure_reason` are class attributes, typed with `ProviderFailureReason`, the values of the migration 0004 CHECK that a provider error can produce.
  - `ALL_PROVIDER_ERRORS` lists every type.
  - A file-level `ruff: noqa: N818`, with its reason, keeps the §8.3 names, which have no `Error` suffix.
- `apps/api/app/ai/providers/__init__.py` (created) and `apps/api/app/ai/providers/base.py` (created, step 2): the `ModelProvider` `Protocol` (runtime-checkable) with `name`, `async generate_itinerary(GenerationRequest) -> ProviderResult[ItineraryOutput]`, `async modify_itinerary(ModificationRequest) -> ProviderResult[EditOperations]`, `async health_check() -> HealthStatus` and `get_model_metadata() -> ModelMetadata`.
  - `name` is declared as a read-only member. With a settable attribute typed `ProviderName`, mypy rejects an adapter whose `name` is a single literal, such as `Literal["FINETUNED_MODEL"]`; this was checked with a scratch file. Callers still read it as an attribute.
  - The interface types are re-exported, so code outside `app/ai/` needs only this module.
- `apps/api/app/ai/providers/finetuned.py` (created, step 4): `FineTunedProvider`, the Stage 2 stub. Its constructor and every operation raise `ProviderBadRequest("FINETUNED_MODEL not enabled in Stage 1")`, which is a `ProviderConfigError` (see PD-IMP-110-2). A `TYPE_CHECKING` block makes `make typecheck` fail if the stub stops matching the interface. Only `app.ai.factory` may import it (`.importlinter`, unchanged).
- `apps/api/app/schemas/ai_export.py` (created, step 5): `python -m app.schemas.ai_export --out <dir> [--check]` writes `gr-1.schema.json` and `io-1.schema.json` from the models. Each file starts with `$schema` (2020-12) and `$id` (`urn:ai-travel-planner:schema:<version>`) and keeps the generated key order. `--check` exits 1 for a missing or stale file. It sits under `app/schemas/` because §4.6 makes `app/schemas/ai.py` the source of these files.
- `Makefile` (modified, Kirtan's file, `openapi` target only): it now runs the AI schema export into `contracts/ai/`, then prints that the OpenAPI export and web types arrive with IMP-214. `openapi-check` is unchanged (IMP-214). **Reason:** card step 5 ("a schema export function used by `make openapi`"), and §4.7 makes `make openapi` export the AI JSON Schemas. No target was renamed or added.
- `contracts/ai/gr-1.schema.json`, `contracts/ai/io-1.schema.json` (created by `make openapi`, committed).
- `apps/api/tests/fixtures/ai.py` (created): SAMPLE gr-1 request data, the §8.7 io-1 example, and `DoubleProvider`, an in-test `ModelProvider` with no SDK and no network. It builds io-1 from the day hints or raises the error it was given, and stands in for MOCK until IMP-207.
- `apps/api/tests/unit/ai/test_schemas.py` (created, step 6; TC-156, TC-157):
  - The io-1 example is valid.
  - Extra fields fail at each level: `price`, `travel_minutes`, `opening_hours` and `total` on the output, a day or an item.
  - The io-1 schema declares exactly the 11 allowed property names.
  - A missing `place_id` fails; 15 days, 13 items and 0 items fail; the item, day and output limits hold.
  - Unknown IDs are reported against the shortlist.
  - gr-1 rules: extra fields, `num_days` that does not match the dates, money as a number, interest `stay`, notes over 500 characters, 11 must-visit places, scope pairing, schema version.
  - The committed JSON Schemas equal the models' output, and `--check` flags a stale file.
  - TC-156: an AST scan finds no `google` import in `app/` outside `app/ai/providers/gemini.py`.
  - TC-157: a stub generation service written against `ModelProvider` runs unchanged with the double, and sees a `ProviderTimeout` as the shared type.
  - The fine-tuned stub raises `ProviderConfigError` (and `ProviderBadRequest`) on construction and on every operation.
- `apps/api/tests/unit/ai/test_provider_errors.py` (created; TC-005): reads the `failure_reason` CHECK list from `apps/api/migrations/sql/0004_ai_and_plan.sql` and asserts it equals the 8 known values. It then checks that every error type's `failure_reason` is in that list, that `ALL_PROVIDER_ERRORS` holds every subclass, the retry flags and reasons of the §8.3 table, the shared configuration base, and the error details. (It is named `test_provider_errors.py` because `tests/unit/core/test_errors.py` already exists and the test folders have no `__init__.py`.)
- `apps/api/tests/contract/test_provider_contract.py` (created, step 6 skeleton; TC-001, TC-158): parameterised over `ADAPTERS`. Today that holds only `double`, with commented places for IMP-207 (`mock`), IMP-301 (`gemini_recorded`) and IMP-512 (the complete suite). It checks:
  - the interface: four operations with the interface's signatures and async-ness;
  - a valid io-1 `ProviderResult` with shortlisted IDs and non-negative or null usage;
  - the `HealthStatus` and `ModelMetadata` shapes;
  - `modify_itinerary` not enabled in the MVP;
  - seven failure types surfacing as the shared types with their reasons.
- This record (created).

`apps/api/migrations/sql/0004_ai_and_plan.sql`, `.importlinter`, `app/core/` and `tests/conftest.py` are unchanged.

## Checks that the tests can fail

Each change was undone afterwards; `git status` showed no tracked file changed.

| Change | Result |
| --- | --- |
| `ProviderTimeout.failure_reason = "timeout"` | `tests/unit/ai/test_provider_errors.py`: `2 failed, 19 passed` |
| Planted `from google import genai` in `app/itinerary/planted.py` (the IMP-102 TC-002 check) | `lint-imports`: `Vendor isolation: google (google.genai) only in app.ai.providers.gemini BROKEN`, `Contracts: 2 kept, 1 broken.`, `app.itinerary.planted -> google (l.1)`; TC-156 test: `1 failed` |
| `contracts/ai/io-1.schema.json` edited by hand (`maxItems` 12 → 13) | the schema-sync test: `1 failed, 1 passed` |

## Commands run

| Command | Result line (quoted exactly) |
| --- | --- |
| `make test-unit ARGS='-k ai'` | `================= 96 passed, 57 deselected, 1 warning in 0.73s =================` (`-k ai` also matches other tests by substring) |
| `make test-contract` | `============================== 11 passed in 0.07s ==============================` |
| `make openapi && git diff --exit-code contracts/ai` | `openapi: OpenAPI export and web types not yet implemented (IMP-214)`; `git diff` printed nothing, exit 0 |
| `python -m app.schemas.ai_export --out ../../contracts/ai --check` | exit 0 |
| `make lint` | `All checks passed!` (ruff) … `All matched files use Prettier code style!` |
| `make typecheck` | `Success: no issues found in 37 source files`; last line `✓ Types generated successfully` (first attempt failed in `apps/web/.next/dev/types`, stale generated files from another branch's dev server; that ignored cache was removed and the run repeated) |
| `make imports` | `Contracts: 3 kept, 0 broken.` |
| `make db-up` | ` Container group12-db-1 Healthy ` |
| `make test` | test-unit `======================== 153 passed, 1 warning in 2.89s ========================`, test-contract `11 passed`, test-api `44 passed`, test-authz `1 passed`; last line `   Duration  1.79s (environment 60%, tests 15%, setup 13%, import 9%, transform 3%)` |
| `make check` | exit 0; last line `   Duration  1.73s (environment 60%, tests 15%, setup 13%, import 9%, transform 2%, worker 1%)` |
| After the rebase on 7c9f5f4: `make check` | exit 0; test-unit `153 passed`, test-contract `11 passed`, test-api `44 passed`, test-authz `1 passed`, test-web `      Tests  48 passed (48)`; last line `   Duration  3.70s (environment 59%, tests 18%, setup 13%, import 8%, transform 2%)` |
| After the rebase: `make openapi && git diff --exit-code contracts/ai` | no diff, exit 0 |
| `make db-down` | see the SYNC REPORT (run after this record was committed) |

## Not run

None.

## Acceptance criteria

| Criterion | Status (verified / not verified) | How |
| --- | --- | --- |
| Vendor SDK imports appear only in app/ai/providers/gemini.py; make imports enforces it (US-034 AC1, FR-040 AC1, TC-002, TC-156) | verified | `make imports`: `Contracts: 3 kept, 0 broken.`; a planted `google` import breaks the contract; TC-156 AST scan passes and fails on the planted import |
| A test double implementing ModelProvider runs through a stub service without changes to the caller (US-034 AC2, TC-157) | verified | `test_tc_157_a_test_double_runs_through_a_stub_service_unchanged`; the double also passes the contract suite |
| Every provider error type carries a failure_reason that exists in the ai_generations CHECK list (TC-005) | verified | `test_every_provider_error_has_a_failure_reason_in_the_check_list` over all 9 types, reading the list from migration 0004; fails when a reason is changed |
| contracts/ai/*.schema.json are regenerated by make openapi and equal the committed files | verified | `make openapi && git diff --exit-code contracts/ai`: no diff; schema-sync unit test |

## Blockers

None.

## Proposed decisions

The card and the specification disagree in the points below. CLAUDE.md says the specification wins. Here each is built so that both texts hold where possible, and recorded for a decision run.

- **PD-IMP-110-1 (configuration errors):** card IMP-110 step 3 (and IMP-207 step 1) names `ProviderConfigError`. §8.3, §8.4, §3.10 (MOD-B05) and later cards (IMP-302, IMP-401, IMP-403 use `ProviderAuthError`) name `ProviderAuthError` and `ProviderBadRequest`, both recording `config_error`. **Built:** `ProviderConfigError` as their common base; all three record `config_error` and are not retryable. Proposed: record this hierarchy in §8.3, or rename the card's term.
- **PD-IMP-110-2 (fine-tuned stub):** card step 4 has the constructor raise `ProviderConfigError('fine-tuned adapter not enabled before Stage 2')`. §8.4 says every call raises `ProviderBadRequest("FINETUNED_MODEL not enabled in Stage 1")`. **Built:** the constructor and every operation raise `ProviderBadRequest` with the §8.4 message. It is a `ProviderConfigError`, so the card's behaviour holds too, apart from the message text.
- **PD-IMP-110-3 (§8.18 worked example):** the gr-1 excerpt sends `"interests": ["history", "food"]`, but IMD-40 and §6.5 limit interests to the place categories except `stay`, and "history" is a tag. The excerpt also has no `day_hints`, which §8.6 lists. **Built:** IMD-40 and §8.6. The test request uses `["sight", "food"]` and adds `day_hints`. Proposed: correct the example.

## Open issues

- **Section references:** the run prompt cites "§8.3" for gr-1 and io-1. In the specification they are §8.6 (gr-1) and §8.7 (io-1); §8.3 holds the interface, result types and errors. All three sections were followed.
- **Where the specification is silent, these choices were made:**
  - `contingency_pct` is a number from 0 to 50, as in the §8.18 example; it is not a money string.
  - `assumptions` entries have no length limit, and neither do `tags` or `hours_summary`.
  - `meal_slots` is a list of strings.
  - The `$id` form is a URN.
  - The base `ProviderError` records `internal`.
- **Gemini wire schema:** the schema without `$schema`, `$id` and `pattern` (§8.7) belongs to the Gemini adapter (IMP-301).
- **`make openapi-check`** is still a placeholder (IMP-214). When IMP-214 builds it, it can call `python -m app.schemas.ai_export --check` for the AI schemas.
- **The double is named `MOCK`,** the only fitting `ProviderName`, and lives in `tests/fixtures/ai.py`. IMP-207 replaces it in the contract suite with the real MOCK adapter. The double can stay as the TC-157 caller-independence check.
