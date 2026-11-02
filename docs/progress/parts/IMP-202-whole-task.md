# IMP-202 · whole-task part

- Run id: RUN-022
- Owner: Jeel (jeelfefar2141)
- Status: PR_OPEN
- Base commit: b0cfdc1
- Branch: feat/IMP-202-whole-task
- Reviewer: Malhar (Malhar1112-v)
- Traces to: US-053; FR-038; NFR-022, NFR-042; TC-004, TC-012, TC-151, TC-152, TC-153; IMD-17, IMD-22, IMD-91
- Card steps built: 1 to 6

## Changed files

- `apps/api/app/generation/records.py` (created, pure; steps 2, 3 and 5):
  - **Vocabularies:** `GenerationStatus`, `CompletedOutcome`, `GenerationScope` and `FailureReason` are Literals copied from the migration 0004 CHECK lists. A test reads the migration file to confirm every value. `FailureReason` is the provider reasons of `app.ai.errors.ProviderFailureReason` (IMD-91) plus `unresolved_validation`.
  - **Transitions:** `ACTIVE_STATUSES` and `TRANSITIONS` (the table below). `check_transition` raises `IllegalTransitionError` for a change outside the table.
  - **Scope (IMD-17):** `check_scope` requires `scope_day_number` 1 to 14 exactly for scope `day`.
  - **Outcome and reason:** `check_outcome` allows only `model`, `model_repaired` or `fallback_rule_based` to complete a generation. `check_failure_reason` checks the reason.
  - **Request hash:** `canonical_json` and `request_hash` give the SHA-256 hex of the request JSON with sorted keys and compact separators. `check_request_hash` refuses anything that is not a 64-character lowercase hex digest, so request content cannot reach the column.
  - **Settings:** `clean_generation_settings` refuses any key containing `prompt` or `text` (case-insensitive) and refuses non-scalar values or strings over 64 characters. It keeps the §8.4 parameter names (`api_style`, `temperature`, `max_output_tokens`, `thinking_level`, `structured_output`, `timeout_s`) and drops other unknown keys.
  - **Usage:** `usage_columns` maps `UsageMetadata` to `input_tokens`, `output_tokens` and `thinking_tokens` exactly. An absent count stays null, `total_tokens` is not stored, and nothing is estimated.
  - **Errors:** `IllegalTransitionError` and `InvalidGenerationRecordError` (a `ValueError`).
- `apps/api/app/generation/repository.py` (created; steps 1, 2 and 4). Every function takes the caller's `AsyncSession`, which the service or job opens with `app.db.session.transaction()`; no engine is opened here.
  - `create_queued(...) -> UUID` inserts a `queued` row after checking scope, hash and settings.
  - `mark_running`, `mark_validating` and `mark_repairing` each lock the row (`SELECT … FOR UPDATE`, populate existing) and check the transition before changing anything.
  - `complete(...)` sets status `completed`, the outcome, `failure_reason` NULL (IMD-22), `completed_at = now()`, the usage columns, `latency_ms`, the repair counts, `validation_summary`, `adapter_version` and `model_version`. A fallback cause goes in `validation_summary["provider_failure"]`.
  - `fail(failure_reason, ...)` sets status and outcome `failed`, the reason and `completed_at = now()`, with optional usage, latency and summary.
  - `cost_estimate_usd` and `cost_basis` are never written, so they stay NULL.
  - `find_active_for_trip` returns the newest row in queued, running, validating or repairing.
  - `get_for_user` is owner-scoped: a missing or foreign generation raises `NotFound` (404).
- `apps/api/tests/api/test_generation_records.py` (created, 41 tests; step 6), against the migrated test database. They cover:
  - full success, fallback and failure records;
  - failing from every active status;
  - null and partly reported usage, and the exact usage mapping;
  - a privacy scan: `row_to_json` of every row for the user must not contain the user's e-mail, the display name, the traveller note, prompt text or `@`;
  - the hash being canonical and the refusal of a non-digest;
  - settings refusals and the allow-list;
  - illegal transitions and final statuses, each comparing a full-row snapshot before and after;
  - a bad outcome or reason;
  - the transition table, and the vocabularies against migration 0004;
  - scope rules, `find_active_for_trip`, owner-scoped `get_for_user`, and a missing id.

The db models and the migration are unchanged. Every card field has an `ai_generations` column.

## Transition table

| From | Allowed to | Pipeline step (§8.2) |
| --- | --- | --- |
| queued | running, failed | step 1 starts; config or quota stop, reaper |
| running | validating, failed | steps 8 and 9 after generation or fallback; failure |
| validating | repairing, completed, failed | step 10; step 11; unresolved or failure |
| repairing | validating, completed, failed | repaired plan checked again; step 11; failure |
| completed | none (final) | |
| failed | none (final) | |

## Commands and results

| Command | Result line |
| --- | --- |
| `make db-up` | `Container group12-db-1 Healthy` |
| `TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/travel_test make test-api ARGS='-k generation_records'` | `41 passed, 142 deselected, 1 warning in 11.36s` |
| `make test-api ARGS='-k schema_drift'` (same URL) | `31 passed, 152 deselected, 1 warning in 1.13s` |
| `make lint` | `All matched files use Prettier code style!` (ruff `All checks passed!`) |
| `make typecheck` | `Success: no issues found in 63 source files` |
| `make imports` | `Contracts: 3 kept, 0 broken.` |
| `make test` | unit `298 passed, 1 warning in 5.03s`; contract `11 passed in 0.08s`; api `183 passed, 1 warning in 40.15s`; authz `9 passed in 0.82s`; web `Tests  48 passed (48)` |
| `make check` | exit 0 (api `183 passed, 1 warning in 42.22s`; `openapi-check: not yet implemented (IMP-214)`) |
| `make db-down` | `Network group12_default Removed` |

Mutation checks, both reverted:
- With the transition check in the repository replaced by `pass`, `make test-api ARGS='-k generation_records'` failed.
- With absent usage stored as 0 instead of null, the same command failed.

Not run: `make e2e` (no journey in this card). `make openapi-check` is still the IMP-214 placeholder.

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| A completed row has provider, model_id, prompt_template_id, prompt_version, mapping_version, scope, status, outcome, latency_ms and completed_at set (FR-038 AC1, TC-151, TC-012) | verified | `test_tc_151_a_completed_generation_has_all_contract_columns`; `test_a_failed_generation_records_its_reason_and_completed_at` |
| When usage metadata is absent, the token fields are NULL (FR-038 AC2, TC-152, TC-004) | verified | `test_tc_152_absent_usage_leaves_the_token_fields_null`; `test_partly_reported_usage_stores_only_the_reported_counts`; `test_usage_maps_exactly_to_the_three_token_columns` |
| No row contains e-mail, name or prompt text (FR-038 AC3, TC-153) | verified | `test_tc_153_no_row_contains_email_name_note_or_prompt_text`; `test_generation_settings_refuse_prompt_or_text_and_non_parameter_values`; `test_a_request_hash_that_is_not_a_digest_is_refused` |
| Illegal status transitions raise and leave the row unchanged | verified | `test_illegal_transitions_raise_and_leave_the_row_unchanged` (7 cases); `test_final_statuses_accept_no_further_change`; `test_complete_refuses_the_failed_outcome_and_fail_an_unknown_reason` |

## Blockers

None.

## Proposed decisions

- **PD-IMP-202-1: transition table.** §8.2 lists the statuses per step but no explicit table, so the table above is derived from the steps.
  - `running → completed` is not allowed: a fallback plan is validated too, so it passes through `validating`.
  - `repairing → validating` is allowed, because the repaired plan is checked again.
  - Every active status may go to `failed`.
- **PD-IMP-202-2: `request_hash` argument.** `create_queued` takes the hash, as the card's signature does, and refuses any value that is not a SHA-256 hex digest. Callers compute it with `records.request_hash(request.model_dump(mode="json"))`.
- **PD-IMP-202-3: settings keys.** The card lists temperature, max_output_tokens and thinking level; §8.4 lists api_style, thinking_level, max_output_tokens, structured_output and timeout_s, and says unknown keys are dropped. The allow-list is the union of both.
  - Keys containing `prompt` or `text` are refused with an error rather than dropped.
  - Other unknown keys are dropped, as §8.4 says.
- **PD-IMP-202-4: where usage, latency and settings are written.** §8.16 writes usage, latency and `generation_settings` "after step 7", but the card puts usage and latency in `complete()` and settings in `create_queued()`. The card is followed. IMP-210 may ask for a separate after-step-7 helper if API-23 must show them earlier.
- **PD-IMP-202-5: exception names.** The exceptions are named `IllegalTransitionError` and `InvalidGenerationRecordError`, with the ruff N818 suffix. They are internal pipeline errors, not API errors; IMP-210 maps them if needed.

## Open issues

- `find_active_for_trip` takes no lock. The one-active-job-per-trip rule (§6, `GENERATION_IN_PROGRESS`) belongs to IMP-210's service, which should take a trip-row lock before `create_queued`.
