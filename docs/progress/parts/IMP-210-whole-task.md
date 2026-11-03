# IMP-210 · whole-task part

- Run id: RUN-030
- Owner: Het (het-lathiya)
- Status: PR_OPEN
- Base commit: 10748fb
- Branch: feat/IMP-210-whole-task
- Reviewer: Manal (manalPatel2557)
- Traces to: US-153; FR-024, FR-025, FR-038; NFR-004, NFR-008; TC-012, TC-115, TC-151, TC-162
- Card steps built: 1 to 7
- Prerequisites found:
  - The part records of IMP-202, IMP-203, IMP-204, IMP-208, IMP-111, IMP-207, IMP-214 and IMP-201 exist on `main`.
  - API-22 and API-23 were declared in `contracts/openapi.v1.json` and answered 501 `NOT_IMPLEMENTED`.
  - The declared `GenerationStartIn` and `GenerationOut` match §6.6.4 and are used unchanged.

## Changed files

- **Step 1: `apps/api/app/generation/service.py` (created).** API-22 applies the §6.4 create rules in order:
  - the trip is owned (404 otherwise) and not archived (409 `CONFLICT`);
  - the trip is complete. Only the `trip_preferences` row can be missing, because title, destination, dates and adults are NOT NULL. A missing row gives 422 with field `preferences`;
  - the trip has no itinerary yet (409 `CONFLICT`);
  - `mode` is `ai`. `rule_based` gives 422 with field `mode` until IMP-402.

  After the checks:
  - `request_hash` is the SHA-256 of `{trip_id, scope, day_number, mode, plan_revision}`.
  - The same hash while a generation is active returns that generation with 200. A different hash gives 409 `GENERATION_IN_PROGRESS`.
  - Otherwise the service runs `create_queued` with provider and model from the active provider, the template id and version from the registry, and `pm-1`. It then commits and submits the job, so the job starts only after the commit (§6.4). The trip row is locked first, so two starts for one trip run one after the other.
  - API-23 runs the reaper for its own row first. It then maps `failure_reason` to `failure_message` and `next_action` (§6.4), and reads `itinerary_version_id` and `plan_revision` from the version the generation saved.
- **Step 2: `apps/api/app/generation/jobs.py` (created).**
  - Jobs run as asyncio tasks, at most 2 at a time (semaphore), each under `asyncio.timeout(120)`.
  - A timeout or an unexpected error ends the job `failed` with `internal`.
  - A timeout also sets `validation_summary.timed_out`, so API-23 says "Generation timed out." (IMD-22).
  - `reap_forever` fails active rows older than 150 s, at start-up and every 60 s.
  - `get_submit` is a FastAPI dependency, so tests can capture the job instead of starting a task.
- **Step 3: `apps/api/app/generation/request_builder.py` (created).** It builds gr-1 from:
  - the trip and its preferences, read through `trips.service`, which is owner-scoped;
  - the must-visit IDs;
  - `budget_settings.contingency_pct`;
  - the first 40 active places by name, read through `places.service.search_places`;
  - the pace limits of `pm-1`, `day_start` 09:00, `day_end` 19:00 and meal slots `["lunch"]` (§8.6);
  - the template from the generation row.

  Notes are sent only as `notes_quoted`: control characters are removed, e-mail addresses are redacted (`redact_text`), and the text is cut to 500 characters.
- **Step 4: `apps/api/app/generation/pipeline.py` (created).** The steps are:
  1. `mark_running`;
  2. `provider.generate_itinerary`; a `ProviderError` ends the job `failed` with that error's `failure_reason`;
  3. `mark_validating`;
  4. the io-1 schema check, again on the model, plus the check that day numbers are unique and within `num_days`, plus the check that place IDs are a subset of the shortlist. Any failure ends the job `failed` with `invalid_output`;
  5. the save and `complete(outcome='model')` in one transaction.

  Each status change is its own short transaction, and none stays open across the provider call. The log holds only the generation id, the failure reason or problem kind, and the latency. It never holds the request, the output, notes or prompt text.
- **Step 4: `apps/api/app/generation/repository.py` (modified).** Added:
  - `fail_stale`, the reaper query; it uses `for update skip locked` and reuses `fail`;
  - `contingency_pct`, a read of `budget_settings`;
  - `lock_trip`, a `for update` on the caller's trip.
- **Step 5: `apps/api/app/itinerary/service.py` and `apps/api/app/itinerary/repository.py` (created).** `save_generated_plan` runs in the caller's transaction, and the pipeline completes the generation record in that same transaction (NFR-008). It:
  - locks the trip;
  - deletes the trip's warnings and days; items are removed by the cascade;
  - inserts days (`plan_date = start_date + day - 1`) and items. Items get origin `model`, times and durations as the output gives them, and `note_origin` `ai` or `none`. Cost and travel columns stay NULL and `source_chunk_ids` keeps its empty default;
  - increments `plan_revision` and sets status `ready` and `plan_stale` false;
  - inserts version `max + 1` with reason `generation`, the snap-1 snapshot (days, items and `budget_settings`) and `generation_id`.

  The generation module calls the itinerary service, never its repository (one writer per table).
- **Step 6: `apps/api/app/generation/router.py` (modified).**
  - Only the API-22 and API-23 bodies changed. API-22 answers 202, or 200 when the same request is already active.
  - The decorators, models and API-30 and API-31 placeholders are unchanged.
- **Outside the card's Files list (PD-IMP-210-1): `apps/api/app/main.py` (5 lines).** The lifespan starts `reap_forever` and cancels it on shut-down. Step 2 needs this.
- **Step 7: `apps/api/tests/api/test_generations.py` (created).** 14 tests, MOCK only.
- This record (created).

Unchanged:
- `contracts/openapi.v1.json` and the web types (`make openapi-check` passes);
- io-1 and gr-1, the status values and failure reasons;
- migrations 0001 to 0007, `MIGRATION_HEAD`;
- `docs/progress/sprint-2.md` and the decision register.

## Commands run

| Command | Result |
| --- | --- |
| `make test-api ARGS='-k generations'` | `16 passed, 207 deselected, 1 warning in 7.65s` |
| `make lint` | `All checks passed!` (ruff) and `All matched files use Prettier code style!` |
| `make typecheck` | `Success: no issues found in 85 source files` (mypy); web `tsc --noEmit` passed |
| `make imports` | `Contracts: 4 kept, 0 broken.` |
| `make test` | unit `385 passed, 1 warning in 9.68s`; contract `35 passed, 1 warning in 0.83s`; api `223 passed, 1 warning in 59.49s`; authz `9 passed in 1.99s`; web `Tests  54 passed (54)` |
| `make test-authz` | `9 passed in 1.81s` |
| `make openapi-check` | `openapi-check: contracts/ and apps/web/lib/api/schema.d.ts are up to date` |
| `make check` | exit 0, with the same result lines |

`make db-up` was run before the tests and `make db-down` after them.

## Checks that the tests can fail

- With the place-ID check disabled in `pipeline.output_problem`, `tests/api/test_generations.py` failed: `1 failed, 13 passed in 7.64s`.
- The change was reverted.
- A separate script against the test database confirmed one behaviour the API tests cannot reach: `session.commit()` inside the `transaction()` (`session.begin()`) context exits cleanly. This is what API-22 does before it submits the job.

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| With MOCK, API-22 returns 202 and API-23 reaches completed with outcome `model`; days, items and a version exist; no Gemini call (US-153 AC1, TC-162) | verified | `test_tc_162_mock_generation_completes_and_saves_the_plan`; the provider socket guard is active |
| A repeated identical POST while active returns the same generation (200); a different request gives 409 `GENERATION_IN_PROGRESS` (FR-024) | verified | `test_same_request_while_active_returns_the_same_generation`, `test_a_different_request_while_active_is_refused` |
| An incomplete trip returns 422 listing the missing fields (TC-115) | verified | `test_tc_115_an_incomplete_trip_lists_the_missing_fields` |
| A failing job leaves the previous plan intact and the record failed with a `failure_reason` (NFR-008) | verified | `test_a_provider_timeout_fails_and_leaves_the_previous_plan_untouched`, `test_an_answer_outside_the_shortlist_fails_with_invalid_output`, `test_the_job_timeout_fails_with_internal_and_says_timed_out` |
| The record names provider, model_id, prompt_template_id, prompt_version and mapping_version (TC-012, TC-151) | verified | `test_tc_012_tc_151_the_record_names_provider_model_template_and_mapping` |
| FR-025: API-23 reports status; owner-scoped, 404 otherwise | verified | the poll in every test; `test_another_users_trip_and_generation_are_not_found` (trip and generation, both 404 `NOT_FOUND`) |
| FR-038: one record per generation, no prompt text or notes stored or logged | verified | the record tests above; the log check for notes and model text in TC-162; gr-1 holds no e-mail, user ID or title (`test_the_request_holds_only_trip_data_and_shortlisted_places`) |
| NFR-004: generation within its time budget | not verified | Only the 120 s hard timeout is enforced and tested. A latency measurement needs the real provider (IMP-301 and later) |
| Reaper fails stale active rows with `internal` | verified | `test_api_23_reaps_a_stale_active_generation` (API-23 path). The start-up and 60 s loop is not covered by a test |

## Known gaps (for the gate card's sprint-2 list)

These are interim by design, each with the card that closes it:
- No recalculation of times, travel or costs (IMP-308).
- No validator rules beyond the schema, day-number and place-ID checks; no repair; no rule-based fallback. A timeout ends `failed` with `provider_timeout` until IMP-403.
- No edits.
- The shortlist is the first 40 places by name, with no hard filters (`stay` is not excluded). A must-visit place beyond the first 40 is not added (IMP-303, IMP-304).
- `hours_summary` holds only the hours label, not the hours of the trip's weekdays (IMP-303).
- The step-11 check that `plan_revision` is unchanged is not built (IMD-23; IMP-305).
- The AI-notice check (IMP-305) and the daily caps (IMP-511) are not built.

## Blockers

None.

## Proposed decisions

- **PD-IMP-210-1.** `apps/api/app/main.py` is outside the card's Files list. Its lifespan is the only place to start the reaper "at start-up and every 60 s" (step 2).
- **PD-IMP-210-2.** §6.4 lists two create rules that the card does not: an archived trip, and a trip that already has an itinerary, each give 409 `CONFLICT`. Both are applied, because the specification wins.
  - Consequence: the card's "previous plan untouched" case cannot be reached through API-22.
  - The test therefore inserts the second queued row directly and runs the job, as API-31 will (IMP-607).
- **PD-IMP-210-3.** `ai_generations` has no column for a failure message. The timeout and the reaper mark the row with `validation_summary.timed_out = true`, and API-23 then returns "Generation timed out." (IMD-22).
  - Please confirm this, or name another place for the marker.
- **PD-IMP-210-4.** `GenerationOut.mode` is derived from `model_id`: `rule_based_planner_v1` means `rule_based`, as §6.4 specifies for that mode. The table has no mode column.

## Open issues

- No test covers the real path end to end: the asyncio task started by `jobs.submit` with the real `transaction()`. The API tests capture the job and run it on the rolled-back test session. The planned E2E journey (IMP-213, `make e2e`) covers this.
