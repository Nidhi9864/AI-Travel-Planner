# CLAUDE.md — AI Travel Planner

Read this file at the start of every session. It is short on purpose; the binding details live in the implementation specification, `docs/spec/IMPLEMENTATION_SPEC.md` (sections cited as §N; search it by heading, for example `## 6.6`). When this file and the specification disagree, the specification wins; report the disagreement.

## 1. Project in one paragraph

A web app where a signed-in traveller describes a trip and gets a day-wise, costed, editable itinerary. Gemini proposes the plan from a shortlist of curated places; the backend validates every place ID, recalculates every time, travel gap and price in code, labels every estimate and saves the plan with its warnings. When Gemini fails, a rule-based planner produces a labelled plan. Eight one-week sprints, ten students. The MVP scope is the requirement register (§2). Nine extensions (release code EXT, §2.5) are built in Sprints 5 to 7 by their own cards, each behind a switch, and are switched off before any MVP feature if time runs short. Anything marked T1, R2, PP or Stage 2 is not built unless a task card says so. In-app flight and hotel booking, payments and live prices are excluded (IMD-46): never add a booking provider, payment flow or booking claim.

## 2. Stack (do not replace)

- Web: Next.js App Router, React, TypeScript strict, Tailwind CSS, shadcn/ui, dnd-kit, TanStack Query, react-hook-form + zod, MapLibre GL JS + OpenFreeMap, openapi-typescript + openapi-fetch.
- API: Python 3.12, FastAPI, Pydantic v2, pydantic-settings, SQLAlchemy 2 async with psycopg 3, Alembic (runs versioned SQL files).
- Data and auth: Supabase Postgres and Supabase Auth; Supabase CLI local stack for development.
- AI: Gemini through `google-genai`, only behind `ModelProvider`; adapters GEMINI, MOCK, FINETUNED_MODEL (stub in Stage 1).
- Routing: OpenRouteService with cache and distance fallback. Hosting: Vercel (web), Render (API container). CI: GitHub Actions.
- Tests: pytest, Vitest + Testing Library, Playwright + axe. Quality: ruff, mypy, import-linter, ESLint, Prettier, pip-audit, npm audit, gitleaks.

Adding a dependency needs a reason in the pull request; adding a framework, service, queue or database needs a decision in `docs/spec/DECISION_REGISTER.md` first.

## 3. Where things live

| Path | Contents |
| --- | --- |
| `apps/api/app/<module>/` | Backend modules: core, auth, trips, places, ai, generation, validation, itinerary, budget, routing, evaluation, and the extension modules prep (packing only), weather and context; each with router.py, service.py, repository.py, schemas.py and, for pure rules, domain or engine files |
| `apps/api/app/schemas/` | Shared contracts: `ai.py` (gr-1, io-1, ProviderResult, findings), `common.py` (Money, Page, error envelope), `labels.py` |
| `apps/api/app/db/models/` | ORM models mirroring the SQL migrations, one file per owning module |
| `apps/api/migrations/sql/` and `versions/` | Schema source of truth (SQL) and the Alembic revisions that execute it |
| `apps/api/tests/` | unit/, contract/, api/, authz/, smoke/, fixtures/ |
| `apps/web/app/` | Routes: `(public)/` landing, sign-in, sign-up; `(app)/` dashboard, profile, trips/... |
| `apps/web/components/<area>/`, `apps/web/lib/` | Components by area; API client, query hooks, auth, formatting, zod schemas |
| `apps/web/tests/unit/`, `apps/web/e2e/` | Vitest component tests; Playwright specs |
| `contracts/` | Generated `openapi.v1.json` and AI JSON Schemas (committed, never edited by hand) |
| `data/fixtures/sampleton/`, `data/places/<slug>/` | SAMPLE test destination; curated destinations |
| `docs/spec/` | The specification (`IMPLEMENTATION_SPEC.md`), the registers (TASK_REGISTER, DECISION_REGISTER, TRACEABILITY_MATRIX), SPRINT_EXECUTION_GUIDE, ORCHESTRATOR_PROMPT and `sql/` (the reference migrations of Appendix A); placed by the operator and committed unchanged in IMP-101 |
| `docs/progress/sprint-N.md`, `docs/progress/gates.md` | Task status and evidence; gate results |

## 4. Architecture rules (enforced by `make imports` and review)

1. Backend layers: routers → services → domain and repositories → clients and adapters. Routers hold no business rules and no SQL. Domain code does no I/O and imports no FastAPI, SQLAlchemy, HTTP client or SDK.
2. `google-genai` is imported only in `app/ai/providers/gemini.py`; only `app/ai/factory.py` imports concrete adapters; OpenRouteService HTTP calls only in `app/routing/client.py`; Open-Meteo calls only in `app/weather/client.py`; MediaWiki calls only in `app/context/client.py` (from its background job, with `WIKI_USER_AGENT`).
3. One writer per table: only the owning module writes its tables (§3); other modules call its service.
4. The user ID comes only from the verified token (`CurrentUser` dependency) and is passed to every repository query. A resource that exists but belongs to someone else returns 404 `NOT_FOUND`, never 403.
5. The browser never queries the database, never holds a provider, routing or database secret, and never computes prices, totals, times or travel gaps; it displays what the API returns.
6. No circular imports between modules; shared types go in `app/schemas/` (backend) or `lib/` (web).

## 5. Commands (run from the repository root)

| Purpose | Command |
| --- | --- |
| Install everything | `make setup` |
| Local Supabase stack (auth + Postgres) / plain test Postgres | `make stack-up`, `make stack-down` / `make db-up`, `make db-down` |
| Apply migrations / reset local data / load seed data | `make db-migrate` / `make db-reset` (local and test only) / `make seed` |
| Run API (port 8000) / web (port 3000) | `make api` / `make web` |
| Lint / types / import boundaries | `make lint` / `make typecheck` / `make imports` |
| Tests | `make test-unit`, `make test-contract`, `make test-api`, `make test-authz`, `make test-web`, `make test` (all except E2E) |
| End-to-end (MOCK provider, local stack) | `make e2e` (filter with `ARGS='--grep <tag>'`) |
| API contract and AI schemas | `make openapi` after any API or schema change; `make openapi-check` must pass |
| Everything a pull request needs | `make check` |
| Evaluation / deployed smoke / live Gemini check | `make eval PROVIDER=MOCK DATASET=<version>` / `make smoke URL=<base url>` / `make live-smoke` (only with a key, never in PR CI) |

`ARGS` passes extra arguments to the wrapped tool (pytest `-k name`, vitest or Playwright filters, seed `--check --strict`). If a command does not exist yet, the task that creates it is in `docs/spec/TASK_REGISTER.md`; do not invent a different command.

## 6. Environment variables

- Names and placeholders are in `.env.example` only; real values live in untracked `apps/api/.env`, `apps/web/.env.local`, the hosting dashboards and the CI secret store.
- Only `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `NEXT_PUBLIC_API_BASE_URL` and `NEXT_PUBLIC_FEATURES_DISABLED` may reach the browser.
- `AI_PROVIDER` is MOCK in local and test, GEMINI in staging and production. The API refuses to start in staging or production if a required `GEMINI_*` value is empty or a placeholder, or if production uses MOCK.
- Never print, log, commit or paste a key, a token, a connection string, a prompt body or personal data. Do not set `GOOGLE_API_KEY`.

## 7. Database and API rules

- Schema changes only through a new migration pair (`migrations/sql/NNNN_name.sql` + `versions/NNNN_name.py`), one per pull request; never edit a merged migration; keep one Alembic head; update the ORM models in the same change; `tests/api/test_schema_drift.py` must pass.
- Tables are only those of the MVP migrations 0001 to 0006 and the extension migrations 0007 to 0010 (§5), each extension migration created by its own card. Do not create T1 or R2 tables.
- API under `/api/v1`, JSON snake_case, UUID identifiers, dates `YYYY-MM-DD`, times `HH:MM` in the destination time zone, timestamps UTC ISO 8601, money as two-decimal strings with a currency code, the error envelope of §6.3 for every error, `plan_revision` on every itinerary read and edit.
- One request and response shape per operation, defined once in the module's `schemas.py`; regenerate `contracts/openapi.v1.json` and the web types in the same pull request.
- Every edit is one transaction that recalculates and revalidates; generation results are saved in one transaction (plan, warnings, version, record).

## 8. AI provider and security rules

- The model may only choose place IDs from the shortlist it was given, their order and times, and short notes. Prices, opening hours, travel times, totals and availability always come from data and code. Model output is parsed into `ItineraryOutput` (io-1) and validated; it never builds SQL, never names a table or user, and is never executed.
- Unknown place IDs, schema failures, timeouts, rate limits, quota and configuration errors follow the error taxonomy (§8): at most the configured retries, at most one repair call, then the labelled rule-based fallback; quota and configuration errors end in `failed` with a rule-based option. Every generation writes its record.
- Tests never call Gemini. Use the MOCK adapter (`MOCK_PROVIDER_SCENARIO`) or recorded responses in `tests/fixtures/provider_recordings/`. Live calls only through `make live-smoke` with an explicit key.
- The three assistive operations (`extract_trip_request`, `explain_day`, `suggest_packing_items`) follow the same rule: the model proposes, code validates every value (trip and preference validators, places on the day, fixed packing vocabulary); each call is written to `ai_assist_calls` and counted against `AI_DAILY_ASSIST_CALLS_PER_USER`; nothing is saved from intake until the traveller confirms (§8.20).
- No private user data is used for training or evaluation datasets (PD-09). No Stage 2 work without a recorded decision.

## 9. Testing expectations

- Write or update tests in the same change as the code; each task card names its test files, TC IDs and command.
- Unit tests for domain rules (validation, budget, ranking, scheduling, fallback); API tests with a real migrated PostgreSQL; an authorization test for every new owned route; contract tests for every adapter; component tests for every new interactive component; E2E for journeys.
- Never report a test as passing unless it ran in this session or in CI and passed; paste the command and the summary line. If a test cannot run (missing Docker, key or account), say so and mark the evidence as missing.
- Do not delete, skip or weaken a failing test to get green; fix the code or report the conflict. Skips are allowed only for disabled cut-list features or extensions (switched off in `FEATURES_DISABLED`) and `live` tests without a key.

## 10. Prohibited shortcuts

- Hard-coded itineraries, prices, hours, routes, success messages or "fake" API responses in production code (fixtures and MOCK scenarios live only in test and mock paths and are labelled SAMPLE).
- Building an extension without its switch (IMD-47); a switched-off extension hides its screens and its routes return 404.
- Calling Gemini, ORS, Open-Meteo or MediaWiki from the browser; secrets in code, tests or fixtures; disabling auth, CORS or RLS to make something work.
- Catch-all exception handlers that hide errors; `# type: ignore`, `any` or `eslint-disable` without a one-line reason.
- Changing an API shape, table, finding code, error code or environment variable name without updating the specification registers and the contract files in the same pull request.
- Rewriting working modules that the task does not name; large refactors without a task.

## 11. Definition of Done for a task part

1. The task's acceptance criteria hold and are shown by the listed tests.
2. `make check` passes locally or in CI; `make e2e` passes when the task touches a journey.
3. OpenAPI and web types regenerated if the API changed; migrations and drift test updated if the schema changed.
4. No new lint, type or import-boundary violations; no secrets; labels and error states present on new screens.
5. The part record `docs/progress/parts/IMP-NNN-<part-slug>.md` is created in the same pull request: run id, owner, status, base commit (not its own head commit: Rebase and merge changes commit IDs), changed files, the commands run with their result lines, each acceptance criterion with verified or not verified and how, blockers, proposed decisions and open issues. `docs/progress/sprint-N.md` is the sprint index; the gate card compiles it from the part records. The card's lead marks the card done when all its parts are merged and its acceptance criteria are verified.
6. The pull request uses the template, cites the IMP task, the part and the requirement IDs, is titled like `IMP-409 · move-controls part`, is assigned to the part owner, names the reviewer (§12) and gets one approval before it is merged with Rebase and merge.

## 12. Team, identity, branches and pull requests

- Ten members own 427 points of the 108 cards, 42 or 43 each (Team Contribution Plan version 2, specification §14.3 and Appendix C). Every card names its lead and its parts in the "Owners and parts" row. Build only the part the prompt names, and use other parts through their contracts.
- **Commit identity.** Every commit of a part is authored and committed as the part's owner, with the git name and email given in the run prompt. Pass them to every git command that writes history: `git -c user.name="<name>" -c user.email="<email>" commit -m "<message>"`, and the same `-c` pair for `commit --amend`, `rebase`, `cherry-pick`, `revert` and `merge`. Never set `user.name` or `user.email` in any git config (global or repository), never use `--author` alone, and never rewrite commits already on `main` or made by another member. Rebasing your part's branch on `main` is done with the owner's `-c` pair and pushed with `git push --force-with-lease`, only on that branch and only before the pull request is approved.
- **One author per commit.** No `Co-authored-by:` line of any kind. No commit message, branch name, pull request title or body, or code comment mentions Claude, Claude Code or Anthropic, or says that an AI assistant wrote or helped with the work; the paths `CLAUDE.md` and `.claude/` are the exceptions. The project documents already in the repository (`CLAUDE.md`, `docs/spec/`) stay as they are, and nothing new states who or what wrote the code. The product's own AI features (Gemini, ModelProvider, "AI-written" labels) are product content, not attribution. The tracked `commit-msg` hook in `.githooks/` and the CI job `attribution` enforce this (IMP-102); `.claude/settings.json` sets `"attribution": {"commit": "", "pr": ""}` (IMP-101).
- **Before pushing**, run both checks and fix only your own new commits if one fails:
  `git log origin/main..HEAD --format='%h|%an|%ae|%cn|%ce|%s'` (only the owner's name and email, as author and committer) and
  `git log origin/main..HEAD --format='%B' | perl -ne 's/CLAUDE\.md|\.claude\///gi; print if /co-authored-by|anthropic|\bclaude\b/i'` (prints nothing).
- One branch per part: `feat|fix|chore/IMP-NNN-<part-slug>` (for example `feat/IMP-409-move-api`, `feat/IMP-409-move-controls`). The backend, database or AI part merges before the screen part that uses it. Commit messages follow Conventional Commits and start with the task ID, for example `feat(itinerary): IMP-409 keyboard move controls`.
- Pull requests are opened with `gh pr create`, assigned to the part owner, with the reviewer named in the run prompt, who is never the operator who opens the pull request and never the part owner (the planner chooses the card's lead, else the owner of the largest other part, else the CODEOWNERS owner, else the review pair). The pull-request body is written to a temporary file outside the repository. Claude Code never merges, never pushes to `main` and never force-pushes an approved branch.
- Merging uses **Rebase and merge** only (merge commits and squash merging are disabled in the repository settings), so every commit keeps its author and each merged part stays credited to its owner; on `main` GitHub records its own committer, which is expected. Kirtan is the integration lead: he keeps `main` green and resolves migration heads and contract conflicts.

## 13. Working with the specification

- Before changing any contract (endpoint, schema, table, code, env var, file layout), read the relevant section (§3 to §9). If the change is needed, stop and report it as a proposed decision instead of making it silently.
- Work one part at a time from `docs/spec/TASK_REGISTER.md`; confirm its prerequisites are merged on `main` (their part records exist in `docs/progress/parts/`); implement only that part; stop at its boundary.
- Record blockers and proposed decisions in the part record and the SYNC REPORT only, with the reason and what is needed. The gate card writes them into `docs/progress/`, and a separate decision run updates `docs/spec/DECISION_REGISTER.md` once the team has decided.

## 14. SYNC REPORT (end of every run)

Every run ends with this block, printed exactly, so the planner can update its ledger (specification Appendix D). Use `none` or `[]` for empty fields; never omit a field; quote command result lines exactly.

```text
<<<SYNC-REPORT
run_id: RUN-…
card: IMP-…
part: <part-slug>
owner: <Member>
status: PR_OPEN | BLOCKED | TESTS_FAILING | PARTIAL | NO_CHANGE
branch: <name or none>
base_commit: <sha>
head_commit: <sha or none>
commits:
  - <sha7> | <author name> <author email> | <committer name> <committer email> | <subject>
attribution_check: PASS | FAIL (<what>)
pr: <url or none>
reviewer_requested: <github user or none>
files_changed: [<paths>]
contracts_changed: none | [<what, and the proposal ID>]
migrations_added: none | [<file>]
commands:
  - cmd: <command>
    result: <exact summary line>
not_run:
  - cmd: <command>
    reason: <why>
acceptance:
  - criterion: <FR/TC id or text>
    status: verified | not verified
    how: <test or observation>
blockers: [<text>]
proposed_decisions: [<text>]
part_record: docs/progress/parts/<IMP-NNN>-<part-slug>.md
SYNC-REPORT>>>
```
