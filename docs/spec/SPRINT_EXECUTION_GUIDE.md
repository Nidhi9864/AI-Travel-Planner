# SPRINT_EXECUTION_GUIDE — AI Travel Planner

The reusable procedure for executing a task and a sprint with Claude Code. Section references (§N) point to the implementation specification; the task cards are in `TASK_REGISTER.md`; gates and the dependency lanes are reproduced at the end of this guide.

This section is the operating procedure for every Claude Code session on the project. It is also published as `docs/spec/SPRINT_EXECUTION_GUIDE.md`; the prompts that start a session are in the task prompt below and the sprint prompt below.

## 1. Inputs Claude Code reads, in this order

| Order | Input | Why |
| --- | --- | --- |
| 1 | `CLAUDE.md` (CLAUDE.md) | Stack, layout, rules, commands, Definition of Done |
| 2 | The task card in `docs/spec/TASK_REGISTER.md` (same content as §10) | Objective, prerequisites, files, steps, interfaces, acceptance criteria, tests, evidence |
| 3 | The contract sections the card's interfaces name: §3 (module), §5 (tables), §6 (endpoints), §7 (screens), §8 and §9 (AI and deterministic rules), §13 (tests), and `docs/spec/AMENDMENT_A1_AWS_RAG.md`, which wins where it differs | The shapes that must not change |
| 4 | `docs/progress/parts/` (one record per merged part), `docs/progress/sprint-N.md` (sprint index) and `docs/progress/gates.md` | What is done, blocked or waiting |
| 5 | `docs/spec/DECISION_REGISTER.md` | Provisional defaults and any decision that changed a contract |
| 6 | The repository itself: the files the card lists and their neighbours, existing tests, `Makefile`, `.env.example` | What already exists; never assume |

## 2. Procedure for one task

1. **Receive.** The run prompt (written by the planner, Appendix D) names one run ID, one task ID, the part to build (the card's "Owners and parts" row), the member who owns it with their git name and email, and the reviewer. Read the card and the inputs of §11.1. Restate the objective, the part's scope and the acceptance criteria it must satisfy in two or three lines.
2. **Check prerequisites.** Every prerequisite task must be `done` in `docs/progress/`; every named contract must exist in the code or the specification. If one is missing, stop and report a blocker (§11.5); do not build the missing piece unless it is a trivial, clearly implied part of this task. A prerequisite that is an extension or cut-list feature switched off by a recorded decision counts as satisfied for gate and test cards, which skip its checks with the reason; when an extension card needs a shared piece of a switched-off extension (the assist-call log of IMP-613), it builds that piece itself as IMD-60 says.
3. **Inspect.** List the files the card names and confirm which exist. Read existing code in the module, its tests and the shared schemas before writing. If the repository structure differs from §4, follow the repository and report the difference.
4. **Detect conflicts.** Compare the card with the code and the contracts. A conflict (a different field name, a missing table, an endpoint that already returns another shape) is reported before coding, with a proposed resolution. Small, obviously compatible additions (an extra index, a helper) are allowed and listed in the report.
5. **Plan.** Write a short plan: files to create or modify, in order; tests to write first or alongside.
6. **Implement.** Follow the card's steps in order, limited to the named part on a shared card; another member's part is used through its contract (stub, generated client or MOCK) and is never built in its place. Reuse existing modules, schemas, error codes, labels and names. Write real behaviour, not placeholders: no TODO stubs in code paths the acceptance criteria exercise.
7. **Test.** Write or update the tests the card lists. Run, in this order, the card's test commands, then `make lint`, `make typecheck`, `make imports`, then `make test` (and `make openapi-check` if the API changed, `make e2e` if a journey changed). Fix every failure your change caused; re-run until green.
8. **Verify the criteria.** Walk through each acceptance criterion and point to the test or observation that shows it. A criterion that needs something unavailable (a real key, a deployed URL, a human session) is marked "not verified" with the reason.
9. **Record and commit.** Create the part record `docs/progress/parts/IMP-NNN-<part-slug>.md` (run ID, owner, status, base commit, changed files, commands with their result lines, acceptance criteria with verified or not verified, blockers, proposed decisions, open issues). Blockers and proposed decisions are recorded there and in the SYNC REPORT only; the decision register is changed by a separate decision run once the team has decided. Commit as the part owner (CLAUDE.md §12), run the two attribution checks, push the branch and open the pull request with the owner as assignee and the named reviewer. Never merge.
10. **Report and stop.** Print the SYNC REPORT of §11.4 and stop at the part boundary. Do not start another part.

## 3. Rules that apply to every task

- Implement only the selected task and what it strictly needs. Do not refactor unrelated code, rename public items, or rewrite modules from scratch.
- Never change a contract silently: endpoints, request and response shapes, tables and columns, finding and error codes, labels, environment variable names, file layout and commands are changed only through a reported proposal and, once approved, in the same pull request as the specification registers.
- Never report a test as passing unless it ran and passed in this session (or in a CI run you can link). Quote the command and its summary line. "Should pass" is not evidence.
- Never fabricate data: no invented prices, hours, places, routes, evaluation numbers, user findings or screenshots. SAMPLE fixtures are labelled SAMPLE everywhere.
- Never call Gemini in automated tests; use MOCK scenarios or recorded responses. Never print or commit secrets.
- When a decision is genuinely open and blocks the task, apply the Provisional default from Appendix B if one exists; otherwise stop and report.

## 4. Report format at the end of a run: the SYNC REPORT

Every run ends with the SYNC REPORT block defined in `CLAUDE.md` §14 (reproduced in Appendix D.4), printed exactly, so that the planner can check it and update its ledger. It carries the run, card, part and owner; the status (`PR_OPEN`, `BLOCKED`, `TESTS_FAILING`, `PARTIAL`, `NO_CHANGE`); the branch, base and head commits; every commit with its author and committer; the result of the attribution check; the pull request and reviewer; the changed files, contracts and migrations; each command with its exact result line; the commands not run and why; each acceptance criterion with verified or not verified and how; blockers; proposed decisions; and the path of the part record.

## 5. Blockers

A blocker is reported, not worked around, when: a prerequisite task is not done; a contract in the card contradicts the code or another section; an account, key, dataset or human decision is missing; or the task cannot meet an acceptance criterion without changing scope. The report names the blocker, what was done up to that point, and the smallest decision or input that would unblock it. Partial work is committed only if it leaves `make check` green and is marked `blocked` in its part record.

## 6. Procedure for a sprint

A sprint is driven by the planner (Appendix D), one part per Claude Code run; Claude Code is never asked to run a whole sprint unattended.

1. **Start.** The planner reads the sprint section of §10, its gate in §14, the dependency map and the sprint's column of the team load table (§14.3), and confirms that the previous gate is recorded as passed or that its open items have owners.
2. **Order.** Parts run in an order that respects prerequisites (§14.2 lists the waves); the backend, database or AI part of a card comes before its screen part. CODE parts are implemented by Claude Code; DATA, HUMAN and VERIFY parts are prepared by Claude Code (imports, checks, templates, checklists) and closed by the named member with evidence.
3. **Per part.** One run applies §11.2: one branch `feat|fix|chore/IMP-NNN-<part-slug>`, commits authored by the part's owner, one part record, one pull request titled like `IMP-409 · move-controls part`, then the SYNC REPORT. The named reviewer approves and the operator merges with Rebase and merge.
4. **Integrate.** After each merge `make check` on `main` must stay green; a red `main` stops new parts until the owner of the breaking change fixes it.
5. **Close.** The gate card (IMP-N99, or the gate task named in §14) compiles `docs/progress/sprint-N.md` from the part records, checks each gate criterion with evidence in `docs/progress/gates.md`, and moves unfinished parts, with a reason, to the next sprint or the deferred list. A sprint is never complete because code was generated; it is complete when the application builds, the relevant tests ran and passed, and the integrated behaviour was verified.

## 7. Planner and executor

The implementation is run by two assistants kept in step through the repository. A planner (a Claude chat that holds this specification, the task register, the decision register and the team plan) writes one prompt per part; Claude Code executes it in the repository and ends with the SYNC REPORT; the operator carries the prompt in one direction and the report in the other, approves through the reviewer and merges. The repository is the source of truth: merged pull requests and the part records in `docs/progress/parts/` decide what is done, and a read-only RESYNC run rebuilds the planner's ledger from them whenever the two disagree. The full protocol, its diagrams and the planner prompt are in Appendix D.

## 7. Prompt template: one run (one task part)

```text
=== RUN <RUN-ID> · <IMP-NNN> <card title> · part: <part-slug> (<points> pts) · Sprint <N>, wave <W> · <NEW | FIX of RUN-xxx | CONTINUE step k of n> ===

You are working on the AI Travel Planner repository as <Member>, <Role title>. Everything you commit in this run is authored and committed by <Member>.

IDENTITY (pass it to every git command that writes history; never set user.name or user.email in git config):
  GIT_NAME="<Git author name>"   GIT_EMAIL="<Git author email>"   GITHUB_USER="<github-username>"
  Commit:  git -c user.name="$GIT_NAME" -c user.email="$GIT_EMAIL" commit -m "<message>"
  Rebase:  git -c user.name="$GIT_NAME" -c user.email="$GIT_EMAIL" rebase origin/main   (then git push --force-with-lease, only on this branch and only before approval)
  No Co-authored-by lines. No mention of Claude, Claude Code or Anthropic, and no statement that an AI wrote or helped, in commits, branch, PR title or body or code comments (the paths CLAUDE.md and .claude/ are fine).

READ FIRST: CLAUDE.md · docs/spec/TASK_REGISTER.md card <IMP-NNN> (copy its steps, acceptance criteria and test commands from there, exactly) · docs/spec/IMPLEMENTATION_SPEC.md <§ list from the card's interfaces> · docs/spec/DECISION_REGISTER.md <IMD list if relevant> · docs/progress/parts/ (records of the prerequisites)

PREFLIGHT (stop with status BLOCKED and the SYNC REPORT if any check fails):
  1. git fetch origin; git status --porcelain --untracked-files=no prints nothing (untracked files are fine). Record the base commit: git rev-parse --short origin/main.
  2. Prerequisites are merged on main: <for each prerequisite: IMP-NNN part — the concrete evidence to check, e.g. its part record docs/progress/parts/IMP-NNN-<slug>.md or a file path that must exist>.
  3. Attribution guard: if .githooks/commit-msg exists, run git config core.hooksPath .githooks; otherwise make sure the local guard from RUN-000 is in .git/hooks/commit-msg.
  4. Branch: NEW run: git switch main && git pull --ff-only && git switch -c <feat|fix|chore>/<IMP-NNN>-<part-slug>. FIX or CONTINUE run: git switch <existing branch> && git pull --ff-only, and rebase on origin/main as IDENTITY says if the pull request shows a conflict.

YOUR PART (build only this): "<part text from Owners and parts>"   (a single-owner card uses the slug whole-task)
Other parts of this card belong to <members>; use them only through their contracts (generated client, stubs, MOCK). Do not create or edit their files: <list>.

FILES: <create/modify list from the card, limited to this part>
STEPS: the card's steps <numbers> that belong to this part, taken from the task register; <for a step shared with another part: which half is this part's and which member does the other half>
CONTRACTS THAT MUST NOT CHANGE: <endpoints, schemas, tables, codes, env vars this part touches, with § refs>
ACCEPTANCE (this part's share of the card): <criterion IDs: FR-xxx ACn, TC-xxx, and the card's criteria by number>
TESTS TO WRITE AND RUN: the card's test files and commands for this part; then make lint, make typecheck, make imports, make test<, make openapi-check if the API changed><, make e2e ARGS='--grep <tag>' if a journey changed>.
EVIDENCE: create docs/progress/parts/<IMP-NNN>-<part-slug>.md with: run id, owner, status, base commit, files changed, commands run with their result lines, acceptance criteria with verified/not verified and how, blockers and proposed decisions, open issues. Do not edit docs/progress/sprint-N.md or the decision register in a part run.

COMMITS (suggested): <2-6 Conventional Commit messages starting with IMP-NNN>
BEFORE PUSH: run the two attribution checks of CLAUDE.md §12 and repair your own new commits if needed.
PUSH AND PR (NEW run; a FIX or CONTINUE run only pushes, except the last CONTINUE step, which opens the PR):
  git push -u origin <branch>
  write the PR body to a temporary file outside the repository (BODY=$(mktemp)) from .github/pull_request_template.md when it exists: linked IDs, what changed, tests run with results, screenshots for UI, contract changed?, migration?, part owner and reviewer
  gh pr create --base main --head <branch> --title "<IMP-NNN> · <part-slug> part" --assignee <owner GitHub user> --reviewer <reviewer GitHub user> --body-file "$BODY"
  Do not merge.

STOP CONDITIONS: a prerequisite missing; a contract conflict; a needed account, key or dataset missing; acceptance impossible without changing scope; main red for reasons outside this part. In each case stop, keep make check green on your branch (or commit nothing), and report.

FINISH: print the SYNC REPORT exactly in the format of CLAUDE.md §14 and stop. Do not start another part.
```

## 8. Prompt template: read-only state check (RESYNC)

```text
=== RESYNC · read-only state dump (no commits, no edits) ===
In the repository root, run git fetch --all --prune, then print a STATE REPORT:
<<<STATE-REPORT
main_head: <sha> <date> <subject>
merged_parts: one line per docs/progress/parts/*.md on main: <file> | owner | status
main_commits_by_author: git shortlog -sne origin/main
recent_main: git log origin/main -n 40 --format='%h|%an|%ae|%s'
open_prs: gh pr list --state open --json number,title,headRefName,author,assignees,reviewRequests,reviewDecision,statusCheckRollup (one line each)
merged_prs_last_50: gh pr list --state merged -L 50 --json number,title,mergedAt (one line each)
alembic_heads: (cd apps/api && alembic heads) or "not available yet"
checks: result line of make check on main, or the reason it cannot run
STATE-REPORT>>>
Stop after printing.
```

## 9. Sprint gates and dependency lanes

**Rule.** No sprint is complete merely because code has been generated. A sprint is complete only when the application builds from a clean clone, the tests named by the sprint's tasks and gate have run and passed (in CI or in a recorded local run), and the integrated behaviour has been demonstrated on the stated environment. Each gate is executed by its VERIFY task (IMP-N99; the journey check IMP-414 feeds SG-4) and recorded in `docs/progress/gates.md` with the date, the commit SHA, each criterion as met or not met, and a link to its evidence. A criterion without linked evidence counts as not met. None of the gates has been reached yet.

### 9.1 Sprint gates

Severities follow IMD-41: severity 1 blocks a journey or exposes data; severity 2 breaks a requirement with no workaround; severity 3 has a workaround; severity 4 is cosmetic. Severity 1 and 2 defects in the gate's scope block every gate.

| Gate | Demonstrably working (environment) | Contracts that must be stable | Tests that must pass | Acceptable known defects | Evidence |
| --- | --- | --- | --- | --- | --- |
| SG-1 end of week 1 | Clean clone: `make setup`, `make stack-up`, `make db-up`, `make db-migrate`, `make seed`, `make api`, `make web` work; sign-up, sign-in and sign-out on the local stack; staging `/health` returns 200 or the deployment is recorded as blocked by missing accounts (local) | Repository layout (§4), env names and `.env.example`, Makefile targets, migrations 0001-0006, ModelProvider interface and AI schemas gr-1 and io-1, error envelope | `make check` (lint, types, imports, unit, contract, api incl. drift test) | Staging blocked by accounts, with owner and date | CI run on main; gate entry; screenshot of local sign-in |
| SG-2 end of week 2 (blueprint Gate 1) | A signed-in user creates a trip, generates with MOCK and sees the saved plan; a generation record exists; destination 1 loaded with its quality report; both Express services healthy, the release task run and migration 0007 applied (AWS staging, Amendment A1) | OpenAPI contract v1 tagged `contract-v1`; all 36 MVP endpoints declared (501 until built); trip, preference and generation shapes; Item `sources[]` (IMD-116) | `make check`, `make test-authz`, `make e2e ARGS='journey'` (skeleton), `make smoke` against staging | Unbuilt endpoints returning 501; UI polish | Tag, CI runs, smoke output, screenshot of the saved plan |
| SG-3 end of week 3 (blueprint Gate 2) | A Gemini-generated plan for a seeded trip, validated for schema and place IDs, times and totals recalculated by the backend, record naming provider, model and prompt version; `retrieval_mode = vector` with at least one cited passage shown on the itinerary page (ACC-19) and the retrieval time recorded (NFR-050) (AWS staging) | Provider error taxonomy, io-1 v1 (gr-2 and io-2 from IMP-316), generation status values, itinerary read shape, `ModelProvider.embed_texts` | `make check`, provider contract suite with recorded responses, `make smoke`; one recorded manual Gemini run | Warnings in the plan; quality not yet measured. If Gemini is unavailable: the slice is shown with MOCK and labelled so, cause recorded, owners named | Record of the Gemini run (generation ID, model ID), smoke output |
| SG-4 end of week 4 (blueprint Gate 3) | Sign-up to a saved, edited itinerary (E2E journey) on staging; provider failure yields the labelled rule-based plan; edits recalculate in one transaction; checkpoint held | Edit request and response shapes with `plan_revision`, finding codes, warning shape, cut-list switch names | `make check`, `make e2e ARGS='journey'`, failure tests at API level, `make smoke` | Features scheduled for Sprints 5 and 6 absent | Checkpoint arithmetic and decision (IMP-499), CI runs, journey recording |
| SG-5 end of week 5 | Staging GEMINI journey with the ranking explanation (IMP-515, extension) and repair, hours and budget checks, add, replace, lock, breakdown, map, caps and rate limits; first Gemini baseline recorded | Cost estimate shape, alternatives shape, rate-limit and cap behaviour | `make check`, `make e2e`, `make smoke`; provider contract suite for MOCK and recorded GEMINI | Severity 3 and 4 with owners | Gate entry, baseline run record (dataset, provider, SHA) |
| SG-6 end of week 6: MVP feature freeze | Optimise day order and packing (IMP-612, IMP-613) done with tests or switched off; every MVP and MVP-S requirement Done with tests or switched off by a recorded cut-list decision; zero 501 MVP routes (extension routes may return 501 until SG-7, IMD-37); floor journey green with all switches off and full journey with all on | All MVP contracts frozen; any change needs a decision entry | `make check`, `make e2e` with switches on and off, `make smoke` | Usability findings scheduled for Sprint 7 | `docs/progress/deferred.md`, freeze entry, CI runs |
| SG-7 end of week 7: release candidate and extension freeze | Every extension (IMP-708 to IMP-713, and any earlier one not yet done) done with tests or switched off and listed; zero 501 routes; ACC-01 to ACC-18 re-run on staging; security pass; accessibility and usability results recorded; final evaluation and cost report on the commit to be tagged; document set drafted | Release configuration for production | `make check`, `make e2e`, `make smoke`, authorization and security suites | Severity 3 and 4 listed in known limitations | Tag `v1.0-rc1`, acceptance record, reports in `docs/test-reports/` |
| SG-8 week 8: release and demo | Production deployment on AWS with GEMINI (CHK-24); RAG index built and retrieval report committed (CHK-25); deployed smoke tests; demo rehearsed; backup video and saved samples; final checklist CHK-01 to CHK-25 | None may change except severe defect fixes with regression tests | `make check`, `make e2e`, `make smoke` against production | Documented known limitations only | Tag `v1.0-mvp`, `docs/acceptance/final-checklist.md`, smoke output, video file |

**Contract stability rule.** Once a gate lists a contract as stable, changing it requires a Proposed entry in the decision register, the updated contract files (`contracts/`, migrations, §6 entry) and a passing contract test in the same pull request; the integration lead (Kirtan) approves.

### 9.2 Dependency map and parallel work

Within a sprint, tasks in the same wave have no prerequisite on each other and can be worked on in parallel by their owners; a wave starts when its prerequisites in earlier waves are merged. Tasks of a later wave may start against the agreed contracts (stubs, MOCK, fixtures) but are merged only after their prerequisites.

| Sprint | Wave | Tasks that can run in parallel (members) |
| --- | --- | --- |
| Sprint 1 | Wave 1 | IMP-101 (Kirtan, Het), IMP-113 (Kirtan, Junaid, Nidhi), IMP-114 (Junaid, Krrish), IMP-115 (Malhar) |
| Sprint 1 | Wave 2 | IMP-102 (Kirtan), IMP-103 (Manal), IMP-104 (Manasvi), IMP-105 (Malhar) |
| Sprint 1 | Wave 3 | IMP-106 (Malhar, Jeel), IMP-109 (Krrish), IMP-110 (Nidhi) |
| Sprint 1 | Wave 4 | IMP-107 (Jeel), IMP-108 (Het), IMP-111 (Manya), IMP-112 (Kirtan) |
| Sprint 1 | Wave 5 | IMP-199 (Kirtan) |
| Sprint 2 | Wave 1 | IMP-201 (Kirtan), IMP-202 (Jeel), IMP-203 (Manal), IMP-205 (Malhar, Jeel), IMP-207 (Manya), IMP-209 (Junaid), IMP-217 (Kirtan), IMP-219 (Het), IMP-311 (Malhar) |
| Sprint 2 | Wave 2 | IMP-204 (Manal), IMP-206 (Jeel, Malhar), IMP-208 (Nidhi), IMP-214 (Kirtan) |
| Sprint 2 | Wave 3 | IMP-210 (Het), IMP-212 (Manasvi), IMP-215 (Junaid), IMP-218 (Junaid, Manasvi) |
| Sprint 2 | Wave 4 | IMP-211 (Het) |
| Sprint 2 | Wave 5 | IMP-213 (Krrish) |
| Sprint 2 | Wave 6 | IMP-216 (Kirtan) |
| Sprint 2 | Wave 7 | IMP-299 (Kirtan) |
| Sprint 3 | Wave 1 | IMP-301 (Nidhi, Manya), IMP-303 (Manya), IMP-304 (Malhar, Jeel), IMP-307 (Junaid), IMP-310 (Junaid) |
| Sprint 3 | Wave 2 | IMP-302 (Kirtan), IMP-305 (Nidhi, Het, Krrish), IMP-312 (Nidhi) |
| Sprint 3 | Wave 3 | IMP-306 (Manya, Junaid), IMP-313 (Manal) |
| Sprint 3 | Wave 4 | IMP-308 (Manal, Het), IMP-314 (Krrish, Malhar), IMP-315 (Jeel) |
| Sprint 3 | Wave 5 | IMP-309 (Manasvi, Het) |
| Sprint 3 | Wave 6 | IMP-316 (Manya, Het) |
| Sprint 3 | Wave 7 | IMP-317 (Manasvi) |
| Sprint 3 | Wave 8 | IMP-399 (Nidhi) |
| Sprint 4 | Wave 1 | IMP-401 (Nidhi), IMP-402 (Malhar, Jeel), IMP-404 (Manal, Junaid), IMP-406 (Manya, Krrish), IMP-410 (Manal, Krrish), IMP-411 (Manal, Krrish), IMP-412 (Manasvi), IMP-413 (Manya) |
| Sprint 4 | Wave 2 | IMP-403 (Nidhi, Krrish), IMP-405 (Manasvi, Jeel), IMP-407 (Het), IMP-318 (Junaid) |
| Sprint 4 | Wave 3 | IMP-408 (Het, Manasvi), IMP-409 (Manasvi, Het) |
| Sprint 4 | Wave 4 | IMP-414 (Krrish, Junaid) |
| Sprint 4 | Wave 5 | IMP-499 (Kirtan) |
| Sprint 5 | Wave 1 | IMP-501 (Junaid, Manal), IMP-502 (Nidhi), IMP-503 (Manya, Manasvi), IMP-504 (Het, Malhar), IMP-505 (Het, Krrish), IMP-506 (Het, Krrish), IMP-507 (Manal, Manasvi), IMP-508 (Manasvi), IMP-509 (Jeel), IMP-510 (Manal, Krrish), IMP-511 (Kirtan), IMP-512 (Junaid), IMP-513 (Krrish), IMP-514 (Manya, Nidhi) |
| Sprint 5 | Wave 2 | IMP-515 (Jeel, Krrish) |
| Sprint 5 | Wave 3 | IMP-599 (Kirtan) |
| Sprint 6 | Wave 1 | IMP-601 (Het), IMP-602 (Manal, Manasvi), IMP-603 (Junaid, Manya, Kirtan), IMP-604 (Malhar, Manasvi, Jeel), IMP-605 (Jeel), IMP-606 (Malhar, Manya), IMP-608 (Manal, Krrish), IMP-609 (Krrish, Het), IMP-610 (Jeel, Malhar), IMP-611 (Junaid, Krrish), IMP-613 (Kirtan, Nidhi, Manya) |
| Sprint 6 | Wave 2 | IMP-607 (Het, Nidhi, Krrish), IMP-612 (Het, Junaid, Manasvi) |
| Sprint 6 | Wave 3 | IMP-699 (Kirtan) |
| Sprint 7 | Wave 1 | IMP-701 (Krrish), IMP-702 (Junaid, Het, Kirtan), IMP-705 (Nidhi), IMP-708 (Nidhi, Manya, Manal, Manasvi), IMP-709 (Nidhi, Het, Manya), IMP-710 (Manal, Malhar, Krrish), IMP-711 (Manasvi, Het), IMP-712 (Junaid, Jeel, Krrish), IMP-713 (Malhar, Jeel, Kirtan) |
| Sprint 7 | Wave 2 | IMP-703 (Krrish), IMP-706 (Manya), IMP-707 (Malhar, Manal, Junaid, Jeel, Kirtan) |
| Sprint 7 | Wave 3 | IMP-704 (Manasvi, Junaid) |
| Sprint 7 | Wave 4 | IMP-799 (Kirtan) |
| Sprint 8 | Wave 1 | IMP-801 (Kirtan, Nidhi), IMP-804 (Malhar, Jeel, Manya) |
| Sprint 8 | Wave 2 | IMP-802 (Junaid, Kirtan, Nidhi, Manasvi) |
| Sprint 8 | Wave 3 | IMP-803 (Malhar, Jeel) |
| Sprint 8 | Wave 4 | IMP-899 (Kirtan) |


Cross-sprint prerequisites of CODE tasks are listed below; a task whose earlier-sprint prerequisite is not done is blocked and reported, never re-implemented.

| Task | Title | Needs from earlier sprints |
| --- | --- | --- |
| IMP-201 | Readiness endpoint and structured request logging with request IDs | IMP-106, IMP-103 |
| IMP-202 | Generation record repository and lifecycle helpers (ai_generations) | IMP-106 |
| IMP-203 | Trips API: create, list and read a trip with validation | IMP-106, IMP-108, IMP-107 |
| IMP-205 | Provenance-preserving place import with quality gate, categories and destinations API | IMP-107 |
| IMP-207 | Mock provider with scenario-based failure injection | IMP-110 |
| IMP-208 | Provider factory and configuration-based selection | IMP-103 |
| IMP-209 | Distance-based travel-time estimate (pure) | IMP-106 |
| IMP-210 | Walking-skeleton generation job: start and poll with MOCK, save a validated plan | IMP-111 |
| IMP-212 | Trip wizard and preference form | IMP-109 |
| IMP-214 | OpenAPI contract v1 export, generated web client and contract check | IMP-110 |
| IMP-215 | Two-user authorization suite for every owned route | IMP-108, IMP-106 |
| IMP-216 | Walking-skeleton end-to-end test and staging deployment | IMP-112 (through IMP-217 and IMP-218, Amendment A1) |
| IMP-217 | AWS staging foundation: RDS PostgreSQL, ECR, SSM, ECS Express services, OIDC deploy role and budget | IMP-112, IMP-113 |
| IMP-219 | Supabase Auth with an AWS database: auth stub bootstrap and user row mirroring | IMP-106, IMP-108 |
| IMP-311 | RAG store: pgvector, corpus and chunk tables, item citations and retrieval record (migration 0007) | IMP-106 |
| IMP-301 | Gemini adapter with structured output, error mapping and recorded-response tests | IMP-208, IMP-113, IMP-111 |
| IMP-302 | Provider metadata and health in readiness | IMP-201 |
| IMP-303 | Normalized generation request and prompt content and size control | IMP-204, IMP-111 |
| IMP-304 | Candidate retrieval, hard-constraint filters and ranking | IMP-204, IMP-206 |
| IMP-305 | Full generation pipeline through the active provider with job progress | IMP-210 |
| IMP-307 | OpenRouteService client with route cache and fallback | IMP-209 |
| IMP-309 | Day-wise itinerary view with labels | IMP-213 |
| IMP-312 | Embedding operation on ModelProvider: Gemini and deterministic MOCK embeddings | IMP-207, IMP-208 |
| IMP-313 | Corpus ingestion and indexing: place and guide documents, chunking, embedding, `make rag-index` | IMP-311, IMP-205 |
| IMP-316 | Grounded generation: passages in the request, validated citations, saved sources | IMP-214 |
| IMP-401 | Retries with backoff and circuit breaker in the Gemini adapter | IMP-301 |
| IMP-402 | Rule-based fallback planner and saved sample itineraries | IMP-304, IMP-209 |
| IMP-403 | Provider failure, timeout and quota handling end to end with fallback notice | IMP-305 |
| IMP-404 | Validator: overlaps, travel gaps, missing constraints and invalid references | IMP-308 |
| IMP-405 | Structured warnings with suggested fixes, persisted with the plan, warnings panel | IMP-202 |
| IMP-406 | Preserve explicit constraints and must-visit places; label AI-written text | IMP-305 |
| IMP-407 | Edit transaction core: recalculate and revalidate every edit atomically with plan revision | IMP-308 |
| IMP-408 | Remove an activity and change start time or duration | IMP-309 |
| IMP-409 | Reorder by drag and by keyboard | IMP-309 |
| IMP-410 | Drafts and reopening the latest saved itinerary | IMP-212, IMP-211 |
| IMP-411 | Transport allowance, stay budget and price source labels | IMP-308 |
| IMP-412 | Loading, empty and error states on every MVP screen | IMP-104 |
| IMP-413 | Evaluation harness (command line) | IMP-310, IMP-207 |
| IMP-318 | Retrieval evaluation: recall, hit rate, citation validity and grounding rate | IMP-316, IMP-314 |
| IMP-501 | Opening-hours check, overpacked days and budget conflicts | IMP-404, IMP-308 |
| IMP-502 | Bounded repair with at most one model retry | IMP-405, IMP-403 |
| IMP-503 | Pace presets and grouping nearby places into days | IMP-304, IMP-209 |
| IMP-504 | Add a user-selected place and reject stale edits | IMP-407 |
| IMP-505 | Replace an activity with a ranked alternative | IMP-407, IMP-304 |
| IMP-506 | Lock and unlock items | IMP-407 |
| IMP-507 | Daily and category cost breakdown; estimate labels on every screen | IMP-411 |
| IMP-508 | Map with numbered markers and list fallback | IMP-309 |
| IMP-509 | Browse places with source labels | IMP-205, IMP-206 |
| IMP-510 | Edit trip settings and flag a stale plan | IMP-203, IMP-212 |
| IMP-511 | Rate limits and daily generation caps | IMP-202, IMP-201 |
| IMP-512 | Provider contract test suite for all adapters | IMP-401, IMP-207 |
| IMP-513 | Keyboard and assistive-technology support | IMP-412 |
| IMP-515 | Explain the ranking: "Why this place?" panel | IMP-304 |
| IMP-601 | Profile page and API | IMP-109, IMP-214 |
| IMP-602 | Trip dashboard with rename, duplicate, archive and delete | IMP-410 |
| IMP-604 | Search, filters and place detail with labelled facts | IMP-509, IMP-411 |
| IMP-605 | Saved places (wishlist) | IMP-509 |
| IMP-606 | Food places and meal slots | IMP-305, IMP-503 |
| IMP-607 | Regenerate one day around locks and the whole itinerary | IMP-506, IMP-305, IMP-502 |
| IMP-608 | Budget alerts and contingency buffer | IMP-507, IMP-501 |
| IMP-609 | Final trip summary and print view | IMP-309, IMP-507 |
| IMP-610 | Itinerary versions: save, list and restore | IMP-407 |
| IMP-612 | Optimise day order to cut travel time | IMP-407, IMP-307, IMP-506 |
| IMP-613 | Packing checklist with AI free-text refinement | IMP-110, IMP-111, IMP-207, IMP-301 |
| IMP-701 | End-to-end regression suite for all primary scenarios | IMP-699, IMP-216, IMP-414 |
| IMP-702 | Authorization and security test pass | IMP-215, IMP-699, IMP-511 |
| IMP-708 | Natural-language trip intake with confirmation | IMP-212, IMP-303, IMP-301, IMP-613 |
| IMP-709 | "Why this plan" explanations for each day | IMP-305, IMP-406, IMP-613 |
| IMP-710 | Rain-aware day swapping with the Open-Meteo forecast | IMP-407, IMP-501 |
| IMP-711 | "Today" companion view for trip days | IMP-309, IMP-508 |
| IMP-712 | Budget-fit suggestions when a plan is over budget | IMP-608, IMP-505 |
| IMP-713 | Destination and place context cards from Wikivoyage and Wikipedia | IMP-604 |


### 9.3 Team ownership and contribution

Ownership follows the Team Contribution Plan, version 2 (27 October 2026), which extends the plan of 26 October 2026 with the nine selected extensions and replaces the blueprint's role owners (M1 to M10). The ten members own 427 points over 108 cards: Manal, Malhar and Manya 42 each and the others 43 (about 128 focused hours, roughly 16 a week). The original 370 points keep their owners; the 57 extension points were split so that every member gained 5 or 6 points in Sprints 5 to 7, where loads were lowest, and Sprint 8 stays free for the release. Task IDs, prerequisites, files and acceptance criteria of the original cards are unchanged. Every card in §10 names its lead and its parts. The point totals below are those of version 2. IMD-65 cut the extensions and Amendment A1 added 33 points; the current plan is in §9.6 (IMD-114).

| Member | Role | Owns | Points | Points by area |
| --- | --- | --- | --- | --- |
| Manal | Backend (main) | Core API, trips and preferences, budget engine and costs, schedule validator rules; extensions: trip-intake endpoint, rain flags and day swap | 42 | Backend 39 · Frontend 2 · Docs 1 |
| Het | Backend (main) | Authentication, generation jobs, itinerary editing (edit core, move, add, replace, lock), regeneration merge; extensions: optimise and today endpoints, day-explanation storage | 43 | Backend 42 · Frontend 1 |
| Junaid | Backend (helper), Testing | Travel times and OpenRouteService, validator checks, authorization, contract and injection suites, user research; extensions: day-order heuristic, budget-fit search | 43 | Testing 22 · Backend 18 · Data 2 · Docs 1 |
| Malhar | Database (main) | Migrations, place import, candidate retrieval, fallback planner, search and filters, demo data; extensions: Open-Meteo client and weather cache, MediaWiki client and context cache | 42 | Database 23 · Data 7 · Backend 5 · Docs 4 · Frontend 3 |
| Jeel | Database (main) | ORM and drift test, places API, ranking, generation records, wishlist, versions, demo data; extensions: ranking explanation, budget-fit and context endpoints | 43 | Database 22 · Data 6 · Frontend 7 · Backend 5 · Docs 3 |
| Kirtan | Deployment and DevOps | Repository, CI, local and cloud deployment, readiness and logging, API contract, rate limits, sprint gates; extensions: packing checklist (lead), context refresh job | 43 | DevOps 31 · Backend 5 · Gates 5 · Data 1 · Docs 1 |
| Nidhi | AI/ML | Provider layer, Gemini adapter, generation pipeline, retries and breaker, repair, one-day regeneration; extensions: trip-intake, day-explanation and packing operations | 43 | AI/ML 40 · Gates 2 · Docs 1 |
| Manya | AI/ML | Prompts, MOCK provider, output validation, constraint handling, pace and grouping, evaluation; extensions: intake, explanation and packing prompts, schemas and evaluation cases | 42 | AI/ML 36 · Docs 4 · Data 2 |
| Manasvi | Frontend (main) | Web skeleton, trip wizard, itinerary view, editing screens, warnings, costs, map, dashboard; extensions: describe-your-trip screen, optimise dialog, Today view | 43 | Frontend 43 |
| Krrish | Frontend (helper), Testing | Sign-in screens, generate page, budget and draft screens, summary, keyboard support, end-to-end suites, accessibility; extensions: why-this-place panel, forecast banner, budget-fit panel | 43 | Frontend 32 · Testing 11 |
| **Total** |  |  | **427** |  |


**Load by sprint.** Points per member and sprint (one point is about three focused hours); bold cells hold 9 or more points (27 or more hours that week). The peaks cluster in Sprint 3 (the Gemini slice), Sprint 4 (the edit core and its screens), Sprint 6 (the places features and the first two extensions) and Sprint 7 for Krrish (three extension screens beside the test suites); plan help for those weeks at sprint planning, and switch extensions off first if a week overruns.

| Member | Role | Sprint 1 | Sprint 2 | Sprint 3 | Sprint 4 | Sprint 5 | Sprint 6 | Sprint 7 | Sprint 8 | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Manal | Backend (main) | 2 | 7 | 5 | 8 | 6 | 8 | 6 | 0 | 42 |
| Het | Backend (main) | 3 | 2 | 6 | **9** | 8 | **10** | 5 | 0 | 43 |
| Junaid | Backend (helper), Testing | 3 | 5 | 8 | 5 | 6 | 7 | 7 | 2 | 43 |
| Malhar | Database (main) | 7 | 8 | 4 | 3 | 2 | **9** | 7 | 2 | 42 |
| Jeel | Database (main) | 4 | **9** | 4 | 4 | 5 | **10** | 5 | 2 | 43 |
| Kirtan | Deployment and DevOps | **10** | 7 | 2 | 2 | 5 | 6 | 5 | 6 | 43 |
| Nidhi | AI/ML | 6 | 2 | **11** | 5 | 6 | 6 | 5 | 2 | 43 |
| Manya | AI/ML | 2 | 2 | **11** | 6 | 8 | 6 | 6 | 1 | 42 |
| Manasvi | Frontend (main) | 5 | 3 | 4 | **10** | 8 | 6 | 6 | 1 | 43 |
| Krrish | Frontend (helper), Testing | 5 | 1 | 2 | **9** | **9** | 7 | **10** | 0 | 43 |
| Team average |  | 4.7 | 4.6 | 5.7 | 6.1 | 6.3 | 7.5 | 6.2 | 1.6 | 42.7 |


**Shared cards.** 55 of the 108 cards touch more than one layer and are split into named parts with their own points. The member with the most points on a card leads it; where two members hold the same points the card's previous role owner leads (the destination 1 curation card is led by Jeel, as the plan states). The lead opens the GitHub issue, tracks the card's acceptance criteria and attaches the completion evidence. Everyone on a shared card follows four rules:

1. **Contract first.** All 36 MVP endpoints get their final shapes in Sprint 2 (IMP-214) and return 501 until built, so screen parts can start against the generated client on day 1 of a sprint. Each extension card declares its own endpoints on day 1 of its sprint in the same way (IMD-37).
2. **API part merges first.** The backend, database or AI part merges once its tests pass; the screen part merges after it (the wave rule of §14.2: start against stubs, merge after the prerequisites).
3. **One branch and pull request per part.** For example Het opens `feat/IMP-409-move-api` and Manasvi opens `feat/IMP-409-move-controls`; the lead's pull request closes the card.
4. **Review across the seam.** The API owner reviews the screen's pull request and the screen owner reviews the API's; each side checks the contract it depends on.

These pairs share the most cards and agree on payloads early:

| Pair | Shared cards |
| --- | --- |
| Malhar + Jeel | IMP-106, 205, 304, 402, 604, 610, 713 |
| Het + Manasvi | IMP-309, 408, 409, 612, 711 |
| Het + Krrish | IMP-305, 505, 506, 607, 609 |
| Manal + Krrish | IMP-410, 411, 510, 608, 710 |
| Nidhi + Manya | IMP-613, 708, 709 (extension operations and their prompts) |
| Nidhi + Krrish | IMP-305, 403, 607 |


### 9.4 How contribution is tracked

A part counts as done, with its points credited to its owner, when its pull request merges to `main` with every required check green and its share of the card's acceptance criteria is shown by tests.

| Item | Rule |
| --- | --- |
| Week 1 set-up | All ten members are collaborators on the private repository; Kirtan sets branch protection on `main`, the merge setting (Rebase and merge only), CODEOWNERS, the `commit-msg` hook and the CI `attribution` job (IMP-102) |
| Board | The GitHub Projects board has one issue per task part, assigned to its owner and labelled with sprint and points |
| Branches | `feat\|fix\|chore/IMP-NNN-<part-slug>`, one branch per part |
| Commits | Authored and committed as the part's owner with the name and email of the team table, also when the operator runs Claude Code for the part (IMD-61); one author per commit, no `Co-authored-by:` line and no mention of AI tools; Conventional Commits starting with the task ID, for example `feat(itinerary): IMP-409 keyboard move controls` |
| Pull requests | Opened from the operator's account with the IMP-102 template (linked task and requirement IDs, what changed, tests run with result lines, screenshots, contract and migration questions), assigned to the part owner, reviewer named by the run prompt; the title names the part, for example `IMP-409 · move-controls part` |
| Reviews | Every pull request needs one approval from the named reviewer's own account (never the operator's account that opened it). CODEOWNERS also requires Kirtan plus one other owner for `contracts/`, migrations and `app/schemas/`, and Nidhi for `app/ai/` |
| Attribution | Merged with Rebase and merge only: rebasing keeps each commit's author, so every merged part stays credited to its owner on `main`; GitHub counts a commit for a member when its author email is linked to that member's account (IMD-63) |
| Integration | Kirtan, as integration lead, merges in dependency order, keeps `main` green, and resolves migration heads and contract conflicts; a red `main` stops merges until fixed |
| Progress | Each part's pull request adds `docs/progress/parts/IMP-NNN-<part-slug>.md` with its status, owner and evidence; the gate card compiles `docs/progress/sprint-N.md` from these records; the lead marks the card done when all parts are merged and the card's acceptance criteria are verified; the planner's ledger is rebuilt from them on RESYNC (Appendix D) |

### 9.5 Judgment calls in the allocation and role names

Equal load and a perfect role match could not both hold, so the plan made the decisions below (version 2 adds the extension rules); any can be changed at sprint planning, and the cut-list checkpoint (IMP-499) rebalances points if extensions or cut-list features are switched off.

| Decision | What it means |
| --- | --- |
| Extensions are additive (version 2) | The nine selected extensions add 9 cards and 57 points (IMP-515, IMP-612, IMP-613, IMP-708 to IMP-713). The 370 points of version 1 keep their owners and parts. Each member gains 5 or 6 points, all in Sprints 5 to 7, which had the lowest loads; Sprint 8 stays free for the release. |
| Screens built by their feature's owner (13 points) | The frontend work exceeds what Manasvi and Krrish can carry, since Krrish also tests. Jeel builds the explore page, place detail drawer, saved-places panel, versions page and the context card (7); Malhar the PlacePicker and meal-slot display (3); Manal the trip actions menu (2); Het the profile page (1). Manasvi reviews all of them. |
| Ranking and the fallback planner go to the database pair | AI/ML would otherwise carry more than 80 points, so IMP-304 ranking and IMP-402 fallback planner go to Jeel and Malhar, the places-data owners; the ranking explanation (IMP-515) follows the ranking to Jeel. |
| Uneven weeks | Kirtan has 10 points in Sprint 1 against a team average of 4.7 and should start IMP-101 and IMP-102 before Sprint 1 if he can. Other peaks: Nidhi and Manya 11 each in Sprint 3, Manasvi 10 and Het 9 in Sprint 4, Het and Jeel 10 in Sprint 6, Krrish 10 in Sprint 7. 42 or 43 points is about 128 focused hours, roughly 16 hours a week, above the 12 assumed by AS-01. |
| Extensions are cut first | If the week 4 checkpoint (IMP-499) or a gate finds the team behind, extensions are switched off before any MVP cut-list feature, in the order packing, context cards, budget fit, Today view, rain swap, optimise order, day explanations, natural-language intake, ranking explanation. Their points then return to the MVP cards and testing of the same sprint. |
| The cut list moves points | If the week 4 checkpoint switches off cut-list features, the cards behind them lose points, most of them Het's, Jeel's, Manal's and Krrish's. Rebalance at that checkpoint by moving Sprint 7 testing and documentation parts to them. |


Where this specification or the blueprint still names a role outside the task cards, read it as follows (the first five mappings are stated in the plan; the others follow the plan's ownership):

| Role in the blueprint | Read as |
| --- | --- |
| M1 | Kirtan |
| M2 | Junaid and Krrish |
| M3 | Manasvi |
| M4 | Manal (trips) and Het (auth) |
| M5 | Malhar and Jeel |
| M6 | Nidhi |
| M7 | Junaid (validation, routing) with Manal (validator rules) |
| M8 | Het |
| M9 | Manal |
| M10 | Manasvi |

### 9.6 Amendment A1 (2 November 2026): AWS hosting and the RAG pipeline

Amendment A1 (`docs/spec/AMENDMENT_A1_AWS_RAG.md`, IMD-99 to IMD-116) makes two changes:

- Hosting moves to AWS: Amazon ECS Express Mode for the web and API containers, Amazon RDS PostgreSQL 16 with pgvector, and Supabase for sign-in only.
- Itinerary generation becomes a RAG pipeline on the Gemini API.

It adds 11 cards worth 33 points. The nine extension cards stay cut (IMD-65), so the plan is 403 points over 119 cards.

| Member | Plan after IMD-65 | Added by A1 (cards, sprint) | Plan after A1 |
| --- | --- | --- | --- |
| Manal | 37 | +3 (IMP-313, S3) | 40 |
| Het | 37 | +2 (IMP-219, S2), +1 (IMP-316, S3) | 40 |
| Junaid | 37 | +2 (IMP-218, S2), +2 (IMP-318, S4) | 41 |
| Malhar | 37 | +3 (IMP-311, S2), +1 (IMP-314, S3) | 41 |
| Jeel | 37 | +3 (IMP-315, S3) | 40 |
| Kirtan | 37 | +4 (IMP-217, S2) | 41 |
| Nidhi | 37 | +3 (IMP-312, S3) | 40 |
| Manya | 37 | +3 (IMP-316, S3) | 40 |
| Manasvi | 37 | +2 (IMP-218, S2), +2 (IMP-317, S3) | 41 |
| Krrish | 37 | +2 (IMP-314, S3) | 39 |
| **Total** | **370** | **+33** | **403** |

Rules added by the amendment:

1. **AWS cards.** Claude Code writes the scripts, workflows and guides. Kirtan, as the AWS account owner, runs every step that touches the account from his own terminal or AWS CloudShell. Live results are "not verified" until his recorded output is attached.
2. **DATA rule for guides.** Destination guides (IMP-314, and IMP-603 optionally) are written and reviewed by members. Claude Code only runs the loader and the quality gate.
3. **RAG order.** The RAG cards follow the order of §9.2: IMP-311 (Sprint 2), then IMP-312 after IMP-301, IMP-313, IMP-315 and IMP-314, IMP-316 after IMP-309, IMP-317, and IMP-318 in Sprint 4. They are MVP and are not on the cut list (IMD-105).
