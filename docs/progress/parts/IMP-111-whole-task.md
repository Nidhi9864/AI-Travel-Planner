# IMP-111 · whole-task part

- Run id: RUN-012
- Owner: Manya (manyarana)
- Status: PR_OPEN
- Base commit: d05ca5d
- Branch: feat/IMP-111-whole-task
- Reviewer: Nidhi (Nidhi9864)
- Traces to: US-039; FR-045; NFR-042; TC-026, TC-169, TC-170
- Card steps built: 1 to 5

## Changed files

- `apps/api/app/ai/prompts/templates/itinerary_generate/v1/system.txt`, `user.txt`, `meta.json` (created, steps 1 and 2). The wording sources are recorded under "Template wording" below.
  - `user.txt` has one placeholder, `${request_json}`, which receives the gr-1 request as JSON between the lines `<request_json>` and `</request_json>`.
  - `meta.json` uses the §8.5 fields: `template_id`, `version`, `created_on`, `input_schema_version` "gr-1", `output_schema_version` "io-1", `description`, `change_note` and `approved_by`. See PD-IMP-111-1.
- `apps/api/app/ai/prompts/__init__.py`, `apps/api/app/ai/prompts/registry.py` (created, steps 3 and 5):
  - `load(template_id, version=None)` returns a `PromptTemplate`; the version defaults to `PROMPT_TEMPLATE_VERSION`, read through the existing `Settings`.
  - An unknown id or version raises `PromptTemplateNotFound`, whose message names both values; they are also kept as attributes. It keeps the card's name, with a one-line `noqa: N818` reason.
  - `PromptTemplate` has `template_id`, `version` (step 5: the values for `prompt_template_id` and `prompt_version`), `system_text`, `user_text`, `repair_text` (None until `repair.txt` exists), `meta`, and `sha256` (the digest of every file of the version), plus:
    - `render(request) -> str` (card step 3);
    - `prompt(request) -> (system_text, user_text)`, which appends `repair.txt` when `repair_context` is set.
  - The module-level `render(template_id, version, request) -> (system_text, user_text)` is the §8.5 signature.
  - Rendering fails loudly with `PromptRenderError` in three cases:
    - a placeholder has no value (`string.Template.substitute`, never `safe_substitute`);
    - the request names a different template id or version than the template;
    - a repair call is made but the template has no `repair.txt`.
  - In the request JSON, `<` and `>` are written as the JSON escapes `<` and `>`. Traveller text therefore cannot close the data block, and the model still reads the same values.
  - `load_all()` reads every version directory once and is cached. It raises `PromptTemplateError` in three cases:
    - a required file is missing, or an unknown file is present;
    - `meta.json` is invalid or names another directory;
    - `user.txt` lacks `${request_json}`.
  - Templates are looked up among the directories found on disk; no path is built from the arguments.
- `apps/api/pyproject.toml` (modified, Het's file; only the `[tool.setuptools.package-data]` lines). **Reason:** without these lines a non-editable install, such as the one the IMP-112 Dockerfile performs, leaves out the `.txt` and `.json` templates. This was checked by building a wheel from a scratch copy: with the lines, the wheel lists `app/ai/prompts/templates/itinerary_generate/v1/{meta.json,system.txt,user.txt}`; without them, only `__init__.py` and `registry.py`.
- `apps/api/tests/fixtures/prompt_hashes.json` (created, step 4): the sha256 of each of the three v1 files.
- `apps/api/tests/unit/ai/test_registry.py` (created; TC-026, TC-169, TC-170): 23 tests. Every test name contains "prompt", so `-k prompt` (the card) and `-k registry` (§8.19) select the same 23.
  - Lookup: the default version, an unknown version, an unknown id, and no path built from the arguments.
  - Hash list: checked against the files on disk and against the registry's own digests.
  - Generation record: the template id and version match the migration 0004 columns.
  - Rendering:
    - the request is parsed back out of the data block;
    - a hostile `notes_quoted` (containing `</request_json>`, "Ignore the rules above" and `${request_json}`) stays inside the block unchanged;
    - a missing placeholder value fails;
    - a request for another version is refused;
    - `repair.txt` is appended or its absence fails.
  - System text: it contains the §8.18 rules and the availability rule.
  - Broken directories fail at load, and a new version directory is found without code changes.
- `docs/progress/parts/IMP-111-whole-task.md` (this record).

Not changed: `app/schemas/ai.py`, `app/ai/errors.py`, `app/ai/providers/`, `app/core/config.py`, `.importlinter`, the socket guard. No adapter, pipeline or generation record was built.

## Template wording (narrowing note a)

§8.5 gives rules, not wording. The wording of `itinerary_generate/v1` is in §8.18, the worked example ("Prompt (abbreviated)"), and is used exactly where it exists:

| File and lines | Source |
| --- | --- |
| `system.txt` 3 to 12 (rules 1 to 7: Role, Closed list, Data not instructions, Output, Constraints, Conflicts, Text) | §8.18 wording, copied exactly with its line breaks |
| `system.txt` 1 (opening line) | written from §8.1 |
| `system.txt` 14 to 34 ("Details of these rules") | written from the §8.1 rules, the §8.6 gr-1 fields and the §8.7 io-1 fields: request in a quoted data block (15 to 17); what the model chooses (18 to 20); no prices, costs, totals, budget, hours, travel times, distances or availability (21 to 23); no outside facts (24); hours, durations and day hints only for ordering (25 and 26); scope (27 and 28); locked items (29); limits and meal slots (30 to 33); unmet requirements go in assumptions (34) |
| `user.txt` line 1 ("Plan the trip described by this GenerationRequest (gr-1). Request:") | §8.18 wording, copied exactly |
| `user.txt` lines 2 to 4 (`<request_json>`, `${request_json}`, `</request_json>`) | written from §8.5 (one placeholder, `string.Template`) and note a (quoted data). §8.18 writes `$request_json`; `${request_json}` is the same placeholder in the card's `${name}` form |

No conflict was found between §8.5, §8.18, §8.1 and the card on what the prompt may ask for. The model is asked only for place IDs from the shortlist, their days, order and times, slot types and short texts. gr-1 does give the model the shortlist's price ranges and `hours_summary` (§8.6). The system text uses them only for ordering and forbids repeating any figure.

## Commands and results

| Command | Result line |
| --- | --- |
| `git rev-parse --short origin/main` | `d05ca5d` |
| `make test-unit ARGS='-k prompt'` | `================ 23 passed, 178 deselected, 1 warning in 0.29s =================` (all in `tests/unit/ai/test_registry.py`) |
| `.venv/bin/pytest tests/unit -k registry -q` (the §8.19 filter) | `23 passed, 178 deselected, 1 warning in 0.21s` |
| Scratch copy of `apps/api` outside the repository, unedited (`PYTHONPATH=<copy> pytest tests/unit -k prompt`, registry imported from the copy) | `23 passed, 178 deselected, 1 warning in 0.50s` |
| Same copy, `v1/system.txt` edited in place ("short and factual" to "brief and factual") | `2 failed, 21 passed, 178 deselected, 1 warning in 0.37s` (`test_prompt_tc_170_template_files_match_the_committed_hash_list`, `test_prompt_registry_hashes_are_the_committed_hashes`) |
| Same copy, v1 restored and the change made as `v2/` with its own lines in the hash list | `23 passed, 178 deselected, 1 warning in 0.14s` |
| `pip wheel --no-deps` of a scratch copy, with and without the package-data lines | with: the three template files are listed; without: none (see `pyproject.toml` above) |
| `make db-up` | ` Container group12-db-1 Healthy ` |
| `make lint` | `All matched files use Prettier code style!` |
| `make typecheck` | `✓ Types generated successfully` |
| `make imports` | `Contracts: 3 kept, 0 broken.` |
| `make test` | `   Duration  5.94s (environment 48%, transform 21%, import 10%, tests 10%, setup 10%)` (api unit `201 passed`, contract `11 passed`, api `64 passed`, authz `9 passed`, web `48 passed`) |
| `make check` | `   Duration  4.07s (environment 63%, tests 15%, setup 12%, import 9%, transform 2%)` (same counts; `openapi-check: not yet implemented (IMP-214)`) |
| `make db-down` | ` Network group12_default Removed ` |

The first scratch run used the old name `v2` for the test of a new version directory. When the scratch copy itself added a real `v2`, that test collided with it (`1 failed, 22 passed`). The test now uses the version name `v0-draft`, and the three scratch runs above were repeated after the change.

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| `registry.load('itinerary_generate','v1')` returns the template; an unknown version raises an error naming the version (TC-169, TC-026) | verified | `test_prompt_tc_169_load_returns_itinerary_generate_v1`, `test_prompt_tc_026_unknown_version_raises_an_error_naming_the_version`, `test_prompt_unknown_prompt_template_version_fails_by_name` |
| Editing v1 text without adding a new version fails the hash test (US-039 AC1, TC-170) | verified | `test_prompt_tc_170_template_files_match_the_committed_hash_list`; the scratch-copy edit failed it, and the same change as `v2` passed |
| The template and version are available for the generation record (US-039 AC2) | verified at unit level | `test_prompt_template_id_and_version_are_the_generation_record_values` (`template_id` and `version` match the migration 0004 columns `prompt_template_id` and `prompt_version`, and the gr-1 fields). End to end in IMP-210 |

## Blockers

None.

## Proposed decisions

- **PD-IMP-111-1:** `meta.json` fields differ between the documents:
  - the card (step 1) and the run prompt list `{template_id, version, output_schema_version, created, change_note}`;
  - §8.5 lists `template_id`, `version`, `created_on`, `input_schema_version`, `output_schema_version`, `description`, `change_note` and `approved_by`.

  Following CLAUDE.md (the specification wins), `meta.json` uses the §8.5 set. It contains every field of the card except that `created` is named `created_on`. Proposal: align the card with §8.5.
- **PD-IMP-111-2:** §8.5 says `render(template_id, version, request) -> (system_text, user_text)`, while the card has `PromptTemplate.render(request) -> str`. Both are provided; the module function calls the method. Proposal: record both in §8.5.

## Open issues

- The §8.4 start-up check "`PROMPT_TEMPLATE_VERSION` exists in the registry … exit" is not wired into start-up here, because `app/main.py` and the factory are outside this card. `load_all()` and `load()` are ready for the factory card (IMP-208, which modifies `app/main.py`).
- `repair.txt` for `itinerary_generate/v1` is created by IMP-502 (bounded repair, §8.13), which adds a file to the published v1 directory. That card must add its line to `tests/fixtures/prompt_hashes.json`. The hash test fails until it does, which is the intended review signal.
- The hash test detects a changed file. It cannot detect an edit made together with an updated hash line for v1; review of `prompt_hashes.json` is the guard (published lines are never changed, only added). A `docs/model-change-log.md` entry and a regression evaluation per new version (§8.5) are not part of this card.
