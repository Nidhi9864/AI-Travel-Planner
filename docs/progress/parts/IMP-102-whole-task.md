# IMP-102 · whole-task part

- Run id: RUN-003 (build), RUN-003b (evidence: red-check pull requests, board, protection status)
- Owner: Kirtan (kirtan-S111)
- Status: PR_OPEN
- Base commit: 4e4a7fe
- Branch: feat/IMP-102-whole-task
- Reviewer: Junaid (Junaid-Kureshi)
- Traces to: US-001; NFR-013, NFR-018, NFR-031, NFR-034, NFR-048
- Card steps built: 1 to 6 and step 7 in RUN-003 (step 7 limited to the collaborator check and `docs/progress/board-issues.md`); the board and its issues in RUN-003b. Step 8 was done by the repository admin between the runs: the classic branch protection rule is saved but not enforced on this plan (see "Branch protection and merge settings").

## Changed files

- `.github/workflows/ci.yml` (created)
- `.githooks/commit-msg` (created, mode 100755)
- `scripts/check_attribution.sh` (created, mode 100755)
- `.github/pull_request_template.md` (created)
- `.github/CODEOWNERS` (created)
- `docs/guides/contributing.md` (created)
- `docs/progress/board-issues.md` (created; RUN-003b added the board link and an Issue column)
- This record (created; updated in RUN-003b)

RUN-003b changed no file of the workflow, the hook, the script, CODEOWNERS, the template or the guide.

No `.gitleaks.toml` was added: gitleaks found nothing in `docs/spec` or anywhere else (commands below), so no allowlist is needed. The Makefile was not changed; `make setup` already sets `core.hooksPath` to `.githooks` now that the directory exists.

## What the files contain

**ci.yml.** Triggers: `pull_request` (types opened, synchronize, reopened, edited, so a body edit re-runs the attribution check) and `push` to `main`. `permissions: contents: read, pull-requests: read`; no secret other than the default `GITHUB_TOKEN`; workflow env `AI_PROVIDER=MOCK`, `APP_ENV=test`. Python 3.12 through `actions/setup-python@v7` (pip cache keyed on `apps/api/pyproject.toml`), Node from `.nvmrc` through `actions/setup-node@v7` (npm cache keyed on `apps/web/package-lock.json`); every job that needs the toolchains installs with `make setup`.

| Job | Trigger | Steps |
| --- | --- | --- |
| `lint-types` | PR and push to main | `make lint`, `make typecheck`, `make imports` |
| `unit` | PR and push to main | `make test-unit`, `make test-contract`, `make test-web` |
| `guards` | PR and push to main | gitleaks 8.30.1 (release archive, sha256 pinned in the workflow and checked); PR: `gitleaks git --log-opts="--no-merges <base.sha>..<head.sha>"` from the payload; push to main: the full history |
| `attribution` | PR only | `bash scripts/check_attribution.sh` with `TEAM_EMAILS: ${{ vars.TEAM_EMAILS }}`, checkout with `fetch-depth: 0` |
| `audit` | PR and push to main | pip-audit of the installed API dependencies (any finding fails); pip-audit of the venv's own installer, report only; `npm audit --audit-level=critical` in `apps/web` |
| `api` | PR and push to main | service `postgres:16` (database `travel_test`, health check `pg_isready`); `TEST_DATABASE_URL` and `DATABASE_URL` set to the §4.7 default `postgresql+psycopg://postgres:postgres@localhost:5432/travel_test`; `make db-migrate`, `make test-api`, `make test-authz` |

**.githooks/commit-msg** (POSIX sh). Removes `CLAUDE.md` and `.claude/` in any case, then rejects, case-insensitively, a line that starts with `co-authored-by:` (leading spaces allowed; rule `co-authored-by`) or one of the two forbidden tool words of card step 4 as a whole word (rule `tool-word`; word edges as perl `\b`, so `claude_code` and `claudette` are not whole-word matches). It prints `commit-msg: rule <name> failed: ...` and exits 1.

**scripts/check_attribution.sh** (bash). Reads `pull_request.base.sha`, `pull_request.head.sha` and `pull_request.body` from `$GITHUB_EVENT_PATH` (python3, present on the runner and on every member's machine; jq is not installed locally), never `HEAD`. For each commit of `git rev-list --no-merges <base>..<head>` it reports rule `team-email` (author email not in `TEAM_EMAILS`, compared without case; commas, spaces, semicolons or new lines separate the list), rule `committer` (committer name or email differs from the author) and the rule of the hook, which it runs as is on the message, so both apply the same rules. It then runs the hook on the pull-request body. Each failure prints `attribution: FAIL commit <sha7> rule <name> failed: ...` (emails are never printed); the last line is `attribution: PASS <n> commit(s) of <base7>..<head7> and the pull request body` or `attribution: FAIL <k> problem(s) in ...`. Exit 0 pass, 1 rule failure, 2 unusable input (empty `TEAM_EMAILS`, missing payload, commits not in the clone).

**Pull-request template.** Linked IMP task, part and requirement IDs; what changed; tests run with commands and result lines; screenshots; contract and migration checkboxes; part owner, reviewer, part record, prerequisites; checklist. No tool, AI-use or generated-by text; the template passes the hook (exit 0).

**CODEOWNERS.** `/contracts/`, `/apps/api/migrations/`, `/apps/api/app/schemas/` → `@kirtan-S111`; `/apps/api/app/ai/` → `@Nidhi9864`. Kirtan only on the first three: see PD-G.

**contributing.md.** Branch naming, Conventional Commits with the task ID, owner identity with the `-c` pair, one author, the hook and its rules, the two before-push checks of CLAUDE.md §12, pull-request title, assignee and reviewer, the template, API part before screen part, one migration per pull request, the six required checks, Rebase and merge only (IMD-63), the part record per pull request (IMD-62), when a part counts as done.

**board-issues.md.** One row per task part of every card: 183 rows, 108 cards, 427 points (Sprint 1: 21 parts, 47 points; per-member totals 43/42 as in §14.3). Title `IMP-NNN · <part text as written on the card>` or `IMP-NNN · whole task`, GitHub assignee, labels `sprint-N` and `points-X`, status. The two IMP-101 parts are marked `merged`.

## Commands run

| Command | Result line (quoted exactly) |
| --- | --- |
| Preflight: `git fetch origin; git status --porcelain --untracked-files=no` | no output; base `git rev-parse --short origin/main` → `4e4a7fe` |
| Preflight on main: `make lint` / `make typecheck` / `make imports` | exit 0 / exit 0 / `Contracts: 3 kept, 0 broken.` |
| `gh api repos/het-lathiya/Group12/collaborators --jq '.[].login'` | `Manasvi1704`, `Junaid-Kureshi`, `Assassin-byte`, `het-lathiya`, `jeelfefar2141`, `Nidhi9864`, `manyarana`, `Malhar1112-v`, `manalPatel2557`, `kirtan-S111` (all ten) |
| `gh api repos/het-lathiya/Group12/invitations --jq '.[].invitee.login'` | no output (no pending invitation) |
| `gh api repos/het-lathiya/Group12 --jq '{allow_squash_merge,allow_merge_commit,allow_rebase_merge}'` | `{"allow_merge_commit":false,"allow_rebase_merge":true,"allow_squash_merge":false}` |
| `gh variable list` | `TEAM_EMAILS` exists: 10 comma-separated emails, Kirtan's among them (values not printed) |
| gitleaks 8.30.1 (docker image) `gitleaks git --redact` over the full history, before the changes | `23 commits scanned.` `no leaks found` |
| gitleaks over `origin/main..HEAD` (`--log-opts="--no-merges <base>..HEAD"`) and over the full history, after the commits | `no leaks found` (both) |
| `apps/api/.venv/bin/pip-audit` (whole venv) | `Found 12 known vulnerabilities in 1 package` — all in `pip 24.0` (the venv's installer), see open issues |
| `pip freeze --exclude-editable` → `pip-audit --requirement <file> --no-deps --disable-pip` (the CI audit step) | `No known vulnerabilities found` |
| `npm audit --audit-level=critical` (apps/web) | exit 0 (the 16 moderate dev-only findings of RUN-001 do not fail it) |
| `actionlint .github/workflows/ci.yml` (rhysd/actionlint 1.7.12, docker) | no output, exit 0 |
| `shellcheck scripts/check_attribution.sh .githooks/commit-msg` (docker) | no output, exit 0 |
| Hook through git: `git commit --allow-empty -m "<message with the vendor word>"` after `git config core.hooksPath .githooks` | `commit-msg: rule tool-word failed: ...`, exit 1, no commit created |
| `make lint` | `All matched files use Prettier code style!` (exit 0; ruff `All checks passed!`) |
| `make typecheck` | `✓ Types generated successfully` (exit 0; mypy `Success: no issues found in 13 source files`) |
| `make imports` | `Contracts: 3 kept, 0 broken.` |
| `make test` | `No test files found, exiting with code 0` (exit 0; API unit `20 passed in 0.16s`; contract, api, authz `pytest: no tests collected (exit 5 treated as success)`) |
| `make check` | `No test files found, exiting with code 0` (exit 0) |

### Hook test (IMD-61, local half)

Message files in a scratch directory outside the repository, passed to `.githooks/commit-msg` directly.

| Message | Exit | Printed rule |
| --- | --- | --- |
| Subject plus a `Co-authored-by: Someone <...>` trailer | 1 | `commit-msg: rule co-authored-by failed: a line starts with 'Co-authored-by:' (one author per commit, IMD-61).` |
| Subject naming the tool word, capitalised | 1 | `commit-msg: rule tool-word failed: the message names an AI tool or its vendor (IMD-61); only the paths CLAUDE.md and .claude/ may appear.` |
| Body naming the tool word followed by "code", lower case | 1 | `commit-msg: rule tool-word failed: ...` |
| Vendor word in upper case | 1 | `commit-msg: rule tool-word failed: ...` |
| Indented trailer in mixed case (`  co-AUTHORED-by: ...`) | 1 | `commit-msg: rule co-authored-by failed: ...` |
| Only `CLAUDE.md` and `.claude/settings.json` | 0 | none |
| `claude.md` and `.CLAUDE/` in other cases | 0 | none |
| The word `claudette` | 0 | none |
| An identifier `claude_code` (underscore joins the word, as perl `\b`) | 0 | none |

### Attribution script test (IMD-61, CI half)

A scratch repository in the scratchpad (outside the repository, no remote, never pushed); one branch per case from a base commit; a payload file per case with `pull_request.base.sha`, `head.sha` and `body`; `TEAM_EMAILS` set from the repository variable (the ten team emails).

| Case | Exit | Result lines |
| --- | --- | --- |
| Clean commit by Kirtan, clean body | 0 | `attribution: PASS 1 commit(s) of 12369af..a5d23e0 and the pull request body` |
| Message with a `Co-authored-by:` trailer | 1 | `attribution: FAIL commit a4d22f6 rule co-authored-by failed: a line starts with 'Co-authored-by:' (one author per commit, IMD-61).` |
| Author and committer `outsider@example.com` | 1 | `attribution: FAIL commit ea6bb88 rule team-email failed: the author email is not in TEAM_EMAILS` |
| Author Kirtan, committer `GitHub <noreply@github.com>` | 1 | `attribution: FAIL commit edb6488 rule committer failed: the committer differs from the author (author and commit as the part owner)` |
| Clean commit, body (CRLF lines) naming the tool | 1 | `attribution: FAIL pull request body rule tool-word failed: the message names an AI tool or its vendor (IMD-61); only the paths CLAUDE.md and .claude/ may appear.` |
| Clean commit, empty `TEAM_EMAILS` | 2 | `attribution: ERROR TEAM_EMAILS is empty; set the repository variable TEAM_EMAILS (comma-separated)` |
| Clean commit, `null` body | 0 | `attribution: PASS ...` |
| Clean commit, `TEAM_EMAILS` upper case with ` ; ` separators | 0 | `attribution: PASS ...` |

Each failing case also prints the summary `attribution: FAIL 1 problem(s) in 1 commit(s) of <base7>..<head7> and the pull request body`.

### TC-002 (local half)

Scratch copy of `apps/api/app` and `.importlinter` outside the repository, with `from google import genai` planted in `app/itinerary/service.py`; `lint-imports --config .importlinter`:

`Contracts: 2 kept, 1 broken.` — broken: `Vendor isolation: google (google.genai) only in app.ai.providers.gemini`, `app.itinerary.service -> google (l.1)`; exit 1.

### CI on the pull request

Pull request https://github.com/het-lathiya/Group12/pull/3, workflow run https://github.com/het-lathiya/Group12/actions/runs/41223146687 (head `958a414`, the six commits before this record was updated). `gh pr checks 3`:

| Job | Conclusion | Job URL | Result line from the log |
| --- | --- | --- | --- |
| `lint-types` | pass (1m39s) | https://github.com/het-lathiya/Group12/actions/runs/41223146687/job/124601692156 | `Contracts: 3 kept, 0 broken.` (also `All checks passed!`, `Success: no issues found in 13 source files`, `All matched files use Prettier code style!`) |
| `unit` | pass (1m36s) | https://github.com/het-lathiya/Group12/actions/runs/41223146687/job/124601692102 | `20 passed in 0.16s`; contract `pytest: no tests collected (exit 5 treated as success)`; web `No test files found, exiting with code 0` |
| `guards` | pass (7s) | https://github.com/het-lathiya/Group12/actions/runs/41223146687/job/124601692264 | `6 commits scanned.` `no leaks found` |
| `attribution` | pass (5s) | https://github.com/het-lathiya/Group12/actions/runs/41223146687/job/124601692047 | `attribution: PASS 6 commit(s) of 4e4a7fe..958a414 and the pull request body` |
| `audit` | pass (1m38s) | https://github.com/het-lathiya/Group12/actions/runs/41223146687/job/124601692212 | `No known vulnerabilities found` (API dependencies); report-only step `Found 12 known vulnerabilities in 1 package` (the venv's `pip 25.0.1`); npm `16 moderate severity vulnerabilities`, exit 0 at `--audit-level=critical` |
| `api` | pass (1m41s) | https://github.com/het-lathiya/Group12/actions/runs/41223146687/job/124601692325 | `db-migrate: not yet implemented (IMP-106)`; api and authz `pytest: no tests collected (exit 5 treated as success)` |

CI used Python 3.12.15 (`python-version: "3.12"`); `.python-version` pins 3.12.3 locally. The commit that adds these results starts a new run on the same pull request.

Second run on the pull request (head `3e8adfc`, the commit above): https://github.com/het-lathiya/Group12/actions/runs/41223394094, conclusion `success`, all six jobs (`lint-types`, `unit`, `guards`, `attribution`, `audit`, `api`) `success`. This is the green run of the card's completion evidence.

## RUN-003b evidence

Preflight: `git fetch origin; git status --porcelain --untracked-files=no` printed nothing; `origin/main` is `4e4a7fe` (unchanged, no rebase); `feat/IMP-102-whole-task` was up to date at `3e8adfc`; `git config core.hooksPath` → `.githooks`.

### Branch protection and merge settings

| Command | Result (quoted exactly) |
| --- | --- |
| `gh api repos/het-lathiya/Group12/branches/main/protection` | `{"message":"Upgrade to GitHub Pro or make this repository public to enable this feature.","documentation_url":"https://docs.github.com/rest/branches/branch-protection#get-branch-protection","status":"403"}` then `gh: Upgrade to GitHub Pro or make this repository public to enable this feature. (HTTP 403)`, exit 1 |
| `gh api repos/het-lathiya/Group12 --jq '{allow_squash_merge,allow_merge_commit,allow_rebase_merge}'` | `{"allow_merge_commit":false,"allow_rebase_merge":true,"allow_squash_merge":false}` |

The operator reports that the admin saved a classic branch protection rule for `main` with the step 8 settings, and that GitHub shows it as **Not enforced** with the banner "Your rules won't be enforced on this private repository until you move to a GitHub Team or Enterprise organization account". The API cannot read the rule on this plan, so its values are not recorded; no screenshot was supplied. Card step 8 covers this case: the rules are followed by agreement and checked by the planner (working agreement below).

"Require review from Code Owners" is left off: card step 8 does not ask for it, and with Kirtan the only owner of `contracts/`, `apps/api/migrations/` and `apps/api/app/schemas/` it would make Kirtan approve his own contract parts (PD-G).

### Working agreement while protection is not enforced

- Merge only with **Rebase and merge** (the only method the repository allows), and only after the named reviewer's approval in GitHub and all six checks (`lint-types`, `unit`, `guards`, `attribution`, `audit`, `api`) green on the pull request's last commit.
- Never push to `main`; never force-push `main` or an approved branch.
- The planner checks every run report (SYNC REPORT) for the approval and the checks; the gate card IMP-199 audits every merged pull request for an approval and green checks.

### Operator's attribution test (IMD-61, pull request half)

| Item | Value |
| --- | --- |
| Pull request | https://github.com/het-lathiya/Group12/pull/4 (`gh pr list --state closed --head test/attribution-check` → number 4, state `CLOSED`, `mergedAt` null) |
| Failing run | https://github.com/het-lathiya/Group12/actions/runs/41225024521 (head `5510ece`, conclusion `failure`) |
| Red job | `attribution` fail, https://github.com/het-lathiya/Group12/actions/runs/41225024521/job/124607265965; the other five jobs pass |
| Rule line from the job log | `attribution: FAIL commit 5510ece rule co-authored-by failed: a line starts with 'Co-authored-by:' (one author per commit, IMD-61).` then `attribution: FAIL 1 problem(s) in 8 commit(s) of 4e4a7fe..5510ece and the pull request body` |
| Remote branch | `git ls-remote --heads origin test/attribution-check` printed nothing (deleted) |

### Throw-away pull request A: TC-343 and TC-002

Branch `test/tc-343-failing-test` from `origin/feat/IMP-102-whole-task`, one commit `f1547f3` by Kirtan (author and committer), adding `apps/api/tests/unit/test_throwaway_failing.py` (`assert 1 + 1 == 3`) and `apps/api/app/trips/throwaway.py` (`from google import genai`, typed so ruff and mypy accept it).

Local check before the push: `make lint` exit 0 (`All checks passed!`, `25 files already formatted`); `make typecheck` exit 0 (`Success: no issues found in 14 source files`); `make imports` exit 2 (`Contracts: 2 kept, 1 broken.`); `make test-unit` `1 failed, 20 passed in 0.20s`.

Pull request https://github.com/het-lathiya/Group12/pull/5, "test: TC-343 failing test and TC-002 planted import (do not merge)", run https://github.com/het-lathiya/Group12/actions/runs/41225650545:

| Job | Conclusion | Job URL | Result line from the log |
| --- | --- | --- | --- |
| `lint-types` | **fail** | https://github.com/het-lathiya/Group12/actions/runs/41225650545/job/124609126238 | `All checks passed!` and `Success: no issues found in 14 source files` (lint and types pass), then `Vendor isolation: google (google.genai) only in app.ai.providers.gemini BROKEN`, `Contracts: 2 kept, 1 broken.`, `app is not allowed to import google:` `-   app.trips.throwaway -> google (l.3)`, `make: *** [Makefile:99: imports] Error 1` |
| `unit` | **fail** | https://github.com/het-lathiya/Group12/actions/runs/41225650545/job/124609126150 | `FAILED tests/unit/test_throwaway_failing.py::test_throwaway_fails_on_purpose - assert (1 + 1) == 3`, `1 failed, 20 passed in 0.13s` |
| `attribution` | pass | https://github.com/het-lathiya/Group12/actions/runs/41225650545/job/124609126287 | (green as expected) |
| `guards`, `audit`, `api` | pass | same run | |

`gh pr view 5 --json mergeStateStatus,mergeable` → `{"mergeStateStatus":"UNSTABLE","mergeable":"MERGEABLE"}` (not `BLOCKED`: protection is not enforced). Closed unmerged with `gh pr close 5 --delete-branch` (remote and local branch deleted).

### Throw-away pull request B: TC-354

Branch `test/tc-354-fake-secret` from `origin/feat/IMP-102-whole-task`, one commit `fbbde87` by Kirtan, adding `apps/api/tests/fixtures/throwaway_fake_secret.txt` with `throwaway_service_api_key = "<40 random letters and digits>"`, generated with Python `secrets` for this test; it is not a real key of any service. The rule chosen is gitleaks `generic-api-key`, which is not a GitHub partner pattern, so push protection was not involved; the push was accepted.

Local check before the push (gitleaks 8.30.1 docker image): `gitleaks dir <file> --redact -v` → `RuleID: generic-api-key`, `leaks found: 1`; `gitleaks git --log-opts="--no-merges origin/feat/IMP-102-whole-task..HEAD" --redact` → `leaks found: 1`.

Pull request https://github.com/het-lathiya/Group12/pull/6, "test: TC-354 fake secret (do not merge)", run https://github.com/het-lathiya/Group12/actions/runs/41225694860:

| Job | Conclusion | Job URL | Result line from the log |
| --- | --- | --- | --- |
| `guards` | **fail** | https://github.com/het-lathiya/Group12/actions/runs/41225694860/job/124609254642 | `RuleID: generic-api-key`, `8 commits scanned.`, `leaks found: 1` |
| `lint-types`, `unit`, `attribution`, `audit`, `api` | pass | same run | |

`gh pr view 6 --json mergeStateStatus,mergeable` → `{"mergeStateStatus":"UNSTABLE","mergeable":"MERGEABLE"}`. Closed unmerged with `gh pr close 6 --delete-branch`. Afterwards `git ls-remote --heads origin 'test/*'` printed nothing; neither throw-away commit is on any remaining branch.

### Board (card step 7)

- Project: https://github.com/users/het-lathiya/projects/1 ("Group12 delivery board", owner `het-lathiya`), linked to `het-lathiya/Group12` with `gh project link 1 --owner het-lathiya --repo het-lathiya/Group12` (exit 0).
- Labels created: `sprint-1` to `sprint-8`, `points-0` to `points-6` (none existed).
- Issues: one per row of `docs/progress/board-issues.md`, title as the row, assignee the part owner, labels `sprint-N` and `points-X`, one-line body naming the card, part and owner with "See docs/spec/TASK_REGISTER.md". Numbers #7 to #189 (#1 to #6 are pull requests); the Issue column of `board-issues.md` holds each number.
- The import skipped any title that already existed and any issue already in the project, and paused 2 s after each creation. It ran in four parts: the first stopped on a network error (`read: connection timed out`) after 21 confirmed creations; the rerun found the 22nd issue already created and added it without a duplicate. No GitHub rate limit was hit.
- Closed: #7 (IMP-101 repo-tree-makefile, comment "Merged via PR #1.") and #8 (IMP-101 api-pyproject-guard, comment "Merged via PR #2.").

Counts read back from GitHub (`gh issue list --state all --limit 500` and `gh project item-list 1 --owner het-lathiya --limit 300 --format json`):

| Item | Count |
| --- | --- |
| Issues | 183 (183 distinct titles; 181 open, 2 closed) |
| Items in the project | 183 |
| Every issue has one assignee, one `sprint-N` and one `points-X` label | yes |

| Sprint | Issues | Points |
| --- | --- | --- |
| 1 | 21 | 47 |
| 2 | 19 | 46 |
| 3 | 18 | 57 |
| 4 | 25 | 61 |
| 5 | 25 | 63 |
| 6 | 30 | 75 |
| 7 | 33 | 62 |
| 8 | 12 | 16 |
| **Total** | **183** | **427** |

| Assignee | Issues | Points |
| --- | --- | --- |
| Assassin-byte (Krrish) | 22 | 43 |
| het-lathiya (Het) | 20 | 43 |
| jeelfefar2141 (Jeel) | 18 | 43 |
| Junaid-Kureshi (Junaid) | 19 | 43 |
| kirtan-S111 (Kirtan) | 23 | 43 |
| Malhar1112-v (Malhar) | 16 | 42 |
| manalPatel2557 (Manal) | 15 | 42 |
| Manasvi1704 (Manasvi) | 17 | 43 |
| manyarana (Manya) | 16 | 42 |
| Nidhi9864 (Nidhi) | 17 | 43 |

### RUN-003b commands on `feat/IMP-102-whole-task`

| Command | Result line (quoted exactly) |
| --- | --- |
| `make check` (after the board-list commit, with this record's edits) | `No test files found, exiting with code 0` (exit 0; `All checks passed!`, `Success: no issues found in 13 source files`, `Contracts: 3 kept, 0 broken.`, `openapi-check: not yet implemented (IMP-214)`, API unit `20 passed in 0.18s`) |

The commit that adds this record starts a new run on PR #3; its results are reported in the run's SYNC REPORT.

## Not run

| Command | Reason |
| --- | --- |
| Reading the branch protection rule through the API | `HTTP 403` "Upgrade to GitHub Pro or make this repository public to enable this feature." (above) |
| Branch protection and merge settings screenshots | Not supplied by the operator; API output recorded instead |
| `make db-migrate` against a real database (TC-337) | `db-migrate: not yet implemented (IMP-106)`; the `api` job runs it and becomes meaningful after IMP-106 |
| `make openapi-check` in the guards job (§13.7) | `not yet implemented (IMP-214)`; IMP-214 extends ci.yml with it (§4.1) |
| `ci.yml` build job (§13.7, TC-338) | Not in this card's six jobs; it comes with the deployment card |
| `make e2e` | The part touches no journey |

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| Hook refuses a `Co-authored-by:` message and the tool and vendor words; accepts the allowed paths (IMD-61, local half) | verified | Hook test table above; also refused through `git commit` with `core.hooksPath=.githooks` (RUN-003) |
| IMD-61: a pull request with a `Co-authored-by:` commit fails the attribution check | verified | Operator's PR #4, run 41225024521: `attribution` fail with `rule co-authored-by`; closed unmerged, branch deleted |
| IMD-61: a non-team author email fails the attribution check | verified (local run) | Attribution script table above (RUN-003), rule `team-email`; not repeated on a pull request |
| TC-343: a failing unit test gives a red required check | verified | PR #5, run 41225650545: `unit` fail, `1 failed, 20 passed in 0.13s` |
| TC-343: the pull request cannot be merged | not verified | `mergeStateStatus` `UNSTABLE`, `mergeable` `MERGEABLE`, not `BLOCKED`: branch protection is not enforced on this plan; the rule is followed by agreement (card step 8, working agreement above) |
| TC-354: a fake key matching a gitleaks rule fails the guards job | verified | PR #6, run 41225694860: `guards` fail, `RuleID: generic-api-key`, `leaks found: 1` |
| TC-002: a `google.genai` import outside `app/ai/providers/gemini.py` fails `make imports` | verified | Local scratch copy (RUN-003) and CI: PR #5 `lint-types` passes lint and types and fails at `make imports` with `Contracts: 2 kept, 1 broken.` (`app.trips.throwaway -> google (l.3)`) |
| The six jobs exist with the exact names and are green on this pull request | verified | Runs 41223146687 (head `958a414`) and 41223394094 (head `3e8adfc`): all six pass |
| Branch protection settings match step 8 | not verified | Rule saved by the admin but "Not enforced" (operator); API `HTTP 403` plan error, values not readable; no screenshot |
| Repository settings allow Rebase and merge only | verified (API output; no screenshot) | `{"allow_merge_commit":false,"allow_rebase_merge":true,"allow_squash_merge":false}` |
| All ten members are collaborators | verified | Collaborator list above (RUN-003); no pending invitations |
| The board holds one issue per task part with owner, sprint and points labels | verified | https://github.com/users/het-lathiya/projects/1: 183 issues, 183 project items, one assignee and one `sprint-N` and `points-X` label each; per-sprint and per-assignee counts match `board-issues.md` and §14.3 (tables above). The export is in this record, not in `docs/progress/sprint-1.md`, which this run does not edit |
| TC-337: the api job applies migrations to a blank PostgreSQL | not verified | Meaningful after IMP-106 |

## Blockers

None.

## Proposed decisions

- PD-G (CODEOWNERS second owner): §14.4 and card step 5 ask for "Kirtan plus one other owner" on `contracts/`, `apps/api/migrations/` and `apps/api/app/schemas/`. CODEOWNERS cannot require two approvals from listed owners (any one listed owner satisfies it) and the specification names no second owner, so only Kirtan is listed. Options for the team: name a second owner and require two approvals in branch protection for those paths by agreement, or accept one code-owner approval plus the named reviewer. "Require review from Code Owners" stays off until the team decides, so that Kirtan never has to approve his own contract parts.
- PD-H (pip-audit scope): the blocking audit covers every installed API dependency (runtime and dev) at its installed version, taken from `pip freeze --exclude-editable`; it leaves out the venv's own `pip`, which `python -m venv` copies from the interpreter and which is not a project dependency. The venv's `pip` is audited in a report-only step so the finding stays visible. Making it blocking needs `make setup` to upgrade pip in the venv (for example `python -m venv --upgrade-deps`), a Makefile change outside this part.
- PD-I (attribution rule wording): the hook and CI script apply card step 4 exactly (a line starting with `co-authored-by:`; the two tool words as whole words). The before-push perl check of CLAUDE.md §12 is broader (it also flags `co-authored-by` anywhere in a line, and the vendor word inside longer words). Anything that passes the perl check passes the hook, so there is no conflict in practice; the team may align the wording in a decision run.
- PD-J (`api` job database URL): `make db-migrate` reads `DATABASE_URL` (§4.7), so the job sets both `DATABASE_URL` and `TEST_DATABASE_URL` to the §4.7 test default. No variable name is new.
- PD-K (branch protection on this plan): the classic rule is saved but not enforced on a private repository of a personal account. Options: keep the working agreement above (card step 8) with the IMP-199 audit, move the repository to a GitHub Team organization, or make it public. Until then TC-343's "cannot be merged" half stays not verified.

## Open issues

- pip-audit of the whole venv reports 12 advisories in its own `pip` (locally `pip 24.0`, in CI `pip 25.0.1`; IDs PYSEC-2026-1795, -1796, -196, -2875, -2876, -3721; fixed in pip 25.3 to 26.2). The project dependencies have none. See PD-H.
- `unit` also runs `make test-contract` (§13.7 lists it; the card step lists `make test-unit` and `make test-web`). §13.7's coverage report is not added: no coverage tool is in the dependencies.
- `guards` does not repeat `make imports`: the provider-isolation import rule already runs in `lint-types` as `make imports`.
- The `edited` trigger re-runs every job when the title or body of a pull request changes; it is what lets the attribution check see body edits.
- `git commit -v` passes the diff to the hook; a diff line containing a tool word would then be refused. Commit without `-v` or reword.
- Branch protection is not enforced (PD-K): GitHub does not block a merge with red checks or without approval; the working agreement and the IMP-199 audit replace it.
- The board, its issues and the throw-away and attribution pull requests are created from the operator's GitHub account (`het-lathiya`); the commits are authored and committed by Kirtan.
- Issue numbers start at #7 because #1 to #6 are pull requests (issues and pull requests share numbering).
- `docs/progress/board-issues.md` and this record are not Prettier-formatted (table padding); `make lint` checks only `apps/web`, and the files were already in this state on the branch before RUN-003b.
- The board export and the protection status are recorded here; copying them into `docs/progress/sprint-1.md` is left to the gate card, which compiles that file.

## After this run

1. Reviewer (Junaid): review PR #3; merge with Rebase and merge after approval and six green checks (working agreement).
2. Team: decide PD-G and PD-K in a decision run.
3. Gate IMP-199: copy the board counts and the protection status into `docs/progress/sprint-1.md`; audit every merged pull request for an approval and green checks.
4. After IMP-106 merges: confirm the `api` job applies the migrations to a blank PostgreSQL (TC-337).
