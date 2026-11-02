# TASK_REGISTER — AI Travel Planner

Canonical ordered task list generated from the implementation specification (§10). Task IDs are stable: a moved task keeps its ID. Statuses and evidence are kept in `docs/progress/sprint-N.md`, not here. Commands are the Makefile targets of CLAUDE.md §5.

**Amendment A1 (2 November 2026; IMD-99 to IMD-116; `docs/spec/AMENDMENT_A1_AWS_RAG.md`).**

- Hosting moves to AWS: ECS Express Mode for the web and API containers, RDS PostgreSQL for the database, and Supabase for sign-in only.
- Generation becomes a RAG pipeline on the Gemini API with pgvector.
- New cards: IMP-217, IMP-218, IMP-219 and IMP-311 (Sprint 2); IMP-312 to IMP-317 (Sprint 3); IMP-318 (Sprint 4). Each has a full card below.
- Cards whose text changed carry an "Amended by A1" line.
- The nine extension cards stay cut (IMD-65).
- The plan is now 403 points over 119 cards (Amendment A1 §10.5).

## Sprint 1 (week 1): Foundation and contracts — gate SG-1

| Task | Title | Type | Lead | Parts (points) | Prerequisites | Points |
| --- | --- | --- | --- | --- | --- | --- |
| IMP-101 | Repository skeleton, toolchain, Makefile, CLAUDE.md and docs/progress folders | CODE | Kirtan | Kirtan 2, Het 1 | none | 3 |
| IMP-102 | CI workflow (lint, types, imports, unit, guards, audit), branch protection, PR template, CODEOWNERS | CODE | Kirtan | Kirtan 2 | IMP-101 | 2 |
| IMP-103 | Backend skeleton: app factory, typed settings with start-up checks, error envelope, basic GET /health | CODE | Manal | Manal 2 | IMP-101 | 2 |
| IMP-104 | Web skeleton: Next.js app, Tailwind and shadcn/ui, responsive AppShell, query provider, state components | CODE | Manasvi | Manasvi 5 | IMP-101 | 5 |
| IMP-105 | Local environments: Supabase CLI stack, docker compose db, .env.example and env templates | CODE | Malhar | Malhar 1 | IMP-101 | 1 |
| IMP-106 | MVP migrations 0001-0006 through Alembic, ORM models, schema-drift test, test database fixture | CODE | Malhar | Malhar 3, Jeel 2 | IMP-103, IMP-105 | 5 |
| IMP-107 | SAMPLE fixture destination and minimal seed command | CODE | Jeel | Jeel 2 | IMP-106 | 2 |
| IMP-108 | Backend token verification and CurrentUser dependency, test token helper | CODE | Het | Het 2 | IMP-103, IMP-106 | 2 |
| IMP-109 | Sign-up, sign-in, sign-out and AuthGuard with Supabase Auth | CODE | Krrish | Krrish 4 | IMP-104, IMP-105 | 4 |
| IMP-110 | ModelProvider interface, shared AI schemas gr-1 and io-1, provider error types | CODE | Nidhi | Nidhi 5 | IMP-103 | 5 |
| IMP-111 | Versioned prompt-template registry | CODE | Manya | Manya 2 | IMP-110 | 2 |
| IMP-112 | Hello-world deployment to Vercel, Render and Supabase staging with deploy workflows | CODE | Kirtan | Kirtan 5 | IMP-102, IMP-103, IMP-104, IMP-113, IMP-106 | 5 |
| IMP-113 | Provision accounts, keys and email sender with named owners | HUMAN | Kirtan | Kirtan 1, Junaid 1, Nidhi 1 | none | 3 |
| IMP-114 | Stakeholder interviews round 1 and recorded findings | HUMAN | Junaid | Junaid 2, Krrish 1 | none | 3 |
| IMP-115 | Seed-data plan and choice of the two demo destinations | HUMAN | Malhar | Malhar 3 | none | 3 |
| IMP-199 | Sprint 1 gate SG-1: runnable skeleton and contracts in place | VERIFY | Kirtan | Kirtan 0 | IMP-101, IMP-102, IMP-103, IMP-104, IMP-105, IMP-106, IMP-107, IMP-108, IMP-109, IMP-110, IMP-111, IMP-112 | 0 |


### IMP-101 Repository skeleton, toolchain, Makefile, CLAUDE.md and docs/progress folders

**Task:** Sprint 1 (week 1) · CODE · 3 points · lead Kirtan with Het · release MVP

**Objective:** A cloned repository has the canonical tree of §4, pinned toolchains, a root Makefile whose targets of §G exist, the root CLAUDE.md and empty progress records, and `make setup` completes on a clean machine.

**Owners and parts**

- Kirtan (lead) — Repo tree, Makefile, toolchain pins, CLAUDE.md, progress folders (2 points)
- Het — API pyproject (ruff, mypy, pytest) and test socket guard (1 points)
- One branch and pull request per part (`feat/IMP-101-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-001; NFR-032, NFR-033

**Dependencies:** Prerequisites: §4 repository structure, §12 CLAUDE.md content, IMD-08 · Downstream: IMP-102, IMP-103, IMP-104, IMP-105, IMP-199

**Files**

- Makefile (create); CLAUDE.md (create); README.md (create); apps/api/pyproject.toml (create); apps/api/.importlinter (create); apps/web/package.json (create); .editorconfig (create); .gitignore (create); .pre-commit-config.yaml (create); docs/progress/sprint-1.md (create); docs/progress/gates.md (create); docs/spec/ (create); apps/api/tests/conftest.py (create); .claude/settings.json (create); docs/progress/parts/README.md (create)

**Implementation**

1. Commit the document set the operator placed in docs/spec/ before this run (IMPLEMENTATION_SPEC.md, TASK_REGISTER.md, DECISION_REGISTER.md, TRACEABILITY_MATRIX.md, SPRINT_EXECUTION_GUIDE.md, ORCHESTRATOR_PROMPT.md and sql/ with the Appendix A files) exactly as supplied; if any file is missing, stop and report it.
2. Create the directory tree of §4 (apps/api/app/<modules> with empty __init__.py, apps/web, contracts/, data/fixtures/, data/places/, docs/{spec,progress,decisions,guides,test-reports,acceptance}, eval/{datasets,results,reports}, .github/workflows) with a one-line README.md or module docstring per directory stating its purpose (NFR-033).
3. Write apps/api/pyproject.toml for Python 3.12: runtime deps fastapi, uvicorn[standard], pydantic>=2, pydantic-settings, sqlalchemy>=2 with psycopg[binary] 3, alembic, httpx, PyJWT[crypto], google-genai; dev extra: pytest, pytest-asyncio, respx, ruff, mypy, import-linter, pip-audit; configure ruff, mypy (strict on app/), pytest markers live and slow.
4. Create apps/web with Next.js (App Router, TypeScript strict, ESLint, Tailwind) and add scripts dev, build, lint, typecheck (tsc --noEmit), format:check (prettier --check .), test (vitest run), e2e (playwright test); commit the lockfile.
5. Write the root Makefile with every target of §G (stack-up/down, db-up/down, db-migrate, db-reset, seed, api, web, lint, typecheck, imports, test-unit, test-contract, test-api, test-authz, test-web, test, e2e, openapi, openapi-check, eval, check, smoke, live-smoke); every target whose code arrives later prints 'not yet implemented (IMP-xxx)' and exits 0, so the required CI checks are green on the skeleton; test targets succeed when no tests exist yet (pytest exit code 5 is treated as success, vitest runs with --passWithNoTests, Playwright with --pass-with-no-tests); ARGS is passed through to pytest/vitest/playwright.
6. Write .importlinter with the layer contract (routers > services > domain/repositories > clients) and the independence contract that only app.ai.providers.gemini imports google.genai and only app.ai.factory imports concrete adapters (NFR-031).
7. Commit the root CLAUDE.md that the operator placed (the text of §12.1) unchanged; create docs/progress/sprint-1.md as the Sprint 1 index with one line per IMP-1xx task part (status todo), docs/progress/gates.md with SG-1..SG-8 headings, and docs/progress/parts/README.md describing the part record (one file per part, fields of CLAUDE.md §11 item 5; the record names its base commit, not its own head commit, because Rebase and merge changes commit IDs).
8. Write README.md quick-start (prerequisites: Git, Docker, Supabase CLI, Python 3.12, Node LTS; then make setup, stack-up, db-up, db-migrate, seed, api, web) and pin Node with .nvmrc and Python with .python-version; record exact tool versions in docs/decisions/versions.md.
9. Write apps/api/tests/conftest.py with a socket guard that refuses connections to provider hosts (Gemini, OpenRouteService) unless the test is marked `live` (blueprint §27.4); `make live-smoke` is the only path that sets the marker.
10. Write .claude/settings.json with {"attribution": {"commit": "", "pr": ""}} and deny rules that keep .env files unread (CLAUDE.md §12, IMD-61); in the Makefile, make setup also runs git config core.hooksPath .githooks once the hook exists (IMP-102). Kirtan's part merges first (tree, Makefile, CLAUDE.md, progress folders); Het's pyproject and socket-guard part is built on top of it.

**Interfaces**

- Modules: MOD-P01, MOD-B01, MOD-F07 · Other: Makefile targets §G, .importlinter

**Acceptance criteria**

- `make setup` exits 0 on a clean clone (Linux/macOS or WSL) and creates apps/api/.venv and apps/web/node_modules.
- `make lint`, `make typecheck` and `make imports` exit 0 on the empty skeleton.
- Every target listed in §G exists in the Makefile (`make -n <target>` succeeds for each).
- CLAUDE.md at the root equals §12.1; docs/progress/sprint-1.md lists IMP-101..IMP-199.
- No file in the repository contains a real secret or a non-placeholder key (TC-354 runs in IMP-102).
- A test that opens a connection to a provider host fails unless it is marked `live` (socket guard).
- .claude/settings.json sets attribution commit and pr to empty strings; make setup sets core.hooksPath to .githooks when the directory exists.

**Tests**

- Makefile — TC-335 — `make setup && make lint && make typecheck && make imports`

**Completion evidence**

- Terminal output of `make setup && make lint && make typecheck && make imports` pasted in docs/progress/sprint-1.md; Commit hash of the skeleton on main; docs/decisions/versions.md with pinned versions

### IMP-102 CI workflow (lint, types, imports, unit, guards, audit), branch protection, PR template, CODEOWNERS

**Task:** Sprint 1 (week 1) · CODE · 2 points · lead Kirtan · release MVP

**Objective:** Every pull request runs one CI workflow that blocks merge on lint, type, import-rule, unit-test, secret-scan or critical-dependency failures, and main is protected.

**Owners and parts:** Kirtan — whole task (2 points); branch `feat/IMP-102-<short>`

**Traces to:** Stories US-001; NFR-013, NFR-018, NFR-031, NFR-034, NFR-048

**Dependencies:** Prerequisites: IMP-101, §13 CI matrix · Downstream: IMP-112, IMP-199

**Files**

- .github/workflows/ci.yml (create); .github/pull_request_template.md (create); .github/CODEOWNERS (create); docs/guides/contributing.md (create); .githooks/commit-msg (create); scripts/check_attribution.sh (create)

**Implementation**

1. Write .github/workflows/ci.yml triggered on pull_request and push to main with jobs (attribution runs on pull_request only, because Rebase and merge rewrites the committer on main): lint-types (make lint, make typecheck, make imports), unit (make test-unit, make test-web), guards (gitleaks secret scan over the diff and full history on main), attribution (scripts/check_attribution.sh over the pull request's commits), audit (pip-audit and npm audit --audit-level=critical; critical findings fail), api (starts service postgres:16, runs make db-migrate against it then make test-api and make test-authz; the job is added now and becomes meaningful after IMP-106).
2. Use actions/setup-python with Python 3.12 and actions/setup-node with the .nvmrc version; cache pip and npm; no provider key is available to pull-request jobs (AI_PROVIDER=MOCK, APP_ENV=test).
3. Add the pull-request template with: linked IMP task and FR/US IDs, what changed, tests run with commands and results, screenshots for UI, 'contract changed?' (OpenAPI/schema/migration) checkbox, part owner and reviewer; it carries no tool or AI-use statement and no generated-by footer (IMD-61).
4. Write .githooks/commit-msg (POSIX sh, executable): first remove the path texts CLAUDE.md and .claude/ (any case) from the message, then reject it when it matches, case-insensitively, the line prefix co-authored-by:, the word anthropic, or the word claude (as in 'claude' or 'claude code'), printing which rule failed. Write scripts/check_attribution.sh for CI (job checkout with fetch-depth 0): for every commit in git rev-list --no-merges <pull_request.base.sha>..<pull_request.head.sha> taken from the event payload (never HEAD, which is GitHub's synthetic merge commit), fail when the author email is not in the repository variable TEAM_EMAILS, when the committer differs from the author, or when the message breaks the commit-msg rules; also fail when the pull request body matches the same patterns (IMD-61). Commits on main after Rebase and merge carry GitHub's committer and are not checked.
5. Add CODEOWNERS: contracts/, apps/api/migrations/ and apps/api/app/schemas/ need Kirtan plus one other owner (NFR-033); apps/api/app/ai/ needs Nidhi.
6. Document in docs/guides/contributing.md the Team Contribution Plan rules (§14.4): one branch per task part named feat|fix|chore/IMP-NNN-<part-slug>; Conventional Commits starting with the task ID, e.g. feat(itinerary): IMP-409 keyboard move controls, authored and committed as the part owner with one author and no Co-authored-by line (IMD-61); pull-request title naming the part, e.g. 'IMP-409 · move-controls part', assigned to the owner with the named reviewer; API part merges before its screen part; one migration per PR; Rebase and merge only (IMD-63); a part record in docs/progress/parts/ per pull request (IMD-62).
7. Confirm that all ten members (Manal, Het, Junaid, Malhar, Jeel, Kirtan, Nidhi, Manya, Manasvi, Krrish) are collaborators on the private repository, and create the GitHub Projects board with one issue per task part (183 parts across the 108 cards of docs/spec/TASK_REGISTER.md), each assigned to its owner and labelled sprint-N and its points; Claude Code may generate the issue list as docs/progress/board-issues.md for the team to import (creating the board with gh needs the project scope: gh auth refresh -s project).
8. Configure the repository (done by the repository admin, normally the owner of the private repository, with Kirtan): branch protection on main with PR required, one approving review, required checks lint-types, unit, guards, attribution, audit, api, linear history, no force push; pull-request merges allow Rebase and merge only (merge commits and squash merging off); the Actions variable TEAM_EMAILS. Branch protection and CODEOWNERS on a private repository need GitHub Pro, Team or Enterprise; without them the same rules are followed by agreement and checked by the planner. Record a screenshot.

**Interfaces**

- Modules: MOD-P01 · Env: AI_PROVIDER, APP_ENV, TEST_DATABASE_URL · Other: GitHub Actions, gitleaks, pip-audit, npm audit, GitHub Projects board

**Acceptance criteria**

- A PR with a deliberately failing unit test shows a red required check and cannot be merged (US-001 AC1, NFR-048, TC-343).
- A PR that adds a fake key matching a gitleaks rule fails the guards job (US-001 AC3, TC-354).
- A PR importing google.genai outside app/ai/providers/gemini.py fails make imports (TC-002).
- The api job applies migrations to a blank PostgreSQL once IMP-106 merges (TC-337).
- Branch protection settings match the step list (screenshot in docs/progress/sprint-1.md).
- All ten members are contributors and the board holds one issue per task part with owner, sprint and points labels (screenshot or export in docs/progress/sprint-1.md).
- A pull request whose commit message contains a Co-authored-by line, or whose commit author email is not in TEAM_EMAILS, fails the attribution check; a commit with such a message is refused locally by the commit-msg hook (IMD-61).
- The repository settings allow Rebase and merge only (screenshot in docs/progress/parts/IMP-102-*.md).

**Tests**

- .github/workflows/ci.yml — TC-343, TC-354, TC-002 — `make check (run by CI on two throw-away pull requests: one with a failing test, one with a fake secret; both must be red, then closed)`
- scripts/check_attribution.sh — new cases — `make check; then the operator runs the negative test by hand: on a throw-away branch test/attribution-check, a commit made with --no-verify that contains a Co-authored-by line must show a red attribution check; the pull request is closed unmerged and the branch deleted`

**Completion evidence**

- Links to the two red CI runs and one green CI run; Branch-protection screenshot in docs/progress/sprint-1.md; Board export or screenshot showing the issues per part

### IMP-103 Backend skeleton: app factory, typed settings with start-up checks, error envelope, basic GET /health

**Task:** Sprint 1 (week 1) · CODE · 2 points · lead Manal · release MVP

**Objective:** `make api` starts a FastAPI app that validates its configuration at start-up, serves GET /health (API-01) and returns every error in the §6 error envelope with a request ID.

**Owners and parts:** Manal — whole task (2 points); branch `feat/IMP-103-<short>`

**Traces to:** Stories US-003; FR-123, FR-124; NFR-013, NFR-015, NFR-035

**Dependencies:** Prerequisites: IMP-101, §6.1 conventions, §6.2 error envelope, §4 .env rules · Downstream: IMP-106, IMP-108, IMP-110, IMP-112, IMP-199, IMP-201, IMP-208

**Files**

- apps/api/app/main.py (create); apps/api/app/core/config.py (create); apps/api/app/core/errors.py (create); apps/api/app/core/health.py (create); apps/api/app/core/request_id.py (create); apps/api/app/core/flags.py (create); apps/api/app/schemas/common.py (create); apps/api/tests/unit/core/test_config.py (create); apps/api/tests/api/test_health.py (create); apps/api/tests/conftest.py (modify)

**Implementation**

1. In core/config.py define one pydantic-settings Settings class with every backend variable of §H (types, defaults from .env.example) and a cached get_settings(); secrets are SecretStr.
2. Add start-up checks run in the app factory: APP_ENV in {local,test,staging,production}; DATABASE_URL present; AI_PROVIDER in {GEMINI,MOCK,FINETUNED_MODEL}; in staging/production refuse AI_PROVIDER=GEMINI when any GEMINI_* value is empty or starts with '<', refuse GEMINI_TIMEOUT_S x (GEMINI_MAX_RETRIES+1) > 70, refuse MOCK in production; FINETUNED_MODEL refused with 'adapter not enabled before Stage 2'; GOOGLE_API_KEY set -> warning only; failures raise ConfigError with a message naming the variable but never its value.
3. In core/errors.py define the envelope models (error.code, message, request_id, details[{field,message}], retry_after_s) in schemas/common.py and domain exceptions (NotFound, Unauthenticated, ValidationFailed, StalePlan, GenerationInProgress, Conflict, RateLimited, QuotaReached, ServiceUnavailable, Internal); register handlers that map them to the HTTP codes of §6.2, map FastAPI RequestValidationError to 422 VALIDATION_ERROR with details, and map any other exception to 500 INTERNAL without stack trace.
4. In core/request_id.py add middleware that accepts a client UUID in X-Request-ID or generates one, stores it in a contextvar and echoes it in the response header.
5. In core/health.py implement API-01 GET /health returning {status:'ok', version (from env BUILD_VERSION or git sha, default 'dev'), environment, provider (AI_PROVIDER value)} and never a secret; mount routers under /api/v1 except /health.
6. Configure CORS from ALLOWED_ORIGINS (exact origins, no wildcard) and disable /docs when APP_ENV=production; parse FEATURES_DISABLED into a set in core/flags.py (IMD-11).
7. Write unit tests for each start-up rule and an API test that GET /health returns 200 with the four fields and that an unknown route returns the 404 envelope with request_id.

**Interfaces**

- API: API-01 · Modules: MOD-B01 · Env: APP_ENV, DATABASE_URL, AI_PROVIDER, GEMINI_API_KEY, GEMINI_MODEL_ID, GEMINI_TIMEOUT_S, GEMINI_MAX_RETRIES, ALLOWED_ORIGINS, FEATURES_DISABLED, LOG_LEVEL · Other: error envelope §6.2

**Acceptance criteria**

- Starting with DATABASE_URL unset exits non-zero with a message naming DATABASE_URL (US-003 AC1, FR-124 AC1, TC-290).
- Starting with APP_ENV=staging, AI_PROVIDER=GEMINI and GEMINI_API_KEY='<Gemini API key>' exits with a configuration error; the key value is not printed (TC-043, TC-291, TC-025).
- AI_PROVIDER=UNKNOWN exits with a clear error (TC-042); AI_PROVIDER=FINETUNED_MODEL is refused (TC-037).
- GET /health returns 200 with status, version, environment, provider and no secret (FR-123 AC1, TC-288, TC-044).
- A request from an origin not in ALLOWED_ORIGINS gets no CORS allow header (TC-351).

**Tests**

- apps/api/tests/unit/core/test_config.py — TC-290, TC-291, TC-042, TC-043, TC-037 — `make test-unit ARGS='-k config'`
- apps/api/tests/api/test_health.py — TC-288, TC-044, TC-351 — `make test-api ARGS='-k health'`

**Completion evidence**

- make test-unit and make test-api output in the PR; curl http://localhost:8000/health output in docs/progress/sprint-1.md

### IMP-104 Web skeleton: Next.js app, Tailwind and shadcn/ui, responsive AppShell, query provider, state components

**Task:** Sprint 1 (week 1) · CODE · 5 points · lead Manasvi · release MVP

**Objective:** `make web` serves a responsive application shell with navigation, shared state components and the TanStack Query provider, with no horizontal scroll from 360 to 1920 px.

**Owners and parts:** Manasvi — whole task (5 points); branch `feat/IMP-104-<short>`

**Traces to:** Stories US-122; FR-114; NFR-026

**Dependencies:** Prerequisites: IMP-101, §7 frontend specification · Downstream: IMP-109, IMP-112, IMP-199, IMP-412

**Files**

- apps/web/app/layout.tsx (create); apps/web/app/(public)/page.tsx (create); apps/web/app/(app)/layout.tsx (create); apps/web/components/shell/AppShell.tsx (create); apps/web/components/states/EmptyState.tsx (create); apps/web/components/states/ErrorState.tsx (create); apps/web/components/states/LoadingSkeleton.tsx (create); apps/web/components/ui/ (create); apps/web/lib/api/queries.ts (create); apps/web/lib/flags.ts (create); apps/web/tests/unit/shell/AppShell.test.tsx (create); apps/web/e2e/smoke.spec.ts (create); apps/web/playwright.config.ts (create); apps/web/vitest.config.ts (create)

**Implementation**

1. Initialise shadcn/ui and add the primitives button, input, label, dialog, dropdown-menu, toast, card, skeleton under components/ui with accessible defaults (visible focus ring, 44 px touch targets).
2. Define design tokens (colours with AA contrast, spacing, type scale) in the Tailwind config; no hard-coded colours in components.
3. Build AppShell: header with app name and account menu placeholder, desktop side or top navigation, phone bottom navigation (Trips, Itinerary, Costs, Profile) below 768 px, a main landmark and a skip-to-content link; (app)/layout.tsx wraps pages in AppShell (AuthGuard is added in IMP-109).
4. Add QueryClientProvider in app/layout.tsx and lib/api/queries.ts with the query-key factory (trips, trip, itinerary, costs, generation) used by later tasks; lib/flags.ts reads NEXT_PUBLIC_FEATURES_DISABLED into isEnabled(name).
5. Implement EmptyState, ErrorState (shows message and request_id when provided, retry button) and LoadingSkeleton; the landing page (public)/page.tsx states the product purpose and links to sign-in and sign-up.
6. Configure Vitest with Testing Library and jsdom; configure Playwright with a webServer that runs `npm run dev` and projects for 360, 768, 1280 and 1920 px widths.
7. Write the AppShell unit test (landmarks, navigation links, skip link) and an e2e viewport test asserting document.scrollWidth <= innerWidth on the landing page at each width.

**Interfaces**

- Modules: MOD-F07, MOD-F01 · Components: AppShell, EmptyState, ErrorState, LoadingSkeleton, Toast · Env: NEXT_PUBLIC_FEATURES_DISABLED, NEXT_PUBLIC_API_BASE_URL · Other: TanStack Query

**Acceptance criteria**

- At 360, 768, 1280 and 1920 px the landing page and an (app) placeholder page show no horizontal scroll and no clipped control (US-122 AC1-AC2, FR-114, TC-278).
- AppShell exposes header, nav and main landmarks and a working skip link (unit test).
- `make test-web` and `make lint` pass; `npm run build --prefix apps/web` succeeds.

**Tests**

- apps/web/tests/unit/shell/AppShell.test.tsx — TC-278 — `make test-web ARGS='AppShell'`
- apps/web/e2e/smoke.spec.ts — TC-278 — `make e2e ARGS='smoke'`

**Completion evidence**

- Screenshots at 360 and 1280 px in docs/progress/sprint-1.md; make test-web output in the PR

### IMP-105 Local environments: Supabase CLI stack, docker compose db, .env.example and env templates

**Task:** Sprint 1 (week 1) · CODE · 1 points · lead Malhar · release MVP

**Objective:** A member runs `make stack-up` (Supabase local Auth + Postgres) and `make db-up` (plain PostgreSQL 16 for tests) and fills their untracked .env files from one placeholder-only .env.example.

**Owners and parts:** Malhar — whole task (1 points); branch `feat/IMP-105-<short>`

**Traces to:** Stories US-003; FR-124; NFR-013, NFR-032, NFR-035

**Dependencies:** Prerequisites: IMP-101, IMD-03, §H environment variables · Downstream: IMP-106, IMP-109, IMP-199

**Files**

- supabase/config.toml (create); docker-compose.yml (create); .env.example (create); apps/web/.env.local.example (create); docs/guides/local-setup.md (create); docs/secrets.md (create)

**Implementation**

1. Run `supabase init` at the root to create supabase/config.toml; keep default ports (API 54321, DB 54322, Studio 54323, Inbucket 54324) and set site_url and additional_redirect_urls to http://localhost:3000 and http://localhost:3000/auth/callback.
2. Write docker-compose.yml with service db (image postgres:16, port 5432, POSTGRES_PASSWORD=postgres, database travel_test, healthcheck pg_isready) and service api (builds apps/api/Dockerfile, env_file apps/api/.env, port 8000; used for local container smoke, IMP-112).
3. Write .env.example with every variable of §H grouped as blueprint §30.4 (placeholders in <angle brackets>, defaults for numbers, AI_PROVIDER=MOCK, local DATABASE_URL=postgresql+psycopg://postgres:postgres@127.0.0.1:54322/postgres, TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/travel_test); apps/web/.env.local.example holds only NEXT_PUBLIC_* lines.
4. Make the Makefile targets stack-up/stack-down call supabase start/stop and print `supabase status -o env` hints for copying ANON_KEY and JWT_SECRET into the untracked env files; db-up/db-down call docker compose for service db.
5. Add .env, apps/api/.env and apps/web/.env.local to .gitignore and add a CI guard step (in ci.yml) that fails if any tracked *.env file other than .env.example exists.
6. Write docs/guides/local-setup.md (60-minute target, NFR-032) and docs/secrets.md (variable, owner role, where stored, rotation rule; never a value).

**Interfaces**

- Modules: MOD-P01, MOD-B01 · Other: Supabase CLI, docker compose, all variables of §4.5 (.env.example)

**Acceptance criteria**

- `make stack-up` starts the local stack and `supabase status` lists API URL 127.0.0.1:54321 and DB 127.0.0.1:54322.
- `make db-up` starts postgres:16 and `docker compose ps` shows db healthy.
- .env.example contains only placeholders and defaults; the secret scan passes (TC-354); a tracked .env file fails CI (NFR-013).
- A member outside the platform squad follows docs/guides/local-setup.md to a running API and web app; time taken is recorded (TC-335).

**Tests**

- .github/workflows/ci.yml — TC-354, TC-338 — `make stack-up && make db-up && docker compose ps`

**Completion evidence**

- Output of `supabase status` (keys redacted) and `docker compose ps` in docs/progress/sprint-1.md; Setup-time note from one member

### IMP-106 MVP migrations 0001-0006 through Alembic, ORM models, schema-drift test, test database fixture

**Task:** Sprint 1 (week 1) · CODE · 5 points · lead Malhar with Jeel · release MVP

**Objective:** `make db-migrate` builds the 15 MVP tables, constraints, row-level-security policies and triggers on an empty database through six Alembic revisions that execute the SQL of Appendix A, and ORM models match the migrated schema.

**Owners and parts**

- Malhar (lead) — SQL migrations 0001-0006 through Alembic, constraints and indexes (3 points)
- Jeel — ORM models, schema-drift test, test database fixture (2 points)
- One branch and pull request per part (`feat/IMP-106-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-008; NFR-012, NFR-034

**Dependencies:** Prerequisites: IMP-103, IMP-105, §5 database specification, Appendix A SQL, IMD-01, IMD-02 · Downstream: IMP-107, IMP-108, IMP-112, IMP-199, IMP-201, IMP-202, IMP-203, IMP-209, IMP-215

**Files**

- apps/api/alembic.ini (create); apps/api/migrations/env.py (create); apps/api/migrations/sql/0001_helpers.sql (create); apps/api/migrations/sql/0002_reference_data.sql (create); apps/api/migrations/sql/0003_accounts_trips.sql (create); apps/api/migrations/sql/0004_ai_and_plan.sql (create); apps/api/migrations/sql/0005_mvp_security.sql (create); apps/api/migrations/sql/0006_updated_at_triggers.sql (create); apps/api/migrations/sql/test_auth_stub.sql (create); apps/api/migrations/versions/0001_helpers.py (create); apps/api/app/db/session.py (create); apps/api/app/db/models/ (create); apps/api/tests/fixtures/db.py (create); apps/api/tests/api/test_schema_drift.py (create); apps/api/tests/authz/test_rls.py (create)

**Implementation**

1. Copy the six migration SQL files and the auth stub verbatim from Appendix A into apps/api/migrations/sql/ (do not retype them).
2. Create Alembic (sync engine with the psycopg driver, URL from DATABASE_URL) and six revisions 0001..0006 chained linearly; each upgrade() reads its SQL file and runs it with op.execute; revision ids are '0001'..'0006' (files 000N_<concern>.py); downgrade() runs sql/down/000N_<concern>.down.sql; `alembic heads` must print one head.
3. In app/db/session.py create the async engine (postgresql+psycopg) and an async session factory plus a transaction() context helper used by services; no other module creates engines.
4. Write SQLAlchemy 2 typed models for the 15 tables in app/db/models/ (one file per owning module: profiles.py, trips.py, places.py, generation.py, itinerary.py, budget.py, routing.py) with exactly the column names, types and nullability of the SQL; the generated column trips.num_days is read-only (Computed).
5. Write tests/fixtures/db.py: a session-scoped fixture that creates the test database at TEST_DATABASE_URL, applies test_auth_stub.sql only if schema auth is absent, runs alembic upgrade head, and gives each test a transaction rolled back at the end; a helper inserts a row into auth.users for test users.
6. Write tests/api/test_schema_drift.py that reflects the migrated database and compares tables, columns, types and nullability with the ORM metadata (fails on any difference), and tests/authz/test_rls.py that connects with role anon and role authenticated and asserts zero rows readable from every public table (US-008 AC2).
7. Make `make db-migrate` and the CI api job run alembic upgrade head on a blank database.

**Interfaces**

- Tables: destinations, data_sources, places, place_opening_hours, profiles, trips, trip_preferences, trip_places, budget_settings, ai_generations, itinerary_days, itinerary_items, itinerary_warnings, itinerary_versions, route_cache · Modules: MOD-D01 · Env: DATABASE_URL, TEST_DATABASE_URL · Other: Alembic, Appendix A

**Acceptance criteria**

- On an empty PostgreSQL 16 (make db-up) and on the Supabase local stack, `make db-migrate` applies 0001-0006 without error and `alembic heads` prints one head (US-008 AC1, NFR-034, TC-337).
- `alembic downgrade base` followed by `alembic upgrade head` succeeds locally.
- test_schema_drift passes: ORM metadata equals the migrated schema.
- Roles anon and authenticated read zero rows from every table (US-008 AC2, NFR-012).
- The CI api job runs the migrations on a blank database and is green.

**Tests**

- apps/api/tests/api/test_schema_drift.py — TC-337 — `make db-up && make test-api ARGS='-k schema_drift'`
- apps/api/tests/authz/test_rls.py — TC-345 — `make test-authz ARGS='-k rls'`

**Completion evidence**

- CI api job log showing upgrade head on a blank database; Output of `alembic heads` and the drift test in docs/progress/sprint-1.md

### IMP-107 SAMPLE fixture destination and minimal seed command

**Task:** Sprint 1 (week 1) · CODE · 2 points · lead Jeel · release MVP

**Objective:** `make seed` loads a synthetic, clearly labelled SAMPLE destination (Sampleton) with about 30 places, opening hours and estimate prices into a migrated database, idempotently.

**Owners and parts:** Jeel — whole task (2 points); branch `feat/IMP-107-<short>`

**Traces to:** NFR-032

**Dependencies:** Prerequisites: IMP-106, §5 seed data specification, IMD-09 · Downstream: IMP-199, IMP-203, IMP-205

**Files**

- data/fixtures/sampleton/destination.json (create); data/fixtures/sampleton/places.csv (create); data/fixtures/sampleton/opening_hours.csv (create); data/fixtures/sampleton/sources.csv (create); data/fixtures/README.md (create); apps/api/app/places/seed.py (create); apps/api/tests/api/test_seed.py (create)

**Implementation**

1. Create the Sampleton files in the column format of §5 (destination: slug sampleton, invented coordinates and bbox, timezone e.g. Europe/London, currency fixed in the file; sources: one data_sources row 'SAMPLE fixture (synthetic)' with source_type other and licence 'synthetic test data'); every place name ends with '(sample)' so it can never be mistaken for real data.
2. Include about 30 places across all categories except stay, at least 6 food places, 3 places with closes_next_day hours, 3 with is_closed on one weekday, 3 with hours_label unavailable and no hours rows, 2 with step_free true, 2 with price_label unavailable; prices are price_label estimate.
3. Implement app/places/seed.py as `python -m app.places.seed <dir> [<dir>...]`: read the files, upsert destinations by slug, data_sources by name, places by (source_id, external_ref), replace each place's opening hours, all in one transaction per directory; print counts read/loaded; exit non-zero on a file-format error.
4. Make `make seed` run it for data/fixtures/sampleton plus any directories in SEED_DIRS; the full provenance import and quality gate replace the loading core in IMP-205 without changing the command.
5. Write tests/api/test_seed.py: loading twice gives the same row counts (idempotent) and every place has source_id and verification_status.

**Interfaces**

- Tables: destinations, data_sources, places, place_opening_hours · Modules: MOD-D02, MOD-B04 · Env: DATABASE_URL, SEED_DIRS · Other: data/fixtures/sampleton

**Acceptance criteria**

- `make seed` on a freshly migrated database loads 1 destination and about 30 places and prints the counts.
- Running `make seed` twice leaves identical row counts.
- Every fixture place name contains '(sample)' and its source is the SAMPLE data source.
- test_seed passes in CI.

**Tests**

- apps/api/tests/api/test_seed.py — TC-110 — `make test-api ARGS='-k seed'`

**Completion evidence**

- make seed output in docs/progress/sprint-1.md; test_seed green in CI

### IMP-108 Backend token verification and CurrentUser dependency, test token helper

**Task:** Sprint 1 (week 1) · CODE · 2 points · lead Het · release MVP

**Objective:** Every route except /health and /health/ready requires a valid Supabase access token, and handlers receive the user ID only from the verified token.

**Owners and parts:** Het — whole task (2 points); branch `feat/IMP-108-<short>`

**Traces to:** Stories US-012; FR-003; NFR-012, NFR-013

**Dependencies:** Prerequisites: IMP-103, IMP-106, IMD-04, §3 authentication flow · Downstream: IMP-199, IMP-203, IMP-215

**Files**

- apps/api/app/auth/tokens.py (create); apps/api/app/auth/deps.py (create); apps/api/app/auth/repository.py (create); apps/api/tests/fixtures/auth.py (create); apps/api/tests/unit/auth/test_tokens.py (create); apps/api/tests/authz/test_route_inventory.py (create); apps/api/app/auth/router.py (create); apps/api/app/auth/schemas.py (create); apps/api/app/auth/service.py (create); apps/api/tests/api/test_me.py (create)

**Implementation**

1. In auth/tokens.py verify the bearer token: if SUPABASE_JWKS_URL is set use PyJWT's JWKS client (cached keys) for asymmetric algorithms, else HS256 with SUPABASE_JWT_SECRET; require exp, sub (UUID) and aud 'authenticated'; any failure raises Unauthenticated (401 UNAUTHENTICATED).
2. In auth/deps.py define the CurrentUser dependency returning user_id (UUID) and email claim; on first sight it calls get_or_create_profile(user_id) in auth/service.py (insert ... on conflict do nothing through auth/repository.py), the only place that creates profiles (profiles is written only by MOD-B02; trips.user_id references profiles).
3. Attach CurrentUser to the /api/v1 router as a dependency so every new route is protected by default; /health and /health/ready stay outside it.
4. Write tests/fixtures/auth.py: make_token(user_id, expired=False, wrong_aud=False, secret=TEST_SECRET) minting HS256 tokens and a fixture that inserts the matching auth.users row in the test DB.
5. Write tests/authz/test_route_inventory.py that walks app.routes and asserts every route except the public allow-list (/health, /health/ready, /docs, /openapi.json) returns 401 without a token (TC-344).
6. Implement API-03 GET /api/v1/me in auth/router.py (schemas in auth/schemas.py, service in auth/service.py) returning the caller's Profile of §6.6.1, created on first call (IMD-14); IMP-305 adds the ai_notice_acknowledged flag of API-04 and IMP-601 the editable fields.
7. Write unit tests for valid, expired, tampered, wrong-audience and missing tokens, and a test that a request body naming another user_id is rejected with 422 (TC-348, IMD-45).

**Interfaces**

- API: all /api/v1 routes, API-03 · Tables: profiles · Modules: MOD-B02 · Env: SUPABASE_JWKS_URL, SUPABASE_JWT_SECRET, SUPABASE_URL · Other: PyJWT

**Acceptance criteria**

- A valid token reaches the handler with user_id equal to the token sub (FR-003 AC1, TC-057).
- A body field user_id naming another user is rejected with 422 VALIDATION_ERROR (FR-003 AC2, TC-058, TC-348, IMD-45).
- No token, an expired, tampered or wrong-audience token returns 401 UNAUTHENTICATED in the envelope (FR-003 AC3, TC-059, TC-347).
- The route-inventory test fails if any non-public route is reachable without a token (TC-344).
- A first authenticated call creates exactly one profiles row for the user.
- GET /api/v1/me returns the caller's profile, creating it on the first call; without a token it returns 401 (IMD-14).

**Tests**

- apps/api/tests/unit/auth/test_tokens.py — TC-057, TC-347 — `make test-unit ARGS='-k tokens'`
- apps/api/tests/authz/test_route_inventory.py — TC-344, TC-058, TC-059, TC-348 — `make test-authz ARGS='-k inventory'`
- apps/api/tests/api/test_me.py — TC-057 — `make test-api ARGS='-k me'`

**Completion evidence**

- make test-unit and make test-authz output in the PR

### IMP-109 Sign-up, sign-in, sign-out and AuthGuard with Supabase Auth

**Task:** Sprint 1 (week 1) · CODE · 4 points · lead Krrish · release MVP-S

**Objective:** A visitor can register, sign in, stay signed in across reloads and sign out using Supabase Auth from the browser, and signed-out visitors are redirected from (app) pages to /sign-in.

**Owners and parts:** Krrish — whole task (4 points); branch `feat/IMP-109-<short>`

**Traces to:** Stories US-010, US-011; FR-001, FR-002; NFR-013

**Dependencies:** Prerequisites: IMP-104, IMP-105, §7 screens sign-in/sign-up · Downstream: IMP-199, IMP-212, IMP-601

**Files**

- apps/web/lib/auth/supabase.ts (create); apps/web/lib/auth/useSession.ts (create); apps/web/app/(public)/sign-in/page.tsx (create); apps/web/app/(public)/sign-up/page.tsx (create); apps/web/app/auth/callback/route.ts (create); apps/web/components/shell/AuthGuard.tsx (create); apps/web/lib/validation/auth.ts (create); apps/web/tests/unit/shell/AuthGuard.test.tsx (create); apps/web/e2e/auth.spec.ts (create); apps/web/e2e/fixtures/users.ts (create)

**Implementation**

1. Create the browser Supabase client in lib/auth/supabase.ts from NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY (the only auth values in the browser) and a useSession hook exposing session, accessToken and signOut.
2. Build /sign-up with react-hook-form + zod (email format, password >= 8 characters, field-level messages); on success show 'check your email' or continue signed in, depending on the project's confirmation setting; on an existing email show the same neutral message (no account enumeration).
3. Build /sign-in (email + password, generic 'email or password is incorrect' message), redirect to /dashboard on success (placeholder page until IMP-602) and the auth/callback route that exchanges the confirmation code for a session.
4. Build AuthGuard in (app)/layout.tsx: while the session loads show LoadingSkeleton; no session -> redirect to /sign-in?next=<path>; sign-out clears the session and the TanStack Query cache and replaces history so Back shows no private data.
5. Write e2e/fixtures/users.ts that creates confirmed test users through the local stack's admin API using SUPABASE_SERVICE_ROLE_KEY (local only, read from the environment, never committed) and e2e/auth.spec.ts covering sign-up validation, sign-in, reload persistence, sign-out and Back.
6. Write a unit test that AuthGuard redirects when there is no session.

**Interfaces**

- Modules: MOD-F01 · Components: AuthGuard, AppShell · Env: NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY · Other: Supabase Auth (local stack)

**Acceptance criteria**

- Valid sign-up creates an account and signs in or asks for confirmation (FR-001 AC1, TC-051).
- Duplicate email shows a neutral message and no second account (FR-001 AC2, TC-052); weak or empty password is rejected per field (FR-001 AC3, TC-053).
- Valid credentials open /dashboard (FR-002 AC1, TC-054); after sign-out, Back shows no private data (FR-002 AC3, TC-056).
- Visiting an (app) route signed out redirects to /sign-in (unit test).
- e2e auth.spec.ts passes against the local stack (E2E-01 part).

**Tests**

- apps/web/tests/unit/shell/AuthGuard.test.tsx — TC-054 — `make test-web ARGS='AuthGuard'`
- apps/web/e2e/auth.spec.ts — TC-051, TC-052, TC-053, TC-054, TC-056 — `make stack-up && make e2e ARGS='auth'`

**Completion evidence**

- Playwright report for auth.spec.ts attached to the PR; Screenshot of sign-up field errors at 360 px

### IMP-110 ModelProvider interface, shared AI schemas gr-1 and io-1, provider error types

**Task:** Sprint 1 (week 1) · CODE · 5 points · lead Nidhi · release MVP

**Objective:** The provider boundary of §8 exists as code: the ModelProvider protocol, its result and metadata types, the GenerationRequest (gr-1) and ItineraryOutput (io-1) Pydantic models with exported JSON Schemas, and the shared provider error types.

**Owners and parts:** Nidhi — whole task (5 points); branch `feat/IMP-110-<short>`

**Traces to:** Stories US-034; FR-040; NFR-031, NFR-043

**Dependencies:** Prerequisites: IMP-103, §8.1 provider interface, §8.3 structured output schema, IMD-06 · Downstream: IMP-111, IMP-199, IMP-207, IMP-214, IMP-613

**Files**

- apps/api/app/ai/providers/base.py (create); apps/api/app/ai/errors.py (create); apps/api/app/schemas/ai.py (create); apps/api/app/ai/providers/finetuned.py (create); contracts/ai/gr-1.schema.json (create); contracts/ai/io-1.schema.json (create); apps/api/tests/unit/ai/test_schemas.py (create); apps/api/tests/contract/test_provider_contract.py (create)

**Implementation**

1. In schemas/ai.py define GenerationRequest (gr-1) and ItineraryOutput (io-1) exactly as §8.3 (field names, types, limits; io-1 days[].items[] reference place_id from the request's candidate list only; no price, hour, travel-time or total fields in io-1), plus ProviderResult[T] (output, usage, finish_reason, latency_ms, provider_request_id, notes), UsageMetadata (input/output/thinking tokens, all optional), HealthStatus and ModelMetadata.
2. In ai/providers/base.py define the ModelProvider Protocol: attribute name ('GEMINI'|'MOCK'|'FINETUNED_MODEL'); async generate_itinerary(GenerationRequest) -> ProviderResult[ItineraryOutput]; async modify_itinerary(ModificationRequest) -> ProviderResult[EditOperations] (R2; adapters may raise NotSupported in the MVP); async health_check() -> HealthStatus; get_model_metadata() -> ModelMetadata.
3. In ai/errors.py define the shared error hierarchy of §8 (ProviderError base; ProviderTimeout, ProviderRateLimited, ProviderQuotaExhausted, ProviderUnavailable, ProviderInvalidOutput, ProviderConfigError) each with retryable flag and failure_reason value matching ai_generations.failure_reason.
4. Create providers/finetuned.py as a Stage 2 stub whose constructor raises ProviderConfigError('fine-tuned adapter not enabled before Stage 2').
5. Add a schema export function used by `make openapi` that writes contracts/ai/gr-1.schema.json and io-1.schema.json; commit the generated files.
6. Write unit tests: valid sample io-1 parses; extra fields, missing place_id, more than 14 days or more than the item limit fail; the JSON Schemas are in sync with the models. Write the contract test skeleton parameterised over adapters (filled by IMP-207/IMP-301/IMP-512).

**Interfaces**

- Modules: MOD-B05 · Other: gr-1, io-1, ProviderResult, ModelMetadata

**Acceptance criteria**

- Vendor SDK imports appear only in app/ai/providers/gemini.py; make imports enforces it (US-034 AC1, FR-040 AC1, TC-002, TC-156).
- A test double implementing ModelProvider runs through a stub service without changes to the caller (US-034 AC2, TC-157).
- Every provider error type carries a failure_reason that exists in the ai_generations CHECK list (TC-005).
- contracts/ai/*.schema.json are regenerated by make openapi and equal the committed files.

**Tests**

- apps/api/tests/unit/ai/test_schemas.py — TC-156, TC-157 — `make test-unit ARGS='-k ai'`
- apps/api/tests/contract/test_provider_contract.py — TC-001, TC-158 — `make test-contract`

**Completion evidence**

- make test-unit and make imports output in the PR; Committed contracts/ai/*.schema.json

### IMP-111 Versioned prompt-template registry

**Task:** Sprint 1 (week 1) · CODE · 2 points · lead Manya · release MVP

**Objective:** Prompt templates are loaded by (template_id, version) from versioned files, and an unknown version fails with a clear error.

**Owners and parts:** Manya — whole task (2 points); branch `feat/IMP-111-<short>`

**Traces to:** Stories US-039; FR-045; NFR-042

**Dependencies:** Prerequisites: IMP-110, §8.5 prompt templates · Downstream: IMP-199, IMP-210, IMP-301, IMP-303, IMP-613

**Files**

- apps/api/app/ai/prompts/registry.py (create); apps/api/app/ai/prompts/templates/itinerary_generate/v1/system.txt (create); apps/api/app/ai/prompts/templates/itinerary_generate/v1/user.txt (create); apps/api/app/ai/prompts/templates/itinerary_generate/v1/meta.json (create); apps/api/tests/unit/ai/test_registry.py (create)

**Implementation**

1. Store each template as templates/<template_id>/<version>/system.txt, user.txt (placeholders in ${name} form, string.Template) and meta.json {template_id, version, output_schema_version: 'io-1', created, change_note}.
2. Write the itinerary_generate v1 texts from §8.5 (system instruction and user template that inserts the gr-1 JSON as quoted data).
3. Implement registry.load(template_id, version) returning PromptTemplate(id, version, system_text, render(request)->str, sha256 of both files); unknown id or version raises PromptTemplateNotFound naming both; version defaults to PROMPT_TEMPLATE_VERSION.
4. Add a unit test that recomputes each template's sha256 and compares with a committed hash list (tests/fixtures/prompt_hashes.json), so a text change without a new version directory fails CI (US-039 AC1).
5. Expose template_id and version so the generation record stores them (prompt_template_id, prompt_version; used from IMP-210).

**Interfaces**

- Tables: ai_generations (prompt_template_id, prompt_version) · Modules: MOD-B05 · Env: PROMPT_TEMPLATE_VERSION

**Acceptance criteria**

- registry.load('itinerary_generate','v1') returns the template; an unknown version raises an error naming the version (TC-169, TC-026).
- Editing v1 text without adding a new version fails the hash test (US-039 AC1, TC-170).
- The template and version are available for the generation record (US-039 AC2, verified end to end in IMP-210).

**Tests**

- apps/api/tests/unit/ai/test_registry.py — TC-026, TC-169, TC-170 — `make test-unit ARGS='-k prompt'`

**Completion evidence**

- make test-unit output in the PR

### IMP-112 Hello-world deployment to Vercel, Render and Supabase staging with deploy workflows

**Task:** Sprint 1 (week 1) · CODE · 5 points · lead Kirtan · release MVP

**Objective:** A push to main deploys the web skeleton to Vercel and the API container to Render, connected to the hosted Supabase staging project; /health is reachable and CORS admits only the staging web origin.

**Amended by A1 (2 November 2026):** the hosted half of this card (Render web service, Vercel project, hosted Supabase database, Render deploy hook) is superseded by IMP-217 and IMP-218 (IMD-99, IMD-103). The merged result stands: the Dockerfile, the smoke test, the local-container path and the deploy workflows that skip while unconfigured. IMP-218 rewrites the workflows for AWS.

**Owners and parts:** Kirtan — whole task (5 points); branch `feat/IMP-112-<short>`

**Traces to:** Stories US-002; FR-123; NFR-005, NFR-015, NFR-035

**Dependencies:** Prerequisites: IMP-102, IMP-103, IMP-104, IMP-113, IMP-106, §3 deployment view · Downstream: IMP-199, IMP-216

**Files**

- apps/api/Dockerfile (create); .github/workflows/deploy-staging.yml (create); .github/workflows/deploy-production.yml (create); docs/guides/deployment.md (create); apps/api/tests/smoke/test_deployed.py (create)

**Implementation**

1. Write apps/api/Dockerfile (python:3.12-slim, non-root user, install the package, never run migrations on start (the deploy workflow runs make db-migrate, IMD-38), then uvicorn on ${PORT:-8000}); build and run it locally with `docker compose up api`.
2. Create the Render web service from the Dockerfile with environment variables set in the dashboard (APP_ENV=staging, DATABASE_URL of the staging Supabase project, SUPABASE_URL, SUPABASE_JWKS_URL or SUPABASE_JWT_SECRET per OD-06, ALLOWED_ORIGINS=<staging web URL>, AI_PROVIDER=MOCK until Sprint 3).
3. Create the Vercel project for apps/web with NEXT_PUBLIC_* variables for staging and preview deployments for pull requests.
4. Write deploy-staging.yml (on push to main after ci.yml succeeds: apply migrations against staging with make db-migrate using the staging DATABASE_URL secret, then trigger the Render deploy hook and wait for the new version, then run make smoke URL=<staging api> (IMD-38)) and deploy-production.yml (manual dispatch with a release tag; same steps against production).
5. Write tests/smoke/test_deployed.py (base URL option): GET /health returns 200 and provider; GET /health/ready is called if present; an OPTIONS request from a foreign origin gets no allow header.
6. Measure the cold-start delay after 15+ minutes idle three times and record it and the wake-up routine in docs/guides/deployment.md (NFR-005).

**Interfaces**

- API: API-01 · Modules: MOD-P01 · Env: APP_ENV, DATABASE_URL, ALLOWED_ORIGINS, NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, NEXT_PUBLIC_API_BASE_URL, NEXT_PUBLIC_FEATURES_DISABLED, PORT · Other: Vercel, Render, Supabase staging

**Acceptance criteria**

- After a push to main, the staging web page loads and staging GET /health returns 200 (US-002 AC1, TC-288).
- A browser request from the staging web origin succeeds; a request from another origin is refused by CORS (US-002 AC2, NFR-015, TC-351).
- The cold-start delay is measured and written in docs/guides/deployment.md (US-002 AC3).
- If IMP-113 accounts are not ready, this task is marked blocked in docs/progress/sprint-1.md and the local container run (`docker compose up api` + make smoke URL=http://localhost:8000) passes instead.

**Tests**

- apps/api/tests/smoke/test_deployed.py — TC-288, TC-351 — `make smoke URL=<staging API URL>`

**Completion evidence**

- Staging web URL and /health response recorded in docs/progress/sprint-1.md; deploy-staging run link; Cold-start measurements in docs/guides/deployment.md

### IMP-113 Provision accounts, keys and email sender with named owners

**Task:** Sprint 1 (week 1) · HUMAN · 3 points · lead Kirtan with Junaid, Nidhi · release MVP

**Objective:** These accounts exist, each with a named owner and with its keys in the team password manager:

- the AWS account (Free plan; IMD-104);
- one Supabase project used for Auth only (IMD-101);
- Gemini (generation and embedding models);
- OpenRouteService.

The Gemini tier, data-use terms and both model identifiers are recorded.

**Amended by A1 (2 November 2026):** AWS replaces Vercel and Render. One Supabase project serves Auth for staging and production, and the database is RDS. Nidhi also records the embedding model.

**Owners and parts**

- Kirtan (lead) — GitHub, AWS account (Free plan, MFA, budget owner) and auth-only Supabase project, secrets register (1 points)
- Junaid — OpenRouteService key and email sender (1 points)
- Nidhi — Gemini API key, generation model ID, embedding model ID and data-use terms (1 points)
- One branch and pull request per part (`feat/IMP-113-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-004; NFR-013, NFR-037

**Dependencies:** Prerequisites: none · Downstream: IMP-112, IMP-217, IMP-301, IMP-312

**Files**

- docs/secrets.md (modify); docs/decisions/accounts.md (create)

**Implementation**

1. Team: create the accounts with team-owned e-mail addresses and record the owner role per account:
   - AWS account on the Free plan, owned by Kirtan, with root MFA; never enable Organizations, Control Tower or IAM Identity Center (IMD-104);
   - one Supabase project for Auth only, with e-mail confirmation as decided in step 4 (IMD-101);
   - Google AI Studio for Gemini;
   - OpenRouteService;
   - optional e-mail sender.

   No Vercel or Render account is needed (IMD-99).
2. Team: store every key in the password manager only; add rows (variable, owner, location, rotation rule) to docs/secrets.md without values.
3. Nidhi: read the official Gemini pricing and terms pages and record in docs/decisions/accounts.md: tier (free or paid), data-use terms accepted, rate limits shown, the chosen GEMINI_MODEL_ID, the chosen GEMINI_EMBEDDING_MODEL_ID (IMD-106), and the date (OD-04, OD-14).
4. Junaid: decide email confirmation on or off for staging, test one sign-up from a non-team address and record the result.
5. Claude Code may help only by drafting the docs/decisions/accounts.md template; it never handles key values.

**Interfaces**

- Modules: MOD-P01 · Env: GEMINI_API_KEY, GEMINI_MODEL_ID, GEMINI_EMBEDDING_MODEL_ID, ORS_API_KEY, SUPABASE_URL, SUPABASE_JWKS_URL, SUPABASE_JWT_SECRET · Other: OD-04, OD-06, OD-14, IMD-100, IMD-101, IMD-104 (AWS Free plan)

**Acceptance criteria**

- Each account has a named owner and a password-manager entry by the end of week 1 (US-004 AC1).
- A sign-up from a non-team address receives the confirmation email, or confirmation is off and documented (US-004 AC2).
- Gemini tier, terms and model identifier are recorded with the date (US-004 AC3).
- No key value appears in the repository (secret scan green, TC-354).

**Tests**

- docs/decisions/accounts.md — TC-354 — `Review by Junaid; CI guards job green`

**Completion evidence**

- docs/decisions/accounts.md and docs/secrets.md merged; Checklist ticked in docs/progress/sprint-1.md

### IMP-114 Stakeholder interviews round 1 and recorded findings

**Task:** Sprint 1 (week 1) · HUMAN · 3 points · lead Junaid with Krrish · release MVP

**Objective:** Five stakeholder interviews are held with consent, findings are stored in the repository and conflicts with the requirement register are raised as change requests.

**Owners and parts**

- Junaid (lead) — Run stakeholder interviews round 1 (2 points)
- Krrish — Interview guide and recorded findings (1 points)
- One branch and pull request per part (`feat/IMP-114-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-151

**Dependencies:** Prerequisites: none · Downstream: none

**Files**

- docs/acceptance/interviews-round1.md (create); docs/acceptance/interview-guide.md (create)

**Implementation**

1. Team: prepare the interview guide and consent note from blueprint §4 and Appendix D.
2. Team: hold five interviews and record anonymised notes (no names or contact details).
3. Team: summarise findings and open one GitHub issue labelled change-request per conflict with §2, citing FR IDs.
4. Claude Code may draft the guide and the summary template; it must not invent interview content.

**Interfaces**

- Other: §2 register

**Acceptance criteria**

- docs/acceptance/interviews-round1.md lists five anonymised interviews (US-151 AC1).
- Every conflict found has a change-request issue citing FR IDs (US-151 AC2).

**Tests**

- docs/acceptance/interviews-round1.md — new cases — `Review by Junaid and the supervisor`

**Completion evidence**

- Merged findings file; Change-request issue links

### IMP-115 Seed-data plan and choice of the two demo destinations

**Task:** Sprint 1 (week 1) · HUMAN · 3 points · lead Malhar · release MVP

**Objective:** A reviewed plan names two demo destinations, their sources with licences and fields, and the minimum count of usable places (100 for destination 1).

**Owners and parts:** Malhar — whole task (3 points); branch `feat/IMP-115-<short>`

**Traces to:** Stories US-152

**Dependencies:** Prerequisites: none · Downstream: IMP-206

**Files**

- data/places/PLAN.md (create); data/places/README.md (create)

**Implementation**

1. Team: choose two destinations by data availability and record the reason; set the minimum usable-place count (100 for destination 1) and the one-city fallback if destination 2 slips.
2. Team: list sources per destination with licence, URL and which fields each provides (PR-02); facts that cannot be sourced stay unavailable.
3. Claude Code may write data/places/README.md describing the file format of §5 (same as the fixture format) and a checklist for curators.
4. Team review with Junaid; record the decision in docs/decisions/.

**Interfaces**

- Tables: destinations, data_sources, places · Modules: MOD-D02 · Other: PR-02

**Acceptance criteria**

- data/places/PLAN.md names two destinations, sources per destination and the minimum usable-place count (US-152 AC1).
- Each source lists its licence and how facts are recorded (US-152 AC2); the 'unavailable, never guessed' rule is stated (US-152 AC3).

**Tests**

- data/places/PLAN.md — new cases — `Review by Junaid`

**Completion evidence**

- Merged PLAN.md with reviewer approval

### IMP-199 Sprint 1 gate SG-1: runnable skeleton and contracts in place

**Task:** Sprint 1 (week 1) · VERIFY · 0 points · lead Kirtan · release MVP

**Objective:** The team demonstrates on a clean clone that the skeleton runs locally end to end and that the contracts Sprint 2 depends on are merged, and records the result in docs/progress/gates.md.

**Owners and parts:** Kirtan — whole task (0 points); branch `feat/IMP-199-<short>`

**Traces to:** NFR-032, NFR-034, NFR-048

**Dependencies:** Prerequisites: IMP-101, IMP-102, IMP-103, IMP-104, IMP-105, IMP-106, IMP-107, IMP-108, IMP-109, IMP-110, IMP-111, IMP-112 · Downstream: none

**Files**

- docs/progress/gates.md (modify); docs/progress/sprint-1.md (modify)

**Implementation**

1. On a clean clone run in order: make setup, make stack-up, make db-up, make db-migrate, make seed, make check; record each exit code.
2. Run make api and make web; open http://localhost:3000, sign up a local user, sign in, reach the placeholder dashboard, sign out.
3. Confirm the contracts are merged: contracts/ai/gr-1 and io-1 schemas, error envelope, migrations 0001-0006, .env.example, CLAUDE.md.
4. Check staging: web URL loads and /health returns 200; if accounts are missing, record 'deployment blocked by IMP-113' with owner and date (local container smoke must pass).
5. Record the result (pass / pass with listed gaps / fail), open defects and carry-over tasks in docs/progress/gates.md under SG-1.

**Interfaces**

- API: API-01 · Tables: all MVP tables · Modules: MOD-P01 · Other: §14 SG-1

**Acceptance criteria**

- All commands of step 1 exit 0 on a clean clone.
- Local sign-up, sign-in and sign-out work against the Supabase local stack.
- CI on main is green (lint, types, imports, unit, guards, audit, api).
- Staging /health returns 200, or the deployment is recorded as blocked by accounts with an owner.
- SG-1 entry in docs/progress/gates.md states the result and the evidence links.

**Tests**

- docs/progress/gates.md — TC-335, TC-337, TC-343 — `make setup && make stack-up && make db-up && make db-migrate && make seed && make check`

**Completion evidence**

- SG-1 record in docs/progress/gates.md with command outputs and CI link

## Sprint 2 (week 2): Walking skeleton — gate SG-2

| Task | Title | Type | Lead | Parts (points) | Prerequisites | Points |
| --- | --- | --- | --- | --- | --- | --- |
| IMP-201 | Readiness endpoint and structured request logging with request IDs | CODE | Kirtan | Kirtan 3 | IMP-106, IMP-103 | 3 |
| IMP-202 | Generation record repository and lifecycle helpers (ai_generations) | CODE | Jeel | Jeel 2 | IMP-106 | 2 |
| IMP-203 | Trips API: create, list and read a trip with validation | CODE | Manal | Manal 3 | IMP-106, IMP-108, IMP-107 | 3 |
| IMP-204 | Preferences and must-visit places API with mapping to filters and ranking weights | CODE | Manal | Manal 4 | IMP-203, IMP-205 | 4 |
| IMP-205 | Provenance-preserving place import with quality gate, categories and destinations API | CODE | Malhar | Malhar 4, Jeel 3 | IMP-107 | 7 |
| IMP-206 | Curate and load demo destination 1 | DATA | Jeel | Jeel 4, Malhar 4 | IMP-205, IMP-115 | 8 |
| IMP-207 | Mock provider with scenario-based failure injection | CODE | Manya | Manya 2 | IMP-110 | 2 |
| IMP-208 | Provider factory and configuration-based selection | CODE | Nidhi | Nidhi 2 | IMP-207, IMP-103 | 2 |
| IMP-209 | Distance-based travel-time estimate (pure) | CODE | Junaid | Junaid 2 | IMP-106 | 2 |
| IMP-210 | Walking-skeleton generation job: start and poll with MOCK, save a validated plan | CODE | Het | Het 1 | IMP-202, IMP-203, IMP-208, IMP-204, IMP-111 | 1 |
| IMP-211 | Itinerary read endpoint and latest-itinerary lookup (minimal) | CODE | Het | Het 1 | IMP-210 | 1 |
| IMP-212 | Trip wizard and preference form | CODE | Manasvi | Manasvi 3 | IMP-109, IMP-203, IMP-204, IMP-214, IMP-205 | 3 |
| IMP-213 | Generate page with progress and read-only itinerary view (skeleton) | CODE | Krrish | Krrish 1 | IMP-210, IMP-211, IMP-212, IMP-214 | 1 |
| IMP-214 | OpenAPI contract v1 export, generated web client and contract check | CODE | Kirtan | Kirtan 3 | IMP-203, IMP-110 | 3 |
| IMP-215 | Two-user authorization suite for every owned route | CODE | Junaid | Junaid 3 | IMP-203, IMP-204, IMP-108, IMP-106 | 3 |
| IMP-216 | Walking-skeleton end-to-end test and staging deployment | CODE | Kirtan | Kirtan 1 | IMP-213, IMP-215, IMP-218 | 1 |
| IMP-217 | AWS staging foundation: RDS PostgreSQL, ECR, SSM, ECS Express services, OIDC deploy role and budget | CODE | Kirtan | Kirtan 4 | IMP-112, IMP-113 | 4 |
| IMP-218 | Web container and AWS deploy workflows with the release task | CODE | Junaid | Junaid 2, Manasvi 2 | IMP-217, IMP-219 | 4 |
| IMP-219 | Supabase Auth with an AWS database: auth stub bootstrap and user row mirroring | CODE | Het | Het 2 | IMP-106, IMP-108 | 2 |
| IMP-311 | RAG store: pgvector, corpus and chunk tables, item citations and retrieval record (migration 0007) | CODE | Malhar | Malhar 3 | IMP-106 | 3 |
| IMP-299 | Sprint 2 gate SG-2 (blueprint Gate 1): walking skeleton on staging | VERIFY | Kirtan | Kirtan 0 | IMP-201, IMP-202, IMP-203, IMP-204, IMP-205, IMP-206, IMP-207, IMP-208, IMP-209, IMP-210, IMP-211, IMP-212, IMP-213, IMP-214, IMP-215, IMP-216, IMP-217, IMP-218, IMP-219, IMP-311 | 0 |


### IMP-201 Readiness endpoint and structured request logging with request IDs

**Task:** Sprint 2 (week 2) · CODE · 3 points · lead Kirtan · release MVP

**Objective:** GET /health/ready (API-02) reports database, migration and provider status and returns 503 when not ready, and every request writes one structured JSON log line with request ID and latency but no secrets, emails or prompt text.

**Owners and parts:** Kirtan — whole task (3 points); branch `feat/IMP-201-<short>`

**Traces to:** Stories US-005, US-006; FR-123, FR-125; NFR-013, NFR-047

**Dependencies:** Prerequisites: IMP-106, IMP-103, §6 API-02, §3 logging rules · Downstream: IMP-299, IMP-302, IMP-511

**Files**

- apps/api/app/core/health.py (modify); apps/api/app/core/logging.py (create); apps/api/app/core/request_id.py (modify); apps/api/tests/api/test_health.py (modify); apps/api/tests/unit/core/test_logging.py (create)

**Implementation**

1. Extend core/health.py with API-02 GET /health/ready: run `select 1` with a 2 s timeout, read the Alembic revision from alembic_version and compare with the expected head, read provider status from the active provider's health_check() (MOCK returns ok), cached 60 s; return the §6 ReadinessOut {status: ready|degraded|not_ready, version, checks: {database: ok|down, migration: <head>|behind, provider: {name, model_id, status: ok|degraded|down}}}, 200, or 503 with the same body when the database is down.
2. In core/logging.py configure JSON logging (stdlib logging with a JSON formatter): fields timestamp, level, request_id, user_hash (sha256 of user_id, first 12 hex), method, route template, status, latency_ms, logger, message.
3. Add a redaction filter applied to every record: removes Authorization headers, values of keys matching *key*, *secret*, *token*, *password*, email addresses (regex) and any field named prompt, system_text, user_text or notes; prompt bodies are never logged at any level by default (FR-125 AC2).
4. Extend the request-ID middleware to time the request and emit one access log line per request (FR-125 AC1); include request_id in error envelopes (already in IMP-103).
5. Write tests: readiness 200 with a migrated DB; 503 not_ready when the DB URL points to a closed port; a log-scan test that sends a request containing an email and a fake key and asserts neither appears in captured log output (TC-358).

**Interfaces**

- API: API-01, API-02 · Tables: alembic_version · Modules: MOD-B01 · Env: LOG_LEVEL · Other: X-Request-ID header

**Acceptance criteria**

- GET /health returns status and version (FR-123 AC1, TC-288).
- With the database unreachable, GET /health/ready returns 503 not_ready naming database (FR-123 AC2, TC-289).
- Each request produces one log line with request_id and latency_ms (FR-125 AC1, TC-292).
- No log line contains a prompt body, email address, token or key value (FR-125 AC2, TC-293, TC-358).
- Responses carry X-Request-ID; a client-supplied UUID is echoed (TC-342).

**Tests**

- apps/api/tests/api/test_health.py — TC-288, TC-289, TC-342 — `make test-api ARGS='-k health'`
- apps/api/tests/unit/core/test_logging.py — TC-292, TC-293, TC-358 — `make test-unit ARGS='-k logging'`

**Completion evidence**

- Test output in the PR; One sample log line (redacted) pasted in docs/progress/sprint-2.md

### IMP-202 Generation record repository and lifecycle helpers (ai_generations)

**Task:** Sprint 2 (week 2) · CODE · 2 points · lead Jeel · release MVP

**Objective:** One repository in MOD-B06 creates and advances ai_generations rows through the status machine of §5/§8 with exact metadata, null token fields when usage is absent and no personal or prompt text.

**Owners and parts:** Jeel — whole task (2 points); branch `feat/IMP-202-<short>`

**Traces to:** Stories US-053; FR-038; NFR-022, NFR-042

**Dependencies:** Prerequisites: IMP-106, §5 ai_generations, §8 generation persistence · Downstream: IMP-210, IMP-299, IMP-405, IMP-511

**Files**

- apps/api/app/generation/repository.py (create); apps/api/app/generation/records.py (create); apps/api/tests/api/test_generation_records.py (create)

**Implementation**

1. In generation/repository.py implement create_queued(trip_id, user_id, provider, model_id, prompt_template_id, prompt_version, mapping_version, scope, request_hash, generation_settings) -> generation_id; scope in {full, day, edit}; request_hash = sha256 of the canonical request JSON (sorted keys), never the content.
2. Implement transition helpers mark_running, mark_validating, mark_repairing (each checks the current status and refuses illegal transitions), complete(outcome in {model, model_repaired, fallback_rule_based}, usage, latency_ms, repair_attempts, deterministic_repairs, validation_summary, adapter_version, model_version) and fail(failure_reason) with completed_at=now(), matching the table CHECK constraint.
3. Map UsageMetadata to input_tokens, output_tokens, thinking_tokens exactly; absent values stay NULL (never estimated, FR-038 AC2); cost_estimate_usd stays NULL until a cost basis is recorded (cost_basis).
4. Implement find_active_for_trip(trip_id) (status in queued, running, validating, repairing) and get_for_user(generation_id, user_id) (owner-scoped; 404 otherwise).
5. Guard generation_settings: only parameter names and values (temperature, max_output_tokens, thinking level); reject any key named prompt or text.
6. Write integration tests for success and failure records (all contract columns set), illegal transitions, null usage, and a scan that no email or prompt text is stored.

**Interfaces**

- Tables: ai_generations · Modules: MOD-B06 · Other: status machine §8

**Acceptance criteria**

- A completed generation row has provider, model_id, prompt_template_id, prompt_version, mapping_version, scope, status, outcome, latency_ms and completed_at set (FR-038 AC1, TC-151, TC-012).
- When usage metadata is absent, token fields are NULL (FR-038 AC2, TC-152, TC-004).
- No row contains email, name or prompt text (FR-038 AC3, TC-153).
- Illegal status transitions raise and leave the row unchanged.

**Tests**

- apps/api/tests/api/test_generation_records.py — TC-151, TC-152, TC-153, TC-004, TC-012 — `make test-api ARGS='-k generation_records'`

**Completion evidence**

- Test output in the PR

### IMP-203 Trips API: create, list and read a trip with validation

**Task:** Sprint 2 (week 2) · CODE · 3 points · lead Manal · release MVP

**Objective:** A signed-in traveller can create a draft trip (API-07), list own trips (API-08) and read one trip (API-10), with one server-side validation schema and owner-only access.

**Owners and parts:** Manal — whole task (3 points); branch `feat/IMP-203-<short>`

**Traces to:** Stories US-016; FR-007, FR-008; NFR-012, NFR-014

**Dependencies:** Prerequisites: IMP-106, IMP-108, IMP-107, §6 API-07, API-08, API-10 · Downstream: IMP-204, IMP-210, IMP-212, IMP-214, IMP-215, IMP-299, IMP-310, IMP-510

**Files**

- apps/api/app/trips/router.py (create); apps/api/app/trips/service.py (create); apps/api/app/trips/repository.py (create); apps/api/app/trips/schemas.py (create); apps/api/app/trips/domain.py (create); apps/api/tests/api/test_trips.py (create); apps/api/tests/unit/trips/test_trip_validation.py (create)

**Implementation**

1. Define TripCreate, TripOut and TripPage in trips/schemas.py exactly as §6 API-07/08/10 (extra fields forbidden; money as decimal strings per IMD-05; map API names to columns as §6 states, e.g. trip name -> trips.title, travellers.adults/children -> adults/children, budget -> budget_amount/budget_currency).
2. Put the validation rules in trips/domain.py (pure): end_date >= start_date; length 1-14 days (configurable maximum, matches the DB CHECK); adults 1-20, children 0-20; budget amount > 0 when given; currency ISO 4217 three letters; group_needs from the fixed vocabulary; destination must exist and be active; return field-level errors used for 422 VALIDATION_ERROR details.
3. Implement trips/repository.py with every query filtered by user_id from CurrentUser and deleted_at IS NULL; create inserts status 'draft', plan_revision 0; a missing or foreign trip raises NotFound (404, same as missing).
4. Implement API-07 POST /api/v1/trips (201 with TripOut; inactive or unknown destination -> 422 listing supported destination ids and names), API-08 GET /api/v1/trips (limit default 20 max 50, offset; items, total, limit, offset; newest first) and API-10 GET /api/v1/trips/{trip_id}.
5. Create the default budget_settings row in the same transaction through the budget repository function (MOD-B09 owns budget_settings; add app/budget/repository.py upsert_settings if absent); API-07 accepts no contingency_pct and creates no trip_preferences row (API-14 does, IMD-25).
6. Write unit tests for every validation rule and API tests for 201, 422 (field named), foreign trip 404, pagination bounds.

**Interfaces**

- API: API-07, API-08, API-10 · Tables: trips, budget_settings, destinations · Modules: MOD-B03, MOD-B09 · Other: error envelope

**Acceptance criteria**

- Valid input creates a trip with status draft returned with 201 and visible in API-08 (FR-007 AC1, TC-068).
- An unknown or inactive destination is rejected with the list of supported destinations (FR-007 AC2, TC-069); group needs are stored (FR-007 AC3, TC-070).
- End date before start date returns 422 naming end_date (FR-008 AC1, TC-071); a trip longer than 14 days is rejected with the limit (FR-008 AC2, TC-072); budget <= 0 is rejected (FR-008 AC3, TC-073).
- User B reading user A's trip gets 404 with no trip data (FR-005 AC1, TC-063).
- API-08 returns only the caller's non-deleted trips with limit <= 50.

**Tests**

- apps/api/tests/api/test_trips.py — TC-068, TC-069, TC-070, TC-071, TC-072, TC-073, TC-063 — `make test-api ARGS='-k trips'`
- apps/api/tests/unit/trips/test_trip_validation.py — TC-071, TC-072, TC-073 — `make test-unit ARGS='-k trip_validation'`

**Completion evidence**

- Test output in the PR; OpenAPI shows API-07/08/10 with the §6 schemas

### IMP-204 Preferences and must-visit places API with mapping to filters and ranking weights

**Task:** Sprint 2 (week 2) · CODE · 4 points · lead Manal · release MVP

**Objective:** A traveller saves and reads trip preferences and must-visit places (API-14, API-15), and a versioned pure mapping turns stored preferences into hard filters and ranking weights.

**Owners and parts:** Manal — whole task (4 points); branch `feat/IMP-204-<short>`

**Traces to:** Stories US-017, US-018; FR-009, FR-010; NFR-016

**Dependencies:** Prerequisites: IMP-203, IMP-205, §6 API-14, API-15, §9 preference mapping · Downstream: IMP-210, IMP-212, IMP-215, IMP-299, IMP-303, IMP-304

**Files**

- apps/api/app/trips/router.py (modify); apps/api/app/trips/schemas.py (modify); apps/api/app/trips/service.py (modify); apps/api/app/trips/preference_mapping.py (create); apps/api/tests/api/test_preferences.py (create); apps/api/tests/unit/trips/test_preference_mapping.py (create)

**Implementation**

1. Define PreferencesIn/PreferencesOut in trips/schemas.py per §6 (interests from the category/tag vocabulary, pace relaxed|balanced|busy, budget_priority saving|balanced|comfort, transport_pref walking|local_transport|car, accommodation_type, step_free_required, notes <= 1000 chars, must_visit_place_ids <= 10).
2. Implement API-14 PUT /api/v1/trips/{trip_id}/preferences: upsert trip_preferences and replace the trip's trip_places rows with relation must_visit in one transaction; each must-visit place must be active and belong to the trip's destination, otherwise 422 naming the place id; set trips.plan_stale = true if an itinerary exists.
3. Implement API-15 GET returning the stored preferences, must-visit places (id, name) and, per field, effect 'filter', 'rank' or 'note' from the mapping (FR-009 AC3).
4. Write trips/preference_mapping.py (pure, MAPPING_VERSION = 'pm-1'): map(prefs, trip) -> {filters: {step_free_required, child_friendly when children>0, categories_excluded}, weights: {interest, distance, price, duration, c_signal}, pace_limits}; values from §9; notes are never filters or weights (quoted data only).
5. Store notes unchanged as user text; they are passed to the model later only as quoted data (§8).
6. Write tests: each preference changes a filter or a weight (TC-077, TC-079), unknown flags never become false, must-visit of another destination is rejected, foreign trip 404.

**Interfaces**

- API: API-14, API-15 · Tables: trip_preferences, trip_places, trips · Modules: MOD-B03, MOD-B06 · Other: MAPPING_VERSION pm-1

**Acceptance criteria**

- Saved preferences are stored per trip and returned unchanged (FR-009 AC1, TC-074).
- Must-visit places are stored as trip_places relation must_visit (FR-009 AC2, TC-075); each field reports filter, rank or note (FR-009 AC3, TC-076).
- step_free_required maps to a hard filter that excludes places whose step_free is not true (FR-010 AC1, TC-077); relaxed pace reduces the long-visit weight as §9 states (FR-010 AC2, TC-078); MAPPING_VERSION is available for the generation record (FR-010 AC3, TC-079).
- Another user's trip returns 404 on both routes.

**Tests**

- apps/api/tests/api/test_preferences.py — TC-074, TC-075, TC-076 — `make test-api ARGS='-k preferences'`
- apps/api/tests/unit/trips/test_preference_mapping.py — TC-077, TC-078, TC-079 — `make test-unit ARGS='-k preference_mapping'`

**Completion evidence**

- Test output in the PR

### IMP-205 Provenance-preserving place import with quality gate, categories and destinations API

**Task:** Sprint 2 (week 2) · CODE · 7 points · lead Malhar with Jeel · release MVP

**Objective:** `make seed` imports curated or fixture place files through a provenance-preserving, idempotent import with a quality gate and report, using one shared category, tag and suitability vocabulary, and API-06 lists active destinations.

**Owners and parts**

- Malhar (lead) — Place import pipeline with provenance and quality gate, category vocabulary (4 points)
- Jeel — Places repository, destinations/categories API, basic place search (API-16) (3 points)
- One branch and pull request per part (`feat/IMP-205-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-024, US-025, US-028; FR-019, FR-022, FR-023; NFR-040

**Dependencies:** Prerequisites: IMP-107, §5 seed data and file format, §6 API-06 · Downstream: IMP-204, IMP-206, IMP-212, IMP-299, IMP-509

**Files**

- apps/api/app/places/import_pipeline.py (create); apps/api/app/places/quality_gate.py (create); apps/api/app/places/vocabulary.py (create); apps/api/app/places/seed.py (modify); apps/api/app/places/router.py (create); apps/api/app/places/repository.py (create); apps/api/app/places/schemas.py (create); apps/api/tests/unit/places/test_quality_gate.py (create); apps/api/tests/api/test_places.py (create); apps/api/tests/api/test_seed.py (modify)

**Implementation**

1. Create places/vocabulary.py as the single source of categories (sight, museum, nature, food, shopping, entertainment, religious, activity, stay), tag vocabulary and suitability flags (step_free, child_friendly, indoor as true/false/unknown=NULL); API enums and import checks import it; stay is not offered in the MVP.
2. Implement quality_gate.check(row, destination) returning reasons: missing source/licence/retrieved date or verification_status (reject), coordinates outside the destination bbox (reject), unknown category or tag (reject), price_min > price_max (reject), unparseable hours (keep the place, store hours_label 'unavailable' and no hour rows, flag), duration outside 15-480 (reject).
3. Rewrite the loading core of seed.py as import_pipeline.run(dir): read files, apply the gate, upsert sources and places idempotently by (source_id, external_ref), replace hours, deactivate (is_active=false) places that failed; write <dir>/quality_report.md (rows read, loaded, rejected with reasons, flagged, usable count vs the minimum in destination.json, shortfall stated) and exit non-zero if the minimum is not met when --strict is given.
4. Add a CI step in ci.yml that runs the gate in --check mode (no DB writes) over data/fixtures/* and data/places/*.
5. Implement API-06 GET /api/v1/destinations (active destinations: id, slug, name, country_code, timezone, currency, center and bbox) with the auth dependency.
6. Implement a basic API-16 GET /api/v1/places (destination_id required, q name search, category filter, limit/offset, active places only) for the must-visit picker; IMP-509 and IMP-604 extend it.
7. Write unit tests for every gate rule and API/integration tests: rows without source rejected and listed, report counts, second import creates no duplicates, unknown suitability stored as NULL and exposed as unknown.

**Interfaces**

- API: API-06, API-16 · Tables: destinations, data_sources, places, place_opening_hours · Modules: MOD-B04, MOD-D02 · Env: SEED_DIRS · Other: quality_report.md, vocabulary

**Acceptance criteria**

- Rows without source or verification status are rejected and listed (FR-022 AC1, TC-108); the report states rows read, loaded and rejected (FR-022 AC2, TC-109); importing twice creates no duplicates (FR-022 AC3, TC-110).
- Coordinates outside the destination are rejected (FR-023 AC1, TC-111); unknown hours format stores hours as unavailable and flags the row (FR-023 AC2, TC-112); a shortfall against the minimum is stated (FR-023 AC3, TC-113).
- A place with tags appears under the tag filter vocabulary; unknown suitability is NULL, never false (FR-019 AC1-AC2, TC-101, TC-102).
- API-06 returns only active destinations to a signed-in user and 401 without a token.
- API-16 returns active places of the requested destination filtered by name and category, paged (basic version for the must-visit picker).

**Tests**

- apps/api/tests/unit/places/test_quality_gate.py — TC-111, TC-112, TC-113, TC-102 — `make test-unit ARGS='-k quality_gate'`
- apps/api/tests/api/test_seed.py — TC-108, TC-109, TC-110, TC-101 — `make test-api ARGS='-k seed'`
- apps/api/tests/api/test_places.py — new cases — `make test-api ARGS='-k destinations'`

**Completion evidence**

- data/fixtures/sampleton/quality_report.md committed; Test output in the PR

### IMP-206 Curate and load demo destination 1

**Task:** Sprint 2 (week 2) · DATA · 8 points · lead Jeel with Malhar · release MVP

**Objective:** At least 100 usable, sourced places for demo destination 1 are in data/places/<slug>/, pass the quality gate and load on staging.

**Owners and parts**

- Jeel (lead) — Lead curation of destination 1, load and quality report (4 points)
- Malhar — Opening hours and prices with sources (4 points)
- One branch and pull request per part (`feat/IMP-206-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-026; NFR-040

**Dependencies:** Prerequisites: IMP-205, IMP-115 · Downstream: IMP-299, IMP-304, IMP-509, IMP-603

**Files**

- data/places/<slug>/destination.json (create); data/places/<slug>/places.csv (create); data/places/<slug>/opening_hours.csv (create); data/places/<slug>/sources.csv (create); data/places/<slug>/quality_report.md (create)

**Implementation**

1. Team: enter places from the sources of data/places/PLAN.md: category, coordinates, typical duration, description written by the team, source and retrieval date per row.
2. Team: enter hours and price ranges only from official or public pages named in sources.csv; mark everything else unavailable; never fill a fact from memory or from an AI assistant (PR-01, PR-03).
3. Junaid: review 20 percent of rows against their sources and record the sample in the report.
4. Claude Code may run `python -m app.places.seed data/places/<slug> --check` and summarise gate failures for the curators; it does not create or alter place facts.
5. Load on staging with SEED_DIRS=data/places/<slug> make seed against the staging DATABASE_URL (run by Kirtan).

**Interfaces**

- Tables: destinations, data_sources, places, place_opening_hours · Modules: MOD-D02 · Env: SEED_DIRS · Other: PR-01, PR-02, PR-03

**Acceptance criteria**

- The import loads at least 100 usable places and the report lists rejects (US-026 AC1).
- Every place has source, licence and last-checked date (US-026 AC2).
- Every price and hour cites a public page in sources.csv; the 20 percent review found no unsourced fact (US-026 AC3).

**Tests**

- data/places/<slug>/quality_report.md — TC-109, TC-113 — `make seed SEED_DIRS=data/places/<slug> ARGS='--check --strict'`

**Completion evidence**

- quality_report.md with counts and review sample; Staging load output in docs/progress/sprint-2.md

### IMP-207 Mock provider with scenario-based failure injection

**Task:** Sprint 2 (week 2) · CODE · 2 points · lead Manya · release MVP

**Objective:** With AI_PROVIDER=MOCK the provider returns a deterministic, schema-valid io-1 itinerary built only from the request's candidate place IDs, makes no network call, and raises each shared error on demand via MOCK_PROVIDER_SCENARIO.

**Owners and parts:** Manya — whole task (2 points); branch `feat/IMP-207-<short>`

**Traces to:** Stories US-035; FR-042; NFR-043

**Dependencies:** Prerequisites: IMP-110, §8 mock adapter · Downstream: IMP-208, IMP-299, IMP-413, IMP-512, IMP-613

**Files**

- apps/api/app/ai/providers/mock.py (create); apps/api/tests/unit/ai/test_mock_provider.py (create); apps/api/tests/contract/test_provider_contract.py (modify)

**Implementation**

1. Implement MockProvider (name 'MOCK', model id 'mock-v1') whose generate_itinerary distributes the request's candidates in their given order over the requested days (pace item limit), assigns start times from 09:00 spaced by each candidate's typical_duration_min + 30 minutes (§8.4), and sets day themes and notes marked as model text; same input -> identical output.
2. Implement scenarios from MOCK_PROVIDER_SCENARIO (honoured when APP_ENV is local, test or staging, never production; IMD-27): ok, flawed -> schema-valid io-1 for Sampleton with one overlap and one missing must-visit place, timeout -> ProviderTimeout raised at once, rate_limited -> ProviderRateLimited, quota -> ProviderQuotaExhausted, invalid_json -> ProviderInvalidOutput, unknown_place -> returns one place_id not in the candidates (for validator tests); unit tests may pass raise_error=<ProviderError> to the constructor for the other error kinds (IMD-27).
3. Return ProviderResult with usage None (so token fields stay NULL), latency_ms measured, finish_reason 'stop'; health_check returns ok; get_model_metadata returns provider MOCK, model mock-v1, adapter_version.
4. Ensure no import of httpx or google.genai in mock.py; add a test that patches socket.connect to raise and runs generate_itinerary successfully.
5. Register MOCK in the parameterised contract test (valid request -> schema-valid io-1; each scenario -> the matching shared error type).

**Interfaces**

- Modules: MOD-B05 · Env: AI_PROVIDER, MOCK_PROVIDER_SCENARIO, APP_ENV · Other: io-1

**Acceptance criteria**

- With AI_PROVIDER=MOCK no network call is made (FR-042 AC1, TC-035, TC-162).
- Each failure scenario raises the matching shared error (FR-042 AC2, TC-034, TC-163).
- Output is deterministic and passes the io-1 schema (TC-033, TC-036, TC-003).
- MOCK_PROVIDER_SCENARIO accepts exactly the seven IMD-27 values, is honoured in local, test and staging and ignored in production.

**Tests**

- apps/api/tests/unit/ai/test_mock_provider.py — TC-033, TC-034, TC-035, TC-036 — `make test-unit ARGS='-k mock_provider'`
- apps/api/tests/contract/test_provider_contract.py — TC-003, TC-162, TC-163 — `make test-contract`

**Completion evidence**

- Test output in the PR

### IMP-208 Provider factory and configuration-based selection

**Task:** Sprint 2 (week 2) · CODE · 2 points · lead Nidhi · release MVP

**Objective:** app/ai/factory.py returns the one active ModelProvider chosen by AI_PROVIDER, and the application refuses to start for an unknown value, FINETUNED_MODEL before Stage 2, or (in staging and production only) GEMINI without a usable key; in local and test GEMINI without a key starts with provider status down and generations end failed with config_error.

**Owners and parts:** Nidhi — whole task (2 points); branch `feat/IMP-208-<short>`

**Traces to:** Stories US-036; FR-043; NFR-013

**Dependencies:** Prerequisites: IMP-207, IMP-103 · Downstream: IMP-210, IMP-299, IMP-301

**Files**

- apps/api/app/ai/factory.py (create); apps/api/app/main.py (modify); apps/api/tests/unit/ai/test_factory.py (create)

**Implementation**

1. Implement get_provider(settings) -> ModelProvider (cached for the process): MOCK -> MockProvider; GEMINI -> GeminiProvider (import inside the branch; until IMP-301 the GEMINI branch raises ProviderConfigError 'Gemini adapter not implemented yet'); FINETUNED_MODEL -> refuse with 'adapter not enabled before Stage 2'.
2. Call get_provider during application start-up (lifespan) so configuration errors stop the process with a clear message (variable named, value never printed); expose the instance through a FastAPI dependency used by generation code.
3. Read keys only from Settings (environment), never from files in the repository (TC-013).
4. Write tests for each AI_PROVIDER value and the messages; assert the factory is the only module importing concrete adapters (make imports).

**Interfaces**

- Modules: MOD-B05, MOD-B01 · Env: AI_PROVIDER, GEMINI_API_KEY, GEMINI_MODEL_ID

**Acceptance criteria**

- In staging and production AI_PROVIDER=GEMINI without a key stops start-up with a clear error; in local and test it starts with provider status down (FR-043 AC1, TC-043, TC-164).
- An unknown value stops start-up with a clear error (FR-043 AC2, TC-042, TC-165).
- FINETUNED_MODEL is refused with 'not enabled before Stage 2' (FR-043 AC3, TC-037, TC-166).
- The key is read from the environment only (TC-013).

**Tests**

- apps/api/tests/unit/ai/test_factory.py — TC-013, TC-037, TC-042, TC-043, TC-164, TC-165, TC-166 — `make test-unit ARGS='-k factory'`

**Completion evidence**

- Test output in the PR

### IMP-209 Distance-based travel-time estimate (pure)

**Task:** Sprint 2 (week 2) · CODE · 2 points · lead Junaid · release MVP

**Objective:** A pure function returns a labelled fallback travel time and distance between two places for each travel mode, used whenever no cached or routing value exists.

**Owners and parts:** Junaid — whole task (2 points); branch `feat/IMP-209-<short>`

**Traces to:** Stories US-088; FR-079

**Dependencies:** Prerequisites: IMP-106, §9 travel-time fallback formula · Downstream: IMP-299, IMP-307, IMP-402, IMP-503

**Files**

- apps/api/app/routing/estimate.py (create); apps/api/app/routing/service.py (create); apps/api/tests/unit/routing/test_estimate.py (create)

**Implementation**

1. Implement estimate(from_lat, from_lon, to_lat, to_lon, mode) -> TravelEstimate(minutes, distance_m, mode, travel_source='fallback_estimate'): haversine distance d in metres, minutes = ceil(k * d / v) with k = 1.3 and v per mode from §9 (walking 75 m/min, car 400 m/min, local_transport per §9); constants live in configuration-like module constants marked Proposed.
2. Expose buffer_minutes(travel_source): 5 after routing_api, 15 after fallback_estimate (used by the validator, FR-079 AC2).
3. Create routing/service.py travel_time(place_a, place_b, mode) that for now returns the estimate; IMP-307 inserts the cache and OpenRouteService before it without changing the signature.
4. Write unit tests: known distance pairs, rounding up, identical points give 0, label is fallback_estimate, buffer values.

**Interfaces**

- Modules: MOD-B10 · Other: travel_source values routing_api | fallback_estimate

**Acceptance criteria**

- With no routing data the fallback value is returned with source fallback_estimate, shown as Estimate (FR-079 AC1, TC-236).
- Fallback values carry the 15-minute buffer, routing values the 5-minute buffer (FR-079 AC2, TC-237).
- estimate() is pure: no I/O, deterministic.

**Tests**

- apps/api/tests/unit/routing/test_estimate.py — TC-236, TC-237 — `make test-unit ARGS='-k estimate'`

**Completion evidence**

- Test output in the PR

### IMP-210 Walking-skeleton generation job: start and poll with MOCK, save a validated plan

**Task:** Sprint 2 (week 2) · CODE · 1 points · lead Het · release MVP

**Objective:** POST API-22 starts an in-process generation job that builds a minimal request from the trip, calls the active provider (MOCK), checks the io-1 schema and place IDs, and saves days, items, a version and the completed generation record in one transaction; GET API-23 reports status until completed.

**Owners and parts:** Het — whole task (1 points); branch `feat/IMP-210-<short>`

**Traces to:** Stories US-153; FR-024, FR-025, FR-038; NFR-004, NFR-008

**Dependencies:** Prerequisites: IMP-202, IMP-203, IMP-208, IMP-204, IMP-111, §6 generation lifecycle, IMD-12 · Downstream: IMP-211, IMP-213, IMP-299, IMP-305

**Files**

- apps/api/app/generation/router.py (create); apps/api/app/generation/service.py (create); apps/api/app/generation/jobs.py (create); apps/api/app/generation/pipeline.py (create); apps/api/app/generation/request_builder.py (create); apps/api/app/itinerary/service.py (create); apps/api/app/itinerary/repository.py (create); apps/api/tests/api/test_generations.py (create)

**Implementation**

1. Implement API-22 POST /api/v1/trips/{trip_id}/generations with body {mode:'ai'|'rule_based'} only (IMD-21; unknown fields rejected with 422; scope is always full and set by the server): owner check, trip completeness check (title, destination, dates, adults and a trip_preferences row, IMD-25; 422 listing missing fields), compute request_hash; if an active generation exists with the same hash return it with 200, a different active one -> 409 GENERATION_IN_PROGRESS; else create_queued and start the job; return 202 with the §6 generation body.
2. In generation/jobs.py run jobs as asyncio tasks guarded by a semaphore of 2 and a 120 s overall timeout (asyncio.timeout); when the 120 s pipeline timeout fires or an unexpected error occurs call fail('internal') with the message "Generation timed out." for the timeout (IMD-22); provider errors are classified by the pipeline, not by the job runner; add the stale-job reaper (at start-up, every 60 s, and on API-23 reads) that fails jobs older than 150 s in a non-terminal status with 'internal'.
3. In request_builder.py build a minimal gr-1 GenerationRequest from the trip, preferences, must-visit places and up to 40 active places of the destination (ordered by name for now; ranking arrives in IMP-304) with prompt template id/version from the registry and MAPPING_VERSION.
4. In pipeline.py (skeleton steps): mark_running -> provider.generate_itinerary -> mark_validating -> schema check and place IDs subset of candidates (on failure fail('invalid_output')) -> save -> complete(outcome='model'); mode 'rule_based' is refused with 422 until IMP-402.
5. In itinerary/service.py implement save_generated_plan(trip_id, user_id, output, generation_id) in one transaction: delete current itinerary_days/items/warnings of the trip, insert days (plan_date = start_date + day-1) and items (origin 'model', times and durations from the output as-is, cost fields NULL until IMP-308), increment trips.plan_revision, set trips.status 'ready', plan_stale false, insert itinerary_versions (version_no next, reason 'generation', snapshot in format snap-1 of §5.2, generation_id) and complete the generation record — all or nothing (NFR-008).
6. Implement API-23 GET /api/v1/generations/{generation_id} (owner-scoped; 404 otherwise) returning status, outcome, failure_reason, provider, repair_attempts, deterministic_repairs, validation_summary, latency_ms, itinerary_version_id, plan_revision.
7. Write API tests with MOCK: 202 then completed within the poll loop; double POST returns the same generation; different request while active -> 409; mock scenario timeout -> failed with provider_timeout (interim: IMP-403 routes it to the rule-based fallback) and the previous plan untouched; another user's generation -> 404; the record lists provider MOCK and template version.

**Interfaces**

- API: API-22, API-23 · Tables: ai_generations, itinerary_days, itinerary_items, itinerary_versions, trips, places · Modules: MOD-B06, MOD-B08, MOD-B05 · Env: AI_PROVIDER, MOCK_PROVIDER_SCENARIO · Other: gr-1, io-1

**Acceptance criteria**

- With AI_PROVIDER=MOCK, POST API-22 returns 202 and API-23 reaches completed with outcome model; days, items and a version exist and no network call to Gemini was made (US-153 AC1, TC-162).
- A repeated identical POST while active returns the same generation (200); a different request returns 409 GENERATION_IN_PROGRESS (FR-024 per §6).
- An incomplete trip returns 422 listing the missing fields (TC-115).
- A failing job leaves the previous plan intact and the record failed with a failure_reason (NFR-008).
- The generation record names provider, model_id, prompt_template_id, prompt_version and mapping_version (TC-012, TC-151).

**Tests**

- apps/api/tests/api/test_generations.py — TC-012, TC-115, TC-151, TC-162 — `make test-api ARGS='-k generations'`

**Completion evidence**

- Test output in the PR; Known gaps list (no recalculation, no validator rules beyond schema and IDs, no edits) recorded in docs/progress/sprint-2.md

### IMP-211 Itinerary read endpoint and latest-itinerary lookup (minimal)

**Task:** Sprint 2 (week 2) · CODE · 1 points · lead Het · release MVP

**Objective:** GET API-24 returns the trip's current saved itinerary (days, items, warnings, plan_revision, labels) and GET API-09 returns the caller's most recently saved itinerary reference.

**Amended by A1 (2 November 2026):** every item carries `sources: []` (IMD-116). IMP-316 fills it.

**Owners and parts:** Het — whole task (1 points); branch `feat/IMP-211-<short>`

**Traces to:** Stories US-153; FR-059; NFR-012

**Dependencies:** Prerequisites: IMP-210, §6 API-24, API-09 · Downstream: IMP-213, IMP-299, IMP-410

**Files**

- apps/api/app/itinerary/router.py (create); apps/api/app/itinerary/schemas.py (create); apps/api/app/itinerary/repository.py (modify); apps/api/tests/api/test_itinerary.py (create)

**Implementation**

1. Define ItineraryOut per §6 API-24: trip_id, plan_revision, plan_stale, outcome and provider of the source generation, days[{day_number, plan_date, theme (with origin ai), items[{id, position, place{id,name,category,lat,lon}, slot_type, start_time, duration_min, is_locked, note, note_origin, cost{min,max,currency,label}|null, travel_from_prev{minutes, distance_m, mode, source}|null, sources[] (always [] until IMP-316; SourceRef of Amendment A1 §7.1)}]}], warnings[] (empty until IMP-405).
2. Implement API-24 GET /api/v1/trips/{trip_id}/itinerary (optional query version_id reserved for IMP-610; returns 404 NOT_FOUND with message 'no itinerary yet' when none exists) with owner scoping on the trip.
3. Implement API-09 GET /api/v1/itineraries/latest returning {trip_id, trip_name, plan_revision, updated_at} for the caller's most recently updated trip that has an itinerary, or 404 when none (full reopen behaviour in IMP-410).
4. Load days and items with two queries (no N+1) ordered by day_number, position.
5. Write API tests: read after the IMP-210 generation, empty trip 404, foreign trip 404, latest returns the newest trip.

**Interfaces**

- API: API-24, API-09 · Tables: itinerary_days, itinerary_items, itinerary_warnings, trips, places, ai_generations · Modules: MOD-B08

**Acceptance criteria**

- After a MOCK generation, API-24 returns the saved days and items in order with plan_revision (US-153 AC1).
- A trip without itinerary returns 404 with the envelope; a foreign trip returns 404 (FR-005 AC2, TC-064).
- API-09 returns the caller's most recent itinerary reference only.

**Tests**

- apps/api/tests/api/test_itinerary.py — TC-064 — `make test-api ARGS='-k itinerary'`

**Completion evidence**

- Test output in the PR

### IMP-212 Trip wizard and preference form

**Task:** Sprint 2 (week 2) · CODE · 3 points · lead Manasvi · release MVP

**Objective:** /trips/new walks the traveller through destination, dates, travellers and group needs, budget, then preferences and must-visit places, using client checks that mirror the server rules, and creates the trip through API-07 and API-14.

**Owners and parts:** Manasvi — whole task (3 points); branch `feat/IMP-212-<short>`

**Traces to:** Stories US-016, US-017; FR-007 to FR-009; NFR-025

**Dependencies:** Prerequisites: IMP-109, IMP-203, IMP-204, IMP-214, §7 /trips/new, IMP-205 · Downstream: IMP-213, IMP-299, IMP-410, IMP-510, IMP-708

**Files**

- apps/web/app/(app)/trips/new/page.tsx (create); apps/web/components/trips/TripWizard.tsx (create); apps/web/components/trips/PreferenceForm.tsx (create); apps/web/lib/validation/trip.ts (create); apps/web/tests/unit/trips/TripWizard.test.tsx (create); apps/web/e2e/trip-create.spec.ts (create)

**Implementation**

1. Write lib/validation/trip.ts zod schemas that mirror §6 API-07/API-14 rules (dates, 1-14 days, adults 1-20, children 0-20, budget > 0 with currency, notes <= 1000, max 10 must-visit places); server 422 details are still mapped onto fields.
2. Build TripWizard as a stepper (Destination from API-06, Dates, Travellers and group needs, Budget, Preferences) with Back/Next, keyboard-operable controls, labels and inline errors; on the last step call API-07 then API-14 and route to /trips/{id}/generate.
3. Build PreferenceForm (interests, pace, budget priority, transport, accommodation type, step-free required, notes with a 'do not enter personal details' hint, must-visit picker searching the destination's places via API-16 (basic search from IMP-205)) showing per-field 'filters / ranks / note only' text from API-15 after save.
4. Use the generated client (lib/api/client.ts) and TanStack Query mutations; on success invalidate the trips query; show ErrorState with request_id on 5xx.
5. Write unit tests for validation messages and step navigation, and e2e trip-create.spec.ts: sign in, create a trip with preferences, land on the generate page.

**Interfaces**

- API: API-06, API-07, API-14, API-15, API-16 · Modules: MOD-F02 · Components: TripWizard, PreferenceForm, ErrorState, LoadingSkeleton · Env: NEXT_PUBLIC_API_BASE_URL · Other: zod, react-hook-form

**Acceptance criteria**

- Valid input creates a draft trip and opens /trips/{id}/generate (FR-007 AC1, TC-068).
- End date before start date shows the field message before submission and the server's 422 is mapped to the same field (FR-008 AC1).
- Preferences and must-visit places are saved and each field shows its effect (FR-009 AC1-AC3, TC-076).
- The wizard is fully operable by keyboard (unit test with user-event tab sequence).

**Tests**

- apps/web/tests/unit/trips/TripWizard.test.tsx — TC-068, TC-076 — `make test-web ARGS='TripWizard'`
- apps/web/e2e/trip-create.spec.ts — TC-068 — `make e2e ARGS='trip-create'`

**Completion evidence**

- Playwright report and screenshots at 360 and 1280 px in the PR

### IMP-213 Generate page with progress and read-only itinerary view (skeleton)

**Task:** Sprint 2 (week 2) · CODE · 1 points · lead Krrish · release MVP

**Objective:** /trips/[tripId]/generate starts a generation, polls its status with backoff and opens /trips/[tripId]/itinerary, which shows the saved days and items read from API-24 without computing anything in the browser.

**Owners and parts:** Krrish — whole task (1 points); branch `feat/IMP-213-<short>`

**Traces to:** Stories US-153; FR-024, FR-025

**Dependencies:** Prerequisites: IMP-210, IMP-211, IMP-212, IMP-214, §7 generate and itinerary screens · Downstream: IMP-216, IMP-299, IMP-309

**Files**

- apps/web/app/(app)/trips/[tripId]/generate/page.tsx (create); apps/web/components/generation/GenerationProgress.tsx (create); apps/web/app/(app)/trips/[tripId]/itinerary/page.tsx (create); apps/web/components/itinerary/DayColumn.tsx (create); apps/web/components/itinerary/ItineraryItemCard.tsx (create); apps/web/tests/unit/generation/GenerationProgress.test.tsx (create)

**Implementation**

1. Generate page: a Generate button calls API-22 with body {mode: 'ai'} (IMD-21); disable it while a request is in flight; store the generation id in the URL query so reload resumes polling.
2. GenerationProgress polls API-23 every 2 s backing off to 5 s, shows status steps (queued, running, validating, repairing), elapsed time, and stops on completed or failed; after 160 s non-terminal it shows 'connection problem, reload' (IMD-12).
3. On completed navigate to /trips/{id}/itinerary; on failed show the failure message for failure_reason with a retry button; on 409 GENERATION_IN_PROGRESS resume polling the active generation.
4. Itinerary page (read-only in Sprint 2): fetch API-24, render one DayColumn per day with ItineraryItemCard (place name, start time, duration, slot type); show EmptyState with a link to generate when API-24 returns 404.
5. The page never invents times, prices, routes or success; every value shown comes from the API response (§7 rule).
6. Write unit tests for the polling state machine with fake timers (completed, failed, timeout after 160 s).

**Interfaces**

- API: API-22, API-23, API-24 · Modules: MOD-F02, MOD-F04 · Components: GenerationProgress, DayColumn, ItineraryItemCard, EmptyState, ErrorState · Other: TanStack Query refetchInterval

**Acceptance criteria**

- Pressing Generate with MOCK shows progress and then the saved itinerary (US-153 AC1).
- Double click starts one generation only.
- A failed generation shows the reason and a retry button; a status still running after 160 s shows the reload message (unit test).
- No time, price or route is computed in the browser (code review checklist item).

**Tests**

- apps/web/tests/unit/generation/GenerationProgress.test.tsx — new cases — `make test-web ARGS='GenerationProgress'`

**Completion evidence**

- Screen recording or screenshots of generate -> itinerary in the PR

### IMP-214 OpenAPI contract v1 export, generated web client and contract check

**Task:** Sprint 2 (week 2) · CODE · 3 points · lead Kirtan · release MVP

**Objective:** `make openapi` writes contracts/openapi.v1.json and regenerates apps/web/lib/api/schema.d.ts, every MVP endpoint of §6 is declared with its request and response models, and CI fails when the committed contract is stale.

**Amended by A1 (2 November 2026):** the Item of `ItineraryOut` (API-24, also in `EditResultOut`) declares `sources[]` of type `SourceRef` `{chunk_id, kind, title, source_name, licence, attribution_text, url, retrieved_on}` (Amendment A1 §7.1, IMD-116). It is part of contract v1 from the start, and IMP-211 returns an empty list until IMP-316. `GenerationOut` (API-23) also declares `retrieval_mode`, `embedding_model_id` and `retrieval_ms` (null until IMP-316).

**Owners and parts:** Kirtan — whole task (3 points); branch `feat/IMP-214-<short>`

**Traces to:** Stories US-007; NFR-033

**Dependencies:** Prerequisites: IMP-203, IMP-110, §6 endpoint catalogue, IMD-06 · Downstream: IMP-212, IMP-213, IMP-299, IMP-601

**Files**

- contracts/openapi.v1.json (create); apps/api/app/openapi_export.py (create); apps/web/lib/api/schema.d.ts (create); apps/web/lib/api/client.ts (create); apps/api/tests/contract/test_openapi_contract.py (create); .github/workflows/ci.yml (modify)

**Implementation**

1. Declare every MVP endpoint of §6 (API-01..04, 06..17, 19..38) with its path, method, request and response models in the owning module's router; endpoints not yet implemented raise a NotImplementedYet domain error mapped to 501 with code NOT_IMPLEMENTED (temporary; the authz suite skips 501 routes) (IMD-37); no route may return 501 after SG-6.
2. Write app/openapi_export.py invoked by `make openapi` to write contracts/openapi.v1.json (sorted keys) and the AI JSON Schemas; run `npx openapi-typescript contracts/openapi.v1.json -o apps/web/lib/api/schema.d.ts`.
3. Write lib/api/client.ts with openapi-fetch: base URL from NEXT_PUBLIC_API_BASE_URL, bearer token from the Supabase session, one silent session refresh on 401 then redirect to /sign-in, parse the error envelope into a typed ApiError {code, message, request_id, details}.
4. Make `make openapi-check` regenerate into a temp dir and diff; add it to the lint-types job in ci.yml.
5. Write tests/contract/test_openapi_contract.py asserting that every MVP API id of §6 maps to exactly one path+method in the document and no non-MVP path is exposed.

**Interfaces**

- API: all MVP endpoints · Modules: MOD-B01, MOD-F01, MOD-P01 · Env: NEXT_PUBLIC_API_BASE_URL · Other: openapi-typescript, openapi-fetch

**Acceptance criteria**

- contracts/openapi.v1.json lists all 36 MVP endpoints with their schemas and no T1/R2 endpoint (test_openapi_contract).
- A change to a response model without regenerating the contract fails make openapi-check in CI.
- The web app compiles against the generated types (make typecheck).
- Changes under contracts/ need a reviewer from the other squad via CODEOWNERS (US-007 AC2, NFR-033).

**Tests**

- apps/api/tests/contract/test_openapi_contract.py — TC-336 — `make openapi-check && make test-contract ARGS='-k openapi'`

**Completion evidence**

- Committed contract file; CI run showing openapi-check

### IMP-215 Two-user authorization suite for every owned route

**Task:** Sprint 2 (week 2) · CODE · 3 points · lead Junaid · release MVP

**Objective:** An automated suite exercises every implemented owned route with a second user and proves that foreign resources answer 404 and are never changed.

**Owners and parts:** Junaid — whole task (3 points); branch `feat/IMP-215-<short>`

**Traces to:** Stories US-013; FR-005; NFR-012

**Dependencies:** Prerequisites: IMP-203, IMP-204, IMP-108, IMP-106 · Downstream: IMP-216, IMP-299, IMP-702

**Files**

- apps/api/tests/authz/test_ownership.py (create); apps/api/tests/authz/route_matrix.py (create); docs/guides/authz-suite.md (create)

**Implementation**

1. Write route_matrix.py: one entry per owned MVP route (API id, method, path template, how to build a valid request for user A's resource); a test fails if an implemented owned route is missing from the matrix (compare with app.routes, skipping 501 routes).
2. Fixture: users A and B (tokens + auth.users + profiles), A owns a trip with preferences, a generation and an itinerary (via MOCK).
3. For each matrix entry call it as B with A's identifiers: expect 404 NOT_FOUND with no A data in the body; for writes, re-read as A and assert nothing changed.
4. Child resources (generation, itinerary items, versions) inherit the trip's ownership (TC-346).
5. Document how to add a route to the matrix in docs/guides/authz-suite.md and run the suite in the CI api job (make test-authz).

**Interfaces**

- API: API-07..15, 19..38 as implemented · Tables: trips, trip_preferences, trip_places, ai_generations, itinerary_* · Modules: MOD-B02

**Acceptance criteria**

- B requesting A's trip gets 404 and nothing about the trip (FR-005 AC1, TC-063, TC-345).
- Every read and write of A's child resources by B is refused (FR-005 AC2, TC-064, TC-346).
- Every implemented owned endpoint is exercised by the suite in CI (FR-005 AC3, TC-065); a new unlisted route fails the suite.

**Tests**

- apps/api/tests/authz/test_ownership.py — TC-063, TC-064, TC-065, TC-345, TC-346 — `make test-authz`

**Completion evidence**

- CI api job output listing the route matrix results

### IMP-216 Walking-skeleton end-to-end test and staging deployment

**Task:** Sprint 2 (week 2) · CODE · 1 points · lead Kirtan · release MVP

**Objective:** A Playwright journey (sign in, create trip, generate with MOCK, see saved itinerary) passes locally and in the e2e workflow, and the same path is run on staging.

**Amended by A1 (2 November 2026):** staging is the AWS deployment of IMP-217 and IMP-218. The prerequisite IMP-112 becomes IMP-218.

**Owners and parts:** Kirtan — whole task (1 points); branch `feat/IMP-216-<short>`

**Traces to:** Stories US-153; NFR-048

**Dependencies:** Prerequisites: IMP-213, IMP-215, IMP-218 · Downstream: IMP-299, IMP-701

**Files**

- apps/web/e2e/journey.spec.ts (create); .github/workflows/e2e.yml (create); docs/progress/sprint-2.md (modify)

**Implementation**

1. Write e2e/journey.spec.ts: create a confirmed test user (fixtures/users.ts), sign in, create a trip in Sampleton through the wizard, press Generate, wait for completed, assert at least one day with items is shown and the outcome is from provider MOCK.
2. Make `make e2e` start the API with AI_PROVIDER=MOCK, APP_ENV=test against the local stack database (migrated and seeded) and the web dev server, then run Playwright.
3. Write .github/workflows/e2e.yml (on push to main and nightly): set up the Supabase CLI, make stack-up, db-migrate against 127.0.0.1:54322, make seed, export keys from `supabase status -o env` into the job environment, run make e2e, upload the Playwright report.
4. Run the same path manually on AWS staging (Amendment A1 §4; deployed by IMP-218) with AI_PROVIDER=MOCK and record what each layer did (web, API, database, provider interface, generation record row) and the known gaps in docs/progress/sprint-2.md.

**Interfaces**

- API: API-06, API-07, API-14, API-22, API-23, API-24 · Tables: trips, ai_generations, itinerary_* · Modules: MOD-P01 · Components: TripWizard, GenerationProgress, DayColumn · Env: AI_PROVIDER, SUPABASE_SERVICE_ROLE_KEY · Other: Playwright

**Acceptance criteria**

- journey.spec.ts passes locally and in e2e.yml with MOCK and no Gemini call (US-153 AC1, TC-369).
- On staging the path runs from the browser and a generation record row exists (US-153 AC2).
- Known gaps are listed for the gate review (US-153 AC3).

**Tests**

- apps/web/e2e/journey.spec.ts — TC-369 — `make stack-up && make db-migrate && make seed && make e2e ARGS='journey'`

**Completion evidence**

- e2e.yml run link with Playwright report; Staging walkthrough notes in docs/progress/sprint-2.md

### IMP-217 AWS staging foundation: RDS PostgreSQL, ECR, SSM, ECS Express services, OIDC deploy role and budget

**Task:** Sprint 2 (week 2) · CODE · 4 points · lead Kirtan · release MVP (Amendment A1)

**Objective:** A documented, repeatable AWS set-up in ap-south-1 gives the team:

- a private RDS PostgreSQL 16 database that supports pgvector;
- two ECR repositories;
- SSM SecureString parameters for every secret;
- one ECS Express Mode service each for the staging API and the staging web app, behind one shared HTTPS load balancer;
- an OIDC role that GitHub Actions can assume without stored keys;
- budget alerts.

**Owners and parts:** Kirtan — whole task (4 points); branch `feat/IMP-217-whole-task`

**Traces to:** Stories US-002, US-004, US-163; FR-123; NFR-005, NFR-013, NFR-015, NFR-035, NFR-049

**Dependencies:** Prerequisites: IMP-112, IMP-113 (AWS account and auth-only Supabase project exist), Amendment A1 §4, IMD-99 to IMD-104 · Downstream: IMP-218, IMP-216, IMP-299, IMP-801

**Files**

- infra/aws/README.md (create)
- infra/aws/env.sh.example (create)
- infra/aws/01_budget.sh, 02_rds.sh, 03_ecr.sh, 04_ssm.sh, 05_iam.sh, 06_services.sh (create)
- infra/aws/services/api.staging.json.tmpl, infra/aws/services/web.staging.json.tmpl (create; complete service configuration with `${IMAGE}` and the other placeholders of Amendment A1 §4.3)
- docs/guides/aws-setup.md (create)
- docs/secrets.md (modify)
- docs/guides/deployment.md (modify)
- .gitignore (modify: infra/aws/env.sh)

**Implementation**

1. **Scripts.** Write idempotent bash scripts (AWS CLI v2) that:
   - read the untracked `infra/aws/env.sh` (copied from `env.sh.example`; region `ap-south-1`, account ID, names of §4.1 of Amendment A1);
   - check that a resource exists before creating it;
   - print only resource names and ARNs, never a secret value.

   Claude Code writes and checks the scripts. Kirtan runs them from his own terminal or AWS CloudShell. Claude Code never holds AWS credentials and never runs them against the account.
2. **Budget (01_budget.sh).** A monthly cost budget of USD 50 with e-mail alerts at USD 25 and USD 50 (NFR-049). The guide warns never to enable AWS Organizations, Control Tower or IAM Identity Center on the Free plan.
3. **Database (02_rds.sh).**
   - RDS PostgreSQL 16 (current minor), `db.t4g.micro` or the smallest class the plan allows, 20 GB gp3, single-AZ;
   - publicly accessible = false, backup retention 1 day, deletion protection on, default VPC;
   - security group `group12-rds` with no inbound rule yet (step 6 adds 5432 from the API service's group);
   - the master password is set by the owner and is not RDS-managed (an RDS-managed password rotates every 7 days and would leave `DATABASE_URL` stale);
   - database `travel_staging`. `travel_production` is created later by IMP-801.
4. **Registry and parameters.**
   - **03_ecr.sh:** repositories `group12-api` and `group12-web`, scan on push, keep the newest 10 images.
   - **04_ssm.sh:** creates the SecureString parameters `/group12/staging/DATABASE_URL`, `GEMINI_API_KEY`, `ORS_API_KEY` and, in HS256 mode, `SUPABASE_JWT_SECRET`.
     - The value is read with `read -s` in the owner's own terminal and passed to `aws ssm put-parameter --cli-input-json file:///dev/stdin` on standard input, never as a command-line argument.
     - It is never written to a file or echoed.
     - `DATABASE_URL` ends with `?sslmode=require`.
5. **Roles (05_iam.sh).**
   - ECS task execution role `group12-ecs-execution`: ECR pull, CloudWatch Logs, and `ssm:GetParameters` plus `kms:Decrypt` (aws/ssm key) on `/group12/*`.
   - Express Mode infrastructure role `group12-ecs-infrastructure`, with the AWS managed policy named in the ECS Express Mode documentation.
   - GitHub OIDC provider `token.actions.githubusercontent.com` and role `group12-github-deploy`:
     - trust limited to the subjects `repo:het-lathiya/Group12:ref:refs/heads/main`, `repo:het-lathiya/Group12:ref:refs/tags/v*` and `repo:het-lathiya/Group12:environment:production` (a job that uses a GitHub environment presents an environment subject);
     - permissions exactly as Amendment A1 §4.4, with action names checked against the AWS CLI reference and listed in the guide.
6. **Services (06_services.sh), in this order.**
   1. Build and push a first API image from the current main with the IMP-112 Dockerfile.
   2. Create the Express Mode service `group12-api-staging` from `services/api.staging.json.tmpl`:
      - port 8000, health check `/health`, 256 CPU units, 512 MiB, minimum and maximum 1 task;
      - plain environment and SSM `secrets`;
      - `DB_AUTH_STUB=true`, `AI_PROVIDER=MOCK` until IMP-316 switches it;
      - Express Mode default networking.
   3. Read the API service's security group and subnets. Add the inbound rule TCP 5432 from that group on `group12-rds`. Record the group and the subnets as the repository variables `API_TASKS_SECURITY_GROUP` and `AWS_SUBNET_IDS`.
   4. Read the API service's HTTPS URL. Build the first web image with `NEXT_PUBLIC_API_BASE_URL=<API URL>/api/v1` and the other `NEXT_PUBLIC_*` values (a temporary Dockerfile outside the repository until IMP-218 commits the real one), then push it.
   5. Create `group12-web-staging` from `services/web.staging.json.tmpl` (port 3000, health check `/`, 256/512, minimum and maximum 1).
   6. Read the web URL. Set `ALLOWED_ORIGINS` to it in the API template and update the API service with the full rendered configuration.
   7. Set log retention to 7 days.
7. **Supabase Auth.** In the auth-only Supabase project, set the Site URL and redirect URLs to the staging web URL and `<web URL>/auth/callback`.
8. **Repository variables.** Add the repository variables of Amendment A1 §4.4 for staging, including `ECS_EXECUTION_ROLE_ARN`, `ECS_INFRASTRUCTURE_ROLE_ARN`, `AWS_SUBNET_IDS` and `API_TASKS_SECURITY_GROUP`. `docs/secrets.md` lists every secret and variable name with owner and location, and no value.
9. **Guide.** Write `docs/guides/aws-setup.md`:
   - the run order and every command with placeholders;
   - how to verify each resource;
   - how to stop or tear down (scale to zero or delete services, snapshot and delete RDS);
   - a cost table built with the AWS Pricing Calculator and marked as an estimate;
   - what to do if the Free plan refuses a service (stop; team decision per IMD-104).
10. **Checks.** Check every script with `bash -n` and, when available, `shellcheck`. Update `docs/guides/deployment.md`: the Render and Vercel sections become pointers to the AWS guide (IMD-99).

**Interfaces**

- Modules: MOD-P01
- Env: DATABASE_URL, GEMINI_API_KEY, ORS_API_KEY, SUPABASE_URL, SUPABASE_JWKS_URL, SUPABASE_JWT_SECRET, ALLOWED_ORIGINS, DB_AUTH_STUB, AI_PROVIDER, NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, NEXT_PUBLIC_API_BASE_URL
- Other: Amendment A1 §4; AWS ECS Express Mode, RDS, ECR, SSM Parameter Store, IAM OIDC, AWS Budgets

**Acceptance criteria**

- The staging API URL answers `GET /health` with 200 over HTTPS and the staging web URL serves the landing page (US-002 AC1, TC-288).
- RDS is not publicly accessible: a connection attempt from outside the VPC fails, and the API connects with `sslmode=require` (TC-433).
- The services' task definitions carry `DATABASE_URL`, `GEMINI_API_KEY`, `ORS_API_KEY` (and `SUPABASE_JWT_SECRET` if used) only as SSM references; no secret value is in the repository, an image or plain environment (TC-434, TC-354).
- Budget alerts at USD 25 and USD 50 exist (NFR-049, TC-435).
- The deploy role's trust policy admits only main, `v*` tags and the `production` environment of het-lathiya/Group12 (TC-436).
- Every live criterion is verified from Kirtan's recorded output; until it exists it is reported as "not verified".

**Tests**

- infra/aws/*.sh — script syntax — `bash -n infra/aws/*.sh`
- apps/api/tests/smoke/test_deployed.py — TC-288, TC-351 — `make smoke URL=<staging API URL>`

**Completion evidence**

- docs/guides/aws-setup.md merged; staging URLs and the /health response in the part record; trust-policy and budget screenshots (no secrets); `aws ecs describe-task-definition` output showing only `secrets` references (values redacted)

### IMP-218 Web container and AWS deploy workflows with the release task

**Task:** Sprint 2 (week 2) · CODE · 4 points · lead Junaid with Manasvi · release MVP (Amendment A1)

**Objective:** The web app has a production container image. A merge to `main` then:

1. builds both images tagged with the commit SHA;
2. runs the release task (auth stub, migrations, optional seed, RAG index) as a one-off ECS task;
3. updates the staging services only if the release task succeeds;
4. passes the deployed smoke test.

A manual run from a tag does the same for production.

**Owners and parts**

- Junaid (lead) — AWS deploy workflows, release task and deployed smoke checks (2 points)
- Manasvi — Web production image: standalone Next.js Dockerfile and local compose service (2 points)
- One branch and one pull request for the card (IMD-66); each commit is authored by the owner of the part it belongs to

**Traces to:** Stories US-002, US-163; FR-123; NFR-013, NFR-015, NFR-035, NFR-048

**Dependencies:** Prerequisites: IMP-217, IMP-219, Amendment A1 §4.3 to §4.6, IMD-102, IMD-103 · Downstream: IMP-216, IMP-299, IMP-801

**Files**

- apps/web/next.config.ts (modify; Manasvi)
- apps/web/Dockerfile (create; Manasvi)
- apps/web/.dockerignore (create; Manasvi)
- docker-compose.yml (modify: `web` service; Manasvi; and the `api` service build context; Junaid)
- .dockerignore at the repository root (create; Junaid: `.git`, `**/node_modules`, `**/.next`, `**/.venv`, `**/.env*`, `infra/aws/env.sh`)
- .github/workflows/ci.yml (modify only if a job builds the API image: new build context; Junaid)
- apps/api/Dockerfile (modify: repository-root build context, `data/places` and `data/guides` copied, `BUILD_VERSION` build argument; Junaid)
- apps/api/scripts/release.sh (create; Junaid)
- .github/workflows/deploy-staging.yml (modify; Junaid)
- .github/workflows/deploy-production.yml (modify; Junaid)
- apps/api/tests/smoke/test_deployed.py (modify; Junaid)
- docs/guides/deployment.md (modify; Junaid)

**Implementation**

1. **(Manasvi) Web image.**
   - Set `output: 'standalone'` in `next.config.ts`.
   - Write a multi-stage `apps/web/Dockerfile` on `node:22-slim`: `npm ci`, `next build` with the four `NEXT_PUBLIC_*` values and `BUILD_VERSION` as build arguments.
   - The runtime stage copies `.next/standalone`, plus `.next/static` into `.next/static` and `public` into `public` (the standalone output does not include them).
   - It runs `node server.js` as a non-root user on `PORT` 3000 with `HOSTNAME=0.0.0.0`.
   - Add `.dockerignore` (node_modules, .next, .env*) and a `web` service in `docker-compose.yml` for local smoke.
   - The image contains no secret and no `.env` file.
2. **(Junaid) API image.**
   - The API image is built from the repository root. Update every place that builds it: the `api` service of `docker-compose.yml` and any CI job.
   - The root `.dockerignore` keeps `.env` files, virtual environments, `node_modules` and `.git` out of the context.
   - The image includes `data/places/` and `data/guides/` (when present) and `scripts/release.sh`, and sets `BUILD_VERSION` from the build argument.
   - It still never migrates on start (IMD-38).
3. **(Junaid) Release script.** `apps/api/scripts/release.sh` (POSIX sh, `set -eu`) runs:
   1. `python -m app.db.auth_stub --if-missing`;
   2. `alembic upgrade head`;
   3. when `SEED_DIRS` is set, `python -m app.places.seed` for each directory;
   4. when the module `app.rag.index` exists, `python -m app.rag.index --strict`. Exit code 3 (embedding provider unavailable) is printed as a warning and does not fail the release; exit codes 1 and 2 fail it (Amendment A1 §4.5).

   Each step prints one line and no secret. IMP-313 makes the index step unconditional.
4. **(Junaid) Deploy workflows.** Rewrite `deploy-staging.yml` (push to main after `ci.yml` succeeds) and `deploy-production.yml` (manual dispatch with a release tag, GitHub environment `production` with Kirtan as required reviewer) as Amendment A1 §4.5:
   1. OIDC credentials (`aws-actions/configure-aws-credentials`, role from `AWS_DEPLOY_ROLE_ARN`);
   2. build and push the API image tagged with the SHA;
   3. run the release task:
      - read the API service's current task definition, replace the image with the new one and register it as the family `group12-api-<env>-release` (`register-task-definition`), because `run-task` cannot override an image;
      - run it with `aws ecs run-task` (command override `sh scripts/release.sh`, subnets `AWS_SUBNET_IDS`, security group `API_TASKS_SECURITY_GROUP`, public IP on);
      - wait, print its CloudWatch log lines into the job log, and fail on a non-zero exit;
   4. update the API service with `aws ecs update-express-gateway-service`, sending the full configuration rendered from `infra/aws/services/api.<env>.json.tmpl` with the new image, and wait;
   5. build and push the web image with the environment's `NEXT_PUBLIC_*` values and update the web service the same way from its template;
   6. `make smoke URL=<API URL>`.

   When a required repository variable is missing, the job ends green with "AWS staging not configured (blocked by IMP-217)" (or "production … IMP-801").
5. **(Junaid) Smoke tests.** Extend `tests/smoke/test_deployed.py`:
   - `/health` reports the deployed `BUILD_VERSION`;
   - `/health/ready` is called when present;
   - an OPTIONS request from the configured web origin gets the allow header, and one from a foreign origin does not.
6. **(Junaid) Forced failure.** Add a `workflow_dispatch` input `simulate_release_failure` to `deploy-staging.yml` that replaces the release command with `false`.
   - Because the OIDC trust admits only `main`, the first real deploy and the forced-failure run happen after this pull request merges.
   - The operator records both run links, and IMP-299 checks them (TC-437, TC-438).
   - Before merge, verify the workflow with `actionlint` (if available) and a dry read of every command.
7. **(Junaid) Guide.** Update `docs/guides/deployment.md`: the deploy flow, rollback (redeploy the previous tag's images; production migrations are forward only) and the local container smoke.

**Interfaces**

- API: API-01, API-02
- Modules: MOD-P01
- Env: BUILD_VERSION, PORT, SEED_DIRS, NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, NEXT_PUBLIC_API_BASE_URL, NEXT_PUBLIC_FEATURES_DISABLED
- Other: repository variables of Amendment A1 §4.4; Amazon ECR, ECS Express Mode

**Acceptance criteria**

- After a merge to main, the staging workflow builds both images with the commit SHA, the release task exits 0, both services are updated and `make smoke` passes against the staging API (US-002 AC1, TC-437, TC-288). This is verified on the first main run after merge and recorded at SG-2 (IMP-299).
- A failing release task stops the workflow before any service update (TC-438), also verified after merge and recorded at IMP-299.
- The web bundle contains only `NEXT_PUBLIC_*` values and neither image contains a secret or an `.env` file (TC-355, TC-434).
- CORS admits the staging web origin and refuses another origin (US-002 AC2, NFR-015, TC-351).
- `docker compose up api web` serves both images locally and `make smoke URL=http://localhost:8000` passes (NFR-035, TC-338).

**Tests**

- apps/api/tests/smoke/test_deployed.py — TC-288, TC-351, TC-437 — `make smoke URL=<staging API URL>`
- .github/workflows/deploy-staging.yml — TC-438 — `workflow_dispatch with simulate_release_failure=true (recorded run)`
- apps/web/Dockerfile — TC-338 — `docker compose up -d api web && make smoke URL=http://localhost:8000`

**Completion evidence**

- Links to one successful staging deploy run and one forced-failure run; local container smoke output; image tags equal to the commit SHA

### IMP-219 Supabase Auth with an AWS database: auth stub bootstrap and user row mirroring

**Task:** Sprint 2 (week 2) · CODE · 2 points · lead Het · release MVP (Amendment A1)

**Objective:** With the database on RDS, which has no Supabase auth schema:

- a release command applies the Appendix A.1 auth stub once;
- with `DB_AUTH_STUB=true`, the first authenticated call of a user created in hosted Supabase Auth creates that user's `auth.users` row (ID only, no e-mail) before the profile;
- profiles, trips and plans then work exactly as on Supabase.

**Owners and parts:** Het — whole task (2 points); branch `feat/IMP-219-whole-task`

**Traces to:** Stories US-012, US-163; FR-003; NFR-012, NFR-020, NFR-022

**Dependencies:** Prerequisites: IMP-106, IMP-108, Amendment A1 §5.1, IMD-101 · Downstream: IMP-218, IMP-216

**Files**

- apps/api/app/db/auth_stub.py (create)
- apps/api/app/db/admin.py (create: operator deletion command)
- apps/api/app/core/config.py (modify: `DB_AUTH_STUB`)
- the auth module's profile creation code that holds `get_or_create_profile` (modify)
- .env.example (modify)
- Makefile (modify: `db-bootstrap`)
- apps/api/tests/api/test_auth_stub_mirror.py (create)

**Implementation**

1. **Stub command.** `python -m app.db.auth_stub --if-missing`:
   - connects with `DATABASE_URL` through synchronous psycopg (the `+psycopg` driver suffix is removed from the URL first);
   - if schema `auth` exists, prints "auth schema present; nothing to do" and exits 0;
   - otherwise runs the stub SQL file that IMP-106 committed under `apps/api/migrations/sql/`, unchanged and in one transaction, then exits 0;
   - on any error, exits 1.

   The URL and credentials are never printed.
2. **Setting.** Add `DB_AUTH_STUB: bool = False` to the settings. Add it to `.env.example` with the comment of Amendment A1 §7.2: `false` on the Supabase CLI local stack, `true` on compose `db`, in test, staging and production.
3. **Mirroring.** When `DB_AUTH_STUB` is true, `get_or_create_profile` (IMD-14) first runs `insert into auth.users (id) values (:user_id) on conflict (id) do nothing` in the same transaction as the profile insert. The e-mail claim is never written to the database. When false, nothing touches `auth.users`.
4. **Make target.** Add `make db-bootstrap` = `cd apps/api && .venv/bin/python -m app.db.auth_stub --if-missing && .venv/bin/alembic upgrade head` (Amendment A1 §7.3).
5. **Tests.** Tests on the compose test database (stub already present):
   - a token for an unknown user creates the `auth.users` row with `email` null and the profile; a second call creates nothing;
   - with the setting false, no `auth.users` write happens;
   - on a fresh database without schema `auth`, `auth_stub --if-missing` creates the stub, and a second run is a no-op;
   - on a database that has schema `auth`, it is a no-op.
6. **Deletion command.** `python -m app.db.admin delete-user --user-id <uuid>`:
   - refuses unless `DB_AUTH_STUB` is true;
   - deletes the `auth.users` row in one transaction (the delete cascades to the profile, trips and plans) and prints only the number of rows deleted.

   Kirtan runs it as a one-off ECS task for the NFR-022 procedure (Amendment A1 §5.1). Test it on the compose database.

**Interfaces**

- API: API-03 (first call path)
- Tables: auth.users (stub), profiles
- Modules: MOD-B02, MOD-D01
- Env: DB_AUTH_STUB, DATABASE_URL

**Acceptance criteria**

- The first call of a new hosted-Auth user on a stub database creates `auth.users(id)` and the profile; repeat calls create nothing; no e-mail is stored (TC-439, FR-003).
- `auth_stub --if-missing` applies the stub once, is a no-op afterwards, and is a no-op on a database with schema `auth` (TC-440).
- `app.db.admin delete-user` removes the user's `auth.users` row and, by cascade, the profile and trips, and refuses when `DB_AUTH_STUB` is false (NFR-022).
- Existing auth and authorization suites pass unchanged (`make test-authz`).

**Tests**

- apps/api/tests/api/test_auth_stub_mirror.py — TC-439, TC-440 — `make test-api ARGS='-k auth_stub'`

**Completion evidence**

- PR with make check green; test output for TC-439 and TC-440

### IMP-311 RAG store: pgvector, corpus and chunk tables, item citations and retrieval record (migration 0007)

**Task:** Sprint 2 (week 2) · CODE · 3 points · lead Malhar · release MVP (Amendment A1)

**Objective:** Migration `0007_rag_store` creates:

- the pgvector extension and the tables `rag_documents` and `rag_chunks`;
- `itinerary_items.source_chunk_ids`;
- the retrieval columns of `ai_generations`.

It also brings the ORM models and the drift test up to date and switches the test database image to `pgvector/pgvector:pg16`, so every environment can store and search 768-dimension embeddings.

**Owners and parts:** Malhar — whole task (3 points); branch `feat/IMP-311-whole-task`

**Traces to:** Stories US-166; FR-136, FR-138; NFR-034

**Dependencies:** Prerequisites: IMP-106, Amendment A1 §5, IMD-107, IMD-110, IMD-113, IMD-115 · Downstream: IMP-313, IMP-315, IMP-316, IMP-299

**Files**

- apps/api/migrations/sql/0007_rag_store.sql (create)
- apps/api/migrations/sql/down/0007_rag_store.down.sql (create)
- apps/api/migrations/versions/0007_rag_store.py (create)
- apps/api/app/db/models/rag.py (create)
- the ORM model files of `itinerary_items` and `ai_generations` (modify)
- apps/api/pyproject.toml (modify: `pgvector`)
- docker-compose.yml (modify: `db` image)
- .github/workflows/ci.yml (modify: `api` job service image)
- apps/api/tests/api/test_schema_drift.py (modify if the vector type needs a mapping)
- apps/api/tests/api/test_rag_store.py (create)

**Implementation**

1. Copy `docs/spec/sql/0007_rag_store.sql` and `docs/spec/sql/down/0007_rag_store.down.sql` unchanged into `apps/api/migrations/sql/` and `migrations/sql/down/` (do not retype them).
2. Add Alembic revision `0007` (down revision `0006`) that executes the two files as the earlier revisions do; keep one head.
3. ORM models:
   - `RagDocument` and `RagChunk` in `app/db/models/rag.py`, with `embedding` typed `pgvector.sqlalchemy.Vector(768)`;
   - `source_chunk_ids` (`ARRAY(UUID)`, server default `'{}'`) on the itinerary item model;
   - `retrieval_mode` and `embedding_model_id` on the generation record model.

   Add the Python dependency `pgvector` with a reason in the PR (IMD-115). The drift test must stay green.
4. Switch the compose `db` service and the CI `api` job service from `postgres:16` to `pgvector/pgvector:pg16`; no other CI change.
5. On the Supabase CLI local stack, run `make db-migrate` and confirm `select extversion from pg_extension where extname = 'vector'` returns a version; record it in the part record.
6. Write `tests/api/test_rag_store.py`:
   - insert a place document and a guide document with chunks, then check that an exact cosine query (`order by embedding <=> :q limit 1`) returns the nearest chunk;
   - check that the CHECK constraints reject a place document without `place_id`, an embedding without `embedding_model_id`, a 1,201-character chunk and more than three `source_chunk_ids`;
   - check that browser roles have no privilege on the new tables.
7. Confirm the CI round trip (`upgrade head`, `downgrade base`, `upgrade head`) passes with 0007.

**Interfaces**

- Tables: rag_documents, rag_chunks, itinerary_items, ai_generations
- Modules: MOD-D01, MOD-B18
- Other: pgvector, Amendment A1 §5.3

**Acceptance criteria**

- Migration 0007 applies to a blank PostgreSQL 16 with pgvector and survives the CI round trip; the drift test is green (TC-441, NFR-034).
- The 0007 checks reject the invalid rows of step 6, and an exact cosine query returns the nearest chunk (TC-442).
- The compose `db` and the CI `api` job run `pgvector/pgvector:pg16`; the local Supabase stack migrates to head with the extension present.

**Tests**

- apps/api/tests/api/test_rag_store.py — TC-441, TC-442 — `make db-up && make test-api ARGS='-k rag_store'`
- apps/api/tests/api/test_schema_drift.py — TC-337 — `make test-api ARGS='-k drift'`

**Completion evidence**

- PR with make check green and the CI api job showing 0007 applied; extension version on the local stack recorded in the part record

### IMP-299 Sprint 2 gate SG-2 (blueprint Gate 1): walking skeleton on staging

**Task:** Sprint 2 (week 2) · VERIFY · 0 points · lead Kirtan · release MVP

**Objective:** The team demonstrates blueprint Gate 1 on staging, tags API contract v1 and records the result.

**Amended by A1 (2 November 2026):** the gate runs on AWS staging and also covers IMP-217, IMP-218, IMP-219 and IMP-311.

**Owners and parts:** Kirtan — whole task (0 points); branch `feat/IMP-299-<short>`

**Traces to:** NFR-012, NFR-034

**Dependencies:** Prerequisites: IMP-201, IMP-202, IMP-203, IMP-204, IMP-205, IMP-206, IMP-207, IMP-208, IMP-209, IMP-210, IMP-211, IMP-212, IMP-213, IMP-214, IMP-215, IMP-216, IMP-217, IMP-218, IMP-219, IMP-311 · Downstream: none

**Files**

- docs/progress/gates.md (modify); docs/progress/sprint-2.md (modify)

**Implementation**

1. On AWS staging (Amendment A1 §4) with AI_PROVIDER=MOCK: sign in, create a trip, press Generate, see the saved itinerary; confirm through API-23 that the generation record exists (provider MOCK, model and prompt version), because RDS is private and Claude Code has no AWS access (Amendment A1 §5.1). Also confirm the IMP-218 deploy evidence: one successful staging deploy run with the release-task log, and one forced-failure run that updated no service (TC-437, TC-438).
2. Confirm migrations 0001 to 0007 apply to an empty database (CI api job) and on staging (release task log), and confirm destination 1 places are loaded on staging with the quality report (IMP-206). Confirm both Express services are healthy, the staging budget alerts exist and the task definitions hold only SSM references (TC-434, TC-435).
3. Run make check and confirm e2e.yml is green on main; run make test-authz.
4. Hold the cross-squad contract review; tag the commit `contract-v1` after contracts/openapi.v1.json is reviewed (US-007 AC1).
5. Record pass / pass with gaps / fail in docs/progress/gates.md under SG-2; if not passed, list gaps with owners for the first two days of Sprint 3 (blueprint §25.4); recalibrate the point scale.

**Interfaces**

- API: API-01, API-02, API-07, API-22, API-23, API-24 · Tables: all MVP tables · Modules: MOD-P01 · Env: AI_PROVIDER · Other: §14 SG-2, blueprint Gate 1

**Acceptance criteria**

- A signed-in user creates a trip, generates with MOCK and sees a saved itinerary on staging; web, API, database and provider interface each handled the request and a generation record exists (Gate 1).
- Migrations apply to an empty database; destination 1 is loaded with its quality report.
- Tag contract-v1 exists on the reviewed commit.
- CI (ci.yml, e2e.yml) is green on main and the authorization suite passes.
- AWS staging: the release task succeeded, both services are healthy, `make smoke` passes against the staging API URL and contract v1 declares `sources[]` (Amendment A1 §10.4).
- SG-2 entry recorded with evidence links.

**Tests**

- docs/progress/gates.md — TC-369, TC-345, TC-337 — `make check && make test-authz && make smoke URL=<staging API URL>`

**Completion evidence**

- SG-2 record in docs/progress/gates.md with CI links, staging screenshots and the contract-v1 tag

## Sprint 3 (week 3): Gemini vertical slice — gate SG-3

| Task | Title | Type | Lead | Parts (points) | Prerequisites | Points |
| --- | --- | --- | --- | --- | --- | --- |
| IMP-301 | Gemini adapter with structured output, error mapping and recorded-response tests | CODE | Nidhi | Nidhi 5, Manya 3 | IMP-208, IMP-113, IMP-111 | 8 |
| IMP-302 | Provider metadata and health in readiness | CODE | Kirtan | Kirtan 2 | IMP-301, IMP-201 | 2 |
| IMP-303 | Normalized generation request and prompt content and size control | CODE | Manya | Manya 5 | IMP-204, IMP-111 | 5 |
| IMP-304 | Candidate retrieval, hard-constraint filters and ranking | CODE | Malhar | Malhar 4, Jeel 4 | IMP-204, IMP-206 | 8 |
| IMP-305 | Full generation pipeline through the active provider with job progress | CODE | Nidhi | Nidhi 4, Het 2, Krrish 2 | IMP-210, IMP-301, IMP-303, IMP-304 | 8 |
| IMP-306 | Output validation: schema and place IDs | CODE | Manya | Manya 3, Junaid 2 | IMP-305 | 5 |
| IMP-307 | OpenRouteService client with route cache and fallback | CODE | Junaid | Junaid 3 | IMP-209 | 3 |
| IMP-308 | Deterministic recalculation of times, durations and trip cost estimate | CODE | Manal | Manal 5, Het 3 | IMP-306, IMP-307 | 8 |
| IMP-309 | Day-wise itinerary view with labels | CODE | Manasvi | Manasvi 4, Het 1 | IMP-213, IMP-308 | 5 |
| IMP-310 | Evaluation dataset version 1 (15 trips) | DATA | Junaid | Junaid 3 | IMP-203 | 3 |
| IMP-312 | Embedding operation on ModelProvider: Gemini and deterministic MOCK embeddings | CODE | Nidhi | Nidhi 3 | IMP-301, IMP-207, IMP-208 | 3 |
| IMP-313 | Corpus ingestion and indexing: place and guide documents, chunking, embedding, `make rag-index` | CODE | Manal | Manal 3 | IMP-311, IMP-312, IMP-205 | 3 |
| IMP-314 | Destination guides for demo destination 1 | DATA | Krrish | Krrish 2, Malhar 1 | IMP-313, IMP-206 | 3 |
| IMP-315 | Hybrid retrieval: semantic place scores and guide passages with lexical fallback | CODE | Jeel | Jeel 3 | IMP-304, IMP-312, IMP-313 | 3 |
| IMP-316 | Grounded generation: passages in the request, validated citations, saved sources | CODE | Manya | Manya 3, Het 1 | IMP-303, IMP-305, IMP-306, IMP-309, IMP-315, IMP-214 | 4 |
| IMP-317 | Sources on itinerary items | CODE | Manasvi | Manasvi 2 | IMP-316, IMP-309 | 2 |
| IMP-399 | Sprint 3 gate SG-3 (blueprint Gate 2): first Gemini itinerary on staging | VERIFY | Nidhi | Nidhi 2 | IMP-301, IMP-302, IMP-303, IMP-304, IMP-305, IMP-306, IMP-307, IMP-308, IMP-309, IMP-312, IMP-313, IMP-314, IMP-315, IMP-316, IMP-317 | 2 |


### IMP-301 Gemini adapter with structured output, error mapping and recorded-response tests

**Task:** Sprint 3 (week 3) · CODE · 8 points · lead Nidhi with Manya · release MVP

**Objective:** With AI_PROVIDER=GEMINI and a valid key, GeminiProvider.generate_itinerary returns a ProviderResult holding a parsed io-1 ItineraryOutput candidate and usage, and every vendor failure surfaces as one shared ProviderError subclass.

**Owners and parts**

- Nidhi (lead) — Gemini adapter: structured output, error mapping (5 points)
- Manya — API-style spike (OD-14) and recorded-response tests (3 points)
- One branch and pull request per part (`feat/IMP-301-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-037; FR-041; NFR-004, NFR-013, NFR-020, NFR-024, NFR-031, NFR-042

**Dependencies:** Prerequisites: IMP-208, IMP-113, IMP-111 · Downstream: IMP-302, IMP-305, IMP-399, IMP-401, IMP-514, IMP-613, IMP-708

**Files**

- apps/api/app/ai/providers/gemini.py (create); apps/api/app/ai/errors.py (modify); apps/api/app/core/config.py (modify); apps/api/tests/unit/ai/test_gemini_adapter.py (create); apps/api/tests/fixtures/provider_recordings/gemini/ (create); docs/decisions/gemini-setup.md (create); apps/api/pyproject.toml (modify)

**Implementation**

1. Confirm on the official Gemini pages the model identifier, API style (Interactions or generateContent, OD-14), structured-output keywords and rate limits for the team key; record them with date and Verified/Unverified status in docs/decisions/gemini-setup.md (blueprint §19.4.8 spike list).
2. Add google-genai to pyproject.toml; import it only in app/ai/providers/gemini.py (import-linter contract must stay green).
3. Implement GeminiProvider(settings) with generate_itinerary(request: GenerationRequest) -> ProviderResult[ItineraryOutput]: render the prompt via the prompt registry (IMP-111), attach the io-1 wire schema (repository schema minus $schema, $id, pattern; blueprint Appendix C), set store=false, send no sampling parameter unless the spike shows the model honours it, use the lowest thinking level the model accepts, timeout = min(GEMINI_TIMEOUT_S, remaining step-7 allowance) converted to ms in http_options.
4. Parse the response: empty text -> ProviderInvalidOutput(empty); json.loads failure -> malformed_json; Pydantic io-1 failure -> schema_violation; MAX_TOKENS/incomplete -> truncated; safety block (HTTP 400 code safety/jailbreak/prohibited_content/blocklist or SAFETY finish) -> blocked. Read the error code before classifying any 400.
5. Map vendor errors to shared types per blueprint §19.4.6: timeout/504 -> ProviderTimeout; 429 rate -> ProviderRateLimited(retry_after_s); 429 quota_exceeded or 402 -> ProviderQuotaExhausted; 500/503 -> ProviderUnavailable; 403 -> ProviderAuthError; 400 invalid_request/404 model_not_found -> ProviderBadRequest. Never put vendor message text into errors, logs or records (NFR-024).
6. Map usage to input_tokens, output_tokens, thinking_tokens, total_tokens (null when absent, never estimated); return generation_settings with the names and values actually sent and adapter_version.
7. Implement health_check (no generation call: down if key or model id missing, else breaker/last-call state) and get_model_metadata (provider GEMINI, model_id exactly as configured, adapter_version).
8. Record sanitised responses (no key, no personal data) as JSON fixtures under tests/fixtures/provider_recordings/gemini/ for ok, blocked, empty, truncated, malformed and 429/503 cases; unit tests replay them through a fake transport (no network). One manual live call is run with make live-smoke and its date and result are written to gemini-setup.md.

**Interfaces**

- Modules: MOD-B05 · Env: GEMINI_API_KEY, GEMINI_MODEL_ID, GEMINI_TIMEOUT_S, GEMINI_MAX_RETRIES, AI_MAX_INPUT_TOKENS, AI_MAX_OUTPUT_TOKENS, PROMPT_TEMPLATE_VERSION · Other: ModelProvider protocol (app/ai/providers/base.py), io-1 wire schema (contracts/ai/io-1.schema.json), ProviderError taxonomy (blueprint §19.3.2)

**Acceptance criteria**

- FR-041 AC1-AC3 hold on recorded responses (TC-159 to TC-161).
- Each invalid-output kind and each vendor error maps to the specified shared type (TC-005, TC-015, TC-019 to TC-023).
- The key is read only from settings/environment and never appears in logs, errors or the generation record (TC-013).
- The request carries the structured-output configuration, store=false and no unsupported sampling parameter (TC-014, TC-030, TC-032); the model id is recorded exactly as configured (TC-031); usage maps or stays null (TC-004, TC-024).
- make imports passes: google-genai is imported only in gemini.py (TC-002).
- One live smoke call on the staging key is recorded with date and outcome in docs/decisions/gemini-setup.md (TC-029, manual).

**Tests**

- apps/api/tests/unit/ai/test_gemini_adapter.py — TC-013, TC-014, TC-015, TC-018, TC-019, TC-020, TC-021, TC-022, TC-023, TC-024, TC-030, TC-031, TC-032, TC-159, TC-160, TC-161 — `make test-unit ARGS='-k gemini'`
- apps/api/tests/contract/test_provider_contract.py — TC-003, TC-004, TC-005 — `make test-contract`
- apps/api/tests/contract/test_provider_contract.py — TC-029 — `make live-smoke (manual, staging key only)`

**Completion evidence**

- PR with make check green (unit, contract, imports).; docs/decisions/gemini-setup.md with verified facts and dated live-smoke result.; Recorded fixtures committed with no secret (gitleaks job green).

### IMP-302 Provider metadata and health in readiness

**Task:** Sprint 3 (week 3) · CODE · 2 points · lead Kirtan · release MVP

**Objective:** GET /health reports the provider name and GET /health/ready reports provider name, model identifier and status (ok, degraded, down) without any secret, and a down provider never takes non-AI routes down.

**Owners and parts:** Kirtan — whole task (2 points); branch `feat/IMP-302-<short>`

**Traces to:** Stories US-041; FR-044; NFR-013, NFR-042

**Dependencies:** Prerequisites: IMP-301, IMP-201 · Downstream: IMP-399

**Files**

- apps/api/app/core/health.py (modify); apps/api/app/ai/factory.py (modify); apps/api/tests/api/test_health.py (modify)

**Implementation**

1. Fill checks.provider {name, model_id, status: ok|degraded|down} of API-02 from get_model_metadata and health_check of the active provider, cached 60 s so health checks cost no quota; API-01 keeps {status, version, provider} with the provider name only and makes no provider call (§6).
2. Extend API-02 readiness with provider status; readiness returns 200 with status degraded when only the provider is down or the breaker is half-open, and 503 SERVICE_UNAVAILABLE only when the database is unreachable.
3. Ensure no key, URL with key, token or prompt text appears in any health payload (serialiser allow-list of fields).
4. Add tests with MOCK (scenario ok, and raise_error=ProviderAuthError(), IMD-27) and with GEMINI configured without a key.

**Interfaces**

- API: API-01, API-02 · Modules: MOD-B01, MOD-B05 · Env: AI_PROVIDER, GEMINI_MODEL_ID

**Acceptance criteria**

- FR-044 AC1-AC2 hold (TC-167, TC-168).
- Health check is cheap and has no side effects: no generation call and no ai_generations row (TC-006).
- Metadata is complete: provider, model_id, adapter_version (TC-007).
- No secret appears in any health response (TC-044).
- With the provider down, API-08 and API-10 still answer 200.

**Tests**

- apps/api/tests/api/test_health.py — TC-044, TC-167, TC-168 — `make test-api ARGS='-k health'`
- apps/api/tests/contract/test_provider_contract.py — TC-006, TC-007 — `make test-contract`

**Completion evidence**

- PR with make check green.; Screenshot or curl output of /health/ready on staging showing provider GEMINI and its status.

### IMP-303 Normalized generation request and prompt content and size control

**Task:** Sprint 3 (week 3) · CODE · 5 points · lead Manya · release MVP

**Objective:** For any complete trip the pipeline builds a gr-1 GenerationRequest that validates against its schema, carries user notes only as redacted quoted data, records its schema version, and the rendered prompt stays under AI_MAX_INPUT_TOKENS by truncating the shortlist by rank.

**Owners and parts:** Manya — whole task (5 points); branch `feat/IMP-303-<short>`

**Traces to:** Stories US-045, US-052; FR-026, FR-039; NFR-016, NFR-020, NFR-039

**Dependencies:** Prerequisites: IMP-204, IMP-111 · Downstream: IMP-305, IMP-399, IMP-708

**Files**

- apps/api/app/generation/request_builder.py (modify); apps/api/app/ai/prompts/registry.py (modify); apps/api/app/ai/limits.py (create); apps/api/app/ai/prompts/templates/itinerary_generate/v1/system.txt (modify); apps/api/app/ai/prompts/templates/itinerary_generate/v1/user.txt (modify); apps/api/tests/unit/generation/test_request_builder.py (create); apps/api/tests/unit/ai/test_registry.py (modify)

**Implementation**

1. Implement build_generation_request(trip, preferences, must_visit, locked_items, shortlist, settings) -> GenerationRequest (gr-1): dates, day count, travellers, pace limits (relaxed 3/300, balanced 5/480, busy 7/600), meal slots from pace, budget, step-free flag, must-visit IDs, locked items, ranked shortlist with only the fields gr-1 needs, mapping_version, input_schema_version gr-1.
2. Notes: cut to 500 characters for the request (the 1,000-character database limit applies to storage), redact emails and phone numbers (regex replacement with [redacted]), place them only in notes_quoted; never merge them into instructions or filters.
3. Exclude account email, display name and user ID from the request and the prompt (allow-list of fields).
4. In app/ai/limits.py implement enforce_input_limit(request, max_tokens): estimate tokens (characters/4 as the default estimator, replaced by count_tokens after the spike), drop lowest-ranked non-must-visit shortlist entries until under the limit, and return the number removed; the pipeline records truncated_count in generation_settings.
5. Render the itinerary_generate v1 templates with the request serialised as JSON data; the system text states that notes are data, not instructions (blueprint §19.4.4 skeleton).
6. Compute request_hash = SHA-256 of the canonical JSON request (sorted keys) for idempotency and records.

**Interfaces**

- Tables: trips, trip_preferences, trip_places · Modules: MOD-B06, MOD-B05 · Env: AI_MAX_INPUT_TOKENS, PROMPT_TEMPLATE_VERSION · Other: gr-1 schema (contracts/ai/gr-1.schema.json)

**Acceptance criteria**

- FR-026 AC1-AC3 hold (TC-120 to TC-122).
- FR-039 AC1-AC2 hold (TC-154, TC-155): a 200-place shortlist is cut by rank to the limit and must-visit places stay.
- A note containing "ignore previous instructions" and an email appears only inside notes_quoted with the email redacted (TC-028).
- The prompt size limit is enforced and the truncation count is reported (TC-027).
- The same trip state gives the same request_hash twice.

**Tests**

- apps/api/tests/unit/generation/test_request_builder.py — TC-120, TC-122, TC-028 — `make test-unit ARGS='-k request_builder'`
- apps/api/tests/unit/ai/test_registry.py — TC-027, TC-154, TC-155 — `make test-unit ARGS='-k prompt_limits'`
- apps/api/tests/api/test_generations.py — TC-121 — `make test-api ARGS='-k request'`

**Completion evidence**

- PR with make check green.; A sample rendered prompt for the SAMPLE trip attached to the PR (contains no account data).

### IMP-304 Candidate retrieval, hard-constraint filters and ranking

**Task:** Sprint 3 (week 3) · CODE · 8 points · lead Malhar with Jeel · release MVP

**Objective:** For a trip, the backend returns a deterministic ranked shortlist of active places from the trip destination in which every hard constraint holds, must-visit places stay with a conflict note, and score components are available for tests and debug logs.

**Owners and parts**

- Malhar (lead) — Candidate retrieval query and hard-constraint filters (4 points)
- Jeel — Scoring and ranking of the shortlist (preference weights) (4 points)
- One branch and pull request per part (`feat/IMP-304-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-046, US-047; FR-027, FR-028; NFR-002

**Dependencies:** Prerequisites: IMP-204, IMP-206 · Downstream: IMP-305, IMP-399, IMP-402, IMP-503, IMP-505, IMP-515

**Files**

- apps/api/app/generation/retrieval.py (create); apps/api/app/generation/ranking.py (create); apps/api/app/places/repository.py (modify); apps/api/tests/unit/generation/test_ranking.py (create); apps/api/tests/api/test_retrieval.py (create)

**Implementation**

1. Add PlaceRepository.candidates(destination_id) returning active places joined with opening hours and labels (one parameterised query).
2. Implement retrieve_candidates(trip, prefs, must_visit) applying hard filters in order: step_free_required (unknown = unsuitable), excluded categories, closed on every trip day (explicit closed rows only), minimum group cost above the activity budget; a must-visit place failing a filter stays with conflict_note set.
3. Implement score(place, ctx) = 0.40 c_interest + 0.25 c_price + 0.15 c_distance + 0.10 c_pace + 0.10 c_signal with the component definitions of blueprint §20.2 (c_signal weight is 0 in the MVP and the other weights are renormalised, §8.9); a high budget priority moves 0.10 from interest to price; return a ScoreParts value object.
4. Sort by score descending, tie-break on place_id; shortlist size min(40, max(12, 8 x days)); always keep must-visit places and enough food places for meal slots; exclude category stay.
5. Read weights and pace factors from app/trips/preference_mapping.py (MAPPING_VERSION 'pm-1', the only source, IMD-29); expose mapping_version for the generation record.
6. Log score parts at DEBUG level only (no user text).

**Interfaces**

- Tables: places, place_opening_hours, trip_preferences, trip_places · Modules: MOD-B06, MOD-B04

**Acceptance criteria**

- FR-027 AC1-AC3 hold (TC-123 to TC-125): step-free trips contain no non-step-free place; a must-visit place failing a filter stays with a note; every candidate ID exists in places.
- FR-028 AC1-AC3 hold (TC-126 to TC-128): better interest match ranks higher; two runs give identical order; score parts are logged in debug mode.
- Shortlist size rule and must-visit retention are covered on the SAMPLE fixture destination.

**Tests**

- apps/api/tests/unit/generation/test_ranking.py — TC-126, TC-127, TC-128 — `make test-unit ARGS='-k ranking'`
- apps/api/tests/api/test_retrieval.py — TC-123, TC-124, TC-125 — `make test-api ARGS='-k retrieval'`

**Completion evidence**

- PR with make check green.; Shortlist for the SAMPLE trip with score parts pasted in the PR description.

### IMP-305 Full generation pipeline through the active provider with job progress

**Task:** Sprint 3 (week 3) · CODE · 8 points · lead Nidhi with Het, Krrish · release MVP

**Objective:** POST API-22 starts a real pipeline (steps 2 to 11) in the background job runner with the active provider; API-23 reports the status (queued, running, validating, repairing, completed, failed); a completed job saves days, items, warnings, version and the generation record in one transaction; the generate page shows the privacy notice before the first generation.

**Owners and parts**

- Nidhi (lead) — Full generation pipeline through the active provider (4 points)
- Het — Job progress states, generation router, privacy-notice flag (API-04) (2 points)
- Krrish — Privacy notice and live progress on the generate page (2 points)
- One branch and pull request per part (`feat/IMP-305-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-048, US-049; FR-024, FR-025, FR-031; NFR-004, NFR-008, NFR-021, NFR-042

**Dependencies:** Prerequisites: IMP-210, IMP-301, IMP-303, IMP-304 · Downstream: IMP-306, IMP-399, IMP-403, IMP-406, IMP-606, IMP-607, IMP-709

**Files**

- apps/api/app/generation/pipeline.py (modify); apps/api/app/generation/service.py (modify); apps/api/app/generation/jobs.py (modify); apps/api/app/generation/router.py (modify); apps/api/app/itinerary/service.py (modify); apps/api/tests/api/test_generations.py (modify); apps/web/app/(app)/trips/[tripId]/generate/page.tsx (modify); apps/web/components/generation/PrivacyNotice.tsx (create); apps/web/components/generation/GenerationProgress.tsx (modify); apps/web/tests/unit/generation/PrivacyNotice.test.tsx (create); apps/api/app/auth/router.py (modify); apps/api/app/auth/schemas.py (modify); apps/api/tests/api/test_me.py (modify)

**Implementation**

1. Replace the walking-skeleton fixture path (IMP-210) with pipeline.run(generation_id): step 1 validate trip completeness: title, destination, dates, adults and a trip_preferences row (IMD-25; 422 VALIDATION_ERROR listing missing fields is returned synchronously by API-22 before the row is created), step 2 build request (IMP-303), steps 3-4 retrieve and rank (IMP-304), step 6 render, step 7 call factory.get_provider().generate_itinerary, steps 8-9 hand the result to validation/recalculation hooks (IMP-306, IMP-308), step 11 save.
2. Update ai_generations.status through running -> validating -> (repairing) -> completed/failed with outcome, failure_reason, latency_ms, tokens, provider, model_id, prompt_template_id, prompt_version, mapping_version, generation_settings, request_hash; API-23 returns the §6 GenerationOut (no separate stage field).
3. Keep the job rules of IMD-12: semaphore 2, one active job per trip (same request_hash returns the existing generation 200, different request 409 GENERATION_IN_PROGRESS), asyncio.wait_for 120 s pipeline timeout, reaper at 150 s.
4. Save step: in one transaction replace itinerary_days/items/warnings for the trip, insert itinerary_versions (reason generation), increment trips.plan_revision, set plan_stale=false, complete the ai_generations row; on any exception roll back and leave the old plan untouched.
5. Persist items only from the validated output: item origin=model, note in note with note_origin=ai, times and costs from the recalculation, never from model fields.
6. Implement the minimal API-04 PATCH /api/v1/me in auth/router.py accepting only ai_notice_acknowledged: true (sets profiles.ai_notice_ack_at = now()); API-22 with mode ai returns 422 with field ai_notice until it is set (IMD-24); IMP-601 extends API-04 with the other fields.
7. Web: before the first generation for the account show PrivacyNotice (provider named, link to terms, note warning); acknowledgement stored in profiles.ai_notice_ack_at via API-04; then call API-22 and poll API-23 (2 s backing off to 5 s, give up at 160 s with a reload offer).
8. Tests run with AI_PROVIDER=MOCK and with the recorded Gemini fixture injected through the factory.

**Interfaces**

- API: API-22, API-23, API-04 · Tables: ai_generations, itinerary_days, itinerary_items, itinerary_warnings, itinerary_versions, trips, profiles · Modules: MOD-B06, MOD-B05, MOD-B08, MOD-F04 · Components: GenerationProgress, PrivacyNotice, FallbackNotice · Env: AI_PROVIDER

**Acceptance criteria**

- FR-024 AC1-AC3 hold (TC-114 to TC-116): privacy notice acknowledged then 202 with a generation id; incomplete trip gives 422 with missing fields.
- FR-025 AC1-AC3 hold (TC-117 to TC-119): polling returns the status; a stale running job is closed by the reaper (TC-309).
- FR-031 AC1-AC3 hold (TC-133 to TC-135): GEMINI returns schema-valid JSON (recorded fixture), MOCK makes no network call, an ID outside the shortlist is rejected before saving.
- A crash injected between items and version insert leaves the previous plan intact (NFR-008).
- Each completed job writes exactly one ai_generations row with provider, model_id and prompt_version (TC-012, TC-151).
- Generation with mode ai before the privacy acknowledgement returns 422 (field ai_notice); after PATCH /api/v1/me {ai_notice_acknowledged: true} it starts (IMD-24, NFR-021).

**Tests**

- apps/api/tests/api/test_generations.py — TC-114, TC-115, TC-116, TC-117, TC-118, TC-119, TC-134, TC-135, TC-309, TC-012 — `make test-api ARGS='-k generations'`
- apps/api/tests/unit/generation/test_pipeline.py — TC-133 — `make test-unit ARGS='-k pipeline'`
- apps/web/tests/unit/generation/PrivacyNotice.test.tsx — new cases — `make test-web ARGS='PrivacyNotice'`
- apps/api/tests/api/test_me.py — new cases — `make test-api ARGS='-k ai_notice'`

**Completion evidence**

- PR with make check green.; Staging run with AI_PROVIDER=MOCK: API-23 response JSON at each status pasted in the PR.

### IMP-306 Output validation: schema and place IDs

**Task:** Sprint 3 (week 3) · CODE · 5 points · lead Manya with Junaid · release MVP

**Objective:** Every provider output is validated in code against io-1 and the shortlist before anything is saved: malformed or schema-breaking output raises ProviderInvalidOutput(kind), unknown, duplicate or out-of-shortlist place IDs and out-of-range days are rejected, and counts are recorded.

**Owners and parts**

- Manya (lead) — Output validation: io-1 schema and place-ID check (3 points)
- Junaid — Prompt-injection test cases (2 points)
- One branch and pull request per part (`feat/IMP-306-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-050; FR-032; NFR-016

**Dependencies:** Prerequisites: IMP-305 · Downstream: IMP-308, IMP-399

**Files**

- apps/api/app/validation/output_check.py (create); apps/api/app/schemas/ai.py (modify); apps/api/app/generation/pipeline.py (modify); apps/api/tests/unit/validation/test_output_check.py (create); apps/api/tests/unit/validation/test_injection_cases.py (create)

**Implementation**

1. Enforce in the io-1 Pydantic model: day count = trip days, items per day <= pace maximum, theme <= 80, note <= 200, summary <= 500 chars, HH:MM pattern for start times, duration 15-480 (DR-04), extra fields forbidden.
2. Implement check_output(output, shortlist_ids, trip_days) -> OutputCheckResult: day_number outside 1..trip days -> item rejected with OUTSIDE_TRIP_DATES; place_id not in the shortlist or not an active place -> UNKNOWN_PLACE; duplicate place_id within the plan -> second occurrence rejected.
3. Classify parse and schema failures as ProviderInvalidOutput(malformed_json | schema_violation) for the repair stage (no blind retry; repair arrives in IMP-502, until then the pipeline uses the IMP-402 fallback with fallback_reason invalid_output, failure_reason null, IMD-22).
4. Write counts (invalid_ids, rejected_items, kind) into ai_generations.validation_summary.
5. Add prompt-injection fixture cases: notes asking to add a place not in the shortlist, to set a price or to ignore rules; the output check must still reject invented IDs and ignore any model price/total fields.

**Interfaces**

- Tables: ai_generations · Modules: MOD-B07, MOD-B06 · Other: io-1 schema, finding codes UNKNOWN_PLACE, OUTSIDE_TRIP_DATES

**Acceptance criteria**

- FR-032 AC1-AC3 hold (TC-136 to TC-138).
- Malformed JSON and schema violations are classified and routed to repair or fallback, never retried blindly (TC-011, TC-022, TC-023).
- An invented place ID never reaches itinerary_items; with no usable plan the job ends fallback_rule_based (TC-307, after IMP-402).
- Injection notes cannot add places outside the shortlist (TC-028).

**Tests**

- apps/api/tests/unit/validation/test_output_check.py — TC-136, TC-137, TC-138, TC-022, TC-023 — `make test-unit ARGS='-k output_check'`
- apps/api/tests/unit/validation/test_injection_cases.py — TC-028 — `make test-unit ARGS='-k injection'`
- apps/api/tests/api/test_generations.py — TC-011 — `make test-api ARGS='-k invalid_output'`

**Completion evidence**

- PR with make check green.; MOCK scenario unknown_place run on local stack showing the rejected item count in validation_summary.

### IMP-307 OpenRouteService client with route cache and fallback

**Task:** Sprint 3 (week 3) · CODE · 3 points · lead Junaid · release MVP

**Objective:** Travel time between two places comes from a non-expired route_cache row, else from OpenRouteService (result cached), else from the distance fallback of IMP-209, each with its travel_source, and a cached pair never triggers an external call.

**Owners and parts:** Junaid — whole task (3 points); branch `feat/IMP-307-<short>`

**Traces to:** Stories US-087; FR-078; NFR-010, NFR-038

**Dependencies:** Prerequisites: IMP-209 · Downstream: IMP-308, IMP-399, IMP-612

**Files**

- apps/api/app/routing/client.py (create); apps/api/app/routing/cache.py (create); apps/api/app/routing/service.py (modify); apps/api/tests/unit/routing/test_routing_service.py (create); apps/api/tests/fixtures/provider_recordings/ors/ (create)

**Implementation**

1. Implement OrsClient.route(from, to, mode) with httpx, ORS_API_KEY from settings, timeout ORS_TIMEOUT_S (8 s), profiles foot-walking for walking and driving-car for car/local_transport; return minutes and metres; raise RoutingUnavailable on timeout, 4xx/5xx or missing key.
2. Implement RouteCacheRepository get(from, to, mode) (expires_at > now) and upsert with travel_source routing_api and expires_at = now + 30 days (Provisional).
3. Implement RoutingService.travel(from, to, mode): cache -> client (then cache) -> estimate.fallback (IMP-209, travel_source fallback_estimate, also cached for 1 day).
4. Add an in-process daily call counter; log a WARNING at 80 percent of the configured daily ORS allowance (value recorded at setup, Unverified).
5. Tests use respx with recorded ORS responses; no test needs a real key.

**Interfaces**

- Tables: route_cache · Modules: MOD-B10 · Env: ORS_API_KEY, ORS_TIMEOUT_S · Other: OpenRouteService directions API

**Acceptance criteria**

- FR-078 AC1-AC2 hold (TC-234, TC-235): the second request for a pair makes no HTTP call.
- With ORS failing or no key, the fallback estimate is returned with travel_source fallback_estimate (TC-236, TC-237 via IMP-209).
- The near-quota warning is logged at the threshold (TC-341, review).

**Tests**

- apps/api/tests/unit/routing/test_routing_service.py — TC-234, TC-235, TC-341 — `make test-unit ARGS='-k routing'`

**Completion evidence**

- PR with make check green.; Log excerpt showing cache hit and fallback paths on the local stack.

### IMP-308 Deterministic recalculation of times, durations and trip cost estimate

**Task:** Sprint 3 (week 3) · CODE · 8 points · lead Manal with Het · release MVP

**Objective:** After validation, the backend computes every start time, end time, duration, travel time, item cost range and trip total from stored data with the budget formulas BF-01 to BF-12, ignoring any time, price or total the model returned, and API-33 returns the totals.

**Owners and parts**

- Manal (lead) — Budget engine and costs API (money in minor units) (5 points)
- Het — Schedule recalculation of times and durations (3 points)
- One branch and pull request per part (`feat/IMP-308-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-051, US-080; FR-033, FR-071; NFR-030

**Dependencies:** Prerequisites: IMP-306, IMP-307 · Downstream: IMP-309, IMP-399, IMP-404, IMP-407, IMP-411, IMP-501

**Files**

- apps/api/app/generation/schedule.py (create); apps/api/app/budget/engine.py (create); apps/api/app/budget/service.py (create); apps/api/app/budget/router.py (create); apps/api/app/budget/schemas.py (create); apps/api/tests/unit/budget/test_engine.py (create); apps/api/tests/unit/generation/test_schedule.py (create); apps/api/tests/api/test_costs.py (create)

**Implementation**

1. Implement schedule.recalculate(days, places, routing, pace): order items by position, first item at day_start (09:00, Provisional), each next start = previous end + travel_from_prev_min + buffer (5 min after routing_api, 15 after fallback_estimate); store travel_from_prev_min/m/mode/source; replace model times and log the difference count only.
2. Implement budget/engine.py as pure functions over minor units (integers, Decimal conversion, half-up rounding once per line): BF-01 per person with child factor (child_half 0.5, child_free 0), BF-02 per group (tag price_per_group), BF-04 missing price -> category estimate with ESTIMATE_USED or 0 listed Unavailable and COST_INCOMPLETE, BF-05/06 allowances, BF-07 range, BF-08 contingency, BF-09 planning total, BF-10 per-traveller split, BF-11 status, BF-12 breakdown.
3. Write item cost_min, cost_max, cost_currency, cost_label for every saved item; prices in another currency are Unavailable (no conversion in the MVP).
4. Expose API-33 GET /api/v1/trips/{trip_id}/costs (owner only, 404 otherwise) returning estimate low/high, contingency, planning_total, per_traveller, budget status, categories and incomplete items; amounts as decimal strings with two decimals plus currency (IMD-05).
5. Ignore and never store any total or price field present in model output.

**Interfaces**

- API: API-33 · Tables: itinerary_items, places, budget_settings, trips · Modules: MOD-B09, MOD-B06, MOD-B10

**Acceptance criteria**

- FR-033 AC1-AC2 hold (TC-139, TC-140): stored totals equal the backend calculation even when the model output contains its own total.
- FR-071 AC1-AC2 hold (TC-221, TC-222).
- Rounding, remainder split, group pricing, missing prices, category estimate and zero price rules hold (TC-295, TC-296, TC-297, TC-299, TC-314, TC-316).
- The worked example of blueprint §20.3 reproduces planning total 13,530 and status near.
- Statement coverage of app/budget >= 85 percent (TC-334, NFR-030).

**Tests**

- apps/api/tests/unit/budget/test_engine.py — TC-221, TC-222, TC-295, TC-296, TC-297, TC-299, TC-314, TC-316 — `make test-unit ARGS='-k budget'`
- apps/api/tests/unit/generation/test_schedule.py — TC-139 — `make test-unit ARGS='-k schedule'`
- apps/api/tests/api/test_costs.py — TC-140 — `make test-api ARGS='-k costs'`

**Completion evidence**

- PR with make check green and coverage report for app/budget.; API-33 response for the SAMPLE trip pasted in the PR.

### IMP-309 Day-wise itinerary view with labels

**Task:** Sprint 3 (week 3) · CODE · 5 points · lead Manasvi with Het · release MVP

**Objective:** The itinerary page shows each day with its items in time order, times, durations, travel times and cost ranges, each fact carrying its source label (SourceBadge) and AI-written text carrying AiBadge; phones show day tabs, desktops a day list.

**Owners and parts**

- Manasvi (lead) — Day-wise itinerary view, SourceBadge and AiBadge labels (4 points)
- Het — Itinerary read schema and service fields (1 points)
- One branch and pull request per part (`feat/IMP-309-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-068; FR-059; NFR-002, NFR-025

**Dependencies:** Prerequisites: IMP-213, IMP-308 · Downstream: IMP-399, IMP-408, IMP-409, IMP-508, IMP-609, IMP-711

**Files**

- apps/api/app/itinerary/router.py (modify); apps/api/app/itinerary/schemas.py (modify); apps/api/app/itinerary/service.py (modify); apps/web/app/(app)/trips/[tripId]/itinerary/page.tsx (modify); apps/web/components/itinerary/DayColumn.tsx (modify); apps/web/components/itinerary/ItineraryItemCard.tsx (modify); apps/web/components/labels/SourceBadge.tsx (create); apps/web/components/labels/AiBadge.tsx (create); apps/web/lib/api/queries.ts (modify); apps/web/tests/unit/itinerary/DayColumn.test.tsx (create); apps/api/tests/api/test_itinerary.py (modify)

**Implementation**

1. Complete API-24 GET /api/v1/trips/{trip_id}/itinerary: days ordered by day_number, items by position with start_time, end_time (computed), duration_min, place summary, cost range with cost_label, travel_from_prev with travel_source, note with note_origin, is_locked; trip totals from the budget service; warnings for the current plan_revision; plan_revision and outcome of the latest generation.
2. Add useItinerary(tripId) query (key ["itinerary", tripId]) in lib/api/queries.ts using the generated client.
3. Build DayColumn and ItineraryItemCard rendering only server values (no client arithmetic on times or money); SourceBadge maps curated -> "Curated, checked <date>", estimate -> "Estimate", unavailable -> "Unavailable"; travel_source fallback_estimate -> "Estimated travel time (distance based)".
4. AiBadge on themes and notes with note_origin ai; FallbackNotice when outcome is fallback_rule_based.
5. Responsive layout: day tabs below 768 px, stacked day list at desktop widths; LoadingSkeleton, EmptyState (no itinerary: link to generate) and ErrorState wired.

**Interfaces**

- API: API-24 · Tables: itinerary_days, itinerary_items, itinerary_warnings · Modules: MOD-B08, MOD-F04, MOD-F07 · Components: DayColumn, ItineraryItemCard, SourceBadge, AiBadge, FallbackNotice, EmptyState, LoadingSkeleton, ErrorState

**Acceptance criteria**

- FR-059 AC1-AC2 hold (TC-195, TC-196): items in time order; estimated costs carry the Estimate label.
- No component computes a total or a time in the browser (code review checklist item in the PR).
- Owner-only: another user gets 404 from API-24 (covered by the IMP-215 suite).
- Page renders at 375 px and 1280 px without horizontal scroll (manual screenshots).

**Tests**

- apps/api/tests/api/test_itinerary.py — TC-195 — `make test-api ARGS='-k itinerary'`
- apps/web/tests/unit/itinerary/DayColumn.test.tsx — TC-196 — `make test-web ARGS='DayColumn'`

**Completion evidence**

- PR with make check green.; Screenshots of the SAMPLE itinerary at 375 px and 1280 px.

### IMP-310 Evaluation dataset version 1 (15 trips)

**Task:** Sprint 3 (week 3) · DATA · 3 points · lead Junaid · release MVP

**Objective:** eval/datasets/trips/v1/ holds 15 versioned evaluation cases, each with an ID, a frozen gr-1 request including its shortlist, hard constraints and expected properties, plus a schema file and a manifest with a content hash.

**Owners and parts:** Junaid — whole task (3 points); branch `feat/IMP-310-<short>`

**Traces to:** Stories US-127; FR-118; NFR-046

**Dependencies:** Prerequisites: IMP-203 · Downstream: IMP-413

**Files**

- eval/datasets/trips/v1/cases.jsonl (create); eval/datasets/trips/v1/manifest.json (create); eval/datasets/trips/schema.json (create); apps/api/tests/unit/evaluation/test_dataset.py (create)

**Implementation**

1. Write the case schema (id, version, category, request gr-1, hard_constraints, expected_properties) in eval/datasets/trips/schema.json.
2. Create 15 cases on the SAMPLE fixture destination following the category shares of blueprint §21.4 (standard 2/3/5-day trips, tight budget, step-free and groups, must-visit conflicts, pace extremes, long trip, single-day regeneration with locks, hostile notes).
3. Write manifest.json with dataset id, version v1, case count, SHA-256 of each case file and of the whole set.
4. Add a unit test that validates every case against the schema and gr-1, checks unique IDs and that the manifest hashes match.
5. Peer review (Kirtan) of constraint coverage and injection cases, recorded in the PR.

**Interfaces**

- Modules: MOD-B15 · Other: gr-1 schema, eval/ directory layout

**Acceptance criteria**

- FR-118 AC1 holds (TC-283): every case has ID, inputs, hard constraints and version.
- Dataset integrity check passes (TC-386); FR-118 AC2 is checked when a training set exists (TC-284, Stage 2).
- No case contains personal data.

**Tests**

- apps/api/tests/unit/evaluation/test_dataset.py — TC-283, TC-386 — `make test-unit ARGS='-k dataset'`

**Completion evidence**

- PR with the dataset, manifest and green unit test.; Review comment by Kirtan confirming coverage.

### IMP-312 Embedding operation on ModelProvider: Gemini and deterministic MOCK embeddings

**Task:** Sprint 3 (week 3) · CODE · 3 points · lead Nidhi · release MVP (Amendment A1)

**Objective:** Every adapter implements `embed_texts(texts, purpose, titles)` and returns 768-dimension, L2-normalised vectors:

- **Gemini** with `GEMINI_EMBEDDING_MODEL_ID` and the prefix or task-type rule of the configured model;
- **MOCK** with deterministic hashed embeddings and no network;
- **FINETUNED_MODEL**, which refuses.

The error taxonomy and a start-up check apply. Tests never call Gemini.

**Owners and parts:** Nidhi — whole task (3 points); branch `feat/IMP-312-whole-task`

**Traces to:** Stories US-164; FR-136, FR-137; NFR-031, NFR-043

**Dependencies:** Prerequisites: IMP-301 (the Gemini adapter file exists), IMP-207, IMP-208, Amendment A1 §6.5, IMD-106, IMD-112 · Downstream: IMP-313, IMP-315

**Files**

- apps/api/app/ai/providers/base.py (modify)
- apps/api/app/schemas/ai.py (modify: `EmbeddingResult`, `EmbeddingPurpose`)
- apps/api/app/ai/providers/gemini.py (modify)
- apps/api/app/ai/providers/mock.py (modify)
- apps/api/app/ai/providers/finetuned.py (modify)
- apps/api/app/core/config.py (modify: `GEMINI_EMBEDDING_MODEL_ID` and its start-up check)
- .env.example (modify)
- apps/api/tests/unit/ai/test_mock_embeddings.py (create)
- apps/api/tests/contract/test_provider_contract.py (modify)
- apps/api/tests/unit/ai/test_gemini_embeddings.py (create)
- apps/api/tests/unit/core/test_config.py (modify)

**Implementation**

1. **Protocol.** Add to the `ModelProvider` protocol: `async embed_texts(texts: Sequence[str], purpose: Literal["document", "query"], titles: Sequence[str | None] | None = None) -> EmbeddingResult`.
   - `EmbeddingResult`: `vectors: list[list[float]]`, `model_id: str`, `usage: UsageMetadata`, `latency_ms: int`.
   - Reject an empty list, more than 32 texts or a text over 2,000 characters with `ProviderBadRequest`.
   - Only `ProviderError` subclasses may escape.
2. **Gemini.**
   - One private function holds the vendor call: `client.aio.models.embed_content` with `model = GEMINI_EMBEDDING_MODEL_ID` and `output_dimensionality = 768`.
   - Each text is sent as its own `Content` object, never as several parts of one content, because `gemini-embedding-2` combines the parts of one content into one embedding. A response whose vector count differs from the text count raises `ProviderInvalidOutput("schema_violation")`.
   - For `gemini-embedding-2`, prefix queries with `task: search result | query: ` and documents with `title: <title or none> | text: `.
   - For `gemini-embedding-001`, set `task_type` `RETRIEVAL_QUERY` or `RETRIEVAL_DOCUMENT` and send no prefix.
   - L2-normalise every vector in code; a vector whose length is not 768 raises `ProviderInvalidOutput("schema_violation")`.
   - Use the timeout and transient-retry rules of §8.4 and its error mapping.
   - Never use or open the generation circuit breaker (IMD-112).
   - Never log text or vectors.
3. **MOCK** (`mock-embed-v1`). Implement the hashed bag-of-words of Amendment A1 §6.5 exactly:
   1. lower-case the text, split on non-alphanumerics, drop tokens under 3 characters;
   2. for each token, `h = sha256(token.encode("utf-8")).hexdigest()`; add `+1` at index `int(h[:8], 16) % 768` when `int(h[8], 16)` is even, else `-1`;
   3. sum and L2-normalise; an empty text gives the unit vector at index 0.
   - Add an optional constructor argument `embed_error` (a `ProviderError`) for tests.
   - `MOCK_PROVIDER_SCENARIO` keeps its seven values and does not affect embeddings.
4. **FINETUNED_MODEL.** The stub raises `ProviderBadRequest("FINETUNED_MODEL not enabled in Stage 1")`.
5. **Settings and start-up check.** Add `GEMINI_EMBEDDING_MODEL_ID` to settings and `.env.example` (Amendment A1 §7.2). For `AI_PROVIDER=GEMINI` in staging and production, exit at start-up when it is empty, starts with `<`, or is not `gemini-embedding-2` or `gemini-embedding-001`, naming the variable and never the value. In local and test, empty is allowed.
6. **Tests.**
   - Contract tests run over MOCK and over a fake Gemini client:
     - 768-length unit vectors, order preserved;
     - one `Content` per text in the received request, plus the purpose/prefix/task-type rule and `output_dimensionality`;
     - a fake response with fewer vectors than texts raises `ProviderInvalidOutput`;
     - error mapping for 429 quota, 429 rate, 403, 400 and timeout.
   - MOCK determinism (same text, same vector; shared words give cosine > 0; no socket opened).
   - Start-up check cases.
   - One `@pytest.mark.live` test that embeds two texts with a real key (skipped without one; run only by `make live-smoke`).

**Interfaces**

- Modules: MOD-B05
- Env: GEMINI_EMBEDDING_MODEL_ID, GEMINI_API_KEY, GEMINI_TIMEOUT_S, GEMINI_MAX_RETRIES, AI_PROVIDER
- Other: ModelProvider protocol (§8.3), Amendment A1 §6.5

**Acceptance criteria**

- MOCK embeddings are deterministic, 768-dimensional, unit length and make no network call (TC-443).
- Gemini embedding requests carry the configured model, 768 dimensions and the model's prefix or task type, and returned vectors are normalised (fake client; TC-444); `google.genai` is imported only in `gemini.py` (`make imports`, TC-002).
- Embedding errors map to the `ProviderError` taxonomy and never open the generation breaker (TC-445).
- Start-up refuses a missing or unsupported `GEMINI_EMBEDDING_MODEL_ID` for GEMINI in staging and production (TC-446).

**Tests**

- apps/api/tests/unit/ai/test_mock_embeddings.py — TC-443 — `make test-unit ARGS='-k embeddings'`
- apps/api/tests/unit/ai/test_gemini_embeddings.py — TC-444, TC-445 — `make test-unit ARGS='-k embeddings'`
- apps/api/tests/contract/test_provider_contract.py — TC-444 — `make test-contract ARGS='-k embed'`
- apps/api/tests/unit/core/test_config.py — TC-446 — `make test-unit ARGS='-k embedding_model'`

**Completion evidence**

- PR with make check and make imports green; live-smoke result recorded only if a key was used by its owner

### IMP-313 Corpus ingestion and indexing: place and guide documents, chunking, embedding, `make rag-index`

**Task:** Sprint 3 (week 3) · CODE · 3 points · lead Manal · release MVP (Amendment A1)

**Objective:** `make rag-index` turns every active place and every guide file that passes the quality gate into documents and chunks with provenance, and embeds them through the active provider. Re-runs are idempotent: unchanged chunks are not embedded again, and removed documents are deactivated, never deleted. The release task runs the index on every deploy.

**Owners and parts:** Manal — whole task (3 points); branch `feat/IMP-313-whole-task`

**Traces to:** Stories US-166; FR-136; NFR-040

**Dependencies:** Prerequisites: IMP-311, IMP-312, IMP-205, Amendment A1 §6.2 to §6.6, IMD-110, IMD-111 · Downstream: IMP-314, IMP-315, IMP-316

**Files**

- apps/api/app/rag/__init__.py, constants.py, documents.py, guides.py, chunker.py, repository.py, service.py, index.py (create)
- apps/api/app/places/service.py (modify: `ensure_data_source`)
- data/fixtures/sampleton/guides/getting-around.md, local-customs.md, food-culture.md (create; synthetic, SAMPLE)
- docs/guides/rag-corpus.md (create)
- Makefile (modify: `rag-index`)
- apps/api/scripts/release.sh (modify: index step unconditional)
- apps/api/.importlinter (modify: pure modules join the pure-domain contract)
- apps/api/tests/unit/rag/test_chunker.py, test_guides.py, test_documents.py (create)
- apps/api/tests/api/test_rag_index.py (create)

**Implementation**

1. **Constants.** `constants.py` holds the constants of Amendment A1 §6.13 (Proposed values).
2. **Place documents.** `documents.py` (pure) builds the place document of §6.2:
   - text `<name> (<category>). Tags: … . <description> Area: <address>`, with empty parts omitted;
   - at most 10 tags, the address cut to 150 characters, and the whole text cut to 1,200 characters at a word boundary;
   - never prices, hours or URLs from `places`;
   - `doc_key` `place:<uuid>`, one chunk.
3. **Guide files.** `guides.py` (pure) parses the flat front matter and body of §6.3 and applies the quality gate:
   - missing or invalid field, body under 300 or over 6,000 characters, a URL that is not `https`;
   - currency amounts, clock-time ranges and the hour or travel phrases of §6.3 (warnings, errors with `--strict`).

   Each finding is returned with file and line.

   SAMPLE guides under `data/fixtures/sampleton/guides/` are allowed only when `APP_ENV` is local or test (IMD-15). They use `source_type: curated_manual`, no URL and `licence: synthetic test data`.
4. **Chunking.** `chunker.py` (pure) implements §6.4: `##` sections, paragraph packing up to 800 characters, sentence and then word fallback, 120-character overlap at a boundary, every chunk 1 to 1,200 characters, `token_estimate = ceil(chars / 4)`, SHA-256 over heading and content.
5. **Data sources.** Add `places.service.ensure_data_source(name, source_type, licence, url, retrieved_on, attribution_text)`; places writes `data_sources` (§3.9, and Amendment A1 §5.1 amends the seed-only rule of §5.6).
   - It upserts by name.
   - A different licence or attribution text for an existing name is a gate error.
   - Different page URLs are allowed, because each page URL is stored on its own document (`rag_documents.url`).
6. **Index service.** `service.index(destination_slug | None, check_only, strict)` implements §6.6:
   1. upsert documents by `doc_key`, re-chunking when the content hash changes;
   2. upsert chunks by `(document_id, chunk_index)`, clearing the embedding of a changed chunk;
   3. deactivate chunks and documents that are no longer in the corpus;
   4. embed missing or other-model chunks in batches of 32 through `ModelProvider.embed_texts(purpose="document", titles=…)`, committing after each batch;
   5. on a `ProviderError`, stop with exit code 3, keeping the batches already saved.
7. **CLI.** `index.py`: `python -m app.rag.index [--destination <slug>] [--check] [--strict]`.
   - It prints a report (documents, chunks, embedded this run, inactive, warnings, errors) with no text and no secret.
   - Exit codes: 0 success, 1 gate errors in strict mode, 2 usage error, 3 embedding provider unavailable.
   - Add `make rag-index` (Amendment A1 §7.3).
8. **Release step.** Make the index step of `scripts/release.sh` unconditional (`python -m app.rag.index --strict`), keeping its rule that exit 3 is a warning and exits 1 and 2 fail the release.
9. **Curator guide.** Write `docs/guides/rag-corpus.md`: the guide file format, the gate rules and the commands, for curators. Write three short synthetic SAMPLE guides for tests, labelled SAMPLE in their title and source name. This is the only guide text Claude Code may write (Amendment A1 §6.3).
10. **Import contracts.** Add `app.rag.documents`, `app.rag.guides` and `app.rag.chunker` to the pure-domain contract of `.importlinter`.
11. **Tests.**
    - chunker limits, headings and overlap;
    - each gate rule (including two pages of one source with different URLs passing, and a different licence failing);
    - place-document content without prices or hours;
    - indexing the SAMPLE fixture with MOCK embeddings: a second run embeds 0; changing one guide paragraph re-embeds only the changed chunks; deleting a guide sets its document and chunks inactive and keeps the rows.

**Interfaces**

- Tables: rag_documents, rag_chunks, data_sources, places
- Modules: MOD-B18, MOD-B04, MOD-B05
- Env: AI_PROVIDER, GEMINI_EMBEDDING_MODEL_ID
- Other: Amendment A1 §6.2 to §6.6, data/guides/ format

**Acceptance criteria**

- Every active place and every gate-passing guide of the SAMPLE fixture is chunked and embedded with the active embedding model, and each chunk resolves to its document and data source (FR-136 AC1, TC-449).
- A guide with missing provenance, out-of-range length or a price, hour or travel-time statement fails the strict gate and is not indexed (FR-136 AC2, TC-448).
- Re-running embeds only new or changed chunks; removed documents are deactivated, never deleted (FR-136 AC3, TC-449).
- Chunker limits, headings and overlap hold (TC-447).

**Tests**

- apps/api/tests/unit/rag/test_chunker.py — TC-447 — `make test-unit ARGS='-k chunker'`
- apps/api/tests/unit/rag/test_guides.py — TC-448 — `make test-unit ARGS='-k guides'`
- apps/api/tests/api/test_rag_index.py — TC-449 — `make test-api ARGS='-k rag_index'`

**Completion evidence**

- PR with make check green; `make rag-index ARGS='--destination sampleton'` report pasted in the part record (first and second run)

### IMP-314 Destination guides for demo destination 1

**Task:** Sprint 3 (week 3) · DATA · 3 points · lead Krrish with Malhar · release MVP (Amendment A1)

**Objective:** Demo destination 1 has 8 to 15 guide documents in `data/guides/<slug>/`, written by the team from cited sources. Every document passes the guide quality gate in strict mode and has been checked against its source by a second member. The release task indexes them on staging.

**Owners and parts**

- Krrish (lead) — Research and write the destination 1 guide documents with sources (2 points)
- Malhar — Source and licence review, strict quality-gate run and quality report (1 points)
- One branch and one pull request for the card (IMD-66); each commit is authored by the owner of the part it belongs to

**Traces to:** Stories US-164, US-166; FR-136; NFR-040

**Dependencies:** Prerequisites: IMP-313, IMP-206, Amendment A1 §6.3, IMD-111 · Downstream: IMP-399, IMP-318

**Files**

- data/guides/<slug>/*.md (create; Krrish)
- data/guides/<slug>/quality_report.md (create; Malhar)

**Implementation**

1. **(Krrish) Topics.** Choose 8 to 15 topics from Amendment A1 §6.3 (getting around, neighbourhoods, customs and etiquette, safety and health, accessibility, food culture, seasonal notes, day-trip context). Write one file per topic, 300 to 6,000 characters (aim for 1,000 to 4,000), with `##` headings.
2. **(Krrish) Writing rules.**
   - Write in your own words from the cited public source; keep any quote short. Wikivoyage text may be adapted under CC BY-SA 4.0 with `attribution_text`.
   - Fill every front-matter field.
   - No prices, no opening hours, no travel times and no booking claims; those facts live in `places` and code.
3. **(Malhar) Review.**
   - Open each source and confirm that every statement in the file is supported by it and that the licence is recorded correctly.
   - Run `make rag-index ARGS='--destination <slug> --check --strict'` on a local database.
   - Write `quality_report.md`: files, sources, licences, reviewer and date, gate result.
4. **Claude Code's role.** Claude Code may only create the folder, run the gate and report findings. It never writes or edits guide content and never fills a source (DATA rule).
5. **Staging.** After merge, the next staging deploy indexes the guides. The release-task log printed by the deploy workflow shows the index report line (chunks embedded), and IMP-399 records it, because it can only exist after merge.

**Interfaces**

- Tables: rag_documents, rag_chunks, data_sources
- Modules: MOD-D02, MOD-B18
- Other: data/guides/ format (Amendment A1 §6.3)

**Acceptance criteria**

- Destination 1 has 8 to 15 guide files that pass `make rag-index ARGS='--destination <slug> --check --strict'` (FR-136 AC2, TC-450).
- Each file is traced to its source by the reviewer, recorded in `quality_report.md` (TC-450).
- After the staging deploy, the index report shows the guide chunks embedded with the active embedding model (FR-136 AC1); this is verified after merge and recorded at IMP-399.

**Tests**

- data/guides/<slug>/ — TC-450 — `make rag-index ARGS='--destination <slug> --check --strict'`

**Completion evidence**

- data/guides/<slug>/quality_report.md; strict gate output; staging release-task index line

### IMP-315 Hybrid retrieval: semantic place scores and guide passages with lexical fallback

**Task:** Sprint 3 (week 3) · CODE · 3 points · lead Jeel · release MVP (Amendment A1)

**Objective:** For each generation, the trip's preferences are embedded once, and the generation then gets:

- a semantic score for every candidate place, which reorders candidates inside the deterministic ranking (mapping `pm-2`) without changing hard filters or must-visit retention;
- up to six diverse guide passages and up to six place passages.

Any embedding failure, or a missing index, falls back to lexical ranking, and the mode is recorded.

**Owners and parts:** Jeel — whole task (3 points); branch `feat/IMP-315-whole-task`

**Traces to:** Stories US-164; FR-137, FR-027, FR-028; NFR-002, NFR-050

**Dependencies:** Prerequisites: IMP-304, IMP-312, IMP-313, Amendment A1 §6.7, §6.11, IMD-107, IMD-108, IMD-112 · Downstream: IMP-316, IMP-318, IMP-399

**Files**

- apps/api/app/rag/query.py, mmr.py (create)
- apps/api/app/rag/service.py (modify: `retrieve`)
- apps/api/app/rag/repository.py (modify: similarity queries)
- apps/api/app/generation/retrieval.py (modify)
- apps/api/app/generation/ranking.py (modify: `c_semantic`)
- apps/api/app/trips/preference_mapping.py (modify: `MAPPING_VERSION = 'pm-2'` and weights)
- apps/api/.importlinter (modify)
- apps/api/tests/unit/rag/test_query.py, test_mmr.py (create)
- apps/api/tests/unit/generation/test_ranking.py (modify)
- apps/api/tests/api/test_rag_retrieval.py (create)

**Implementation**

1. **Query text.** `query.py` (pure): `build_query_text(...)` exactly as Amendment A1 §6.7, from the trip's destination name, preferences, group needs, step-free flag and the redacted `notes_quoted`; at most 1,000 characters; deterministic.
2. **MMR.** `mmr.py` (pure): maximal marginal relevance over candidate vectors (λ = 0.7, k = 6, at most 2 chunks per document); ties are broken by chunk ID.
3. **Similarity queries.** `rag/repository.py`: two parameterised exact-cosine queries over active chunks of the destination whose `embedding_model_id` equals the active embedding model:
   - place similarity, as the maximum over each candidate's chunks;
   - the top 20 guide chunks with their vectors.

   No approximate index (IMD-107).
4. **Retrieve.** `rag.service.retrieve(ctx) -> RetrievalResult`:
   1. embed the query once with `purpose="query"`;
   2. compute place similarities for the candidates that passed the hard filters;
   3. select guide passages by MMR;
   4. return the best chunk of every candidate place (`place_best_chunk`), because `app.rag` must not import the generation ranking (Amendment A1 §8.2); IMP-316 picks the top 6 after ranking;
   5. record `mode`, `embedding_model_id` and `retrieval_ms`.

   On any `ProviderError`, or when no chunk of the destination carries the active embedding model, return `mode = lexical_fallback` with no similarities and no passages, and log the error kind at WARNING without text.
5. **Ranking.** `ranking.py` gains `c_semantic`: min-max normalised similarity over the candidates (0.5 when all are equal or there is a single candidate; 0 without an embedded chunk). `ScoreParts` gains `semantic`.
6. **Weights.** Weights `pm-2` in `preference_mapping.py` (the only source, IMD-29): interest 0.30, semantic 0.20, price 0.25, distance 0.15, pace 0.10, signal 0.00. `budget_priority = saving` moves 0.10 from interest to price. In lexical fallback the semantic weight is 0 and the rest are renormalised. Hard filters, must-visit retention, shortlist size and the tie-break are unchanged. `mapping_version` becomes `pm-2` in new generation records.
7. **Pipeline.** `generation/retrieval.py` calls `rag.service.retrieve` before ranking and passes the result on for IMP-316. Retrieval never raises to the pipeline. The pipeline stores `retrieval_ms` with the result so that IMP-316 can write it to the generation record.
8. **Import contract.** Add `app.rag.query` and `app.rag.mmr` to the pure-domain contract.
9. **Tests.**
   - On the SAMPLE fixture with MOCK embeddings, a trip whose interests or notes share words with one place's document ranks that place higher in vector mode than in lexical mode (same inputs give the same order twice).
   - A failing query embedding (`embed_error`) and an empty index both give `lexical_fallback`, and the generation still completes.
   - MMR keeps at most 2 chunks per guide document.
   - Must-visit places stay when their similarity is lowest.
   - `retrieval_ms` is set.

**Interfaces**

- Tables: rag_chunks, rag_documents, places, trip_preferences, trip_places
- Modules: MOD-B18, MOD-B06, MOD-B03, MOD-B05
- Env: AI_PROVIDER, GEMINI_EMBEDDING_MODEL_ID
- Other: Amendment A1 §6.7, §6.11

**Acceptance criteria**

- Vector mode ranks a place matching the trip's interests or notes higher than lexical mode, and the order is deterministic (FR-137 AC1 and AC2, TC-451).
- Hard filters and must-visit places are unchanged by the semantic component (FR-137 AC2, FR-027 AC2).
- When the query embedding fails or the destination has no embeddings, the generation completes with `retrieval_mode = lexical_fallback` (FR-137 AC3, TC-452).
- Guide passages hold at most two chunks per document (TC-453).
- Retrieval timing is recorded for the NFR-050 measurement at SG-3 (TC-459).

**Tests**

- apps/api/tests/unit/rag/test_query.py, test_mmr.py — TC-453 — `make test-unit ARGS='-k "rag and (query or mmr)"'`
- apps/api/tests/unit/generation/test_ranking.py — TC-451 — `make test-unit ARGS='-k ranking'`
- apps/api/tests/api/test_rag_retrieval.py — TC-451, TC-452, TC-459 — `make test-api ARGS='-k rag_retrieval'`

**Completion evidence**

- PR with make check green; shortlist of the SAMPLE trip with score parts in vector and lexical mode pasted in the part record

### IMP-316 Grounded generation: passages in the request, validated citations, saved sources

**Task:** Sprint 3 (week 3) · CODE · 4 points · lead Manya with Het · release MVP (Amendment A1)

**Objective:** The generation request carries the retrieved passages as quoted reference data (`gr-2`, template `itinerary_generate/v2`). The model may cite up to three of them per item (`io-2`). Code drops any citation that was not supplied, the generation record names the retrieval mode and embedding model, and the itinerary service saves each item's validated citations and returns them as `sources[]` in API-24.

**Owners and parts**

- Manya (lead) — gr-2 and io-2 schemas, template v2, passage size control, citation check, retrieval fields on the generation record, MOCK citations (3 points)
- Het — Save validated citations on items and return `sources[]` in API-24 (1 points)
- One branch and one pull request for the card (IMD-66); each commit is authored by the owner of the part it belongs to

**Traces to:** Stories US-164, US-165; FR-138, FR-139, FR-032, FR-035; NFR-016, NFR-020, NFR-042

**Dependencies:** Prerequisites: IMP-303, IMP-305, IMP-306, IMP-309, IMP-315, IMP-214, Amendment A1 §6.8 to §6.12, IMD-109, IMD-110 · Downstream: IMP-317, IMP-318, IMP-399

**Files**

- apps/api/app/schemas/ai.py (modify: gr-2, io-2; Manya)
- contracts/ai/gr-2.schema.json, contracts/ai/io-2.schema.json (create beside the unchanged gr-1 and io-1 files; Manya)
- apps/api/app/ai/prompts/templates/itinerary_generate/v2/system.txt, user.txt, repair.txt, meta.json (create; Manya)
- docs/model-change-log.md (modify; Manya)
- apps/api/app/generation/request_builder.py (modify; Manya)
- apps/api/app/ai/limits.py (modify; Manya)
- apps/api/app/validation/output_check.py (modify; Manya)
- apps/api/app/generation/pipeline.py (modify; Manya)
- apps/api/app/ai/providers/mock.py (modify; Manya)
- .env.example (modify: `PROMPT_TEMPLATE_VERSION=v2`; Manya)
- infra/aws/services/api.staging.json.tmpl (modify: `PROMPT_TEMPLATE_VERSION=v2` and, when the Gemini key exists, `AI_PROVIDER=GEMINI` with `GEMINI_MODEL_ID` and `GEMINI_EMBEDDING_MODEL_ID` from docs/decisions/accounts.md; Manya, with Kirtan informed)
- apps/api/tests/unit/generation/test_request_builder.py (modify; Manya)
- apps/api/tests/unit/validation/test_output_check.py (modify; Manya)
- apps/api/tests/unit/validation/test_injection_cases.py (modify; Manya)
- apps/api/app/itinerary/service.py (modify; Het)
- apps/api/app/itinerary/repository.py (modify; Het)
- apps/api/app/itinerary/schemas.py (modify; Het)
- apps/api/app/rag/service.py (modify: `resolve_sources`; Het)
- apps/api/tests/api/test_itinerary.py (modify; Het)

**Implementation**

1. **(Manya) Schemas.**
   - `gr-2` = `gr-1` + `context_passages[]` (0 to 12: `passage_id`, `kind`, `title` ≤ 120, `text` = the whole chunk ≤ 1,200, `place_id` or null) + `retrieval {mode, embedding_model_id}`; `input_schema_version` `gr-2`.
   - `io-2` = `io-1` + `days[].items[].source_ids` (0 to 3 strings, default empty); `output_schema_version` `io-2`.
   - Same wire-schema rules as §8.7.
   - gr-2 and io-2 are added beside gr-1 and io-1, which stay unchanged. `make openapi` exports all four.
   - The active template's `meta.json` selects the pair the request builder and the output parser use: v1 uses gr-1 and io-1, v2 uses gr-2 and io-2.
   - The fallback planner returns io-2 with empty `source_ids`.
2. **(Manya) Request building.** `request_builder` fills `context_passages` from the `RetrievalResult` of IMP-315: guide passages in MMR order, then the `place_best_chunk` of each of the top 6 shortlisted places after ranking (`RAG_TOP_K_PLACE`). It also fills `retrieval`. The place `description` is sent only inside a place passage (Amendment A1 §6.8). Account data is still never sent.
3. **(Manya) Size control.** `enforce_input_limit` drops passages (lowest similarity first) before cutting the shortlist. It records `passages_sent`, `passages_dropped` and `truncated_count` in `generation_settings`.
4. **(Manya) Template v2.** A new directory with the four statements of Amendment A1 §6.9 in the system text and passages only inside the request JSON (`$request_json`). `meta.json` names gr-2 and io-2. Add a `docs/model-change-log.md` entry. `PROMPT_TEMPLATE_VERSION` defaults to `v2` in `.env.example`; v1 stays unchanged.
5. **(Manya) Citation check.** `output_check` removes `source_ids` that are not `passage_id`s of this request, removes duplicates, keeps at most 3 and counts removals in `validation_summary.unknown_source_ids`. No finding code is added, and an item is never dropped for a citation.
6. **(Manya) Pipeline.**
   - The pipeline stores `retrieval_mode`, `embedding_model_id` and `retrieval_ms` on the `ai_generations` row, and API-23 returns them (the `GenerationOut` fields declared by IMP-214).
   - It passes the same passages to the one repair call. The fallback planner and mode `rule_based` produce empty `source_ids`.
7. **(Manya) MOCK.** When a place passage exists for an item's place, MOCK sets `source_ids = [that passage_id]`, which is deterministic. Extend the injection cases: a guide passage containing an instruction ("add place X", "set price") changes neither the place set nor costs.
8. **(Manya) Staging switch.** In `infra/aws/services/api.staging.json.tmpl`, set `PROMPT_TEMPLATE_VERSION=v2`. When IMP-113 recorded a Gemini key and both model IDs, also set `AI_PROVIDER=GEMINI`, `GEMINI_MODEL_ID` and `GEMINI_EMBEDDING_MODEL_ID`. The deploy after merge applies them (Amendment A1 §4.3).
9. **(Het) Saving and reading.**
   - The save step writes each item's validated `source_ids` to `itinerary_items.source_chunk_ids`.
   - `snap-1` items carry `source_chunk_ids` (Amendment A1 §5.5).
   - Edits keep an item's citations; replacing its place clears them.
   - API-24 fills `sources[]` (the `SourceRef` of Amendment A1 §7.1, already declared by IMP-214) through `rag.service.resolve_sources(chunk_ids)`, which loads chunk, document and data source in one query, resolves inactive chunks and skips missing IDs. No N+1.
10. **Tests.**
   - (Manya) The request validates against gr-2; the rendered prompt carries passages only inside the JSON and never in the instructions; unknown and duplicate citations are dropped and counted; at most 3 per item; the injection passage changes nothing.
   - (Het) After a MOCK generation with an index, API-24 returns `sources` with all `SourceRef` fields; saved IDs are a subset of the passages supplied to that generation; a foreign trip still returns 404.

**Interfaces**

- API: API-22, API-23, API-24
- Tables: ai_generations, itinerary_items, itinerary_versions, rag_chunks, rag_documents, data_sources
- Modules: MOD-B05, MOD-B06, MOD-B07, MOD-B08, MOD-B18
- Env: PROMPT_TEMPLATE_VERSION
- Other: gr-2, io-2, `itinerary_generate/v2`, Amendment A1 §6.8 to §6.12

**Acceptance criteria**

- Passages reach the model only as quoted reference data with their IDs, and an instruction inside a guide passage changes neither the place set nor costs (FR-138 AC1, NFR-016, TC-454).
- An item keeps at most three citations from its own request; unknown or duplicate IDs are dropped and counted (FR-138 AC2, TC-455).
- The saved plan records each item's citations, and the generation record (and API-23) names `retrieval_mode`, `embedding_model_id` and `retrieval_ms` (FR-138 AC3, NFR-042, TC-459).
- API-24 returns, per item, `sources[]` with title, kind, source name, licence or attribution, URL and retrieval date (FR-139 AC1, TC-456).
- `make openapi-check` is green with gr-1, io-1, gr-2 and io-2.

**Tests**

- apps/api/tests/unit/generation/test_request_builder.py — TC-454 — `make test-unit ARGS='-k request_builder'`
- apps/api/tests/unit/validation/test_output_check.py — TC-455 — `make test-unit ARGS='-k output_check'`
- apps/api/tests/unit/validation/test_injection_cases.py — TC-454 — `make test-unit ARGS='-k injection'`
- apps/api/tests/api/test_itinerary.py — TC-456 — `make test-api ARGS='-k itinerary'`

**Completion evidence**

- PR with make check and make openapi-check green; one rendered v2 prompt for the SAMPLE trip (no account data) and one API-24 response with sources pasted in the part records

### IMP-317 Sources on itinerary items

**Task:** Sprint 3 (week 3) · CODE · 2 points · lead Manasvi · release MVP (Amendment A1)

**Objective:** The itinerary page shows, under each AI-written note, the sources the note relies on: title, kind, source name, licence or attribution, retrieval date and a safe link. Items without citations show nothing extra.

**Owners and parts:** Manasvi — whole task (2 points); branch `feat/IMP-317-whole-task`

**Traces to:** Stories US-165; FR-139, FR-035; NFR-025, NFR-040

**Dependencies:** Prerequisites: IMP-316, IMP-309, Amendment A1 §7.1 · Downstream: IMP-399, IMP-609

**Files**

- apps/web/components/itinerary/ItemSources.tsx (create)
- apps/web/components/itinerary/ItineraryItemCard.tsx (modify)
- apps/web/tests/unit/itinerary/ItemSources.test.tsx (create)

**Implementation**

1. **Component.** `ItemSources` takes the item's `sources` from the generated client types (`SourceRef`) and renders nothing when the list is empty.
2. **Disclosure.** A button "Sources (n)" with `aria-expanded` and `aria-controls`, operable with Enter and Space, toggles a list.
3. **List items.** Each item shows the title, a kind label ("Guide" or "Place record"), the source name, the licence or `attribution_text` and the retrieval date (formatted with `lib/format`).
4. **Links.** When `url` is set, the title is a link with `target="_blank"` and `rel="noopener noreferrer"`, and only `https` URLs are rendered as links. No chunk ID or similarity is shown.
5. **Placement.** `ItineraryItemCard` renders `ItemSources` directly under the note when `note_origin` is `ai`. The AiBadge stays on the note.
6. **Tests.** Component tests:
   - list rendered from a fixture;
   - empty list renders nothing;
   - keyboard toggle;
   - link attributes;
   - a non-https URL is shown as text;
   - axe finds no violation.

**Interfaces**

- API: API-24
- Modules: MOD-F04, MOD-F07
- Components: ItineraryItemCard, ItemSources, AiBadge

**Acceptance criteria**

- The itinerary page shows each AI-written note's sources, and items without citations show none (FR-139 AC2, TC-457).
- Source links open outside the app with `noopener noreferrer`, and no internal ID is shown as text (FR-139 AC3, TC-457).
- The disclosure works by keyboard, and axe reports no violation (NFR-025, TC-457).

**Tests**

- apps/web/tests/unit/itinerary/ItemSources.test.tsx — TC-457 — `make test-web ARGS='ItemSources'`

**Completion evidence**

- PR with make check green; screenshots at 375 px and 1280 px of an item with sources (MOCK, local stack)

### IMP-399 Sprint 3 gate SG-3 (blueprint Gate 2): first Gemini itinerary on staging

**Task:** Sprint 3 (week 3) · VERIFY · 2 points · lead Nidhi · release MVP

**Objective:** Sprint gate SG-3 (blueprint Gate 2) is decided and recorded: a Gemini-generated itinerary for a seeded trip is visible on staging after schema and place-ID validation and backend recalculation, or the documented fallback rule is applied.

**Amended by A1 (2 November 2026):** staging is AWS, and the gate checks the RAG pipeline (IMP-312 to IMP-317).

**Owners and parts:** Nidhi — whole task (2 points); branch `feat/IMP-399-<short>`

**Traces to:** enabling work (no requirement)

**Dependencies:** Prerequisites: IMP-301, IMP-302, IMP-303, IMP-304, IMP-305, IMP-306, IMP-307, IMP-308, IMP-309, IMP-312, IMP-313, IMP-314, IMP-315, IMP-316, IMP-317 · Downstream: none

**Files**

- docs/progress/gates.md (modify); docs/progress/sprint-3.md (modify)

**Implementation**

1. Confirm IMP-301 to IMP-309 are done in docs/progress/sprint-3.md with evidence links; IMP-302 and IMP-310 may slip to Sprint 4 without failing the gate (blueprint §25.5).
2. Deploy main to staging with AI_PROVIDER=GEMINI; run make smoke URL=<staging api> and record the result.
3. On staging, as a test account, open the seeded SAMPLE or destination-1 trip, start generation and wait for completed.
4. Check the generation record through API-23: provider GEMINI, model_id as configured, prompt_version set, outcome model or model_repaired, retrieval_mode, embedding_model_id and retrieval_ms. Check that API-33 totals equal the engine output, not model values.
5. If Gemini does not produce a plan: record the cause (quota, structured output, prompt) in gates.md, keep any demo on MOCK with the demo-data banner and never present it as a Gemini result; Nidhi and Manya continue on it while Sprint 4 proceeds on MOCK.
6. RAG check on AWS staging (Amendment A1 §10.4):
   - the release task log shows the destination-1 guide and place chunks embedded with GEMINI_EMBEDDING_MODEL_ID;
   - the API-23 response of the Gemini run has retrieval_mode = vector and the embedding model;
   - the itinerary page shows at least one note with sources (ACC-19);
   - record retrieval_ms from API-23 for at least 10 staging generations and their p95 (NFR-050, TC-459).

   If embeddings are unavailable, record lexical_fallback, the cause and the owners, and make no RAG claim.
7. Record pass or not passed with reasons, owners and dates in docs/progress/gates.md.

**Interfaces**

- API: API-22, API-23, API-24, API-33, API-02 · Tables: ai_generations · Modules: MOD-B05, MOD-B06, MOD-B07, MOD-B09 · Env: AI_PROVIDER, GEMINI_API_KEY, GEMINI_MODEL_ID

**Acceptance criteria**

- A Gemini-generated plan is visible on staging and its generation record names provider, model id and prompt version (TC-370, manual).
- make check is green on main at the gate commit.
- make smoke passes against staging.
- The Gemini plan on AWS staging has retrieval_mode = vector and cites at least one passage shown on the itinerary page, and the retrieval time p95 is recorded (ACC-19, NFR-050, TC-459); otherwise lexical_fallback is recorded with its cause.
- The gate decision is recorded; warnings may remain and no quality claim is made.

**Tests**

- apps/api/tests/smoke/test_deployed.py — new cases — `make smoke URL=<staging api url>`
- apps/web/e2e/generate.spec.ts — TC-370 — `make e2e ARGS='generate' (manual Gemini run on staging, recorded)`

**Completion evidence**

- docs/progress/gates.md SG-3 entry with screenshot of the itinerary and the ai_generations row (no secrets).; CI run link for main at the gate commit.

## Sprint 4 (week 4): Core itinerary reliability — gate SG-4

| Task | Title | Type | Lead | Parts (points) | Prerequisites | Points |
| --- | --- | --- | --- | --- | --- | --- |
| IMP-401 | Retries with backoff and circuit breaker in the Gemini adapter | CODE | Nidhi | Nidhi 3 | IMP-301 | 3 |
| IMP-402 | Rule-based fallback planner and saved sample itineraries | CODE | Malhar | Malhar 3, Jeel 2 | IMP-304, IMP-209 | 5 |
| IMP-403 | Provider failure, timeout and quota handling end to end with fallback notice | CODE | Nidhi | Nidhi 2, Krrish 1 | IMP-401, IMP-402, IMP-305 | 3 |
| IMP-404 | Validator: overlaps, travel gaps, missing constraints and invalid references | CODE | Manal | Manal 4, Junaid 3 | IMP-308 | 7 |
| IMP-405 | Structured warnings with suggested fixes, persisted with the plan, warnings panel | CODE | Manasvi | Manasvi 2, Jeel 2 | IMP-404, IMP-202 | 4 |
| IMP-406 | Preserve explicit constraints and must-visit places; label AI-written text | CODE | Manya | Manya 3, Krrish 1 | IMP-305 | 4 |
| IMP-407 | Edit transaction core: recalculate and revalidate every edit atomically with plan revision | CODE | Het | Het 5 | IMP-308, IMP-404 | 5 |
| IMP-408 | Remove an activity and change start time or duration | CODE | Het | Het 2, Manasvi 2 | IMP-407, IMP-309 | 4 |
| IMP-409 | Reorder by drag and by keyboard | CODE | Manasvi | Manasvi 3, Het 2 | IMP-407, IMP-309 | 5 |
| IMP-410 | Drafts and reopening the latest saved itinerary | CODE | Manal | Manal 2, Krrish 2 | IMP-212, IMP-211 | 4 |
| IMP-411 | Transport allowance, stay budget and price source labels | CODE | Manal | Manal 2, Krrish 2 | IMP-308 | 4 |
| IMP-412 | Loading, empty and error states on every MVP screen | CODE | Manasvi | Manasvi 3 | IMP-104 | 3 |
| IMP-413 | Evaluation harness (command line) | CODE | Manya | Manya 3 | IMP-310, IMP-207 | 3 |
| IMP-318 | Retrieval evaluation: recall, hit rate, citation validity and grounding rate | CODE | Junaid | Junaid 2 | IMP-413, IMP-316, IMP-314 | 2 |
| IMP-414 | End-to-end journey test on staging | VERIFY | Krrish | Krrish 3, Junaid 2 | IMP-403, IMP-408, IMP-409 | 5 |
| IMP-499 | Sprint 4 gate SG-4 (blueprint Gate 3) and cut-list checkpoint | VERIFY | Kirtan | Kirtan 2 | IMP-401, IMP-402, IMP-403, IMP-404, IMP-405, IMP-406, IMP-407, IMP-408, IMP-409, IMP-410, IMP-411, IMP-412, IMP-413, IMP-414, IMP-318 | 2 |


### IMP-401 Retries with backoff and circuit breaker in the Gemini adapter

**Task:** Sprint 4 (week 4) · CODE · 3 points · lead Nidhi · release MVP

**Objective:** The Gemini adapter retries only ProviderTimeout, ProviderRateLimited and ProviderUnavailable with bounded backoff inside the 70 s step-7 allowance, and an in-memory circuit breaker skips the provider while open: after transient errors the fallback runs immediately, after a quota or auth error the generation ends failed with the original cause (IMD-44).

**Amended by A1 (2 November 2026):** embedding calls (`embed_texts`, IMD-112) are neither counted by nor blocked by the circuit breaker; the breaker covers generation calls only.

**Owners and parts:** Nidhi — whole task (3 points); branch `feat/IMP-401-<short>`

**Traces to:** Stories US-038; FR-047; NFR-004, NFR-006

**Dependencies:** Prerequisites: IMP-301 · Downstream: IMP-403, IMP-499, IMP-512

**Files**

- apps/api/app/ai/breaker.py (create); apps/api/app/ai/providers/gemini.py (modify); apps/api/app/ai/factory.py (modify); apps/api/tests/unit/ai/test_retry.py (create); apps/api/tests/unit/ai/test_breaker.py (create)

**Implementation**

1. Implement retry in the adapter: attempts = 1 + GEMINI_MAX_RETRIES (default 1); backoff 1, 2, 4, 8 s with random jitter, capped by the remaining allowance; honour retry_after_s but never beyond the budget; never retry ProviderAuthError, ProviderBadRequest, ProviderQuotaExhausted or ProviderInvalidOutput. Disable or account for SDK-internal retries so the total stays at two attempts (record the setting in gemini-setup.md).
2. Implement CircuitBreaker (one instance per provider in the factory): states closed/open/half_open; opens after 5 consecutive provider-failure generations or one QuotaExhausted/AuthError; cool-down 60 s (transient), 15 min (quota), until restart (auth); the next real request is the half-open probe.
3. While open the pipeline skips step 7: if the breaker opened for transient errors it builds the rule-based plan and records the cause in validation_summary.provider_failure, returned as fallback_reason (IMD-22); if it opened for quota or auth it ends the generation failed with provider_quota_exhausted or config_error and no fallback (IMD-44).
4. health_check reports down while open and degraded while half-open (used by API-02).
5. Tests use MOCK scenarios timeout, rate_limited and quota plus raise_error=ProviderUnavailable() and raise_error=ProviderAuthError() (IMD-27) and an injectable clock; no real sleeping.

**Interfaces**

- API: API-02 · Modules: MOD-B05 · Env: GEMINI_TIMEOUT_S, GEMINI_MAX_RETRIES, MOCK_PROVIDER_SCENARIO

**Acceptance criteria**

- FR-047 AC1-AC2 hold (TC-174, TC-175): five consecutive transient failures open the breaker; an open transient breaker uses the fallback without a provider call; a quota-opened breaker ends the next AI generation failed / provider_quota_exhausted without a provider call (IMD-44).
- Only transient errors are retried (TC-009); 429 uses bounded backoff (TC-016); quota exhaustion is not retried (TC-017); timeout is enforced (TC-018).
- Breaker opens and recovers through half-open (TC-010).
- No path exceeds two provider attempts or the 70 s allowance.

**Tests**

- apps/api/tests/unit/ai/test_retry.py — TC-009, TC-016, TC-017, TC-018 — `make test-unit ARGS='-k retry'`
- apps/api/tests/unit/ai/test_breaker.py — TC-010, TC-174, TC-175 — `make test-unit ARGS='-k breaker'`

**Completion evidence**

- PR with make check green.; Test output showing the breaker state transitions with the fake clock.

### IMP-402 Rule-based fallback planner and saved sample itineraries

**Task:** Sprint 4 (week 4) · CODE · 5 points · lead Malhar with Jeel · release MVP

**Objective:** A deterministic rule-based planner builds an io-1 ItineraryOutput from the ranked shortlist without any model; its plans pass the same validation and save steps, are labelled built without AI, and two saved sample itineraries per demo destination pass validation (§8.15).

**Owners and parts**

- Malhar (lead) — Rule-based fallback planner (3 points)
- Jeel — Saved sample itineraries (data) (2 points)
- One branch and pull request per part (`feat/IMP-402-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-058; FR-036; NFR-006, NFR-007

**Dependencies:** Prerequisites: IMP-304, IMP-209 · Downstream: IMP-403, IMP-499

**Files**

- apps/api/app/generation/fallback_planner.py (create); apps/api/app/generation/samples.py (create); apps/api/app/generation/pipeline.py (modify); data/fixtures/sampleton/sample_itineraries/ (create); apps/api/tests/unit/generation/test_fallback_planner.py (create); apps/api/tests/api/test_generations.py (modify)

**Implementation**

1. Implement plan_rule_based(request, ranked, routing) per blueprint §20.7: group days (simple nearest-neighbour grouping now; IMP-503 replaces it with the clustering), must-visit first, nearest-neighbour order inside a day from day_start, each item after previous end + travel + buffer, a meal slot from food places in the lunch window, stop at the pace item/minute limit.
2. Write theme, note and summary from fixed templates and mark them as built without AI (note_origin none or template marker; no AiBadge).
3. Leave out any place the validator would flag as an error; report an unplaceable must-visit place as MUST_VISIT_MISSING.
4. Wire into the pipeline: mode rule_based on API-22 and every fallback path set outcome fallback_rule_based; model_id rule_based_planner_v1 is set at insert only when mode rule_based was requested (not counted against the AI cap); a fallback after an AI attempt keeps the configured model_id and counts against the cap (IMD-43).
5. Create two saved sample itineraries for the SAMPLE destination (and later per curated destination) as JSON io-1 files; samples.py loads and validates them; a test asserts they pass validation.
6. Keep the mock provider output code separate from the planner (no shared function) so fallback tests are not circular.

**Interfaces**

- API: API-22 · Tables: ai_generations, itinerary_items · Modules: MOD-B06, MOD-B07 · Other: io-1 schema

**Acceptance criteria**

- FR-036 AC1-AC3 hold (TC-145 to TC-147): unavailable provider -> labelled rule-based plan saved; two runs give identical plans; each destination has two saved samples that pass validation.
- Fallback plans contain no error-level finding by construction on the SAMPLE trips.
- Generation outcome recorded as fallback_rule_based; model_id is rule_based_planner_v1 for mode rule_based and the configured model for a fallback after an AI attempt (TC-331, IMD-43).

**Tests**

- apps/api/tests/unit/generation/test_fallback_planner.py — TC-146, TC-147 — `make test-unit ARGS='-k fallback'`
- apps/api/tests/api/test_generations.py — TC-145, TC-331 — `make test-api ARGS='-k fallback'`

**Completion evidence**

- PR with make check green.; Sample itinerary files committed with a passing validation test.

### IMP-403 Provider failure, timeout and quota handling end to end with fallback notice

**Task:** Sprint 4 (week 4) · CODE · 3 points · lead Nidhi with Krrish · release MVP

**Objective:** Every provider failure ends in the specified outcome and failure_reason: timeout, rate limit, outage, a breaker opened by transient errors, invalid output and unresolved validation produce a labelled rule-based plan; quota or cap exhaustion pauses AI with a rule-based option; config faults fail cleanly; the trip is never left half-changed.

**Owners and parts**

- Nidhi (lead) — Failure, timeout and quota outcomes end to end (2 points)
- Krrish — FallbackNotice on the generate page (1 points)
- One branch and pull request per part (`feat/IMP-403-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-059; FR-037; NFR-006, NFR-007, NFR-024

**Dependencies:** Prerequisites: IMP-401, IMP-402, IMP-305 · Downstream: IMP-414, IMP-499, IMP-502

**Files**

- apps/api/app/generation/pipeline.py (modify); apps/api/app/generation/service.py (modify); apps/api/app/generation/outcomes.py (create); apps/web/components/generation/FallbackNotice.tsx (modify); apps/web/app/(app)/trips/[tripId]/generate/page.tsx (modify); apps/api/tests/api/test_generation_failures.py (create); apps/web/tests/unit/generation/FallbackNotice.test.tsx (create)

**Implementation**

1. Implement outcomes.resolve(error_or_result) implementing the table of blueprint §19.2.2: ProviderTimeout/RateLimited/Unavailable after retries or breaker open for transient errors (a quota or auth breaker keeps the original failed cause, IMD-44) -> fallback_rule_based with fallback_reason provider_timeout/provider_rate_limited/provider_unavailable (stored in validation_summary.provider_failure; failure_reason stays null, IMD-22); ProviderInvalidOutput -> fallback_rule_based invalid_output; not usable after repair -> fallback_rule_based unresolved_validation; ProviderQuotaExhausted -> failed provider_quota_exhausted; AuthError/BadRequest -> failed config_error; unexpected -> failed internal.
2. Run the fallback planner automatically for the fallback outcomes inside the remaining 15 s reserve; if the fallback itself fails, end failed internal.
3. On failed outcomes write nothing to itinerary tables (old plan and plan_revision unchanged).
4. Map each outcome to a user message key; the web shows FallbackNotice ("Built by rules because the AI service was unavailable or failed checks"), a paused-AI notice with a "Build a rule-based plan" button (API-22 mode rule_based) for quota, and ErrorState with request_id for failed.
5. Failure-injection tests with MOCK scenarios timeout, rate_limited, quota, invalid_json, unknown_place and raise_error=ProviderUnavailable() / ProviderAuthError() (IMD-27).

**Interfaces**

- API: API-22, API-23 · Tables: ai_generations · Modules: MOD-B06, MOD-F04 · Components: FallbackNotice, GenerationProgress, ErrorState · Env: MOCK_PROVIDER_SCENARIO

**Acceptance criteria**

- FR-037 AC1-AC3 hold (TC-148 to TC-150): timeout retries then falls back; quota exhaustion pauses AI and offers rule-based; trip data unchanged after any failure.
- Each vendor failure maps to one shared type and failure_reason (TC-005, TC-017).
- Provider outage leaves the trip unchanged (TC-308); an invented place ID leads to the fallback plan (TC-307).
- No vendor message text appears in API-23 or logs (NFR-024).

**Tests**

- apps/api/tests/api/test_generation_failures.py — TC-148, TC-149, TC-150, TC-307, TC-308 — `make test-api ARGS='-k generation_failures'`
- apps/web/tests/unit/generation/FallbackNotice.test.tsx — new cases — `make test-web ARGS='FallbackNotice'`

**Completion evidence**

- PR with make check green.; Screenshots of the fallback notice and the paused-AI notice on the local stack.

### IMP-404 Validator: overlaps, travel gaps, missing constraints and invalid references

**Task:** Sprint 4 (week 4) · CODE · 7 points · lead Manal with Junaid · release MVP

**Objective:** A rule-registry validator produces findings with code, severity, item reference and suggested fix for OVERLAP, TRANSFER_TOO_SHORT, MUST_VISIT_MISSING, UNKNOWN_PLACE and OUTSIDE_TRIP_DATES on any plan, using the recalculated times and travel data.

**Owners and parts**

- Manal (lead) — Validator rules: overlaps, travel gaps (4 points)
- Junaid — Validator rules: missing constraints, invalid references (3 points)
- One branch and pull request per part (`feat/IMP-404-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-061, US-064; FR-050, FR-051, FR-055; NFR-030

**Dependencies:** Prerequisites: IMP-308 · Downstream: IMP-405, IMP-407, IMP-499, IMP-501

**Files**

- apps/api/app/validation/rules.py (create); apps/api/app/validation/validator.py (create); apps/api/app/schemas/ai.py (modify); apps/api/tests/unit/validation/test_rules_schedule.py (create); apps/api/tests/unit/validation/test_rules_references.py (create); apps/api/app/validation/README.md (create)

**Implementation**

1. Define Finding (code, severity error|warning|info, message <= 500, day_number, item_ref d<day>-i<pos> or place_id, suggested_fix <= 500) and the 13-code catalogue with severities of blueprint §20.4 in rules.py.
2. Implement validate(plan, ctx) -> list[Finding] running registered rules in fixed order; rules are pure (no I/O); ctx carries places, travel times, pace limits, must-visit IDs, trip dates and active place IDs.
3. OVERLAP: next start < previous end on the same day (back-to-back allowed; different days never compared).
4. TRANSFER_TOO_SHORT: 0 <= gap < travel minutes + buffer (5 after routing_api, 15 after fallback_estimate); message carries the shortfall.
5. MUST_VISIT_MISSING (place ID reference), UNKNOWN_PLACE (not an active place or not in the shortlist), OUTSIDE_TRIP_DATES (day outside 1..num_days; items on start and end dates accepted).
6. Document every rule with its boundary cases in app/validation/README.md.

**Interfaces**

- Modules: MOD-B07 · Other: finding codes OVERLAP, TRANSFER_TOO_SHORT, MUST_VISIT_MISSING, UNKNOWN_PLACE, OUTSIDE_TRIP_DATES

**Acceptance criteria**

- FR-050 AC1-AC2 hold (TC-176, TC-177); overlaps on different days are not flagged (TC-306).
- FR-051 AC1-AC2 hold (TC-178, TC-179).
- FR-055 AC1-AC2 hold (TC-186, TC-187); items on trip start and end dates are accepted (TC-305).
- Back-to-back items produce no OVERLAP; a 10-minute gap with a 30-minute transfer produces TRANSFER_TOO_SHORT.
- Statement coverage of app/validation >= 85 percent (TC-334).

**Tests**

- apps/api/tests/unit/validation/test_rules_schedule.py — TC-176, TC-177, TC-178, TC-179, TC-306 — `make test-unit ARGS='-k rules_schedule'`
- apps/api/tests/unit/validation/test_rules_references.py — TC-186, TC-187, TC-305 — `make test-unit ARGS='-k rules_references'`

**Completion evidence**

- PR with make check green and coverage report for app/validation.

### IMP-405 Structured warnings with suggested fixes, persisted with the plan, warnings panel

**Task:** Sprint 4 (week 4) · CODE · 4 points · lead Manasvi with Jeel · release MVP

**Objective:** Every finding carries a cause and at least one suggested fix, findings and the validation summary are stored with the plan revision and version, API-24 and API-32 return them, and the itinerary page shows a WarningsPanel grouped by severity with links to the items.

**Owners and parts**

- Manasvi (lead) — WarningsPanel (2 points)
- Jeel — Persist structured warnings and suggested fixes with the plan (2 points)
- One branch and pull request per part (`feat/IMP-405-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-065, US-067; FR-056, FR-058; NFR-028

**Dependencies:** Prerequisites: IMP-404, IMP-202 · Downstream: IMP-499, IMP-502

**Files**

- apps/api/app/validation/validator.py (modify); apps/api/app/validation/router.py (create); apps/api/app/itinerary/repository.py (modify); apps/web/components/itinerary/WarningsPanel.tsx (create); apps/web/tests/unit/itinerary/WarningsPanel.test.tsx (create); apps/api/tests/api/test_itinerary.py (modify); apps/api/tests/unit/validation/test_findings.py (create)

**Implementation**

1. Attach suggested_fix text from the catalogue to every finding (e.g. OVERLAP: move the later item to end + travel + buffer, or swap).
2. Persist findings as itinerary_warnings rows (trip_id, plan_revision, code, severity, message, day_number, item_id, place_id, suggested_fix; MUST_VISIT_MISSING stores place_id with item_id null, IMD-42) and validation_summary (counts by severity, deterministic_repairs, repair_attempts) on itinerary_versions and ai_generations, inside the save transaction.
3. API-24 returns warnings for the current plan_revision; implement API-32 POST /api/v1/trips/{trip_id}/itinerary/validate that re-runs validation, replaces the warnings for the current revision and returns them (owner only).
4. WarningsPanel: findings grouped by severity then day, text and icon, suggested fix, "Go to item" link focusing the ItineraryItemCard; announced via a polite live region.
5. Reading a stored version returns its stored warnings (restore offers revalidation; full version UI in IMP-610).

**Interfaces**

- API: API-24, API-32 · Tables: itinerary_warnings, itinerary_versions, ai_generations · Modules: MOD-B07, MOD-B08, MOD-F04 · Components: WarningsPanel, ItineraryItemCard

**Acceptance criteria**

- FR-056 AC1-AC2 hold (TC-188, TC-189).
- FR-058 AC1-AC2 hold (TC-193, TC-194): saved version returns its warnings and repair summary.
- API-32 by another user returns 404.
- WarningsPanel shows cause and suggested fix for each finding and is keyboard reachable.

**Tests**

- apps/api/tests/unit/validation/test_findings.py — TC-188, TC-189 — `make test-unit ARGS='-k findings'`
- apps/api/tests/api/test_itinerary.py — TC-193, TC-194 — `make test-api ARGS='-k warnings'`
- apps/web/tests/unit/itinerary/WarningsPanel.test.tsx — new cases — `make test-web ARGS='WarningsPanel'`

**Completion evidence**

- PR with make check green.; Screenshot of the WarningsPanel for the MOCK flawed scenario.

### IMP-406 Preserve explicit constraints and must-visit places; label AI-written text

**Task:** Sprint 4 (week 4) · CODE · 4 points · lead Manya with Krrish · release MVP

**Objective:** Must-visit places and explicit constraints survive generation (present, or reported with MUST_VISIT_MISSING and a reason), and AI-written text is stored and shown separately from retrieved facts with an AI-written label.

**Owners and parts**

- Manya (lead) — Keep must-visit places and explicit constraints in the pipeline (3 points)
- Krrish — AI-written text labels on item cards (1 points)
- One branch and pull request per part (`feat/IMP-406-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-056, US-057; FR-034, FR-035; NFR-016

**Dependencies:** Prerequisites: IMP-305 · Downstream: IMP-499, IMP-709

**Files**

- apps/api/app/generation/pipeline.py (modify); apps/api/app/generation/retrieval.py (modify); apps/api/app/itinerary/service.py (modify); apps/web/components/itinerary/ItineraryItemCard.tsx (modify); apps/api/tests/api/test_generations.py (modify); apps/web/tests/unit/labels/AiBadge.test.tsx (create)

**Implementation**

1. Force must-visit place IDs into the shortlist regardless of rank or size cap; after recalculation check each is in the plan.
2. If a must-visit place is absent, emit MUST_VISIT_MISSING (error) with the reason (filter conflict, closed every day, no room) and a suggested fix; never drop it silently.
3. Check explicit constraints after generation: step-free, excluded categories and pace limits; violations become findings.
4. Store model text only in itinerary_days.theme and itinerary_items.note with note_origin ai; facts (hours, prices, travel) come only from columns filled by the backend.
5. Show AiBadge on theme and note with note_origin ai; SourceBadge stays on hours and price.

**Interfaces**

- Tables: itinerary_items, itinerary_days, trip_places · Modules: MOD-B06, MOD-B07, MOD-B08, MOD-F04 · Components: AiBadge, SourceBadge, ItineraryItemCard

**Acceptance criteria**

- FR-034 AC1-AC2 hold (TC-141, TC-142).
- FR-035 AC1-AC2 hold (TC-143, TC-144): AI note and retrieved fact are distinct columns and labels.
- With MOCK dropping a must-visit place, the saved plan has MUST_VISIT_MISSING naming it.

**Tests**

- apps/api/tests/api/test_generations.py — TC-141, TC-142, TC-143, TC-144 — `make test-api ARGS='-k must_visit or ai_text'`
- apps/web/tests/unit/labels/AiBadge.test.tsx — new cases — `make test-web ARGS='AiBadge'`

**Completion evidence**

- PR with make check green.; Screenshot showing AI-written label beside a source-labelled price.

### IMP-407 Edit transaction core: recalculate and revalidate every edit atomically with plan revision

**Task:** Sprint 4 (week 4) · CODE · 5 points · lead Het · release MVP

**Objective:** Every itinerary edit runs through one edit pipeline that, in a single transaction, checks plan_revision, applies the operation, recalculates times and costs, revalidates, saves warnings, increments plan_revision and returns the recalculated day, totals and findings.

**Amended by A1 (2 November 2026):** edits keep the `source_chunk_ids` of every item they keep (Amendment A1 §6.10, IMD-110).

**Owners and parts:** Het — whole task (5 points); branch `feat/IMP-407-<short>`

**Traces to:** Stories US-073; FR-064; NFR-003, NFR-008

**Dependencies:** Prerequisites: IMP-308, IMP-404 · Downstream: IMP-408, IMP-409, IMP-499, IMP-504, IMP-505, IMP-506, IMP-610, IMP-612, IMP-710

**Files**

- apps/api/app/itinerary/edits.py (create); apps/api/app/itinerary/service.py (modify); apps/api/app/itinerary/schemas.py (modify); apps/api/tests/api/test_edits.py (create); apps/api/tests/api/test_edit_performance.py (create)

**Implementation**

1. Define EditOperation variants (move, retime, remove, add, lock, replace) and apply_edit(trip_id, user_id, base_revision, op) in app/itinerary/edits.py; locking the trip row (SELECT ... FOR UPDATE) inside the transaction.
2. If base_revision != trips.plan_revision raise StalePlan -> 409 STALE_PLAN with nothing changed (full UX in IMP-504).
3. Before the revision check refuse with 409 GENERATION_IN_PROGRESS when a generation for the trip is queued, running, validating or repairing (IMD-23).
4. Structurally impossible edits (day out of range, unknown place, moving a locked item) raise InvalidEdit -> 422 INVALID_EDIT.
5. After applying: schedule.recalculate (IMP-308), budget engine, validator (IMP-404); save items, warnings for the new revision, plan_revision + 1, and an automatic itinerary_versions row with reason edit (IMD-18; pruned by IMP-610; with the versions switch off only one backup copy is kept).
6. Edits with resulting conflicts succeed and return the findings (PR-06); only impossible edits are rejected.
7. Edit response schema: {plan_revision, day (recalculated), totals, warnings}; the web replaces its cache with it.

**Interfaces**

- API: API-25, API-26, API-27, API-29 · Tables: itinerary_items, itinerary_warnings, itinerary_versions, trips · Modules: MOD-B08, MOD-B07, MOD-B09

**Acceptance criteria**

- FR-064 AC1-AC2 hold (TC-206, TC-207): every edit response has recalculated totals; a failing validation step leaves data consistent and is reported.
- An interrupted edit leaves consistent data (TC-312, fault injection).
- Edit recalculation on a 10-day fixture stays under the p95 1.5 s target locally (TC-330, recorded, not a gate).
- A stale base revision returns 409 STALE_PLAN and changes nothing.
- An edit while a generation for the trip is active returns 409 GENERATION_IN_PROGRESS and changes nothing (IMD-23).

**Tests**

- apps/api/tests/api/test_edits.py — TC-206, TC-207, TC-312 — `make test-api ARGS='-k edits'`
- apps/api/tests/api/test_edit_performance.py — TC-330 — `make test-api ARGS='-k edit_performance'`

**Completion evidence**

- PR with make check green.; Timing output of the 10-day fixture test in the PR.

### IMP-408 Remove an activity and change start time or duration

**Task:** Sprint 4 (week 4) · CODE · 4 points · lead Het with Manasvi · release MVP

**Objective:** A traveller can remove an item (with an undo message) and change an item's start time or duration; each change goes through the edit pipeline and the page shows the recalculated day, totals and warnings returned by the server.

**Owners and parts**

- Het (lead) — Remove and retime edit operations (2 points)
- Manasvi — ItemEditor (2 points)
- One branch and pull request per part (`feat/IMP-408-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-070, US-072; FR-061, FR-063; NFR-003

**Dependencies:** Prerequisites: IMP-407, IMP-309 · Downstream: IMP-414, IMP-499

**Files**

- apps/api/app/itinerary/router.py (modify); apps/api/app/itinerary/edits.py (modify); apps/web/components/itinerary/ItemEditor.tsx (create); apps/web/components/itinerary/ItineraryItemCard.tsx (modify); apps/web/lib/api/queries.ts (modify); apps/api/tests/api/test_edits.py (modify); apps/web/tests/unit/itinerary/ItemEditor.test.tsx (create)

**Implementation**

1. API-27 DELETE /api/v1/itinerary/items/{item_id} with plan_revision as a query parameter (?plan_revision=N, IMD-26): remove op; removing a must-visit item yields MUST_VISIT_MISSING in the response.
2. API-26 PATCH /api/v1/itinerary/items/{item_id} with {plan_revision, start_time?, duration_min?}: retime op; duration outside 15-480 -> 422 VALIDATION_ERROR; following items shift or conflicts are flagged.
3. Ownership via the item's trip: another user gets 404.
4. ItemEditor: inline time and duration inputs with zod rules mirroring the server; saving state on the item; ConfirmDialog for removal and a Toast with undo (undo re-adds via API-25 when available, otherwise restores through a new edit; Provisional: undo within the toast lifetime only).
5. Mutations invalidate ["itinerary", tripId] and ["costs", tripId] together and apply the server response; no client-side recalculation.

**Interfaces**

- API: API-26, API-27 · Tables: itinerary_items · Modules: MOD-B08, MOD-F04 · Components: ItemEditor, ItineraryItemCard, ConfirmDialog, Toast

**Acceptance criteria**

- FR-061 AC1-AC2 hold (TC-200, TC-201).
- FR-063 AC1-AC2 hold (TC-204, TC-205).
- Totals on the page after an edit equal the API response values.

**Tests**

- apps/api/tests/api/test_edits.py — TC-200, TC-201, TC-204, TC-205 — `make test-api ARGS='-k remove or retime'`
- apps/web/tests/unit/itinerary/ItemEditor.test.tsx — new cases — `make test-web ARGS='ItemEditor'`

**Completion evidence**

- PR with make check green.; Short screen recording or screenshots of remove and retime on the local stack.

### IMP-409 Reorder by drag and by keyboard

**Task:** Sprint 4 (week 4) · CODE · 5 points · lead Manasvi with Het · release MVP

**Objective:** Items can be reordered within and across days by drag and drop (dnd-kit) and by keyboard move controls with screen-reader announcements; both call the same move operation and show the recalculated result and any conflict warning.

**Owners and parts**

- Manasvi (lead) — Drag-and-drop and keyboard MoveControls (dnd-kit) (3 points)
- Het — Move/reorder edit operation (2 points)
- One branch and pull request per part (`feat/IMP-409-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-069; FR-060; NFR-003, NFR-025

**Dependencies:** Prerequisites: IMP-407, IMP-309 · Downstream: IMP-414, IMP-499

**Files**

- apps/api/app/itinerary/edits.py (modify); apps/web/components/itinerary/MoveControls.tsx (create); apps/web/components/itinerary/DayColumn.tsx (modify); apps/web/tests/unit/itinerary/MoveControls.test.tsx (create); apps/api/tests/api/test_edits.py (modify)

**Implementation**

1. Move op on API-26: {plan_revision, day_number, position}; renumber positions in both affected days inside the transaction (deferrable unique constraint on day_id, position).
2. Drag and drop with dnd-kit pointer and keyboard sensors; drop calls the mutation; optimistic reordering is not used (server response replaces data).
3. MoveControls: Move up, Move down, Move to day buttons with aria-labels; announce "Moved <place> to day N position M" in a polite live region.
4. Conflicts after a move appear in WarningsPanel; the edit is not hidden or reverted.

**Interfaces**

- API: API-26 · Modules: MOD-B08, MOD-F04 · Components: MoveControls, DayColumn, ItineraryItemCard, WarningsPanel

**Acceptance criteria**

- FR-060 AC1-AC3 hold (TC-197, TC-198, TC-199).
- Keyboard-only reordering works without a pointer (TC-374 path, full keyboard journey verified in IMP-513).

**Tests**

- apps/api/tests/api/test_edits.py — TC-199 — `make test-api ARGS='-k move'`
- apps/web/tests/unit/itinerary/MoveControls.test.tsx — TC-197, TC-198 — `make test-web ARGS='MoveControls'`

**Completion evidence**

- PR with make check green.; Screen recording of drag and keyboard reorder.

### IMP-410 Drafts and reopening the latest saved itinerary

**Task:** Sprint 4 (week 4) · CODE · 4 points · lead Manal with Krrish · release MVP

**Objective:** The trip wizard autosaves a draft after each step and restores it later; Open latest opens the newest saved itinerary or offers generation when none exists.

**Owners and parts**

- Manal (lead) — Draft trips and latest-itinerary reopening API (2 points)
- Krrish — Draft resume in wizard and dashboard (2 points)
- One branch and pull request per part (`feat/IMP-410-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-019, US-020; FR-013, FR-014; NFR-002

**Dependencies:** Prerequisites: IMP-212, IMP-211 · Downstream: IMP-499, IMP-602

**Files**

- apps/api/app/trips/service.py (modify); apps/api/app/itinerary/router.py (modify); apps/web/components/trips/TripWizard.tsx (modify); apps/web/app/(app)/dashboard/page.tsx (modify); apps/api/tests/api/test_trips.py (modify); apps/api/tests/api/test_itinerary.py (modify)

**Implementation**

1. Drafts: API-07 creates with status draft and accepts partial optional fields allowed by FR-013; API-11 PATCH saves each wizard step; required fields are enforced only when the trip moves to ready (API-22 validation step).
2. Wizard: autosave on step change (debounced 1 s), "Continue draft" entry on the dashboard for draft trips, form restored from API-10 + API-15.
3. API-09 GET /api/v1/itineraries/latest: the trip with the most recent itinerary_versions.created_at for the user; 200 {trip_id, version_id} or 404 NOT_FOUND when none (web then offers generation via EmptyState, not an error).
4. Dashboard "Open latest" action uses API-09.

**Interfaces**

- API: API-07, API-09, API-10, API-11, API-15 · Tables: trips, trip_preferences, itinerary_versions · Modules: MOD-B03, MOD-B08, MOD-F02 · Components: TripWizard, EmptyState

**Acceptance criteria**

- FR-013 AC1-AC2 hold (TC-085, TC-086), including resume after sign-out.
- FR-014 AC1-AC2 hold (TC-087, TC-088).

**Tests**

- apps/api/tests/api/test_trips.py — TC-085, TC-086 — `make test-api ARGS='-k draft'`
- apps/api/tests/api/test_itinerary.py — TC-087, TC-088 — `make test-api ARGS='-k latest'`

**Completion evidence**

- PR with make check green.; Screenshot of the continue-draft and open-latest entries.

### IMP-411 Transport allowance, stay budget and price source labels

**Task:** Sprint 4 (week 4) · CODE · 4 points · lead Manal with Krrish · release MVP

**Objective:** Travellers can set a transport allowance per day and a stay budget per night that enter the cost totals labelled "traveller input", and every price in the API and UI carries exactly one of Estimate, Curated (with date) or Unavailable, never Live or Verified.

**Owners and parts**

- Manal (lead) — Transport allowance, stay budget, price source labels API (2 points)
- Krrish — BudgetSettingsForm and SourceBadge variants (2 points)
- One branch and pull request per part (`feat/IMP-411-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-081, US-083; FR-072, FR-076; NFR-028

**Dependencies:** Prerequisites: IMP-308 · Downstream: IMP-499, IMP-507, IMP-604

**Files**

- apps/api/app/budget/router.py (modify); apps/api/app/budget/repository.py (create); apps/api/app/schemas/labels.py (modify); apps/web/components/costs/BudgetSettingsForm.tsx (create); apps/web/components/trips/TripWizard.tsx (modify); apps/web/components/labels/SourceBadge.tsx (modify); apps/api/tests/unit/budget/test_allowances.py (create); apps/web/tests/unit/labels/SourceBadge.test.tsx (create)

**Implementation**

1. API-34 PATCH /api/v1/trips/{trip_id}/budget-settings {transport_allowance_per_day?, stay_budget_per_night?} (decimal strings, >= 0; contingency_pct accepted but its UI is IMP-608); owner only; upsert budget_settings; upserts budget_settings only and returns the recalculated CostSummaryOut with its budget findings, without writing itinerary_warnings (§6).
2. Budget engine BF-05/BF-06 use the inputs; missing input -> line Unavailable and the total states it.
3. Define the label enum in app/schemas/labels.py as exactly {curated, estimate, unavailable}; curated carries checked_on date; a unit test asserts no other value can be serialised.
4. Wizard budget step: BudgetSettingsForm fields; SourceBadge shows text plus colour (never colour alone).

**Interfaces**

- API: API-34, API-33 · Tables: budget_settings, places · Modules: MOD-B09, MOD-F02, MOD-F07 · Components: BudgetSettingsForm, SourceBadge

**Acceptance criteria**

- FR-072 AC1-AC2 hold (TC-223, TC-224).
- FR-076 AC1-AC2 hold (TC-231, TC-232): no live or verified label can be produced.
- Another user's PATCH returns 404.

**Tests**

- apps/api/tests/unit/budget/test_allowances.py — TC-223, TC-224, TC-232 — `make test-unit ARGS='-k allowances or labels'`
- apps/web/tests/unit/labels/SourceBadge.test.tsx — TC-231 — `make test-web ARGS='SourceBadge'`

**Completion evidence**

- PR with make check green.; Screenshot of the cost strip with traveller-input lines.

### IMP-412 Loading, empty and error states on every MVP screen

**Task:** Sprint 4 (week 4) · CODE · 3 points · lead Manasvi · release MVP

**Objective:** Every MVP screen shows a LoadingSkeleton while waiting, an EmptyState with a next action when there is nothing, and an ErrorState that says what happened and what to do next with the request_id, using one error catalogue keyed by API error code.

**Owners and parts:** Manasvi — whole task (3 points); branch `feat/IMP-412-<short>`

**Traces to:** Stories US-124; FR-116; NFR-028

**Dependencies:** Prerequisites: IMP-104 · Downstream: IMP-499, IMP-513

**Files**

- apps/web/components/states/LoadingSkeleton.tsx (modify); apps/web/components/states/EmptyState.tsx (modify); apps/web/components/states/ErrorState.tsx (modify); apps/web/lib/api/errors.ts (create); docs/guides/error-catalogue.md (create); apps/web/tests/unit/states/ErrorState.test.tsx (create)

**Implementation**

1. Write the error catalogue: one entry per §6 error code (UNAUTHENTICATED, NOT_FOUND, STALE_PLAN, GENERATION_IN_PROGRESS, CONFLICT, VALIDATION_ERROR, INVALID_EDIT, RATE_LIMITED, AI_QUOTA_REACHED, INTERNAL, SERVICE_UNAVAILABLE, network error) with "what happened" and "what to do next" text, in docs/guides/error-catalogue.md and lib/api/errors.ts.
2. ErrorState shows the catalogue text, a retry or navigation action and the request_id; RATE_LIMITED shows retry_after_s.
3. Apply the three states to trip wizard, dashboard, explore, generate and itinerary pages (remaining pages adopt them when built).
4. Review the catalogue against all messages in the app (Krrish) and record the review in the PR.

**Interfaces**

- Modules: MOD-F07 · Components: LoadingSkeleton, EmptyState, ErrorState, Toast

**Acceptance criteria**

- FR-116 AC1 holds (TC-281): a failed request states what happened and what to do.
- Error catalogue review recorded (TC-384).
- No screen shows a raw error object or stack text.

**Tests**

- apps/web/tests/unit/states/ErrorState.test.tsx — TC-281 — `make test-web ARGS='ErrorState'`

**Completion evidence**

- PR with make check green.; docs/guides/error-catalogue.md and review note.

### IMP-413 Evaluation harness (command line)

**Task:** Sprint 4 (week 4) · CODE · 3 points · lead Manya · release MVP

**Objective:** python -m app.evaluation.run --dataset itinerary/v1 --provider MOCK runs every case through the same pipeline functions offline, computes the versioned metric definitions with the production validator and budget engine, and writes results and a manifest.

**Owners and parts:** Manya — whole task (3 points); branch `feat/IMP-413-<short>`

**Traces to:** Stories US-128; FR-119; NFR-046

**Dependencies:** Prerequisites: IMP-310, IMP-207 · Downstream: IMP-499, IMP-514

**Files**

- apps/api/app/evaluation/run.py (create); apps/api/app/evaluation/metrics.py (create); apps/api/app/evaluation/manifest.py (create); eval/metrics_v1.md (create); apps/api/tests/unit/evaluation/test_harness.py (create)

**Implementation**

1. CLI arguments: --dataset, --provider (MOCK|GEMINI|RULE_BASED), --repeats (default 3), --out eval/results/<run_id>/; the provider instance is chosen by the flag and never changes the application default.
2. For each case: run steps 6 to 10 on the frozen request, store the raw output, score with the production validator and budget engine.
3. Implement metrics 1 to 6, 10, 11 and 13 of blueprint §21.4 (12 cost per success with a dated price table or null; 7 and 9 marked not computed in v1) with definitions fixed in eval/metrics_v1.md.
4. Write a run manifest: run_id, dataset id/version/hash, provider, model_id, prompt template id/version, schema versions, settings sent, git commit, start/end times.
5. GEMINI runs are manual (make eval PROVIDER=GEMINI) and count against the caps; never run in PR CI.

**Interfaces**

- Modules: MOD-B15, MOD-B06, MOD-B07, MOD-B09 · Env: AI_PROVIDER, GEMINI_API_KEY · Other: eval/datasets/trips/v1, make eval

**Acceptance criteria**

- FR-119 AC1-AC2 hold (TC-285, TC-286): MOCK run completes offline; metric definitions are identical across providers.
- Harness dry run with MOCK passes in CI (TC-387).
- Output validity uses the same validator as production (TC-041).

**Tests**

- apps/api/tests/unit/evaluation/test_harness.py — TC-285, TC-286, TC-387, TC-041 — `make test-unit ARGS='-k harness'`
- eval/results/ — new cases — `make eval DATASET=trips/v1 PROVIDER=MOCK`

**Completion evidence**

- PR with make check green.; eval/results/<run_id>/run.json from a MOCK run committed or attached.

### IMP-318 Retrieval evaluation: recall, hit rate, citation validity and grounding rate

**Task:** Sprint 4 (week 4) · CODE · 2 points · lead Junaid · release MVP (Amendment A1)

**Objective:** The evaluation harness has a retrieval suite. It measures, on a team-labelled query set:

- `recall@6` of relevant guide documents;
- the hit rate of relevant places in the top 12, in vector and lexical mode;
- citation validity and grounding rate of generated plans.

Every number carries its run metadata.

**Owners and parts:** Junaid — whole task (2 points); branch `feat/IMP-318-whole-task`

**Traces to:** Stories US-167; FR-140; NFR-041, NFR-046

**Dependencies:** Prerequisites: IMP-413, IMP-316, IMP-314 (labels for destination 1), Amendment A1 §6.14 · Downstream: IMP-514, IMP-705

**Files**

- eval/datasets/retrieval/v1/queries.jsonl (create)
- eval/datasets/retrieval/v1/manifest.json (create)
- apps/api/app/evaluation/retrieval_metrics.py (create; pure)
- apps/api/app/evaluation/run.py (modify: `--suite retrieval`)
- apps/api/tests/unit/evaluation/test_retrieval_metrics.py (create)

**Implementation**

1. **Labelled queries.** Write `queries.jsonl` with 10 to 20 lines for the SAMPLE fixture and destination 1. Each line holds a destination slug, preference fields and notes, `relevant_guide_doc_keys` and `relevant_place_refs`. Place references are stable `{source_name, external_ref}` pairs, never database UUIDs, which change on every reseed; the harness resolves them to IDs.
   - Junaid writes the labels and Malhar and Krrish review them; record the reviewers in `manifest.json`.
   - The labels are member input under the DATA rule: Claude Code never invents labels and may only build the file layout and validate it. The planner asks the operator for the labelled file before the run.
2. **Metrics.** `retrieval_metrics.py` (pure):
   - `recall_at_k(selected_doc_keys, relevant, k=6)`;
   - `place_hit_rate(ranked_place_ids, relevant, top=12)`;
   - `citation_validity(saved_ids, supplied_ids)` (must be 1.0);
   - `grounding_rate(items)`, the share of AI-written notes with at least one citation.
3. **Harness.** `make eval` passes `$(ARGS)` to the harness; add the pass-through if the Makefile lacks it. `run.py --suite retrieval` runs `rag.service.retrieve` and the ranking for every query, in vector mode and with embeddings forced off (lexical). For the generation metrics it runs the MOCK pipeline. It writes `eval/results/<run_id>/run.json` with dataset version, provider, embedding model and commit SHA (NFR-041), and a short report in `eval/reports/`.
4. **Tests.** Unit tests for every metric (edge cases: empty relevant set, k larger than the list) and one harness run on the SAMPLE queries with MOCK, which must be identical on a second run.

**Interfaces**

- Modules: MOD-B15, MOD-B18
- Env: AI_PROVIDER, GEMINI_EMBEDDING_MODEL_ID
- Other: eval/datasets/retrieval/v1/, Amendment A1 §6.14

**Acceptance criteria**

- The harness reports `recall@6` and the place hit rate in vector and lexical mode (FR-140 AC1, TC-458).
- It reports citation validity (1.0) and grounding rate for MOCK generations (FR-140 AC2, TC-458).
- Each run record names the dataset version, provider, embedding model and commit; two MOCK runs give identical numbers (FR-140 AC3, NFR-041).

**Tests**

- apps/api/tests/unit/evaluation/test_retrieval_metrics.py — TC-458 — `make test-unit ARGS='-k retrieval_metrics'`
- eval/ (harness run) — TC-458 — `make eval DATASET=retrieval/v1 ARGS='--suite retrieval'`

**Completion evidence**

- Two identical MOCK run records under eval/results/; the report in eval/reports/; label review recorded in the manifest

### IMP-414 End-to-end journey test on staging

**Task:** Sprint 4 (week 4) · VERIFY · 5 points · lead Krrish with Junaid · release MVP

**Objective:** A Playwright journey test (sign up, create a trip, generate with MOCK, edit, save and reopen) passes against the local stack in CI and against staging, and one Gemini run of the same journey is recorded.

**Owners and parts**

- Krrish (lead) — E2E journey test on staging (3 points)
- Junaid — Journey test fixtures, test report (2 points)
- One branch and pull request per part (`feat/IMP-414-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-140; NFR-048

**Dependencies:** Prerequisites: IMP-403, IMP-408, IMP-409 · Downstream: IMP-499, IMP-611, IMP-701

**Files**

- apps/web/e2e/journey.spec.ts (modify); apps/web/e2e/fixtures/users.ts (modify); .github/workflows/e2e.yml (modify); docs/test-reports/journey-sprint4.md (create)

**Implementation**

1. Extend e2e/journey.spec.ts (created by IMP-216): create a test user (local service-role key via e2e/fixtures/users.ts; on staging a pre-created test account), create a SAMPLE trip, generate with AI_PROVIDER=MOCK, wait for completed, remove one item and retime another, reload, open latest, assert the edits and server totals persist.
2. Add a staging reset step: delete the e2e test user's trips via the API before the run (no direct database access from tests).
3. Run the journey in e2e.yml on merge to main and nightly against the composed local stack; add a manual staging job using BASE_URL.
4. Run the journey once manually with AI_PROVIDER=GEMINI on staging and record outcome, latency and any warnings in docs/test-reports/journey-sprint4.md.

**Interfaces**

- API: API-07, API-22, API-23, API-24, API-26, API-27, API-09 · Modules: MOD-P01, MOD-F04 · Env: SUPABASE_SERVICE_ROLE_KEY, AI_PROVIDER

**Acceptance criteria**

- The journey passes with MOCK on the local stack in CI (TC-369).
- The journey passes on staging with MOCK; the Gemini run is recorded with its date (TC-370).
- Test data is created through the app and removed after the run.

**Tests**

- apps/web/e2e/journey.spec.ts — TC-369 — `make e2e ARGS='journey'`
- apps/web/e2e/journey.spec.ts — TC-370 — `BASE_URL=<staging web url> make e2e ARGS='journey' (manual, Gemini)`

**Completion evidence**

- CI e2e job run link green.; docs/test-reports/journey-sprint4.md with the staging and Gemini results.

### IMP-499 Sprint 4 gate SG-4 (blueprint Gate 3) and cut-list checkpoint

**Task:** Sprint 4 (week 4) · VERIFY · 2 points · lead Kirtan · release MVP

**Objective:** Sprint gate SG-4 (blueprint Gate 3) and the cut-list checkpoint are decided and recorded: the whole journey works on staging, a provider failure yields a labelled fallback plan, edits recalculate atomically, and any required cuts are applied by flag.

**Amended by A1 (2 November 2026):** also waits for IMP-318 (Amendment A1 §10.3).

**Owners and parts:** Kirtan — whole task (2 points); branch `feat/IMP-499-<short>`

**Traces to:** enabling work (no requirement)

**Dependencies:** Prerequisites: IMP-401, IMP-402, IMP-403, IMP-404, IMP-405, IMP-406, IMP-407, IMP-408, IMP-409, IMP-410, IMP-411, IMP-412, IMP-413, IMP-414, IMP-318 · Downstream: none

**Files**

- docs/progress/gates.md (modify); docs/progress/sprint-4.md (modify); docs/decisions/cut-list-checkpoint.md (create)

**Implementation**

1. Confirm the Sprint 4 tasks are done with evidence in docs/progress/sprint-4.md; a half-finished story counts as zero points.
2. On staging: run the journey (IMP-414), set AI_PROVIDER=MOCK with MOCK_PROVIDER_SCENARIO=timeout on staging (IMD-33) and show a labelled fallback plan; edit an item and confirm totals change in one response.
3. Count C = story points of stories completed in Sprints 1 to 4 (planned 203).
4. Compute points to cut = max(0, 359 - 2C); zones: C >= 180 no cut; 162 <= C <= 179 team and supervisor decide; C < 162 cuts mandatory; C < 158 even the whole list (43 points) is not enough and further scope reduction is escalated (Awaiting validation).
5. Apply cuts in cut-list order until the number is reached: 1 versions (8), 2 trip_management (5), 3 contingency (1), 4 budget_alerts (3), 5 wishlist (3), 6 alternatives (5), 7 regeneration (10), 8 locks (3), 9 meal_slots (5); set FEATURES_DISABLED and NEXT_PUBLIC_FEATURES_DISABLED, mark the affected IMP tasks as cut in TASK_REGISTER and docs/progress.
6. Record the gate result, C, the arithmetic, the decision and owners in docs/decisions/cut-list-checkpoint.md and docs/progress/gates.md.

**Interfaces**

- API: API-22, API-26, API-27 · Modules: MOD-P01 · Env: FEATURES_DISABLED, NEXT_PUBLIC_FEATURES_DISABLED

**Acceptance criteria**

- Sign-up to a saved, edited itinerary passes on staging (TC-369, IMP-414 evidence).
- A provider failure produces a labelled fallback plan (TC-148, IMP-403 evidence; the browser-level outage journey TC-371 follows in Sprint 7).
- Edits recalculate in one transaction (IMP-407 evidence).
- make check and the e2e job are green on main at the gate commit.
- The checkpoint decision with its arithmetic is recorded; any cut is applied by flag, not by deleting code.

**Tests**

- apps/web/e2e/journey.spec.ts — TC-369 — `make e2e ARGS='journey'`
- apps/api/tests/api/test_generation_failures.py — TC-148, TC-308 — `make test-api ARGS='-k generation_failures'`
- apps/api/tests/smoke/test_deployed.py — new cases — `make smoke URL=<staging api url>`

**Completion evidence**

- docs/decisions/cut-list-checkpoint.md with C, the arithmetic and the decision.; docs/progress/gates.md SG-4 entry with CI links.

## Sprint 5 (week 5): Core trip management — gate SG-5

| Task | Title | Type | Lead | Parts (points) | Prerequisites | Points |
| --- | --- | --- | --- | --- | --- | --- |
| IMP-501 | Opening-hours check, overpacked days and budget conflicts | CODE | Junaid | Junaid 3, Manal 2 | IMP-404, IMP-308 | 5 |
| IMP-502 | Bounded repair with at most one model retry | CODE | Nidhi | Nidhi 5 | IMP-405, IMP-403 | 5 |
| IMP-503 | Pace presets and grouping nearby places into days | CODE | Manya | Manya 6, Manasvi 1 | IMP-304, IMP-209 | 7 |
| IMP-504 | Add a user-selected place and reject stale edits | CODE | Het | Het 3, Malhar 2 | IMP-407 | 5 |
| IMP-505 | Replace an activity with a ranked alternative | CODE | Het | Het 3, Krrish 2 | IMP-407, IMP-304 | 5 |
| IMP-506 | Lock and unlock items | CODE | Het | Het 2, Krrish 1 | IMP-407 | 3 |
| IMP-507 | Daily and category cost breakdown; estimate labels on every screen | CODE | Manal | Manal 3, Manasvi 2 | IMP-411 | 5 |
| IMP-508 | Map with numbered markers and list fallback | CODE | Manasvi | Manasvi 5 | IMP-309 | 5 |
| IMP-509 | Browse places with source labels | CODE | Jeel | Jeel 3 | IMP-205, IMP-206 | 3 |
| IMP-510 | Edit trip settings and flag a stale plan | CODE | Manal | Manal 1, Krrish 1 | IMP-203, IMP-212 | 2 |
| IMP-511 | Rate limits and daily generation caps | CODE | Kirtan | Kirtan 5 | IMP-202, IMP-201 | 5 |
| IMP-512 | Provider contract test suite for all adapters | CODE | Junaid | Junaid 3 | IMP-401, IMP-207 | 3 |
| IMP-513 | Keyboard and assistive-technology support | CODE | Krrish | Krrish 3 | IMP-412 | 3 |
| IMP-514 | Evaluation run records and first Gemini baseline | DATA | Manya | Manya 2, Nidhi 1 | IMP-413, IMP-301 | 3 |
| IMP-515 | Explain the ranking: "Why this place?" panel | CODE | Jeel | Jeel 2, Krrish 2 | IMP-304, IMP-509 | 4 |
| IMP-599 | Sprint 5 gate SG-5 | VERIFY | Kirtan | Kirtan 0 | IMP-501, IMP-502, IMP-503, IMP-504, IMP-505, IMP-506, IMP-507, IMP-508, IMP-509, IMP-510, IMP-511, IMP-512, IMP-513, IMP-514, IMP-515 | 0 |


### IMP-501 Opening-hours check, overpacked days and budget conflicts

**Task:** Sprint 5 (week 5) · CODE · 5 points · lead Junaid with Manal · release MVP

**Objective:** The validator emits CLOSED_ON_DAY, OUTSIDE_HOURS, HOURS_UNVERIFIED, DAY_TOO_LONG, BUDGET_EXCEEDED, BUDGET_NEAR, COST_INCOMPLETE and ESTIMATE_USED with the §8/§9 severities after every generation, edit and API-32 call.

**Owners and parts**

- Junaid (lead) — Opening-hours and overpacked-day checks (3 points)
- Manal — Budget conflict check (2 points)
- One branch and pull request per part (`feat/IMP-501-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-062, US-063; FR-052 to FR-054; NFR-003, NFR-030, NFR-040

**Dependencies:** Prerequisites: IMP-404, IMP-308 · Downstream: IMP-599, IMP-608, IMP-710

**Files**

- apps/api/app/validation/rules.py (modify); apps/api/app/validation/validator.py (modify); apps/api/app/generation/pipeline.py (modify); apps/api/tests/unit/validation/test_hours.py (create); apps/api/tests/unit/validation/test_day_length_budget.py (create); apps/api/tests/api/test_itinerary.py (modify)

**Implementation**

1. Add the opening-hours rule to rules.py following the six-row decision list of §9 (blueprint §20.4): unavailable label or no rows -> HOURS_UNVERIFIED (info, no conflict claimed); previous-weekday row closing after midnight that covers the visit -> no finding; no row for the weekday -> HOURS_UNVERIFIED; closed row -> CLOSED_ON_DAY (error); visit inside an open row -> none; otherwise OUTSIDE_HOURS (error).
2. Evaluate start and end in the destination's local time zone (destinations.timezone) from itinerary_days.plan_date + start_time; never in UTC.
3. Add DAY_TOO_LONG (warning): active minutes = sum(duration_min) + sum(travel_from_prev_min) per day; compare with the pace preset of trip_preferences.pace (relaxed 3 items/300 min, balanced 5/480, busy 7/600, from settings, Provisional) and include both figures in the message.
4. Add the budget rules by calling the pure budget engine (app/budget/engine.py, BF-11) instead of re-computing totals: BUDGET_EXCEEDED (warning, message carries the excess as a money string) if P > B; BUDGET_NEAR (info) if 100*P >= theta*B with theta = 90 (code constant BUDGET_NEAR_PCT in app/budget/engine.py, IMD-29); no finding when the budget is empty or zero.
5. Add COST_INCOMPLETE (warning, trip-level) when any item cost_label is unavailable or uses a category estimate, and ESTIMATE_USED (info, item-level) for each item priced by a category estimate (BF-04).
6. Register the new rules in validator.py so pipeline step 9, the edit pipeline (IMP-407) and API-32 all run the same rule list; findings are persisted to itinerary_warnings by the existing writer (IMP-405).
7. Write boundary unit tests: closed day, unknown hours, overnight row, local time zone, pace limits at exactly the limit and one above, budget at 89, 90 and 101 percent.

**Interfaces**

- API: API-32, API-24 · Tables: itinerary_warnings, place_opening_hours, trip_preferences, destinations · Modules: MOD-B07, MOD-B09 · Other: finding codes §8, BF-11, constant BUDGET_NEAR_PCT in app/budget/engine.py (IMD-29)

**Acceptance criteria**

- FR-052 AC1-AC2, FR-053 AC1-AC2 and FR-054 AC1-AC2 hold (TC-180 to TC-185).
- A visit crossing midnight on an overnight row produces no finding (TC-301); hours are compared in destination local time (TC-302).
- Pace and near-budget thresholds are exact at the boundary (TC-303, TC-304).
- A place with unavailable hours never produces CLOSED_ON_DAY or OUTSIDE_HOURS.
- Budget findings are never repaired by dropping items (checked by a unit test on repair input).

**Tests**

- apps/api/tests/unit/validation/test_hours.py — TC-180, TC-181, TC-301, TC-302 — `make test-unit ARGS='-k hours'`
- apps/api/tests/unit/validation/test_day_length_budget.py — TC-182, TC-183, TC-184, TC-185, TC-303, TC-304 — `make test-unit ARGS='-k "day_length or budget"'`
- apps/api/tests/api/test_itinerary.py — TC-180 — `make test-api ARGS='-k validate'`

**Completion evidence**

- PR with make check green in CI; Unit test output listing the boundary cases; API-32 response JSON for a seeded SAMPLE trip showing the new codes

### IMP-502 Bounded repair with at most one model retry

**Task:** Sprint 5 (week 5) · CODE · 5 points · lead Nidhi · release MVP-S

**Objective:** Invalid plans are repaired deterministically first, then by at most one model call with the whole request and the exact findings, and anything unresolved is saved as visible findings or replaced by the rule-based plan.

**Owners and parts:** Nidhi — whole task (5 points); branch `feat/IMP-502-<short>`

**Traces to:** Stories US-066; FR-057; NFR-007, NFR-030

**Dependencies:** Prerequisites: IMP-405, IMP-403 · Downstream: IMP-599, IMP-607

**Files**

- apps/api/app/validation/repair.py (create); apps/api/app/generation/pipeline.py (modify); apps/api/tests/unit/validation/test_repair.py (create); apps/api/tests/api/test_generations.py (modify); apps/api/app/ai/prompts/templates/itinerary_generate/v1/repair.txt (create)

**Implementation**

1. Implement deterministic repair in repair.py (pure, no I/O): forward-shift start times to max(own start, previous end + travel + buffer) skipping locked items; then for error findings in the fixed order UNKNOWN_PLACE, OUTSIDE_TRIP_DATES, CLOSED_ON_DAY, OUTSIDE_HOURS, OVERLAP apply the cheapest fix (move to another day with room, swap with next item, drop the lowest-ranked unlocked non-must-visit item); insert a missing must-visit into the best day with room; count each fix.
2. Never change prices, hours or travel times; never move is_locked items; never drop must-visit places; never act on budget findings.
3. In pipeline step 10 (pipeline.py): after deterministic repair, revalidate; if errors remain and repair_attempts = 0, make exactly one provider call with the previous output and the exact findings in repair_context using the itinerary_generate/v1 template with its repair.txt appended (§8.5, §8.13), with its own 25 s allowance and no transport retry; set ai_generations.repair_attempts = 1 and status repairing.
4. Revalidate the repaired output; if usable (at least one item and none of UNKNOWN_PLACE, OUTSIDE_TRIP_DATES, OVERLAP, CLOSED_ON_DAY remains, §8.12) save with outcome model_repaired and the remaining warnings; otherwise build the rule-based plan (IMP-402) and save with outcome fallback_rule_based, failure_reason null and validation_summary.provider_failure = unresolved_validation (returned as fallback_reason, IMD-22).
5. Store deterministic_repairs count and the validation_summary on ai_generations.
6. Add tests with the MOCK scenarios invalid_json and unknown_place and flawed (overlap and missing must-visit place); assert the provider call count via the mock call log.

**Interfaces**

- API: API-22, API-23 · Tables: ai_generations, itinerary_warnings · Modules: MOD-B07, MOD-B06, MOD-B05 · Env: MOCK_PROVIDER_SCENARIO · Other: repair_context (§8), prompt template itinerary_repair v1

**Acceptance criteria**

- FR-057 AC1-AC3 hold (TC-190 to TC-192).
- Invalid model output is routed to repair, never to a blind retry (TC-011); the mock records at most 2 calls per generation (1 generate + 1 repair).
- Locked items and must-visit places are unchanged by repair (TC-313 repair part).
- Repair terminates on every fixture (no loop) and repair_attempts is never above 1 (DB check constraint).

**Tests**

- apps/api/tests/unit/validation/test_repair.py — TC-190, TC-313 — `make test-unit ARGS='-k repair'`
- apps/api/tests/api/test_generations.py — TC-011, TC-191, TC-192 — `make test-api ARGS='-k repair'`

**Completion evidence**

- PR with make check green; Test log showing provider call counts per scenario; API-23 JSON of a model_repaired generation from the MOCK scenario

### IMP-503 Pace presets and grouping nearby places into days

**Task:** Sprint 5 (week 5) · CODE · 7 points · lead Manya with Manasvi · release MVP

**Objective:** Pace presets set the per-day item and active-minute limits used by grouping, prompt hints and validation, and the shortlist is grouped into geographically compact days passed as day_hints.

**Owners and parts**

- Manya (lead) — Pace presets and grouping nearby places into days (6 points)
- Manasvi — Pace control in the preference form (1 points)
- One branch and pull request per part (`feat/IMP-503-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-054, US-055; FR-029, FR-030; NFR-030

**Dependencies:** Prerequisites: IMP-304, IMP-209 · Downstream: IMP-599, IMP-606

**Files**

- apps/api/app/core/config.py (modify); apps/api/app/generation/grouping.py (create); apps/api/app/generation/request_builder.py (modify); apps/web/components/trips/PreferenceForm.tsx (modify); apps/api/tests/unit/generation/test_grouping.py (create); apps/api/tests/unit/generation/test_pace.py (create); apps/api/app/generation/presets.py (create)

**Implementation**

1. Define the PACE_PRESETS code constant in app/generation/presets.py (IMD-29; not an environment variable) (relaxed: 3 items, 300 active min; balanced: 5, 480; busy: 7, 600; Provisional) and one accessor used by grouping, request_builder and the DAY_TOO_LONG rule (no duplicated numbers).
2. Implement grouping.py (pure): farthest-point seeding of one seed per day from must-visit places then shortlist; remaining places in descending score go to the day with room (< pace max items) whose centroid is nearest (haversine); ties break on place_id.
3. Pass the result as day_hints in GenerationRequest gr-1 and cap items per day at the pace maximum in request_builder.
4. Ensure the pace selector in PreferenceForm (already built in IMP-212) posts pace via API-14 and that a pace change after generation sets trips.plan_stale (reuse IMP-510 rule if merged; otherwise leave to IMP-510).
5. Add determinism tests (same input twice -> identical groups), two-distant-cluster fixture, and a cap test per preset.
6. Record average daily travel minutes of grouped plans over the SAMPLE fixture trips in the evaluation metrics output (FR-030 AC2) via app/evaluation/metrics.py.

**Interfaces**

- API: API-14, API-22 · Tables: trip_preferences · Modules: MOD-B06, MOD-F02, MOD-B15 · Components: PreferenceForm · Other: gr-1 day_hints, constant PACE_PRESETS in app/generation/presets.py (IMD-29)

**Acceptance criteria**

- FR-029 AC1-AC2 and FR-030 AC1-AC2 hold (TC-129 to TC-132).
- With a relaxed pace, no generated MOCK day exceeds 3 items or 300 active minutes.
- Two runs with the same input produce byte-identical day_hints.
- The evaluation run output contains avg_daily_travel_min for the grouped plans.

**Tests**

- apps/api/tests/unit/generation/test_pace.py — TC-129, TC-130 — `make test-unit ARGS='-k pace'`
- apps/api/tests/unit/generation/test_grouping.py — TC-131, TC-132 — `make test-unit ARGS='-k grouping'`

**Completion evidence**

- PR with make check green; Unit test output; make eval PROVIDER=MOCK output showing avg_daily_travel_min

### IMP-504 Add a user-selected place and reject stale edits

**Task:** Sprint 5 (week 5) · CODE · 5 points · lead Het with Malhar · release MVP

**Objective:** A traveller can add a chosen place to a day at a feasible time with the day revalidated, and any edit based on an old plan_revision is refused with 409 STALE_PLAN without changing data.

**Owners and parts**

- Het (lead) — Add-place edit and stale-edit rejection (3 points)
- Malhar — PlacePicker (uses the place search API) (2 points)
- One branch and pull request per part (`feat/IMP-504-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-071, US-074; FR-062, FR-069; NFR-003, NFR-008

**Dependencies:** Prerequisites: IMP-407 · Downstream: IMP-599

**Files**

- apps/api/app/itinerary/edits.py (modify); apps/api/app/itinerary/router.py (modify); apps/api/app/itinerary/schemas.py (modify); apps/web/components/itinerary/PlacePicker.tsx (create); apps/web/app/(app)/trips/[tripId]/itinerary/page.tsx (modify); apps/web/lib/api/client.ts (modify); apps/api/tests/api/test_edits.py (modify); apps/web/tests/unit/itinerary/PlacePicker.test.tsx (create)

**Implementation**

1. Implement the add operation for API-25 (POST /api/v1/trips/{trip_id}/itinerary/items, body place_id, day_number, optional start_time, plan_revision) in edits.py through the IMP-407 edit transaction: insert after the last item at the earliest feasible time (previous end + travel + buffer) when start_time is absent; origin user.
2. Reject with 422 INVALID_EDIT for day_number outside 1..num_days or an unknown/inactive place; a duplicate place on the same day is allowed but produces no silent merge.
3. Keep the addition when it creates findings (e.g. CLOSED_ON_DAY, DAY_TOO_LONG); return EditResultOut with plan_revision, changed_days, totals, findings.
4. Verify plan_revision on every edit route (API-25 to API-29) inside the locked trip transaction: mismatch -> 409 STALE_PLAN, nothing written; an active generation -> 409 GENERATION_IN_PROGRESS (IMD-23) (check at the top of the shared edit transaction so all edits inherit it).
5. Build PlacePicker reusing the explore search (API-16) inside a dialog; on success replace the itinerary query data with the response; on 409 STALE_PLAN refetch API-24 and show the "This plan changed since you opened it" Toast with a reload action.
6. Offer an Undo action in the Toast that calls API-27 for the new item (traveller can cancel the addition, FR-062 AC2).

**Interfaces**

- API: API-25, API-26, API-27, API-16, API-24 · Tables: itinerary_items, itinerary_warnings, trips · Modules: MOD-B08, MOD-F04 · Components: PlacePicker, DayColumn, Toast, WarningsPanel · Other: error codes STALE_PLAN, INVALID_EDIT

**Acceptance criteria**

- FR-062 AC1-AC2 hold (TC-202, TC-203); FR-069 AC1 holds (TC-217).
- Two clients editing from the same revision: the second gets 409 STALE_PLAN and the database rows are byte-identical before and after (TC-217).
- Adding a place to day 0 or day num_days+1 returns 422 INVALID_EDIT.
- The page never computes times or totals itself: after the edit it renders the server response only.

**Tests**

- apps/api/tests/api/test_edits.py — TC-202, TC-203, TC-217 — `make test-api ARGS='-k "add_place or stale"'`
- apps/web/tests/unit/itinerary/PlacePicker.test.tsx — new cases — `make test-web ARGS='PlacePicker'`

**Completion evidence**

- PR with make check green; API test log for the two-tab conflict; Screenshot of the stale-plan message with reload

### IMP-505 Replace an activity with a ranked alternative

**Task:** Sprint 5 (week 5) · CODE · 5 points · lead Het with Krrish · release MVP-S · Cut-list item 6 (flag alternatives): when disabled the traveller still removes an activity (API-27) and adds another place (API-25).

**Objective:** For any unlocked item the traveller sees up to three ranked alternatives with time and cost differences and can apply one, after which the day is recalculated and revalidated.

**Amended by A1 (2 November 2026):** replacing an item's place clears its `source_chunk_ids` (Amendment A1 §6.10).

**Owners and parts**

- Het (lead) — Replace edit with ranked alternatives (3 points)
- Krrish — AlternativesDialog (2 points)
- One branch and pull request per part (`feat/IMP-505-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-075; FR-065; NFR-003

**Dependencies:** Prerequisites: IMP-407, IMP-304 · Downstream: IMP-599, IMP-712

**Files**

- apps/api/app/itinerary/edits.py (modify); apps/api/app/itinerary/router.py (modify); apps/api/app/generation/ranking.py (modify); apps/web/components/itinerary/AlternativesDialog.tsx (create); apps/api/tests/api/test_edits.py (modify); apps/web/tests/unit/itinerary/AlternativesDialog.test.tsx (create)

**Implementation**

1. Implement API-28 GET /api/v1/itinerary/items/{item_id}/alternatives: candidates = active places of the trip destination, same slot_type category family, not already in the plan, passing the hard filters of IMP-304; score with the existing ranking function (no copy of the formula); return at most 3 with cost_delta (money strings) and duration_delta_min computed by the budget engine and routing estimate.
2. Implement API-29 POST /api/v1/itinerary/items/{item_id}/replace (body place_id, plan_revision) through the edit transaction: keep start_time, set duration to the new place typical_duration_min, recompute and revalidate, return EditResultOut.
3. Locked items: API-28 returns an empty list with reason locked; API-29 returns 422 INVALID_EDIT.
4. Build AlternativesDialog: list with SourceBadge on prices, deltas, Apply button; empty result shows "No alternative fits this slot" (FR-065 AC3).
5. Guard both routes and the dialog with the IMD-11 flag 'alternatives': disabled -> routes 404 NOT_FOUND, Replace action hidden.

**Interfaces**

- API: API-28, API-29 · Tables: itinerary_items, places · Modules: MOD-B08, MOD-B06, MOD-B09, MOD-F04 · Components: AlternativesDialog, ItineraryItemCard, SourceBadge · Env: FEATURES_DISABLED

**Acceptance criteria**

- FR-065 AC1-AC3 hold (TC-208 to TC-210).
- Alternatives are ordered by the same ranking score used by generation (unit check on equal inputs).
- With FEATURES_DISABLED containing 'alternatives' both routes return 404 and the floor journey still passes: remove an activity and add another place (TC-372).
- Stale plan_revision on API-29 returns 409 STALE_PLAN.

**Tests**

- apps/api/tests/api/test_edits.py — TC-208, TC-209, TC-210 — `make test-api ARGS='-k alternative'`
- apps/web/tests/unit/itinerary/AlternativesDialog.test.tsx — new cases — `make test-web ARGS='AlternativesDialog'`

**Completion evidence**

- PR with make check green; Screenshot of the dialog with three alternatives and deltas

### IMP-506 Lock and unlock items

**Task:** Sprint 5 (week 5) · CODE · 3 points · lead Het with Krrish · release MVP-S · Cut-list item 8 (flag locks): when disabled no item can be locked, but must-visit places stay protected by the validator.

**Objective:** Travellers can lock and unlock itinerary items; locked items never move under repair or regeneration, and must-visit items are locked when created.

**Owners and parts**

- Het (lead) — Lock/unlock and locks respected by repair (2 points)
- Krrish — Lock toggle on item cards (1 points)
- One branch and pull request per part (`feat/IMP-506-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-076; FR-066; NFR-008

**Dependencies:** Prerequisites: IMP-407 · Downstream: IMP-599, IMP-607, IMP-612

**Files**

- apps/api/app/itinerary/edits.py (modify); apps/api/app/itinerary/service.py (modify); apps/api/app/generation/request_builder.py (modify); apps/api/app/validation/repair.py (modify); apps/web/components/itinerary/ItineraryItemCard.tsx (modify); apps/api/tests/api/test_edits.py (modify); apps/api/tests/unit/validation/test_repair.py (modify)

**Implementation**

1. Support is_locked in API-26 PATCH (body locked: bool, plan_revision) through the edit transaction; a move or retime of a locked item without unlocking returns 422 INVALID_EDIT.
2. When the save step writes items for a place in trip_places with relation must_visit, set is_locked = true.
3. Pass locked items (place_id, day_number, start_time, duration_min) to request_builder as fixed constraints for day and full regeneration (used by IMP-607).
4. Make repair.py skip locked items in every operation (already required in IMP-502; add explicit tests).
5. Add the lock toggle to ItineraryItemCard as a button with aria-pressed and a visible lock icon + text 'Locked'.
6. Guard with the IMD-11 flag 'locks': disabled -> the toggle is hidden and PATCH with locked returns 404 NOT_FOUND for that field; must-visit protection by the validator (MUST_VISIT_MISSING) still applies.

**Interfaces**

- API: API-26 · Tables: itinerary_items, trip_places · Modules: MOD-B08, MOD-B06, MOD-B07, MOD-F04 · Components: ItineraryItemCard · Env: FEATURES_DISABLED

**Acceptance criteria**

- FR-066 AC1-AC2 hold (TC-211, TC-212).
- Repair and regeneration leave locked items at the same day and time (TC-313).
- The lock toggle is keyboard operable and announces its state (aria-pressed).
- With 'locks' disabled the floor journey passes (TC-372) and must-visit places stay protected by MUST_VISIT_MISSING.

**Tests**

- apps/api/tests/api/test_edits.py — TC-211, TC-212 — `make test-api ARGS='-k lock'`
- apps/api/tests/unit/validation/test_repair.py — TC-313 — `make test-unit ARGS='-k locked'`

**Completion evidence**

- PR with make check green; Test output for lock cases

### IMP-507 Daily and category cost breakdown; estimate labels on every screen

**Task:** Sprint 5 (week 5) · CODE · 5 points · lead Manal with Manasvi · release MVP

**Objective:** The costs page shows a day and category breakdown whose rows add up to the planning total, and every price, opening time and travel time on every MVP screen carries its label.

**Owners and parts**

- Manal (lead) — Daily and category cost breakdown API (3 points)
- Manasvi — Costs page and CostBreakdown (2 points)
- One branch and pull request per part (`feat/IMP-507-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-082, US-125; FR-073, FR-117; NFR-030, NFR-040

**Dependencies:** Prerequisites: IMP-411 · Downstream: IMP-599, IMP-608, IMP-609

**Files**

- apps/api/app/budget/engine.py (modify); apps/api/app/budget/router.py (modify); apps/api/app/budget/schemas.py (modify); apps/web/app/(app)/trips/[tripId]/costs/page.tsx (modify); apps/web/components/costs/CostBreakdown.tsx (create); apps/web/components/labels/SourceBadge.tsx (modify); apps/api/tests/unit/budget/test_breakdown.py (create); apps/web/tests/unit/costs/CostBreakdown.test.tsx (create); docs/test-reports/label-review.md (create)

**Implementation**

1. Add BF-12 to engine.py: by_day[d] = items on day d + transport allowance t + stay s for d <= N; by_category over activities, food, other, transport, accommodation; the contingency buffer is its own row in both tables so each adds up to the planning total P exactly (integer minor units inside the engine, money strings at the API edge per IMD-05).
2. Extend CostSummaryOut of API-33 with by_day[] and by_category[] (each with low, high, label) without breaking existing fields.
3. Build CostBreakdown as two accessible tables (optional simple bar chart is not required); render values from the API only; refetch on itinerary edits via the shared query invalidation.
4. Audit every MVP screen (explore, place detail, itinerary, costs, summary) and render SourceBadge for price_label/hours_label and the travel label for travel_source (routing_api -> "Estimated travel time from a routing service", fallback_estimate -> "Estimated travel time (distance based)").
5. Record the screen-by-screen label checklist in docs/test-reports/label-review.md and fix gaps.

**Interfaces**

- API: API-33 · Tables: itinerary_items, budget_settings, trips · Modules: MOD-B09, MOD-F06, MOD-F07 · Components: CostBreakdown, CostSummary, SourceBadge · Other: BF-12, label table §7

**Acceptance criteria**

- FR-073 AC1-AC2 hold (TC-225, TC-226); category and day sums equal the trip total for all fixtures (TC-300).
- FR-117 AC1 holds (TC-282); the label review lists every screen with no missing label (TC-385).
- After an edit the breakdown shows the new values without a manual reload.

**Tests**

- apps/api/tests/unit/budget/test_breakdown.py — TC-225, TC-300 — `make test-unit ARGS='-k breakdown'`
- apps/api/tests/api/test_costs.py — TC-226 — `make test-api ARGS='-k costs'`
- apps/web/tests/unit/costs/CostBreakdown.test.tsx — TC-282 — `make test-web ARGS='CostBreakdown'`

**Completion evidence**

- PR with make check green; docs/test-reports/label-review.md committed; Screenshot of the costs page

### IMP-508 Map with numbered markers and list fallback

**Task:** Sprint 5 (week 5) · CODE · 5 points · lead Manasvi · release MVP-S

**Objective:** The itinerary page shows the selected day on a MapLibre map with numbered markers in visit order linked to the list, and falls back to a list view when tiles fail.

**Owners and parts:** Manasvi — whole task (5 points); branch `feat/IMP-508-<short>`

**Traces to:** Stories US-089; FR-080; NFR-010, NFR-026

**Dependencies:** Prerequisites: IMP-309 · Downstream: IMP-599, IMP-711

**Files**

- apps/web/components/map/MapPanel.tsx (create); apps/web/components/map/MapListFallback.tsx (create); apps/web/app/(app)/trips/[tripId]/itinerary/page.tsx (modify); apps/web/tests/unit/map/MapPanel.test.tsx (create); docs/decisions/map-tiles.md (create)

**Implementation**

1. Add maplibre-gl and load MapPanel client-side only (dynamic import, no SSR) with the OpenFreeMap style URL from a constant in lib/ (no key).
2. Render one numbered marker per item of the selected day in position order, using lat/lon from the itinerary response (no geocoding); draw straight segments between consecutive stops (no routing geometry in the MVP).
3. Link markers and DayColumn: selecting a marker scrolls to and focuses the item card; selecting a card highlights its marker.
4. On a style or tile load error, or when WebGL is unavailable, replace the map with MapListFallback (ordered list with the same numbers) and show 'Map unavailable; list view shown'.
5. Show the required attribution on the map; record the tile provider terms and attribution text, checked date and status (Unverified until checked) in docs/decisions/map-tiles.md.
6. Desktop: map in the right pane; phone: map behind a "Map" tab.

**Interfaces**

- API: API-24 · Modules: MOD-F05, MOD-F04 · Components: MapPanel, DayColumn, ItineraryItemCard · Other: OpenFreeMap tiles (§9)

**Acceptance criteria**

- FR-080 AC1-AC3 hold (TC-238 to TC-240).
- With the tile request blocked (Playwright route abort or mocked error in the unit test) the list view appears and the itinerary remains usable.
- Markers carry accessible names "Stop N: <place name>".

**Tests**

- apps/web/tests/unit/map/MapPanel.test.tsx — TC-238, TC-239, TC-240 — `make test-web ARGS='MapPanel'`
- apps/web/e2e/itinerary-edit.spec.ts — TC-240 — `make e2e ARGS='itinerary-edit'`

**Completion evidence**

- PR with make check green; Screenshots: map with markers (desktop) and list fallback; docs/decisions/map-tiles.md

### IMP-509 Browse places with source labels

**Task:** Sprint 5 (week 5) · CODE · 3 points · lead Jeel · release MVP-S

**Objective:** The explore page lists the active places of the trip destination in pages, each with its source and verification status, and states that the data is sample/estimated where it is.

**Owners and parts:** Jeel — whole task (3 points); branch `feat/IMP-509-<short>`

**Traces to:** Stories US-029; FR-016; NFR-002, NFR-040

**Dependencies:** Prerequisites: IMP-205, IMP-206 · Downstream: IMP-515, IMP-599, IMP-604, IMP-605

**Files**

- apps/api/app/places/router.py (modify); apps/api/app/places/repository.py (modify); apps/api/app/places/schemas.py (modify); apps/web/app/(app)/trips/[tripId]/explore/page.tsx (create); apps/web/components/places/PlaceCard.tsx (create); apps/api/tests/api/test_places.py (modify); apps/web/tests/unit/places/PlaceCard.test.tsx (create)

**Implementation**

1. Implement API-16 GET /api/v1/places with destination_id (required), limit (default 20, max 50), offset; return Page{items: PlaceSummaryOut[], total, limit, offset}; only is_active places of active destinations; order by name then id.
2. Include source name, verification_status and price_label in PlaceSummaryOut; never return places that failed the quality gate.
3. Build the explore page with PlaceCard grid, pagination controls, LoadingSkeleton/EmptyState/ErrorState, and a banner when the destination dataset is the SAMPLE fixture or uses estimates ("Sample data; prices and hours are estimates unless marked Curated").
4. Use SourceBadge for price and verification labels.
5. Add API tests for paging, destination scoping and inactive rows, and a component test for the badge and banner.

**Interfaces**

- API: API-16, API-06 · Tables: places, data_sources, destinations · Modules: MOD-B04, MOD-F03 · Components: PlaceCard, SourceBadge, EmptyState, LoadingSkeleton

**Acceptance criteria**

- FR-016 AC1-AC3 hold (TC-092 to TC-094).
- limit=51 returns 422 VALIDATION_ERROR; places of another destination never appear.
- Request without a token returns 401 UNAUTHENTICATED.

**Tests**

- apps/api/tests/api/test_places.py — TC-092, TC-093, TC-094 — `make test-api ARGS='-k places_list'`
- apps/web/tests/unit/places/PlaceCard.test.tsx — new cases — `make test-web ARGS='PlaceCard'`

**Completion evidence**

- PR with make check green; Screenshot of the explore page with the sample-data banner

### IMP-510 Edit trip settings and flag a stale plan

**Task:** Sprint 5 (week 5) · CODE · 2 points · lead Manal with Krrish · release MVP-S

**Objective:** A traveller can edit trip settings; changes that affect the plan (dates, travellers, budget, destination, pace) set plan_stale and show an out-of-date banner, title-only changes do not.

**Owners and parts**

- Manal (lead) — Edit trip settings and stale-plan flag (1 points)
- Krrish — Trip edit page and StalePlanBanner (1 points)
- One branch and pull request per part (`feat/IMP-510-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-021; FR-011; NFR-008

**Dependencies:** Prerequisites: IMP-203, IMP-212 · Downstream: IMP-599

**Files**

- apps/api/app/trips/service.py (modify); apps/api/app/trips/router.py (modify); apps/api/app/trips/domain.py (modify); apps/api/app/generation/service.py (modify); apps/web/app/(app)/trips/[tripId]/edit/page.tsx (create); apps/web/components/itinerary/StalePlanBanner.tsx (create); apps/api/tests/api/test_trips.py (modify)

**Implementation**

1. Implement API-11 PATCH /api/v1/trips/{trip_id} for title, start_date, end_date, travellers, budget (and archived flag later in IMP-602) with the same validation as API-07.
2. In domain.py define PLAN_AFFECTING_FIELDS = dates, adults, children, group_needs, budget, destination; set trips.plan_stale = true when any of them changes and an itinerary exists; also when API-14 changes pace, interests or must-visit places.
3. Clear plan_stale in the save step of a completed full generation (generation/service.py).
4. Reuse TripWizard in edit mode at /trips/[tripId]/edit (prefilled from API-10 and API-15).
5. Show StalePlanBanner on the itinerary page when plan_stale is true with a "Regenerate" action (links to generate page; whole-plan regeneration API-31 when IMP-607 is merged).
6. Changing dates so that items fall outside the trip leaves the items and lets the validator raise OUTSIDE_TRIP_DATES.

**Interfaces**

- API: API-11, API-10, API-14, API-15 · Tables: trips, trip_preferences · Modules: MOD-B03, MOD-F02, MOD-F04 · Components: TripWizard, StalePlanBanner

**Acceptance criteria**

- FR-011 AC1-AC2 hold (TC-080, TC-081).
- plan_stale is cleared after a completed regeneration.
- PATCH of another user's trip returns 404 NOT_FOUND (covered by the authz suite).

**Tests**

- apps/api/tests/api/test_trips.py — TC-080, TC-081 — `make test-api ARGS='-k stale'`
- apps/api/tests/authz/test_ownership.py — TC-345 — `make test-authz`

**Completion evidence**

- PR with make check green; Screenshot of the stale-plan banner

### IMP-511 Rate limits and daily generation caps

**Task:** Sprint 5 (week 5) · CODE · 5 points · lead Kirtan · release MVP

**Objective:** Expensive endpoints are rate limited per user and per address with 429 RATE_LIMITED, and generation is refused with 429 AI_QUOTA_REACHED before any provider call when the per-user or global daily cap is reached.

**Owners and parts:** Kirtan — whole task (5 points); branch `feat/IMP-511-<short>`

**Traces to:** Stories US-009, US-040; FR-046, FR-126; NFR-017, NFR-037, NFR-039

**Dependencies:** Prerequisites: IMP-202, IMP-201 · Downstream: IMP-599, IMP-702

**Files**

- apps/api/app/core/rate_limit.py (modify); apps/api/app/generation/service.py (modify); apps/api/app/ai/limits.py (modify); apps/api/app/ai/providers/gemini.py (modify); apps/api/tests/api/test_generations.py (modify); apps/api/tests/unit/core/test_rate_limit.py (create); docs/guides/usage-queries.md (create); docs/decisions/provider-spend-limit.md (create); apps/api/app/generation/jobs.py (modify)

**Implementation**

1. Implement an in-memory sliding-window limiter in rate_limit.py keyed by user id and client address, limit RATE_LIMIT_PER_MIN (60); apply as a dependency to API-16, API-22, API-25 to API-31; on excess return 429 RATE_LIMITED with Retry-After header and retry_after_s (§6 envelope).
2. In generation/service.py, before creating the ai_generations row, count today's (UTC) rows for the user and globally excluding model_id rule_based_planner_v1 (reference operation 1, §5); if >= AI_DAILY_GENERATIONS_PER_USER or AI_DAILY_GENERATIONS_GLOBAL return 429 AI_QUOTA_REACHED with the next UTC midnight as reset time; never call the provider.
3. Add the daily purge of ai_generations rows whose retention_until has passed (90 days, OD-10) to the scheduler in app/generation/jobs.py; linked generation ids become null (IMD-31).
4. When the global cap is reached, the error details tell the client that mode rule_based is available; the generate page offers a "Build a rule-based plan" button that calls API-22 with mode rule_based (not counted against the cap).
5. Apply AI_MAX_INPUT_TOKENS / AI_MAX_OUTPUT_TOKENS in limits.py (request builder trims the shortlist; adapter sets max output tokens) when set.
6. Document the daily-count query in docs/guides/usage-queries.md and the provider-side spending/quota limit chosen at setup (owner Kirtan, status Awaiting validation until set) in docs/decisions/provider-spend-limit.md.

**Interfaces**

- API: API-22, API-16, API-25, API-26, API-27, API-28, API-29, API-30, API-31 · Tables: ai_generations · Modules: MOD-B01, MOD-B05, MOD-B06 · Env: RATE_LIMIT_PER_MIN, AI_DAILY_GENERATIONS_PER_USER, AI_DAILY_GENERATIONS_GLOBAL, AI_MAX_INPUT_TOKENS, AI_MAX_OUTPUT_TOKENS · Other: error codes RATE_LIMITED, AI_QUOTA_REACHED

**Acceptance criteria**

- FR-126 AC1 holds (TC-294, TC-353); a limited generation request makes no provider call and leaves the usage count unchanged.
- FR-046 AC1-AC3 hold (TC-171 to TC-173, TC-310, TC-311).
- The cap check runs before the ai_generations insert and before any provider call (asserted with the MOCK call log).
- The purge job deletes generation records past retention_until and leaves plans and versions intact (IMD-31).

**Tests**

- apps/api/tests/unit/core/test_rate_limit.py — TC-294 — `make test-unit ARGS='-k rate_limit'`
- apps/api/tests/api/test_generations.py — TC-171, TC-172, TC-173, TC-310, TC-311, TC-353 — `make test-api ARGS='-k "quota or rate_limit"'`
- apps/api/tests/api/test_generations.py — new cases — `make test-api ARGS='-k purge'`

**Completion evidence**

- PR with make check green; API test log of 429 responses; docs/guides/usage-queries.md and docs/decisions/provider-spend-limit.md

### IMP-512 Provider contract test suite for all adapters

**Task:** Sprint 5 (week 5) · CODE · 3 points · lead Junaid · release MVP

**Objective:** One shared contract suite runs against every adapter (MOCK always, GEMINI with recorded responses, live only by marker) and the import rule keeps vendor SDKs inside adapters.

**Owners and parts:** Junaid — whole task (3 points); branch `feat/IMP-512-<short>`

**Traces to:** Stories US-042; FR-040; NFR-031, NFR-043

**Dependencies:** Prerequisites: IMP-401, IMP-207 · Downstream: IMP-599

**Files**

- apps/api/tests/contract/test_provider_contract.py (modify); apps/api/tests/contract/conftest.py (create); apps/api/tests/fixtures/provider_recordings/ (modify); apps/api/.importlinter (modify); docs/guides/adding-a-provider.md (create)

**Implementation**

1. Write one parametrised suite (fixture adapter in [mock, gemini_recorded]) covering: the four operations exist with the agreed signatures; generate_itinerary returns a schema-valid io-1 ProviderResult with usage and latency; each failure scenario maps to the shared error types (timeout, rate limited, quota, unavailable, invalid output, config); health_check and get_model_metadata shapes.
2. Drive the Gemini adapter from recorded responses (no key, no network: respx or the SDK transport stub); a test with marker live re-runs the generate case against the real API and is skipped without GEMINI_API_KEY.
3. Add a test that the generation service imports no concrete adapter (only factory/base).
4. Confirm the import-linter contract (google-genai only in app/ai/providers/gemini.py) is in make imports and CI.
5. Document in docs/guides/adding-a-provider.md how a future adapter (Stage 2 FINETUNED_MODEL) joins the suite by adding one fixture id.

**Interfaces**

- Modules: MOD-B05, MOD-P01 · Other: ModelProvider interface §8, provider error types, pytest marker live

**Acceptance criteria**

- FR-040 AC1-AC3 hold (TC-156 to TC-158).
- TC-001, TC-002, TC-003, TC-005 and TC-008 pass for MOCK and recorded GEMINI.
- make test-contract runs with no network and no key; make live-smoke is the only path that calls Gemini.

**Tests**

- apps/api/tests/contract/test_provider_contract.py — TC-001, TC-003, TC-005, TC-008, TC-156, TC-157, TC-158 — `make test-contract`
- apps/api/.importlinter — TC-002 — `make imports`

**Completion evidence**

- PR with make check green; make test-contract output with both adapter ids; docs/guides/adding-a-provider.md

### IMP-513 Keyboard and assistive-technology support

**Task:** Sprint 5 (week 5) · CODE · 3 points · lead Krrish · release MVP

**Objective:** The core journey (sign in, create trip, generate, review and edit itinerary, costs) is fully keyboard operable and screen-reader friendly, with automated axe checks in CI.

**Owners and parts:** Krrish — whole task (3 points); branch `feat/IMP-513-<short>`

**Traces to:** Stories US-123; FR-115; NFR-025

**Dependencies:** Prerequisites: IMP-412 · Downstream: IMP-599, IMP-703

**Files**

- apps/web/components/shell/AppShell.tsx (modify); apps/web/components/itinerary/DayColumn.tsx (modify); apps/web/components/itinerary/MoveControls.tsx (modify); apps/web/components/generation/GenerationProgress.tsx (modify); apps/web/components/itinerary/WarningsPanel.tsx (modify); apps/web/e2e/journey.spec.ts (modify); docs/guides/keyboard-map.md (create)

**Implementation**

1. Write the keyboard map (focus order, skip link to main content, shortcuts if any) for the core pages in docs/guides/keyboard-map.md and implement the skip link in AppShell.
2. Ensure every interactive element is a native control or has role, name and keyboard handlers; MoveControls give up/down/day buttons as the alternative to dragging (dnd-kit keyboard sensor enabled).
3. Use semantic structure on the itinerary: each day a section with heading "Day N, <date>", items in an ordered list with time first; WarningsPanel grouped by severity with headings.
4. Announce asynchronous results through polite live regions: generation status changes, edit results, stale-plan message.
5. Add @axe-core/playwright scans to the journey spec on each core page; violations of serious or critical impact fail the test.

**Interfaces**

- Modules: MOD-F07, MOD-F04 · Components: AppShell, DayColumn, MoveControls, GenerationProgress, WarningsPanel

**Acceptance criteria**

- FR-115 AC1-AC2 hold (TC-279, TC-280).
- The keyboard-only journey passes (TC-374) and the automated scan reports no serious or critical violations (TC-383).
- The manual screen-reader pass (TC-382) is scheduled for IMP-703 and is not claimed here.

**Tests**

- apps/web/e2e/journey.spec.ts — TC-279, TC-374, TC-383 — `make e2e ARGS='journey'`
- apps/web/tests/unit/itinerary/DayColumn.test.tsx — TC-280 — `make test-web ARGS='DayColumn'`

**Completion evidence**

- PR with make check green; Playwright report with the axe results attached; docs/guides/keyboard-map.md

### IMP-514 Evaluation run records and first Gemini baseline

**Task:** Sprint 5 (week 5) · DATA · 3 points · lead Manya with Nidhi · release MVP

**Objective:** Every evaluation run writes a complete run record, and the first Gemini baseline over dataset v1 (15 trips) is run and committed with a note that claims nothing beyond the dataset.

**Owners and parts**

- Manya (lead) — Evaluation run records (2 points)
- Nidhi — First Gemini baseline report (1 points)
- One branch and pull request per part (`feat/IMP-514-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-129, US-130; FR-120; NFR-041, NFR-042, NFR-046

**Dependencies:** Prerequisites: IMP-413, IMP-301 · Downstream: IMP-599, IMP-705

**Files**

- apps/api/app/evaluation/manifest.py (modify); apps/api/app/evaluation/run.py (modify); apps/api/tests/unit/evaluation/test_run_record.py (create); eval/results/ (create); eval/reports/baseline-1.md (create)

**Implementation**

1. Define the run-record schema in manifest.py: run_id, started_at, git_commit, dataset_id, dataset_version, provider, model_id, prompt_template_id, prompt_version, input/output schema versions, settings, metric values, case count, failures; writing fails if any required field is missing.
2. Write the record to eval/results/<run_id>/run.json plus per-case outputs; never write API keys or prompt bodies.
3. Run make eval PROVIDER=MOCK DATASET=trips/v1 in CI as a smoke check of the harness.
4. Nidhi runs make eval PROVIDER=GEMINI DATASET=trips/v1 by hand with the staging key within the daily caps, commits the record and writes eval/reports/baseline-1.md: dataset size (15), metric values, observed prompt problems, explicit statement that no quality claim beyond these 15 trips is made.
5. If Gemini is unavailable, record the attempt and the error in the report; the task is then Done only with the MOCK record and a dated blocker in docs/progress/sprint-5.md.

**Interfaces**

- Modules: MOD-B15 · Env: AI_PROVIDER, GEMINI_API_KEY, GEMINI_MODEL_ID · Other: eval/datasets/trips/v1

**Acceptance criteria**

- FR-120 AC1 holds (TC-287); an incomplete record cannot be saved (TC-390).
- eval/results contains a GEMINI run record for dataset v1 (TC-391, manual) or a documented blocker.
- The baseline note states the dataset size and makes no claim beyond it (PR-12).

**Tests**

- apps/api/tests/unit/evaluation/test_run_record.py — TC-287, TC-390 — `make test-unit ARGS='-k run_record'`
- eval/reports/baseline-1.md — TC-391 — `make eval PROVIDER=GEMINI DATASET=trips/v1`

**Completion evidence**

- PR with make check green; Committed eval/results/<run_id>/run.json for GEMINI; eval/reports/baseline-1.md

### IMP-515 Explain the ranking: "Why this place?" panel

**Task:** Sprint 5 (week 5) · CODE · 4 points · lead Jeel with Krrish · release EXT · Extension; switch ranking_explain (cut 9 of 9, last). When disabled place cards show no "Why this place?" link; ranking and generation are unchanged.

**Objective:** For any place shown for a trip, the traveller can open "Why this place?" and read the ranking components (interest, price, distance, pace and signal, the last unused in the MVP, with their weights; plus whether the place is a must-visit or removed by a hard filter; WhyOut, §6.5.1) in plain words, computed exactly by the ranking domain function under the trip's current preferences.

**Owners and parts**

- Jeel (lead) — Ranking components API (API-63) from the ranking domain function (2 points)
- Krrish — "Why this place?" panel (2 points)
- One branch and pull request per part (`feat/IMP-515-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-154; FR-127; NFR-003

**Dependencies:** Prerequisites: IMP-304, IMP-509 · Downstream: IMP-599

**Files**

- apps/api/app/generation/ranking.py (modify); apps/api/app/generation/router.py (modify); apps/api/app/generation/schemas.py (modify); apps/web/components/places/WhyThisPlacePanel.tsx (create); apps/web/components/places/PlaceCard.tsx (modify); apps/api/tests/unit/generation/test_ranking_explain.py (create); apps/api/tests/api/test_why_place.py (create); apps/web/tests/unit/places/WhyThisPlacePanel.test.tsx (create); contracts/openapi.v1.json (modify)

**Implementation**

1. Contract first: on day 1 of the sprint the API part declares this card's endpoints with their final shapes (§6) and regenerates contracts/openapi.v1.json with make openapi; handlers return 501 NOT_IMPLEMENTED until built (IMD-37: allowed for extension routes until SG-7), so the screen part starts against the regenerated web client (Team Contribution Plan v2).
2. Add explain_components(place, preferences, mapping) to app/generation/ranking.py (pure): reuse the exact weights and component functions of the ranking score (no second formula) and return each component with its weight, value and contribution, plus must_visit=true when the place is a must-visit of the trip.
3. Map components to plain-language phrases with fixed thresholds (e.g. interest match >= 0.7 "matches your interests: museums, food"); return phrases plus the numeric components in WhyPlaceOut (§6), with based_on="current preferences" and mapping_version pm-1.
4. Implement API-63 GET /api/v1/trips/{trip_id}/places/{place_id}/why in app/generation/router.py: owned trip else 404; place must be active and in the trip destination else 404; nothing is stored.
5. Build WhyThisPlacePanel (places area): opened from PlaceCard and from itinerary item cards; lists phrases, a small bar per component, and "Always kept: must-visit" when applicable; loading, error and empty states from §7.
6. Add the switch: Guard with the extension switch 'ranking_explain' (IMD-11, EXT): when FEATURES_DISABLED / NEXT_PUBLIC_FEATURES_DISABLED contains 'ranking_explain' the routes return 404 NOT_FOUND and the UI entry point is hidden (TC-432).
7. Write unit tests proving explain_components sums to the ranking score used by retrieval for the same inputs, plus API and component tests.

**Interfaces**

- API: API-63 · Tables: places, trip_preferences, trip_places · Modules: MOD-B06, MOD-F03, MOD-F04 · Components: WhyThisPlacePanel, PlaceCard, ItineraryItemCard · Env: FEATURES_DISABLED, NEXT_PUBLIC_FEATURES_DISABLED · Other: mapping_version pm-1

**Acceptance criteria**

- FR-127 AC1-AC3 hold (TC-399 to TC-401).
- The contributions returned by API-63 add up to the ranking score of the same place and preferences used by candidate ranking (unit equality check).
- Another user's trip or a place outside the destination returns 404 (TC-431).
- With the switch ranking_explain disabled API-63 returns 404 and the link is hidden (TC-432).

**Tests**

- apps/api/tests/unit/generation/test_ranking_explain.py — TC-399, TC-400 — `make test-unit ARGS='-k ranking_explain'`
- apps/api/tests/api/test_why_place.py — TC-401, TC-431, TC-432 — `make test-api ARGS='-k why_place'`
- apps/web/tests/unit/places/WhyThisPlacePanel.test.tsx — new cases — `make test-web ARGS='WhyThisPlacePanel'`

**Completion evidence**

- PR with make check green; Screenshot of the panel for one must-visit place and one ranked place

### IMP-599 Sprint 5 gate SG-5

**Task:** Sprint 5 (week 5) · VERIFY · 0 points · lead Kirtan · release MVP

**Objective:** Sprint 5 gate SG-5 is passed and recorded: validation, repair, editing, costs, map and limits work together on staging with MOCK and GEMINI.

**Owners and parts:** Kirtan — whole task (0 points); branch `feat/IMP-599-<short>`

**Traces to:** enabling work (no requirement)

**Dependencies:** Prerequisites: IMP-501, IMP-502, IMP-503, IMP-504, IMP-505, IMP-506, IMP-507, IMP-508, IMP-509, IMP-510, IMP-511, IMP-512, IMP-513, IMP-514, IMP-515 · Downstream: none

**Files**

- docs/progress/sprint-5.md (modify); docs/progress/gates.md (modify)

**Implementation**

1. Confirm every Sprint 5 task is done or explicitly carried over in docs/progress/sprint-5.md with evidence links.
2. Run make check and make e2e on main; record the CI run links.
3. Deploy main to staging; run make smoke URL=<staging api> and the staging journey: generate with GEMINI, add a place, replace an activity, lock an item, view costs breakdown and map.
4. Trigger a provider failure on staging (AI_PROVIDER=MOCK with MOCK_PROVIDER_SCENARIO=timeout on staging, IMD-33) and confirm the labelled fallback plus repair outcome recording.
5. Check the generation caps: a user at the cap gets 429 AI_QUOTA_REACHED without a provider call.
6. Record pass/fail per criterion, open defects with severity and owner, and the cut-list flags currently disabled in docs/progress/gates.md.
7. Check the extension IMP-515: API-63 and the "Why this place?" panel work on staging with ranking_explain enabled, or the switch is off and the decision is recorded.

**Interfaces**

- Other: SG-5 criteria §14

**Acceptance criteria**

- make check and make e2e are green on the gate commit.
- Staging journey with GEMINI works end to end with all Sprint 5 functions; outcome labels are shown.
- No open blocker-severity defect; known defects listed with owners.
- Gate decision and evidence recorded in docs/progress/gates.md.
- IMP-515 is done with TC-399 to TC-401 passing, or ranking_explain is switched off with a recorded decision.

**Tests**

- apps/web/e2e/journey.spec.ts — TC-369 — `make e2e`
- apps/api/tests/smoke/test_deployed.py — new cases — `make smoke URL=<staging-api-url>`

**Completion evidence**

- CI run links for make check and make e2e; Smoke output against staging; docs/progress/gates.md SG-5 entry

## Sprint 6 (week 6): MVP completion and feature freeze — gate SG-6

| Task | Title | Type | Lead | Parts (points) | Prerequisites | Points |
| --- | --- | --- | --- | --- | --- | --- |
| IMP-601 | Profile page and API | CODE | Het | Het 2 | IMP-109, IMP-214 | 2 |
| IMP-602 | Trip dashboard with rename, duplicate, archive and delete | CODE | Manal | Manal 6, Manasvi 2 | IMP-410 | 8 |
| IMP-603 | Curate and load demo destination 2 | DATA | Junaid | Junaid 2, Manya 2, Kirtan 1 | IMP-206 | 5 |
| IMP-604 | Search, filters and place detail with labelled facts | CODE | Malhar | Malhar 4, Manasvi 2, Jeel 1 | IMP-509, IMP-411 | 7 |
| IMP-605 | Saved places (wishlist) | CODE | Jeel | Jeel 3 | IMP-509 | 3 |
| IMP-606 | Food places and meal slots | CODE | Malhar | Malhar 3, Manya 2 | IMP-305, IMP-503 | 5 |
| IMP-607 | Regenerate one day around locks and the whole itinerary | CODE | Het | Het 4, Nidhi 4, Krrish 2 | IMP-506, IMP-305, IMP-502, IMP-610 | 10 |
| IMP-608 | Budget alerts and contingency buffer | CODE | Manal | Manal 2, Krrish 2 | IMP-507, IMP-501 | 4 |
| IMP-609 | Final trip summary and print view | CODE | Krrish | Krrish 2, Het 1 | IMP-309, IMP-507 | 3 |
| IMP-610 | Itinerary versions: save, list and restore | CODE | Jeel | Jeel 6, Malhar 2 | IMP-407 | 8 |
| IMP-611 | Usability session 1 and recorded findings | HUMAN | Junaid | Junaid 2, Krrish 1 | IMP-414 | 3 |
| IMP-612 | Optimise day order to cut travel time | CODE | Het | Het 3, Junaid 3, Manasvi 2 | IMP-407, IMP-307, IMP-506, IMP-606 | 8 |
| IMP-613 | Packing checklist with AI free-text refinement | CODE | Kirtan | Kirtan 5, Nidhi 2, Manya 2 | IMP-110, IMP-111, IMP-207, IMP-301 | 9 |
| IMP-699 | Sprint 6 gate SG-6: MVP feature-complete and feature freeze | VERIFY | Kirtan | Kirtan 0 | IMP-601, IMP-602, IMP-603, IMP-604, IMP-605, IMP-606, IMP-607, IMP-608, IMP-609, IMP-610, IMP-611, IMP-612, IMP-613 | 0 |


### IMP-601 Profile page and API

**Task:** Sprint 6 (week 6) · CODE · 2 points · lead Het · release MVP-S

**Objective:** A signed-in traveller can view and edit display name, home currency and default preferences, and new trips are prefilled from those defaults.

**Owners and parts:** Het — whole task (2 points); branch `feat/IMP-601-<short>`

**Traces to:** Stories US-014; FR-004; NFR-012, NFR-014

**Dependencies:** Prerequisites: IMP-109, IMP-214 · Downstream: IMP-699

**Files**

- apps/api/app/auth/router.py (modify); apps/api/app/auth/service.py (modify); apps/api/app/auth/repository.py (modify); apps/api/app/auth/schemas.py (modify); apps/web/app/(app)/profile/page.tsx (create); apps/web/components/profile/ProfileForm.tsx (create); apps/web/components/trips/TripWizard.tsx (modify); apps/api/tests/api/test_me.py (modify); apps/web/tests/unit/profile/ProfileForm.test.tsx (create)

**Implementation**

1. Extend API-03 (built in IMP-108) and API-04 PATCH /api/v1/me (privacy flag built in IMP-305) with display_name (1..60 characters per FR-004; DB allows 80), preferred_currency (ISO 4217 uppercase 3 letters), home_country (ISO 3166-1 alpha-2) and default preferences.
2. Store default preferences in profiles.default_preferences (jsonb object with the PreferencesIn keys except notes and must_visit_place_ids; IMD-16); API-04 accepts and returns display_name (1 to 60), preferred_currency, home_country and default_preferences.
3. Unknown fields -> 422 VALIDATION_ERROR; invalid currency -> 422 with details field preferred_currency.
4. Build the profile page with ProfileForm (react-hook-form + zod mirroring the server rules), success Toast, ErrorState.
5. Prefill TripWizard budget currency and preferences from API-03 when creating a new trip.

**Interfaces**

- API: API-03, API-04 · Tables: profiles · Modules: MOD-B02, MOD-F01 · Components: ProfileForm, TripWizard, Toast

**Acceptance criteria**

- FR-004 AC1-AC3 hold (TC-060 to TC-062).
- The profile id always equals the token user id; a body user_id is rejected as an unknown field.
- A new trip form is prefilled with the saved defaults.

**Tests**

- apps/api/tests/api/test_me.py — TC-060, TC-061, TC-062 — `make test-api ARGS='-k me'`
- apps/web/tests/unit/profile/ProfileForm.test.tsx — new cases — `make test-web ARGS='ProfileForm'`

**Completion evidence**

- PR with make check green; Screenshot of the profile page

### IMP-602 Trip dashboard with rename, duplicate, archive and delete

**Task:** Sprint 6 (week 6) · CODE · 8 points · lead Manal with Manasvi · release MVP-S · Cut-list item 2 (flag trip_management): when disabled trips can still be created, listed and opened; deletion on request is an operator procedure.

**Objective:** The dashboard lists the traveller's trips with title, destination, dates and status (archived behind a filter) and offers rename, duplicate, archive/restore and soft delete with confirmation.

**Amended by A1 (2 November 2026):** duplicating a trip copies each item's `source_chunk_ids` (Amendment A1 §6.10).

**Owners and parts**

- Manal (lead) — Rename, duplicate, archive, delete trip API; TripActionsMenu wired to the new endpoints (6 points)
- Manasvi — Dashboard and TripCard (2 points)
- One branch and pull request per part (`feat/IMP-602-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-022, US-023; FR-012, FR-015; NFR-012, NFR-022

**Dependencies:** Prerequisites: IMP-410 · Downstream: IMP-699

**Files**

- apps/api/app/trips/router.py (modify); apps/api/app/trips/service.py (modify); apps/api/app/trips/repository.py (modify); apps/web/app/(app)/dashboard/page.tsx (modify); apps/web/components/trips/TripCard.tsx (create); apps/web/components/trips/TripActionsMenu.tsx (create); apps/api/tests/api/test_trips.py (modify); apps/web/tests/unit/trips/TripActionsMenu.test.tsx (create); apps/api/app/generation/jobs.py (modify)

**Implementation**

1. Extend API-08 GET /api/v1/trips with limit/offset (default 20, max 50), filter status (default excludes archived) and fields title, destination name, dates, status, has_itinerary; exclude rows with deleted_at; order by updated_at desc.
2. API-11 PATCH supports title (1..120) and archived (true -> status archived; false -> status draft or ready depending on has_itinerary); an archived trip is read-only: edit routes return 409 CONFLICT until restored (IMD-35).
3. API-12 DELETE sets deleted_at (soft delete, hidden from all lists, purged after 30 days by the retention job of §5).
4. Add the daily purge to the scheduler in app/generation/jobs.py: delete trips whose deleted_at is older than 30 days, children by cascade (IMD-31).
5. API-13 POST duplicate copies trip settings, trip_preferences, trip_places (must_visit and saved), budget_settings and the current itinerary days/items including locks in one transaction; not versions or generations; new title "<title> (copy)".
6. Build the dashboard with TripCard, TripActionsMenu, ConfirmDialog for delete and archive, EmptyState "Create your first trip", and an "Show archived" filter.
7. Guard rename/duplicate/archive/delete (API-11 archived, API-12, API-13, menu) with the IMD-11 flag 'trip_management'; the list and create stay available.

**Interfaces**

- API: API-08, API-11, API-12, API-13 · Tables: trips, trip_preferences, trip_places, budget_settings, itinerary_days, itinerary_items · Modules: MOD-B03, MOD-F02 · Components: TripCard, TripActionsMenu, ConfirmDialog, EmptyState · Env: FEATURES_DISABLED

**Acceptance criteria**

- FR-012 AC1-AC3 hold (TC-082 to TC-084); FR-015 AC1-AC3 hold (TC-089 to TC-091).
- Another user's trip ids return 404 for list, rename, duplicate, archive and delete (TC-345, TC-346).
- Duplicate leaves the original byte-identical and copies days and items including is_locked.
- With 'trip_management' disabled the dashboard still lists and creates trips (TC-372).
- The purge job removes trips soft-deleted more than 30 days ago and keeps younger ones (IMD-31).

**Tests**

- apps/api/tests/api/test_trips.py — TC-082, TC-083, TC-084, TC-089, TC-090, TC-091 — `make test-api ARGS='-k "dashboard or duplicate or archive or delete"'`
- apps/api/tests/authz/test_ownership.py — TC-345, TC-346 — `make test-authz`
- apps/web/tests/unit/trips/TripActionsMenu.test.tsx — new cases — `make test-web ARGS='TripActionsMenu'`
- apps/api/tests/api/test_trips.py — new cases — `make test-api ARGS='-k purge'`

**Completion evidence**

- PR with make check green; Screenshots of dashboard, empty state and delete confirmation

### IMP-603 Curate and load demo destination 2

**Task:** Sprint 6 (week 6) · DATA · 5 points · lead Junaid with Kirtan, Manya · release MVP

**Objective:** Demo destination 2 is curated from public sources, imported through the quality gate, and its report states the usable count against the minimum.

**Amended by A1 (2 November 2026):** step 6 adds the optional destination-2 guides (Amendment A1 §6.3, IMD-111).

**Owners and parts**

- Junaid (lead) — Opening hours and prices for destination 2, with sources (2 points)
- Manya — Curate a share of destination 2 places and verify sources (2 points)
- Kirtan — Load destination 2 into staging and production; run the quality report (1 points)
- One branch and pull request per part (`feat/IMP-603-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-027; NFR-040

**Dependencies:** Prerequisites: IMP-206 · Downstream: IMP-699

**Files**

- data/places/<slug-2>/destination.json (create); data/places/<slug-2>/places.csv (create); data/places/<slug-2>/opening_hours.csv (create); data/places/<slug-2>/sources.csv (create); data/places/<slug-2>/quality_report.md (create)

**Implementation**

1. Team enters about 60 places (incl. at least 10 food places for meal slots) in the fixture file format of §5, each with source URL, licence and checked-on date; prices and hours only from the named public page, never from memory or an AI.
2. Claude Code may only run validation tooling: make seed SEED_DIRS=data/places/<slug-2> on a local database and report rejected rows; it must not invent place data.
3. Fix or remove rejected rows; commit quality_report.md with usable count, minimum (Proposed 40 usable places), rejected rows with reasons.
4. If the count is below the minimum, record the team decision to demo one destination in docs/decisions/ (FR-less story US-027 AC2).
5. Load into staging with the same seed command.
6. Optional (Amendment A1 §6.3, IMD-111): add guide documents for destination 2 in data/guides/<slug-2>/, written and reviewed by the same rules as IMP-314, and pass the strict gate. Without them, destination 2 uses place documents only.

**Interfaces**

- Tables: destinations, places, place_opening_hours, data_sources · Modules: MOD-D02, MOD-B04

**Acceptance criteria**

- Import report states the count against the minimum (US-027 AC1).
- Every row has source, licence and checked-on date; no row fails the gate silently.
- A below-minimum result has a recorded decision (US-027 AC2).

**Tests**

- apps/api/tests/api/test_seed.py — new cases — `make test-api ARGS='-k seed'`

**Completion evidence**

- data/places/<slug-2>/quality_report.md committed; Staging seed output

### IMP-604 Search, filters and place detail with labelled facts

**Task:** Sprint 6 (week 6) · CODE · 7 points · lead Malhar with Jeel, Manasvi · release MVP-S

**Objective:** Travellers can search and filter places by text, category, price band, duration, interest, distance and accessibility, and open a detail drawer whose hours and prices are labelled and never guessed.

**Owners and parts**

- Malhar (lead) — Search and filter queries, place detail API, indexes (4 points)
- Manasvi — PlaceFilterBar (2 points)
- Jeel — PlaceDetailDrawer with labelled facts (1 points)
- One branch and pull request per part (`feat/IMP-604-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-030, US-031; FR-017, FR-018; NFR-002, NFR-040

**Dependencies:** Prerequisites: IMP-509, IMP-411 · Downstream: IMP-699, IMP-713

**Files**

- apps/api/app/places/router.py (modify); apps/api/app/places/repository.py (modify); apps/api/app/places/schemas.py (modify); apps/web/components/places/PlaceFilterBar.tsx (create); apps/web/components/places/PlaceDetailDrawer.tsx (create); apps/web/app/(app)/trips/[tripId]/explore/page.tsx (modify); apps/api/tests/api/test_places.py (modify); apps/web/tests/unit/places/PlaceDetailDrawer.test.tsx (create)

**Implementation**

1. Extend API-16 query params: q (name/tags, case-insensitive), category[], price_max (money string), duration_max_min, interest[], step_free (bool), near_lat/near_lon with max_distance_m (orders by haversine distance when given); unknown params -> 422.
2. If an index is needed for these filters, add it in a new migration (one per PR, owner MOD-D01) and update the schema-drift test; do not edit merged migrations.
3. Return an empty page with total 0; the UI explains which filters to relax.
4. Implement API-17 GET /api/v1/places/{place_id}: PlaceOut with description, hours[] in destination local time with hours_label and checked date, price range with price_label, source (name, URL, retrieval date), suitability flags; inactive -> 404.
5. Build PlaceFilterBar with filter state in the URL query string, keyboard operable; PlaceDetailDrawer showing "Curated, checked on <date>", "Hours unavailable", "Estimate" via SourceBadge.
6. Apply the rate limit dependency (IMP-511) to API-16.

**Interfaces**

- API: API-16, API-17 · Tables: places, place_opening_hours, data_sources · Modules: MOD-B04, MOD-F03 · Components: PlaceFilterBar, PlaceDetailDrawer, SourceBadge

**Acceptance criteria**

- FR-017 AC1-AC3 hold (TC-095 to TC-097); FR-018 AC1-AC3 hold (TC-098 to TC-100).
- A place without hours shows "Hours unavailable" and no time; a missing price shows "Unavailable", never 0.
- Filter state survives a page reload (URL).

**Tests**

- apps/api/tests/api/test_places.py — TC-095, TC-096, TC-097, TC-098 — `make test-api ARGS='-k "filter or place_detail"'`
- apps/web/tests/unit/places/PlaceDetailDrawer.test.tsx — TC-099, TC-100 — `make test-web ARGS='PlaceDetailDrawer'`

**Completion evidence**

- PR with make check green; Screenshots of filters with an empty result and of the detail drawer

### IMP-605 Saved places (wishlist)

**Task:** Sprint 6 (week 6) · CODE · 3 points · lead Jeel · release MVP-S · Cut-list item 5 (flag wishlist): when disabled there is no saved list; explore, must-visit selection and generation are unaffected.

**Objective:** Travellers can save and unsave places for a trip and see the saved list; saved places raise the ranking signal but are never treated as must-visit.

**Owners and parts:** Jeel — whole task (3 points); branch `feat/IMP-605-<short>`

**Traces to:** Stories US-032; FR-020; NFR-012

**Dependencies:** Prerequisites: IMP-509 · Downstream: IMP-699

**Files**

- apps/api/app/places/router.py (modify); apps/api/app/places/service.py (modify); apps/api/app/generation/ranking.py (modify); apps/web/components/places/PlaceCard.tsx (modify); apps/web/components/places/SavedPlacesPanel.tsx (create); apps/api/tests/api/test_places.py (modify)

**Implementation**

1. Implement API-19 PUT and API-20 DELETE /api/v1/trips/{trip_id}/saved-places/{place_id} as idempotent upsert/delete of trip_places with relation saved (PUT on an existing must_visit row returns 409 CONFLICT; repeated PUT returns 200 with the same row).
2. Implement API-21 GET /api/v1/trips/{trip_id}/saved-places returning PlaceSummaryOut items.
3. In ranking.py set c_signal = 1 for saved places (0 for rejected, 0.5 otherwise) only when the wishlist feature is enabled; saved places never enter the must-visit list or locked items.
4. Add a save toggle (aria-pressed) on PlaceCard and the SavedPlacesPanel on the explore page.
5. Guard API-19..21 and the UI with the IMD-11 flag 'wishlist'.

**Interfaces**

- API: API-19, API-20, API-21 · Tables: trip_places · Modules: MOD-B04, MOD-B06, MOD-F03 · Components: PlaceCard, SavedPlacesPanel · Env: FEATURES_DISABLED

**Acceptance criteria**

- FR-020 AC1-AC3 hold (TC-103 to TC-105).
- Duplicate saves create one row (unique trip_id, place_id); another user's trip returns 404.
- With 'wishlist' disabled the floor journey passes (TC-372).

**Tests**

- apps/api/tests/api/test_places.py — TC-103, TC-104, TC-105 — `make test-api ARGS='-k saved'`
- apps/api/tests/authz/test_ownership.py — TC-345 — `make test-authz`

**Completion evidence**

- PR with make check green; Screenshot of the saved-places panel

### IMP-606 Food places and meal slots

**Task:** Sprint 6 (week 6) · CODE · 5 points · lead Malhar with Manya · release MVP-S · Cut-list item 9 (flag meal_slots): when disabled no meal slots are planned; meal times stay free with a note.

**Objective:** Full-day plans contain lunch (and, by pace, breakfast/dinner) meal slots filled from nearby food places, or left empty with a note, and food places never show ratings.

**Owners and parts**

- Malhar (lead) — Food places data and meal-slot retrieval; meal-slot display on item cards (3 points)
- Manya — Meal slots in the request builder and fallback planner (2 points)
- One branch and pull request per part (`feat/IMP-606-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-060; FR-083

**Dependencies:** Prerequisites: IMP-305, IMP-503 · Downstream: IMP-612, IMP-699

**Files**

- apps/api/app/core/config.py (modify); apps/api/app/generation/retrieval.py (modify); apps/api/app/generation/request_builder.py (modify); apps/api/app/generation/fallback_planner.py (modify); apps/web/components/itinerary/ItineraryItemCard.tsx (modify); apps/api/tests/unit/generation/test_meal_slots.py (create); data/fixtures/sampleton/places.csv (modify); apps/api/app/generation/presets.py (modify)

**Implementation**

1. Define the MEAL_WINDOWS code constant in app/generation/presets.py (IMD-29; not an environment variable) (breakfast 07:30-09:30, lunch 12:00-14:00, dinner 18:30-20:30; Provisional) and the rule: a day longer than 6 active hours gets a lunch slot.
2. In retrieval.py keep enough food-category places in the shortlist (nearest to each day group, preference-filtered) for the meal slots.
3. Mark meal slots in gr-1 so the model fills them with food places only; validate slot_type meal items reference food places (else UNKNOWN_PLACE-style invalid reference finding via the existing rule).
4. Fallback planner inserts the lunch slot from food places; if none fits, leave the slot empty with a note "No food place found nearby" (note_origin none -> use a day-level message, not an AI note).
5. Show meal items in ItineraryItemCard with a meal icon; never render a rating field.
6. Guard with the IMD-11 flag 'meal_slots': disabled -> no meal slots are requested or inserted.

**Interfaces**

- API: API-22, API-24 · Tables: itinerary_items, places · Modules: MOD-B06, MOD-F04, MOD-D02 · Components: ItineraryItemCard · Env: FEATURES_DISABLED · Other: slot_type meal, constant MEAL_WINDOWS in app/generation/presets.py (IMD-29)

**Acceptance criteria**

- FR-083 AC1-AC2 hold (TC-243, TC-244).
- With MOCK and the SAMPLE fixture every full day has a lunch item from a food place or an empty-slot note.
- With 'meal_slots' disabled generation still succeeds without meal items (TC-372).

**Tests**

- apps/api/tests/unit/generation/test_meal_slots.py — TC-243, TC-244 — `make test-unit ARGS='-k meal'`
- apps/api/tests/api/test_generations.py — TC-243 — `make test-api ARGS='-k meal'`

**Completion evidence**

- PR with make check green; Screenshot of a day with a lunch slot

### IMP-607 Regenerate one day around locks and the whole itinerary

**Task:** Sprint 6 (week 6) · CODE · 10 points · lead Het with Nidhi, Krrish · release MVP-S · Cut-list item 7 (flag regeneration): when disabled the traveller edits by hand or creates a new trip.

**Objective:** A traveller can regenerate one day around locked items or the whole itinerary as a new version through the generation job protocol; other days stay byte-identical and a failure leaves the plan unchanged.

**Amended by A1 (2 November 2026):** regenerated items take the citations of the new generation and kept locked items keep theirs; the request is gr-2 with passages when template v2 is active (Amendment A1 §6.8, §6.10).

**Owners and parts**

- Het (lead) — Merge regenerated day and whole-itinerary regeneration API (4 points)
- Nidhi — Regenerate one day around locks (request scope, pipeline) (4 points)
- Krrish — Regenerate controls in DayColumn (2 points)
- One branch and pull request per part (`feat/IMP-607-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-077, US-078; FR-067, FR-068; NFR-004, NFR-008

**Dependencies:** Prerequisites: IMP-506, IMP-305, IMP-502, IMP-610 · Downstream: IMP-699

**Files**

- apps/api/app/generation/router.py (modify); apps/api/app/generation/service.py (modify); apps/api/app/generation/request_builder.py (modify); apps/api/app/generation/pipeline.py (modify); apps/api/app/itinerary/service.py (modify); apps/web/app/(app)/trips/[tripId]/itinerary/page.tsx (modify); apps/web/components/itinerary/DayColumn.tsx (modify); apps/api/tests/api/test_generations.py (modify); apps/api/tests/api/test_itinerary.py (modify)

**Implementation**

1. Implement API-30 POST /api/v1/trips/{trip_id}/itinerary/days/{day_number}/regenerate and API-31 POST /api/v1/trips/{trip_id}/itinerary/regenerate with body RegenerateIn (plan_revision, mode); both handled in app/generation/router.py (IMD-13), return 202 + GenerationOut and reuse the API-22 job protocol (one active job per trip, request-hash idempotency, caps).
2. Build the day-scoped gr-1 request: the day, its locked items as fixed constraints, neighbouring days' place ids as exclusions, remaining budget share; scope day with scope_day_number in ai_generations (IMD-17).
3. Save step for scope day: in one transaction verify plan_revision, replace only that day's unlocked items (the regeneration snapshot was already written when the job was started by API-30/API-31, always, IMD-18), recompute and revalidate the whole trip, bump plan_revision, write warnings and complete the generation; other days' rows untouched.
4. Full regeneration: same transaction pattern, locked items preserved, previous plan restorable through versions (reason regeneration).
5. On failure or stale revision the plan is unchanged and the generation ends failed (or 409 STALE_PLAN at start).
6. UI: "Regenerate day" in DayColumn and "Regenerate all" with ConfirmDialog; progress via GenerationProgress; outcome notice via FallbackNotice.
7. Guard both with the IMD-11 flag 'regeneration'.

**Interfaces**

- API: API-30, API-31, API-23, API-24 · Tables: ai_generations, itinerary_days, itinerary_items, itinerary_versions, itinerary_warnings, trips · Modules: MOD-B08, MOD-B06, MOD-F04 · Components: DayColumn, GenerationProgress, ConfirmDialog, FallbackNotice · Env: FEATURES_DISABLED · Other: gr-1 scope day

**Acceptance criteria**

- FR-067 AC1-AC2 hold (TC-213, TC-214); FR-068 AC1-AC2 hold (TC-215, TC-216).
- Rows of non-target days are byte-identical before and after a day regeneration (row hash comparison in the test).
- Locked items keep day and start_time (TC-313); restore of the pre-regeneration version works (TC-376, with IMP-610).
- With 'regeneration' disabled the routes return 404 and manual editing remains (TC-372).

**Tests**

- apps/api/tests/api/test_generations.py — TC-213, TC-214, TC-215, TC-216, TC-313 — `make test-api ARGS='-k regenerate'`
- apps/web/e2e/itinerary-edit.spec.ts — TC-376 — `make e2e ARGS='itinerary-edit'`

**Completion evidence**

- PR with make check green; API test log with the byte-identity check; Screen recording or screenshots of a day regeneration

### IMP-608 Budget alerts and contingency buffer

**Task:** Sprint 6 (week 6) · CODE · 4 points · lead Manal with Krrish · release MVP-S · Cut-list items 3 (flag contingency) and 4 (flag budget_alerts): without contingency the buffer line is zero and stated; without alerts the validator budget warning still appears.

**Objective:** The costs page and itinerary cost strip show near-budget and over-budget alerts and a contingency line that the traveller can set from 0 to 50 percent.

**Owners and parts**

- Manal (lead) — Budget alerts and contingency buffer (2 points)
- Krrish — BudgetAlert component (2 points)
- One branch and pull request per part (`feat/IMP-608-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-084, US-085; FR-074, FR-075; NFR-030

**Dependencies:** Prerequisites: IMP-507, IMP-501 · Downstream: IMP-699, IMP-712

**Files**

- apps/api/app/budget/engine.py (modify); apps/api/app/budget/router.py (modify); apps/api/app/budget/service.py (modify); apps/web/components/costs/BudgetAlert.tsx (create); apps/web/components/costs/BudgetSettingsForm.tsx (modify); apps/api/tests/unit/budget/test_alerts_contingency.py (create); apps/web/tests/unit/costs/BudgetAlert.test.tsx (create)

**Implementation**

1. Implement BF-08 contingency C = round(S_hi * p / 100) and BF-09 P = S_hi + C in engine.py (already partly present from IMP-308; make p configurable per trip from budget_settings.contingency_pct, default 10).
2. Implement BF-11 alerts in the API-33 response: alerts[] with code BUDGET_EXCEEDED (excess) or BUDGET_NEAR (ratio_pct), theta = BUDGET_NEAR_PCT (90, code constant in app/budget/engine.py, IMD-29); the same engine function feeds the validator findings (IMP-501), no second implementation.
3. API-34 PATCH /api/v1/trips/{trip_id}/budget-settings accepts contingency_pct 0..50 (else 422) together with the allowances.
4. Build BudgetAlert banners (role status, text not colour only) on the costs page and in the itinerary cost strip; add the contingency input to BudgetSettingsForm.
5. Guard alerts with flag 'budget_alerts' and the contingency with flag 'contingency' (disabled -> p = 0 and the estimate states that no buffer is included).

**Interfaces**

- API: API-33, API-34 · Tables: budget_settings, trips · Modules: MOD-B09, MOD-F06 · Components: BudgetAlert, BudgetSettingsForm, CostSummary · Env: FEATURES_DISABLED · Other: BF-08, BF-09, BF-11, constant BUDGET_NEAR_PCT in app/budget/engine.py (IMD-29)

**Acceptance criteria**

- FR-074 AC1-AC2 hold (TC-227, TC-228); FR-075 AC1-AC2 hold (TC-229, TC-230).
- Contingency applies to S_hi and the category sums still equal the planning total (TC-298, TC-300).
- With 'budget_alerts' and 'contingency' disabled the costs page still shows the estimate and the validator budget warning (TC-372).

**Tests**

- apps/api/tests/unit/budget/test_alerts_contingency.py — TC-227, TC-228, TC-229, TC-230, TC-298 — `make test-unit ARGS='-k "alerts or contingency"'`
- apps/web/tests/unit/costs/BudgetAlert.test.tsx — new cases — `make test-web ARGS='BudgetAlert'`

**Completion evidence**

- PR with make check green; Screenshots of near and over budget banners

### IMP-609 Final trip summary and print view

**Task:** Sprint 6 (week 6) · CODE · 3 points · lead Krrish with Het · release MVP

**Objective:** The summary page lists every day with times, places, travel notes, labelled costs, unresolved warnings and the estimate statement, and prints cleanly from the browser.

**Owners and parts**

- Krrish (lead) — Summary page and print layout (2 points)
- Het — Summary API (1 points)
- One branch and pull request per part (`feat/IMP-609-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-109; FR-094; NFR-040

**Dependencies:** Prerequisites: IMP-309, IMP-507 · Downstream: IMP-699

**Files**

- apps/api/app/itinerary/router.py (modify); apps/api/app/itinerary/service.py (modify); apps/api/app/itinerary/schemas.py (modify); apps/web/app/(app)/trips/[tripId]/summary/page.tsx (create); apps/web/components/versions/PrintLayout.tsx (create); apps/api/tests/api/test_itinerary.py (modify); apps/web/tests/unit/versions/PrintLayout.test.tsx (create)

**Implementation**

1. Implement API-35 GET /api/v1/trips/{trip_id}/summary as a read-only projection built from the current plan, the cost engine and stored warnings (no new calculations in the router): trip header, days (date, theme with AI label, items with times, travel line with source label, cost with label), totals, unresolved findings, checked-on dates, and the closing statement "Prices and hours are estimates unless marked Curated".
2. Build the summary page and a print stylesheet (PrintLayout: no navigation, page breaks between days); the Print button calls window.print(); no server-side PDF.
3. Show unresolved warnings in a separate section; empty itinerary -> EmptyState with a link to generate.
4. Test that labels and warnings appear in the API response and the rendered page.

**Interfaces**

- API: API-35 · Tables: itinerary_days, itinerary_items, itinerary_warnings, trips · Modules: MOD-B08, MOD-B09, MOD-F06 · Components: PrintLayout, SourceBadge, AiBadge, EmptyState

**Acceptance criteria**

- FR-094 AC1-AC2 hold (TC-254, TC-255).
- Every price, hour and travel time in the summary carries its label; AI-written themes carry the AI-written badge.
- The print preview shows no navigation and one day per page section (manual check recorded with a screenshot).

**Tests**

- apps/api/tests/api/test_itinerary.py — TC-254, TC-255 — `make test-api ARGS='-k summary'`
- apps/web/tests/unit/versions/PrintLayout.test.tsx — new cases — `make test-web ARGS='PrintLayout'`

**Completion evidence**

- PR with make check green; Screenshot of the summary and of the print preview

### IMP-610 Itinerary versions: save, list and restore

**Task:** Sprint 6 (week 6) · CODE · 8 points · lead Jeel with Malhar · release MVP-S · Cut-list item 1 (flag versions): when disabled there is no history or restore; one backup copy of the previous itinerary is kept for regeneration.

**Objective:** Each trip keeps up to 20 itinerary versions written automatically on generation, regeneration and restore and on Save version, and any version can be restored as the new current plan.

**Amended by A1 (2 November 2026):** `snap-1` snapshots store each item's `source_chunk_ids`, and a restore brings them back; a snapshot without them reads as empty (Amendment A1 §5.5).

**Owners and parts**

- Jeel (lead) — Version snapshots (snap-1): save, list, restore; versions page and VersionList (6 points)
- Malhar — Restore transaction and retention (2 points)
- One branch and pull request per part (`feat/IMP-610-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-110; FR-095; NFR-008, NFR-045

**Dependencies:** Prerequisites: IMP-407 · Downstream: IMP-607, IMP-699

**Files**

- apps/api/app/itinerary/versions.py (create); apps/api/app/itinerary/router.py (modify); apps/api/app/itinerary/service.py (modify); apps/api/app/generation/pipeline.py (modify); apps/web/app/(app)/trips/[tripId]/versions/page.tsx (create); apps/web/components/versions/VersionList.tsx (create); apps/api/tests/api/test_versions.py (create); apps/web/tests/unit/versions/VersionList.test.tsx (create)

**Implementation**

1. In versions.py write the snapshot in format snap-1 of §5.2 (days and items incl. locks and notes, budget_settings, plan_revision; no costs or findings) with version_no = max+1 per trip and reason in generation | regeneration | edit | restore | fallback | manual (IMD-18); called by the pipeline save step, by every edit (API-25 to API-29, reason edit), when a regeneration job starts (reason regeneration, always; one backup copy when the versions switch is off) and before restore. API-24 with version_id builds ItineraryOut from the snapshot on read by running the budget engine and the validator, writing nothing (IMD-18).
2. Retention: keep at most 20 versions per trip; when exceeded delete the oldest automatic version (never a named one; IMD-18).
3. API-36 GET list (id, version_no, reason, plan_revision, created_at, finding counts); API-37 POST {plan_revision, name} saves the current plan as a named version (reason manual, name 1 to 60 characters, unique per trip, 409 CONFLICT on a duplicate; kind derived named or automatic; IMD-18); API-37 and API-38 return 409 GENERATION_IN_PROGRESS while a generation is active (IMD-23); API-38 POST restore in one transaction: snapshot current, replace days and items from the snapshot, bump plan_revision, write a restore version, revalidate.
4. Build the versions page with VersionList, Save version button, Restore with ConfirmDialog; after restore invalidate itinerary, costs and warnings queries.
5. Guard API-36..38 and the page with the IMD-11 flag 'versions'; when disabled keep one backup copy of the previous itinerary for regeneration (blueprint §25.6 item 1).

**Interfaces**

- API: API-36, API-37, API-38 · Tables: itinerary_versions, itinerary_days, itinerary_items, trips · Modules: MOD-B08, MOD-F04 · Components: VersionList, ConfirmDialog · Env: FEATURES_DISABLED

**Acceptance criteria**

- FR-095 AC1-AC2 hold (TC-256, TC-257).
- Restore keeps the replaced plan in history (TC-318); the limit removes only the oldest automatic version (TC-319).
- A stale screen editing after a restore gets 409 STALE_PLAN.
- With 'versions' disabled the floor journey passes (TC-372).
- A duplicate version name returns 409 CONFLICT; named versions are never pruned (IMD-18).

**Tests**

- apps/api/tests/api/test_versions.py — TC-256, TC-257, TC-318, TC-319 — `make test-api ARGS='-k versions'`
- apps/web/tests/unit/versions/VersionList.test.tsx — new cases — `make test-web ARGS='VersionList'`

**Completion evidence**

- PR with make check green; Screenshot of the versions page after a restore

### IMP-611 Usability session 1 and recorded findings

**Task:** Sprint 6 (week 6) · HUMAN · 3 points · lead Junaid with Krrish · release MVP

**Objective:** Usability session 1 with five participants is run on staging and its observed findings are triaged into backlog items.

**Owners and parts**

- Junaid (lead) — Run usability session 1 (2 points)
- Krrish — Record findings (1 points)
- One branch and pull request per part (`feat/IMP-611-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-142; NFR-027

**Dependencies:** Prerequisites: IMP-414 · Downstream: IMP-699, IMP-704

**Files**

- docs/acceptance/usability-1/plan.md (create); docs/acceptance/usability-1/findings.md (create)

**Implementation**

1. Claude Code may draft the task script, consent text and observation sheet in docs/acceptance/usability-1/plan.md; the team recruits five participants and runs the sessions.
2. Use test accounts and the SAMPLE or curated data only; no participant personal data is stored beyond first name or a code.
3. Record what participants did (task completion, errors, time), not opinions only.
4. Triage findings by severity into issues with labels and owners; link them from findings.md.
5. Feed top issues into IMP-704 (usability session 2).

**Interfaces**

- Other: staging environment, NFR-027 first-use success

**Acceptance criteria**

- Five sessions recorded with observed behaviour (US-142 AC1).
- Top issues exist as backlog items with owners (US-142 AC2).
- No result is reported that was not observed.

**Tests**

- docs/acceptance/usability-1/findings.md — new cases — `manual (team) - no automated command`

**Completion evidence**

- docs/acceptance/usability-1/plan.md and findings.md; Links to the created issues

### IMP-612 Optimise day order to cut travel time

**Task:** Sprint 6 (week 6) · CODE · 8 points · lead Het with Junaid, Manasvi · release EXT · Extension; switch optimise_order (cut 6 of 9). When disabled the traveller still reorders by drag or keyboard (API-26).

**Objective:** On any day the traveller can preview a reordering of the unlocked items that shortens total travel while respecting locks, meal slots and opening hours, see the minutes saved, and apply it as one ordinary edit.

**Owners and parts**

- Het (lead) — Preview and apply endpoints (API-66, API-67) as one edit (3 points)
- Junaid — Ordering heuristic (nearest neighbour + 2-opt) over the travel-time matrix (3 points)
- Manasvi — Optimise button and before/after preview dialog (2 points)
- One branch and pull request per part (`feat/IMP-612-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-157; FR-130; NFR-003

**Dependencies:** Prerequisites: IMP-407, IMP-307, IMP-506, IMP-606 · Downstream: IMP-699

**Files**

- apps/api/app/itinerary/optimise.py (create); apps/api/app/itinerary/router.py (modify); apps/api/app/itinerary/service.py (modify); apps/api/app/itinerary/schemas.py (modify); apps/web/components/itinerary/OptimiseDayDialog.tsx (create); apps/web/components/itinerary/DayColumn.tsx (modify); apps/api/tests/unit/itinerary/test_optimise.py (create); apps/api/tests/api/test_optimise.py (create); apps/web/tests/unit/itinerary/OptimiseDayDialog.test.tsx (create); contracts/openapi.v1.json (modify)

**Implementation**

1. Contract first: on day 1 of the sprint the API part declares this card's endpoints with their final shapes (§6) and regenerates contracts/openapi.v1.json with make openapi; handlers return 501 NOT_IMPLEMENTED until built (IMD-37: allowed for extension routes until SG-7), so the screen part starts against the regenerated web client (Team Contribution Plan v2).
2. Implement app/itinerary/optimise.py (pure): split the day into segments between locked items and fixed meal slots; within each segment order unlocked items by nearest neighbour from the segment start, then improve with 2-opt; travel minutes come from a matrix built by the routing service (route_cache first, fallback estimate otherwise; no new external call per permutation).
3. Keep a proposal only if total travel falls by at least 5 minutes and recalculation plus validation adds no new error finding (OVERLAP, CLOSED_ON_DAY, OUTSIDE_HOURS, UNKNOWN_PLACE, OUTSIDE_TRIP_DATES); otherwise return status no_better_order (or nothing_to_optimise with fewer than three movable items), as OptimisePreviewOut in §6.5.1.
4. Implement API-66 GET .../days/{day_number}/optimise (preview, no write): proposed order, travel minutes before and after, findings after the change, plan_revision it is based on.
5. Implement API-67 POST .../days/{day_number}/optimise with body OptimiseApplyIn {plan_revision, item_ids}: verify item_ids are exactly the day's items with locked items and meal slots in their positions (else 422 INVALID_EDIT), then apply as one edit transaction through the edit core (recalculate, revalidate, automatic version reason edit, IMD-18); stale revision 409 STALE_PLAN; active generation 409 GENERATION_IN_PROGRESS (IMD-23).
6. Build OptimiseDayDialog: "Optimise order" button in DayColumn header opens the preview with before/after list and minutes saved; Apply calls API-67 and replaces the plan with the response; "No better order found" when status is no_better_order or nothing_to_optimise.
7. Add the switch: Guard with the extension switch 'optimise_order' (IMD-11, EXT): when FEATURES_DISABLED / NEXT_PUBLIC_FEATURES_DISABLED contains 'optimise_order' the routes return 404 NOT_FOUND and the UI entry point is hidden (TC-432).

**Interfaces**

- API: API-66, API-67 · Tables: itinerary_items, itinerary_days, itinerary_warnings, itinerary_versions, route_cache, trips · Modules: MOD-B08, MOD-B10, MOD-B07, MOD-F04 · Components: OptimiseDayDialog, DayColumn · Env: FEATURES_DISABLED, NEXT_PUBLIC_FEATURES_DISABLED

**Acceptance criteria**

- FR-130 AC1-AC3 hold (TC-409 to TC-412).
- Locked items and meal slots keep their positions and times after optimisation (unit test).
- A proposal never adds an error finding; when no order saves 5 minutes the preview says so and nothing changes.
- Apply with a stale plan_revision returns 409 STALE_PLAN and changes nothing.
- With optimise_order disabled both routes return 404 and the button is hidden (TC-432).

**Tests**

- apps/api/tests/unit/itinerary/test_optimise.py — TC-409, TC-410 — `make test-unit ARGS='-k optimise'`
- apps/api/tests/api/test_optimise.py — TC-411, TC-412, TC-431, TC-432 — `make test-api ARGS='-k optimise'`
- apps/web/tests/unit/itinerary/OptimiseDayDialog.test.tsx — new cases — `make test-web ARGS='OptimiseDayDialog'`

**Completion evidence**

- PR with make check green; Screenshot of a preview showing minutes saved on a SAMPLE trip

### IMP-613 Packing checklist with AI free-text refinement

**Task:** Sprint 6 (week 6) · CODE · 9 points · lead Kirtan with Nidhi, Manya · release EXT · Extension; switch packing (cut 1 of 9, first). When disabled the packing page and API-43, API-74, API-75 are hidden; no other feature depends on it except the assist-call log, which stays.

**Objective:** Each trip has a grouped, tickable packing checklist built by rules from trip length, travellers and place categories (no weather input, IMD-48); the traveller can type a need and accept AI-suggested items that come only from a fixed vocabulary; every AI call is logged and capped.

**Owners and parts**

- Kirtan (lead) — Packing rules, checklist and assist-log tables, packing endpoints (API-43, API-75) and packing page (5 points)
- Nidhi — suggest_packing_items operation and refine endpoint (API-74) (2 points)
- Manya — Item vocabulary, ps-1 validation and evaluation cases (2 points)
- One branch and pull request per part (`feat/IMP-613-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-096, US-162; FR-088, FR-135; NFR-021

**Dependencies:** Prerequisites: IMP-110, IMP-111, IMP-207, IMP-301 · Downstream: IMP-699, IMP-708, IMP-709

**Files**

- apps/api/migrations/sql/0007_packing_and_assist.sql (create); apps/api/migrations/sql/down/0007_packing_and_assist.down.sql (create); apps/api/migrations/versions/0007_packing_and_assist.py (create); apps/api/app/db/models/prep.py (create); apps/api/app/db/models/ai.py (create); apps/api/app/prep/router.py (create); apps/api/app/prep/service.py (create); apps/api/app/prep/repository.py (create); apps/api/app/prep/schemas.py (create); apps/api/app/prep/packing_rules.py (create); data/packing/vocabulary.json (create); apps/api/app/ai/assist_log.py (create); apps/api/app/ai/providers/base.py (modify); apps/api/app/ai/providers/gemini.py (modify); apps/api/app/ai/providers/mock.py (modify); apps/api/app/schemas/ai.py (modify); apps/api/app/ai/prompts/templates/packing_refine/v1/system.txt (create); apps/api/app/ai/prompts/templates/packing_refine/v1/user.txt (create); apps/api/app/ai/prompts/templates/packing_refine/v1/meta.json (create); apps/web/app/(app)/trips/[tripId]/packing/page.tsx (create); apps/web/components/prep/PackingList.tsx (create); apps/web/components/prep/PackingRefineForm.tsx (create); apps/api/tests/unit/prep/test_packing_rules.py (create); apps/api/tests/api/test_packing.py (create); apps/api/tests/contract/test_provider_contract.py (modify); apps/web/tests/unit/prep/PackingList.test.tsx (create); contracts/openapi.v1.json (modify)

**Implementation**

1. Contract first: on day 1 of the sprint the API part declares this card's endpoints with their final shapes (§6) and regenerates contracts/openapi.v1.json with make openapi; handlers return 501 NOT_IMPLEMENTED until built (IMD-37: allowed for extension routes until SG-7), so the screen part starts against the regenerated web client (Team Contribution Plan v2).
2. Write migration 0007_packing_and_assist (EXT_CONTRACT §5): checklist_items (kind check limited to packing, origin rule|ai|user, status active|suggested|rejected) and ai_assist_calls (purpose trip_intake|day_explanation|packing_refine, retention_until now()+90 days), RLS owner policies, no browser privileges, indexes; ORM models; schema-drift test stays green; verify upgrade/downgrade on the test database.
3. Implement packing_rules.py (pure): base items plus rules by trip length, children in the party, place categories in the plan (e.g. religious -> modest clothing, nature -> walking shoes) (no weather input: the weather module arrives in Sprint 7, IMD-48); every label comes from data/packing/vocabulary.json.
4. Implement API-43 GET /api/v1/trips/{trip_id}/packing-list: create rule items idempotently on first read (no duplicates on repeat calls), return items grouped by category with origin and status; API-75 PATCH .../packing-list/items/{item_id}: tick, accept or reject a suggestion, edit a user item label (1 to 160 chars).
5. Add ModelProvider operation suggest_packing_items(PackingSuggestionRequest) -> ProviderResult[PackingSuggestionOutput] (ps-1) to base.py, GEMINI and MOCK (deterministic suggestions; FINETUNED_MODEL stub refuses); template packing_refine/v1; export contracts/ai/ps-1.schema.json via make openapi.
6. Implement API-74 POST .../packing-list/refine (need <= 200 chars): check AI_DAILY_ASSIST_CALLS_PER_USER (429 AI_QUOTA_REACHED), call the provider, keep at most 10 items that match the vocabulary case-insensitively, drop the rest, never remove rule items, save them with origin ai and status suggested; write one ai_assist_calls row per call (ok, rejected or failed) through app/ai/assist_log.py.
7. Build /trips/[tripId]/packing with PackingList (groups, checkboxes, AI-suggested items marked with AiBadge and Accept/Reject) and PackingRefineForm; loading, empty and error states.
8. Add the switch: Guard with the extension switch 'packing' (IMD-11, EXT): when FEATURES_DISABLED / NEXT_PUBLIC_FEATURES_DISABLED contains 'packing' the routes return 404 NOT_FOUND and the UI entry point is hidden (TC-432).

**Interfaces**

- API: API-43, API-74, API-75 · Tables: checklist_items, ai_assist_calls, itinerary_items, places, trips · Modules: MOD-B12, MOD-B05, MOD-D01, MOD-F08 · Components: PackingList, PackingRefineForm, AiBadge · Env: AI_DAILY_ASSIST_CALLS_PER_USER, FEATURES_DISABLED, NEXT_PUBLIC_FEATURES_DISABLED, MOCK_PROVIDER_SCENARIO · Other: schema ps-1, prompt template packing_refine/v1

**Acceptance criteria**

- FR-088 AC1 and FR-135 AC1-AC3 hold (TC-425 to TC-429).
- Repeated GET creates no duplicate rule items.
- Off-vocabulary suggestions never reach the database; rule items are never removed by refinement.
- Every refine call writes one ai_assist_calls row and the daily cap returns 429 AI_QUOTA_REACHED (TC-430).
- Migration 0007 applies and reverts on a blank database and the drift test passes.
- With packing disabled the routes return 404 and the page link is hidden (TC-432).

**Tests**

- apps/api/tests/unit/prep/test_packing_rules.py — TC-425, TC-426 — `make test-unit ARGS='-k packing'`
- apps/api/tests/api/test_packing.py — TC-427, TC-428, TC-430, TC-431, TC-432 — `make test-api ARGS='-k packing'`
- apps/api/tests/contract/test_provider_contract.py — TC-429 — `make test-contract ARGS='-k packing'`
- apps/web/tests/unit/prep/PackingList.test.tsx — new cases — `make test-web ARGS='PackingList'`

**Completion evidence**

- PR with make check green including the drift test; Screenshot of a packing list with one accepted AI suggestion on a SAMPLE trip

### IMP-699 Sprint 6 gate SG-6: MVP feature-complete and feature freeze

**Task:** Sprint 6 (week 6) · VERIFY · 0 points · lead Kirtan · release MVP

**Objective:** Sprint 6 gate SG-6 is passed and recorded: every MVP and MVP-S requirement is implemented or explicitly cut, and the feature freeze is in force.

**Owners and parts:** Kirtan — whole task (0 points); branch `feat/IMP-699-<short>`

**Traces to:** enabling work (no requirement)

**Dependencies:** Prerequisites: IMP-601, IMP-602, IMP-603, IMP-604, IMP-605, IMP-606, IMP-607, IMP-608, IMP-609, IMP-610, IMP-611, IMP-612, IMP-613 · Downstream: IMP-701, IMP-702, IMP-705

**Files**

- docs/progress/sprint-6.md (modify); docs/progress/gates.md (modify); docs/progress/deferred.md (create)

**Implementation**

1. Generate the requirement coverage report from docs/spec/TRACEABILITY_MATRIX.md: each MVP/MVP-S FR has a done task and passing tests, or a recorded cut-list decision.
2. Run make check and make e2e on main; run the floor journey with all nine cut-list flags disabled (TC-372) and with all enabled.
3. Deploy to staging and run the full primary journey with GEMINI (sign in, create, generate, validate costs, edit, regenerate a day, restore a version, summary).
4. Record deferred functionality (unfinished stories, disabled flags, T1 items not started) in docs/progress/deferred.md with owner and reason.
5. Declare the feature freeze in docs/progress/gates.md: from Sprint 7 only defects, hardening, documents and planned Sprint 7/8 tasks are merged.
6. MVP freeze plus extensions: IMP-612 (optimise_order) and IMP-613 (packing) are done with tests or switched off; Sprint 7 extensions (IMP-708 to IMP-713) may still be dropped in the cut order if the MVP is not feature-complete; record the extension plan for Sprint 7.

**Interfaces**

- Env: FEATURES_DISABLED · Other: SG-6 criteria §14, TRACEABILITY_MATRIX.md

**Acceptance criteria**

- Every MVP/MVP-S FR is either Done with tests or listed as cut with the checkpoint decision.
- make check and make e2e green; floor journey green with all flags disabled (TC-372) and with all enabled (TC-369).
- Staging GEMINI journey demonstrated and recorded.
- docs/progress/deferred.md and the freeze entry exist.
- IMP-612 and IMP-613 are done (TC-409 to TC-412, TC-425 to TC-430) or switched off, and the Sprint 7 extension plan is recorded.

**Tests**

- apps/web/e2e/journey.spec.ts — TC-369, TC-372 — `make e2e`
- apps/api/tests/smoke/test_deployed.py — new cases — `make smoke URL=<staging-api-url>`

**Completion evidence**

- CI links; docs/progress/gates.md SG-6 entry; docs/progress/deferred.md

## Sprint 7 (week 7): Quality and usability — gate SG-7

| Task | Title | Type | Lead | Parts (points) | Prerequisites | Points |
| --- | --- | --- | --- | --- | --- | --- |
| IMP-701 | End-to-end regression suite for all primary scenarios | CODE | Krrish | Krrish 3 | IMP-699, IMP-216, IMP-414 | 3 |
| IMP-702 | Authorization and security test pass | CODE | Junaid | Junaid 2, Het 2, Kirtan 1 | IMP-215, IMP-699, IMP-511 | 5 |
| IMP-703 | Accessibility check on real devices and fixes | HUMAN | Krrish | Krrish 3 | IMP-513, IMP-701 | 3 |
| IMP-704 | Usability session 2 and fixes of the top issues | HUMAN | Manasvi | Manasvi 2, Junaid 1 | IMP-611, IMP-703 | 3 |
| IMP-705 | Final evaluation baseline and cost report | DATA | Nidhi | Nidhi 1 | IMP-514, IMP-699 | 1 |
| IMP-706 | Stage 2 readiness package (documents only) | HUMAN | Manya | Manya 3 | IMP-705 | 3 |
| IMP-707 | SRS, architecture, test plan, user guide and deployment guide | HUMAN | Malhar | Malhar 2, Manal 1, Junaid 1, Jeel 1, Kirtan 1 | IMP-701, IMP-702 | 6 |
| IMP-708 | Natural-language trip intake with confirmation | CODE | Nidhi | Nidhi 2, Manya 2, Manal 2, Manasvi 2 | IMP-212, IMP-303, IMP-301, IMP-613 | 8 |
| IMP-709 | "Why this plan" explanations for each day | CODE | Nidhi | Nidhi 2, Het 2, Manya 1 | IMP-305, IMP-406, IMP-613 | 5 |
| IMP-710 | Rain-aware day swapping with the Open-Meteo forecast | CODE | Manal | Manal 3, Malhar 2, Krrish 2 | IMP-407, IMP-501 | 7 |
| IMP-711 | "Today" companion view for trip days | CODE | Manasvi | Manasvi 2, Het 1 | IMP-309, IMP-508 | 3 |
| IMP-712 | Budget-fit suggestions when a plan is over budget | CODE | Junaid | Junaid 3, Jeel 2, Krrish 2 | IMP-608, IMP-505 | 7 |
| IMP-713 | Destination and place context cards from Wikivoyage and Wikipedia | CODE | Malhar | Malhar 3, Jeel 2, Kirtan 1 | IMP-604 | 6 |
| IMP-799 | Sprint 7 gate SG-7: release candidate | VERIFY | Kirtan | Kirtan 2 | IMP-701, IMP-702, IMP-703, IMP-704, IMP-705, IMP-707, IMP-706, IMP-708, IMP-709, IMP-710, IMP-711, IMP-712, IMP-713 | 2 |


### IMP-701 End-to-end regression suite for all primary scenarios

**Task:** Sprint 7 (week 7) · CODE · 3 points · lead Krrish · release MVP

**Objective:** Every primary-journey scenario E2E-01 to E2E-08 and the edit, lock, regenerate and version-restore regressions run as Playwright specs against the composed stack with AI_PROVIDER=MOCK, on every merge to main and nightly.

**Owners and parts:** Krrish — whole task (3 points); branch `feat/IMP-701-<short>`

**Traces to:** Stories US-141; NFR-012, NFR-025, NFR-026, NFR-048

**Dependencies:** Prerequisites: IMP-699, IMP-216, IMP-414 · Downstream: IMP-703, IMP-707, IMP-799

**Files**

- apps/web/e2e/auth.spec.ts (modify); apps/web/e2e/trip-create.spec.ts (modify); apps/web/e2e/generate.spec.ts (modify); apps/web/e2e/validate-costs.spec.ts (create); apps/web/e2e/itinerary-edit.spec.ts (create); apps/web/e2e/reopen.spec.ts (create); apps/web/e2e/provider-failure.spec.ts (create); apps/web/e2e/ownership.spec.ts (create); apps/web/e2e/journey.spec.ts (modify); apps/web/e2e/fixtures/users.ts (modify); apps/web/playwright.config.ts (modify); .github/workflows/e2e.yml (modify); .github/pull_request_template.md (modify); apps/web/e2e/extensions.spec.ts (create)

**Implementation**

1. Inspect the existing specs from IMP-216 and IMP-414 and list which of E2E-01 to E2E-08 (§13) are missing; reuse e2e/fixtures/users.ts for user creation, do not add a second user helper.
2. Add the missing specs named in contract §J; each test title starts with its E2E or TC identifier and each step uses test.step("<user action>") so a failure names the user step (US-141 AC2).
3. itinerary-edit.spec.ts: reorder to create an overlap (expect OVERLAP finding), remove an item, retime an item, lock an item, regenerate day 2 (locked item keeps its time), save a version, change the plan, restore the version and reload (TC-376).
4. provider-failure.spec.ts in the separate Playwright project provider-failure (API on port 8001, web on 3001; IMD-33): start the API with MOCK_PROVIDER_SCENARIO=timeout, then quota; expect the FallbackNotice and a saved rule-based plan for timeout, and for quota the paused-AI message (failed, provider_quota_exhausted) with the rule-based option and no further provider call (TC-371, ACC-03, ACC-17).
5. Add a floor-journey project in playwright.config.ts that runs journey.spec.ts with FEATURES_DISABLED and NEXT_PUBLIC_FEATURES_DISABLED set to all nine cut-list names (TC-372); add a 360 px viewport project (TC-373) and a keyboard-only journey (TC-374) with axe scans after each page.
6. Stabilise flaky tests: replace fixed waits with web-first assertions on GenerationProgress terminal states; run the suite three times with --repeat-each=3 and record run times in docs/test-reports/e2e-sprint7.md.
7. Update e2e.yml to run on push to main and nightly (cron) with the Supabase local stack and MOCK; upload the Playwright HTML report as a workflow artefact.
8. Add a pull-request template checkbox: "E2E specs touched by this change pass locally (make e2e)".
9. Add apps/web/e2e/extensions.spec.ts tagged @ext: with all extension switches on and MOCK, run one short scenario per enabled extension (why-this-place, describe a trip, explain a day, optimise a day, rain banner with a mocked forecast, Today view at a fixed time, budget-fit apply, context card, packing refine); each test skips with the reason when its switch is off. The extension cards IMP-708 to IMP-713 are not prerequisites of this card: each scenario is added in the extension card's own pull request or when it merges, and a switched-off extension stays skipped (§11.2).

**Interfaces**

- API: API-07, API-22, API-23, API-24, API-26, API-27, API-30, API-33, API-37, API-38 · Modules: MOD-P01, MOD-F04 · Components: GenerationProgress, FallbackNotice, WarningsPanel, MoveControls, ItemEditor, VersionList · Env: MOCK_PROVIDER_SCENARIO, FEATURES_DISABLED, NEXT_PUBLIC_FEATURES_DISABLED, SUPABASE_SERVICE_ROLE_KEY · Other: E2E-01..E2E-08

**Acceptance criteria**

- make e2e passes locally three consecutive times with AI_PROVIDER=MOCK and no retries configured (flake rate 0 of 3 runs recorded)
- Specs exist and pass for E2E-01 to E2E-08 and for TC-369, TC-371, TC-372, TC-373, TC-374, TC-375, TC-376
- A deliberately broken assertion makes CI fail and the report shows the test name and the failing user step (US-141 AC2, NFR-048)
- The floor journey passes with all nine cut-list features disabled (TC-372)
- No spec needs a Gemini key, a hosted Supabase project or network access beyond the local stack
- make e2e ARGS='--grep @ext' passes for every enabled extension and skips disabled ones with the reason.

**Tests**

- apps/web/e2e/itinerary-edit.spec.ts — TC-376 — `make e2e ARGS='itinerary-edit'`
- apps/web/e2e/provider-failure.spec.ts — TC-371 — `make e2e ARGS='provider-failure'`
- apps/web/e2e/journey.spec.ts — TC-369, TC-372, TC-373, TC-374 — `make e2e ARGS='journey'`
- apps/web/e2e/ownership.spec.ts — TC-375 — `make e2e ARGS='ownership'`
- apps/web/e2e/extensions.spec.ts — TC-432 — `make e2e ARGS='--grep @ext'`

**Completion evidence**

- Green e2e.yml run on main with the Playwright HTML report artefact; docs/test-reports/e2e-sprint7.md with three local run results, run times and the flaky-test list (empty or with owners); PR link

### IMP-702 Authorization and security test pass

**Task:** Sprint 7 (week 7) · CODE · 5 points · lead Junaid with Het, Kirtan · release MVP

**Objective:** Every protected MVP route is proven owner-only by a second user, injection, secret, bundle, CORS, header and dependency checks pass on the release-candidate commit, and the results are recorded.

**Amended by A1 (2 November 2026):** step 8 adds the AWS checks. The extension routes of step 7 are cut (IMD-65), so their cases skip with that reason.

**Owners and parts**

- Junaid (lead) — Authorization suite re-run and injection corpus (2 points)
- Het — Auth and ownership fixes found by the pass (2 points)
- Kirtan — Security headers and secret-scan review (1 points)
- One branch and pull request per part (`feat/IMP-702-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-144; NFR-011 to NFR-016, NFR-018, NFR-024

**Dependencies:** Prerequisites: IMP-215, IMP-699, IMP-511 · Downstream: IMP-707, IMP-799

**Files**

- apps/api/tests/authz/test_ownership.py (modify); apps/api/tests/authz/test_route_inventory.py (modify); apps/api/tests/authz/test_security_headers.py (modify); apps/api/tests/api/test_injection.py (create); apps/api/tests/fixtures/injection_corpus.json (create); docs/test-reports/security-sprint7.md (create)

**Implementation**

1. Add test_route_inventory.py: load contracts/openapi.v1.json and fail if any operation other than API-01 and API-02 is missing from the ownership matrix in test_ownership.py or does not require a bearer token (TC-344).
2. Extend test_ownership.py so user B calls every owned MVP route (API-03/04 as self only, API-07..38 owned routes, child resources: items, versions, generations) with user A identifiers and receives 404 NOT_FOUND with no A data in the body (TC-345, TC-346); include tampered, expired and wrong-issuer tokens (TC-347) and a body user_id that is rejected with 422 (TC-348, IMD-45).
3. Add test_injection.py: SQL payloads in trip name, notes and place search are stored or searched as text (TC-349); a note with prompt-injection text from injection_corpus.json, run through the pipeline with the MOCK provider, leaves the allowed place set and the computed costs unchanged (TC-357, ACC-15).
4. Extend test_security_headers.py: unknown Origin gets no CORS allow header (TC-351); against staging with make smoke, HTTPS and the security headers of §6 are present (TC-352).
5. Run the CI guard jobs on the candidate commit: secret scan over the full history (TC-354), bundle inspection that only NEXT_PUBLIC_* values are present (TC-355), pip-audit and npm audit with no critical findings (TC-356); assert log lines contain no e-mail, notes text or prompt body (TC-358, TC-025).
6. Record each check with commit SHA, date, command and result in docs/test-reports/security-sprint7.md; open a severity-1 defect for any failure (a failed security item blocks SG-7).
7. Extend the ownership and route-inventory suites to the extension routes API-43 and API-63 to API-75 (owned trips and items return 404 to another user; reference-data context routes require a token), and check that disabled extension switches return 404 (TC-431, TC-432); the route inventory picks up each extension route when its card merges, so the extension cards are not prerequisites of this card (§11.2).
8. AWS checks (Amendment A1 §11):
   - RDS is not reachable from outside the VPC and requires TLS (TC-433);
   - task definitions hold secrets only as SSM references and the images contain no secret (TC-434);
   - the OIDC deploy role trusts only main and v* tags (TC-436);
   - the ECR scan has no critical finding.

   Record each in docs/test-reports/security-sprint7.md.

**Interfaces**

- API: API-03, API-04, API-07..API-38 (owned MVP routes), API-43, API-63, API-64, API-65, API-66, API-67, API-68, API-69, API-70, API-71, API-72, API-73, API-74, API-75 · Tables: trips, itinerary_items, itinerary_versions, ai_generations · Modules: MOD-B02, MOD-B06, MOD-P01 · Env: ALLOWED_ORIGINS · Other: contracts/openapi.v1.json

**Acceptance criteria**

- make test-authz passes and test_route_inventory fails if a new protected route is added without an ownership case (NFR-012, CHK-04)
- TC-344 to TC-351 and TC-353 to TC-358 pass on the candidate commit; TC-352 passes against staging
- No secret in repository history, logs or bundle (CHK-03); CORS and headers verified (CHK-05)
- docs/test-reports/security-sprint7.md lists every check with commit, date and result; nothing is marked passed that was not run
- TC-431 passes: every extension route is in the route inventory and refuses another user's resources with 404.
- TC-433, TC-434 and TC-436 are recorded as passed on AWS staging, or as failed with a severity-1 defect.

**Tests**

- apps/api/tests/authz/test_ownership.py — TC-345, TC-346, TC-347, TC-348 — `make test-authz`
- apps/api/tests/authz/test_route_inventory.py — TC-344 — `make test-authz ARGS='-k inventory'`
- apps/api/tests/api/test_injection.py — TC-349, TC-357 — `make test-api ARGS='-k injection'`
- apps/api/tests/smoke/test_deployed.py — TC-352 — `make smoke URL=<staging API URL>`
- apps/api/tests/authz/test_ownership.py — TC-431, TC-432 — `make test-authz ARGS='-k extension'`

**Completion evidence**

- docs/test-reports/security-sprint7.md; CI run link with guards, audit and test-authz green on the candidate commit; Staging smoke output for TC-352

### IMP-703 Accessibility check on real devices and fixes

**Task:** Sprint 7 (week 7) · HUMAN · 3 points · lead Krrish · release MVP

**Objective:** The core journey has been tested on two real phones and with a screen reader, findings are recorded with severity, critical findings are fixed, and automated axe scans show no critical violations.

**Owners and parts:** Krrish — whole task (3 points); branch `feat/IMP-703-<short>`

**Traces to:** Stories US-126; FR-114, FR-115; NFR-025, NFR-026

**Dependencies:** Prerequisites: IMP-513, IMP-701 · Downstream: IMP-704, IMP-799

**Files**

- docs/test-reports/accessibility-sprint7.md (create); apps/web/components/** (modify); apps/web/tests/unit/** (modify)

**Implementation**

1. Team (Junaid): run the core journey (sign in, create trip, generate, edit, costs, summary) on two real phones (one iOS, one Android, recorded models and browsers) and with one desktop screen reader (TC-382); use the sheet template in docs/test-reports/.
2. Record each finding with page, component, WCAG criterion if known, severity (1-4 per §13) and reproduction steps; do not record findings that were not observed.
3. Claude Code may: generate the observation-sheet template, reproduce a recorded finding in a component test, and implement the fix for each critical (severity 1-2) finding in a separate small PR with a regression test.
4. Run the axe scans in the keyboard and 360 px journeys (from IMP-701) and the Vitest accessibility assertions; fix critical violations (TC-383).
5. Update the report with fixed / open status per finding and owners for open items.

**Interfaces**

- Modules: MOD-F07, MOD-F04 · Components: AppShell, MoveControls, WarningsPanel, ItemEditor, Toast, ConfirmDialog · Other: Real devices, Screen reader

**Acceptance criteria**

- A report exists with the devices, screen reader, date, tester and every observed finding with severity (US-126 AC1)
- Every severity 1 and 2 finding is fixed with a regression test or has an owner and a documented workaround
- The keyboard-only journey (TC-374) and axe scans (TC-383) report no critical violations in CI (US-126 AC2, NFR-025)
- Claude Code produced no finding, result or device observation itself

**Tests**

- apps/web/e2e/journey.spec.ts — TC-373, TC-374, TC-383 — `make e2e ARGS='journey'`
- apps/web/tests/unit/** — regression tests for fixed findings — `make test-web`

**Completion evidence**

- docs/test-reports/accessibility-sprint7.md; PR links of the fixes; CI run with axe results

### IMP-704 Usability session 2 and fixes of the top issues

**Task:** Sprint 7 (week 7) · HUMAN · 3 points · lead Manasvi with Junaid · release MVP

**Objective:** A second moderated usability session with five participants repeats the core journey after the session-1 fixes, the number completing within ten minutes is recorded as measured, and unresolved findings have owners.

**Owners and parts**

- Manasvi (lead) — Usability session 2 and top-issue fixes (2 points)
- Junaid — Session notes and retest (1 points)
- One branch and pull request per part (`feat/IMP-704-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-143; NFR-027, NFR-028

**Dependencies:** Prerequisites: IMP-611, IMP-703 · Downstream: IMP-799

**Files**

- docs/test-reports/usability-session-2.md (create); apps/web/components/** (modify)

**Implementation**

1. Before the session, fix the top findings of session 1 (docs/test-reports/usability-session-1.md) in small PRs with tests; Claude Code may implement these fixes.
2. Team (Manasvi moderates, Junaid takes notes): run the session with five participants on staging using the same tasks and success definition as session 1 (TC-381).
3. Record per participant: completed yes/no, time to itinerary, errors observed, quotes noted by the moderator; record the count completing within ten minutes (NFR-027).
4. Compare with session 1 in a table and list unresolved findings with owners and severity.
5. Claude Code may prepare the task script, consent text template and the results table structure; it must not fill in participant data or invent results.

**Interfaces**

- Modules: MOD-F07 · Other: Staging site

**Acceptance criteria**

- docs/test-reports/usability-session-2.md contains five participant rows with measured outcomes and the date (US-143 AC1)
- The comparison with session 1 and the unresolved-findings list with owners exist (US-143 AC2)
- Fixes made before the session are merged with green CI

**Tests**

- apps/web/e2e/journey.spec.ts — TC-369 — `make e2e ARGS='journey'`

**Completion evidence**

- docs/test-reports/usability-session-2.md; PR links of the fixes

### IMP-705 Final evaluation baseline and cost report

**Task:** Sprint 7 (week 7) · DATA · 1 points · lead Nidhi · release MVP

**Objective:** The evaluation harness has been re-run on the release-candidate commit with MOCK, the rule-based planner and GEMINI, the results are compared with the first baseline, and a cost and latency report cites only recorded runs.

**Amended by A1 (2 November 2026):** step 7 adds the retrieval suite of IMP-318 (FR-140).

**Owners and parts:** Nidhi — whole task (1 points); branch `feat/IMP-705-<short>`

**Traces to:** Stories US-131; FR-120; NFR-004, NFR-039, NFR-041

**Dependencies:** Prerequisites: IMP-514, IMP-699 · Downstream: IMP-706, IMP-799, IMP-804

**Files**

- eval/results/<run_id>/ (create); eval/reports/final-baseline.md (create); docs/test-reports/cost-latency-report.md (create)

**Implementation**

1. Identify the candidate commit (main after IMP-701 and IMP-702 merged) and record its SHA; confirm the dataset version from IMP-310 is unchanged (TC-386).
2. Run make eval PROVIDER=MOCK DATASET=trips/v1 twice and confirm identical metrics (reproducibility, ACC-14).
3. Run the rule-based planner through the same harness and metric code (TC-393).
4. Nidhi runs make eval PROVIDER=GEMINI DATASET=trips/v1 with the protected staging key within the daily cap (TC-392); never in PR CI.
5. Write eval/reports/final-baseline.md comparing with the first baseline (IMP-514): every number links to a run record under eval/results/ (TC-390, TC-397).
6. Write docs/test-reports/cost-latency-report.md: latency, token use and fallback rate taken from run records and ai_generations rows only (TC-396, NFR-041); mark anything unmeasured as "not measured".
7. Run the retrieval suite of IMP-318 on the same commit:
   - make eval DATASET=retrieval/v1 ARGS='--suite retrieval' with MOCK;
   - with GEMINI (staging key, within the cap), run by Nidhi.

   Add recall@6, place hit rate, citation validity and grounding rate to final-baseline.md, each citing its run record (FR-140).

**Interfaces**

- Tables: ai_generations · Modules: MOD-B15, MOD-B05 · Env: GEMINI_API_KEY, GEMINI_MODEL_ID, AI_PROVIDER · Other: eval/datasets/, eval/results/, eval/reports/

**Acceptance criteria**

- Run records for MOCK (two), rule-based (one) and GEMINI (one) exist with dataset version, provider, model id, prompt and schema versions and commit SHA (FR-120, TC-390)
- final-baseline.md compares with the first baseline and every figure cites a run record (US-131 AC1, TC-397)
- The cost and latency report contains no number without a run record (US-131 AC2, NFR-041)
- If the Gemini run could not be made (key, quota), the report says so and no Gemini figure is claimed
- The retrieval metrics of FR-140 are reported for MOCK and, if possible, GEMINI, each with a run record (TC-458)

**Tests**

- apps/api/tests/unit/evaluation/test_metrics.py — TC-388, TC-389 — `make test-unit ARGS='-k evaluation'`
- eval/ (harness run) — TC-386, TC-390, TC-392, TC-393, TC-396 — `make eval PROVIDER=GEMINI DATASET=trips/v1`

**Completion evidence**

- eval/results/<run_id>/ manifests for each run; eval/reports/final-baseline.md; docs/test-reports/cost-latency-report.md

### IMP-706 Stage 2 readiness package (documents only)

**Task:** Sprint 7 (week 7) · HUMAN · 3 points · lead Manya · release MVP

**Objective:** A Stage 2 readiness package (migration-gate criteria draft, data-governance policy, dataset schema, data-card template) is committed under docs/stage2/, marked Proposed, and states that fine-tuning is not part of the eight-week commitment.

**Owners and parts:** Manya — whole task (3 points); branch `feat/IMP-706-<short>`

**Traces to:** Stories US-132

**Dependencies:** Prerequisites: IMP-705 · Downstream: IMP-799

**Files**

- docs/stage2/README.md (create); docs/stage2/migration-gate-criteria.md (create); docs/stage2/data-governance-policy.md (create); docs/stage2/dataset-schema.md (create); docs/stage2/data-card-template.md (create)

**Implementation**

1. Draft migration-gate-criteria.md from blueprint §22 and §33.4 (criteria E1 to E7, evaluation on the same cases and day as the Gemini baseline, rollback rehearsal) and mark every threshold Proposed.
2. Draft data-governance-policy.md: no private user data used for training without a consent process; sources and licences; retention; approval owner (blueprint §18.8).
3. Draft dataset-schema.md (fields of one training example derived from gr-1 input and io-1 output, as a JSON Schema fragment) and data-card-template.md.
4. README.md states: Stage 2 is conditional, not scheduled in weeks 1 to 8, does not change AI_PROVIDER or any MVP code, and starts only after the gates of migration-gate-criteria.md.
5. Claude Code may draft these documents from the blueprint; it must not add training code, export scripts, a fine-tuned adapter, or any claim of training results.

**Interfaces**

- Modules: MOD-B15 · Env: FINETUNED_ENDPOINT_URL, FINETUNED_API_KEY, FINETUNED_MODEL_NAME · Other: contracts/ai/gr-1.schema.json, contracts/ai/io-1.schema.json

**Acceptance criteria**

- All five files exist under docs/stage2/, each marked Proposed with owner and date (US-132 AC1, CHK-23)
- README.md states that fine-tuning is not part of the eight-week commitment (US-132 AC2)
- The PR changes no file outside docs/stage2/ and make check stays green
- TC-361 still passes: no code path exports user data to training files

**Tests**

- existing suites (doc-only change); TC-361 lives with IMP-702 security checks — TC-361 — `make check`

**Completion evidence**

- PR link with docs/stage2/ files only; Reviewer approval by Manasvi

### IMP-707 SRS, architecture, test plan, user guide and deployment guide

**Task:** Sprint 7 (week 7) · HUMAN · 6 points · lead Malhar with Manal, Junaid, Jeel, Kirtan · release MVP

**Objective:** The course document set (SRS, architecture, API specification, test plan) and the user and deployment guides exist in docs/, match the deployed system, and both guides have been followed successfully by a member outside the platform squad.

**Amended by A1 (2 November 2026):** steps 2 and 4 cover the AWS deployment and the RAG pipeline.

**Owners and parts**

- Malhar (lead) — SRS and data model section (2 points)
- Manal — Architecture and API documentation (1 points)
- Junaid — Test plan (1 points)
- Jeel — User guide (1 points)
- Kirtan — Deployment guide (1 points)
- One branch and pull request per part (`feat/IMP-707-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-145, US-146; NFR-022, NFR-027, NFR-032, NFR-033

**Dependencies:** Prerequisites: IMP-701, IMP-702 · Downstream: IMP-799, IMP-804

**Files**

- docs/srs.md (create); docs/architecture.md (create); docs/api.md (create); docs/test-plan.md (create); docs/guides/user-guide.md (create); docs/guides/deployment-guide.md (create); README.md (modify)

**Implementation**

1. Assemble docs/srs.md from this specification §2 and the blueprint; list every difference between documented and built behaviour (US-145 AC2).
2. Export architecture and ER diagrams into docs/architecture.md, including the AWS deployment view and the RAG pipeline (corpus, chunking, embeddings, retrieval, grounding, citations; Amendment A1 §3 and §6); docs/api.md links contracts/openapi.v1.json and the published OpenAPI page (NFR-033); docs/test-plan.md summarises §13 with links to test reports.
3. Write docs/guides/user-guide.md (create trip, generate, edit, costs, labels Estimate/Curated/Unavailable, known limits) with screenshots taken by the team.
4. Write docs/guides/deployment-guide.md, building on docs/guides/aws-setup.md and docs/guides/deployment.md:
   - AWS ECS Express Mode, RDS and SSM, and the auth-only Supabase project (Amendment A1 §4);
   - environment values per Amendment A1 §4.2 and §7.2;
   - the release task (migrations, seed, RAG index);
   - smoke tests and rollback;
   - cost guardrails;
   - the operator account-deletion procedure for NFR-022 (Supabase Auth user plus auth.users row on RDS).
5. Claude Code may draft from the repository and this specification, and must run every command it documents locally before writing it; commands it could not run are marked "not verified".
6. A member outside the platform squad follows README setup (time recorded, NFR-032, TC-335) and the deployment guide on a clean account; record the outcome in docs/progress/sprint-7.md.

**Interfaces**

- API: API-01, API-02 · Modules: MOD-P01 · Other: contracts/openapi.v1.json

**Acceptance criteria**

- Each required document exists in docs/ with owner and version (US-145 AC1)
- The architecture document matches the deployed system or lists the differences (US-145 AC2)
- A member outside the platform squad completed README setup (time recorded) and a clean deployment answered /health (US-146 AC2, CHK-18)
- A new member created a trip and an itinerary from the user guide without help (US-146 AC1)
- make openapi-check is green, so docs/api.md points to a current contract

**Tests**

- contracts/openapi.v1.json — TC-336 — `make openapi-check`
- README.md (setup procedure) — TC-335 — `make setup && make check`

**Completion evidence**

- docs/ files listed above in a merged PR; Onboarding record with elapsed setup time in docs/progress/sprint-7.md; Deployment-guide trial: /health response from the clean deployment

### IMP-708 Natural-language trip intake with confirmation

**Task:** Sprint 7 (week 7) · CODE · 8 points · lead Nidhi with Manya, Manal, Manasvi · release EXT · Extension; switch nl_intake (cut 8 of 9). When disabled the trip wizard is the only way to create a trip.

**Objective:** The traveller can describe a trip in one sentence; Gemini extracts a proposed trip and preferences, every value passes the existing validators, and nothing is saved until the traveller confirms each field and the existing API-07 and API-14 create the trip.

**Owners and parts**

- Nidhi (lead) — extract_trip_request operation (GEMINI, MOCK) (2 points)
- Manya — trip_intake prompt, ti-1 schema and evaluation cases (2 points)
- Manal — Intake endpoint (API-64) with TripIn/PreferencesIn validation (2 points)
- Manasvi — Describe-your-trip screen and confirmation step (2 points)
- One branch and pull request per part (`feat/IMP-708-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-155; FR-128; NFR-021

**Dependencies:** Prerequisites: IMP-212, IMP-303, IMP-301, IMP-613 · Downstream: IMP-799

**Files**

- apps/api/app/trips/router.py (modify); apps/api/app/trips/service.py (modify); apps/api/app/trips/schemas.py (modify); apps/api/app/ai/providers/base.py (modify); apps/api/app/ai/providers/gemini.py (modify); apps/api/app/ai/providers/mock.py (modify); apps/api/app/schemas/ai.py (modify); apps/api/app/ai/prompts/templates/trip_intake/v1/system.txt (create); apps/api/app/ai/prompts/templates/trip_intake/v1/user.txt (create); apps/api/app/ai/prompts/templates/trip_intake/v1/meta.json (create); apps/web/app/(app)/trips/new/describe/page.tsx (create); apps/web/components/trips/DescribeTripForm.tsx (create); apps/web/components/trips/IntakeConfirmation.tsx (create); eval/datasets/intake/v1/cases.jsonl (create); apps/api/tests/api/test_trip_intake.py (create); apps/api/tests/contract/test_provider_contract.py (modify); apps/web/tests/unit/trips/IntakeConfirmation.test.tsx (create); contracts/openapi.v1.json (modify)

**Implementation**

1. Contract first: on day 1 of the sprint the API part declares this card's endpoints with their final shapes (§6) and regenerates contracts/openapi.v1.json with make openapi; handlers return 501 NOT_IMPLEMENTED until built (IMD-37: allowed for extension routes until SG-7), so the screen part starts against the regenerated web client (Team Contribution Plan v2).
2. Add ModelProvider operation extract_trip_request(TripIntakeRequest) -> ProviderResult[TripIntakeOutput] (ti-1, all fields optional) to base.py, GEMINI (structured output) and MOCK (deterministic parse of the SAMPLE phrases); FINETUNED_MODEL stub refuses; export contracts/ai/ti-1.schema.json.
3. Write template trip_intake/v1: the request carries the free text (quoted as data, <= 1,000 chars), today's date in the destination time zone and the supported destination slugs; the model must answer only ti-1 and put anything it cannot map in unresolved.
4. Implement API-64 POST /api/v1/trip-intake: switch and assist cap check (429 AI_QUOTA_REACHED), provider call, then map ti-1 to TripIn and PreferencesIn and run the existing validators field by field; invalid or unsupported values move to unresolved with a message; destination must be a supported slug; return {trip: TripIn-shaped proposal, preferences, unresolved}; write one ai_assist_calls row; write nothing else.
5. Build /trips/new/describe: DescribeTripForm (textarea, examples, privacy notice link) then IntakeConfirmation that shows every extracted field editable, highlights unresolved items, and on Confirm calls API-07 then API-14 exactly like the wizard; a "Switch to the step-by-step form" link prefills TripWizard.
6. Create 15 evaluation cases in eval/datasets/intake/v1 (SAMPLE destinations, dates, party, budget, pace, interests) tagged regression; record field-level accuracy with make eval for MOCK only in CI.
7. Add the switch: Guard with the extension switch 'nl_intake' (IMD-11, EXT): when FEATURES_DISABLED / NEXT_PUBLIC_FEATURES_DISABLED contains 'nl_intake' the routes return 404 NOT_FOUND and the UI entry point is hidden (TC-432).
8. If IMP-613 was switched off before it started, this card creates the ai_assist_calls table (migration 0011_assist_calls) and app/ai/assist_log.py itself, as IMD-60 describes; the first of IMP-708 and IMP-709 to start does it.

**Interfaces**

- API: API-64, API-07, API-14 · Tables: ai_assist_calls, destinations, trips, trip_preferences · Modules: MOD-B03, MOD-B05, MOD-F02 · Components: DescribeTripForm, IntakeConfirmation, TripWizard, PrivacyNotice · Env: AI_DAILY_ASSIST_CALLS_PER_USER, FEATURES_DISABLED, NEXT_PUBLIC_FEATURES_DISABLED, MOCK_PROVIDER_SCENARIO · Other: schema ti-1, prompt template trip_intake/v1

**Acceptance criteria**

- FR-128 AC1-AC3 hold (TC-402 to TC-405).
- API-64 writes no trip or preferences row; only API-07 and API-14 do after confirmation.
- Impossible values (end before start, unsupported destination, budget <= 0) never appear as accepted fields; they are listed in unresolved.
- Each call writes one ai_assist_calls row and counts against the daily assist cap (TC-430).
- With nl_intake disabled API-64 returns 404 and the describe entry point is hidden (TC-432).

**Tests**

- apps/api/tests/api/test_trip_intake.py — TC-402, TC-403, TC-404, TC-430, TC-432 — `make test-api ARGS='-k trip_intake'`
- apps/api/tests/contract/test_provider_contract.py — TC-405 — `make test-contract ARGS='-k intake'`
- apps/web/tests/unit/trips/IntakeConfirmation.test.tsx — new cases — `make test-web ARGS='IntakeConfirmation'`

**Completion evidence**

- PR with make check green; Intake evaluation report for MOCK in eval/reports/; Screenshot of the confirmation step with one unresolved field

### IMP-709 "Why this plan" explanations for each day

**Task:** Sprint 7 (week 7) · CODE · 5 points · lead Nidhi with Het, Manya · release EXT · Extension; switch day_explain (cut 7 of 9). When disabled days show their theme only.

**Objective:** For each day the traveller can request a short AI-written explanation of why its places were grouped and ordered that way; code accepts it only if it names places on that day and states no prices or times, stores it with the plan revision it explains, and labels it AI-written.

**Owners and parts**

- Nidhi (lead) — explain_day operation and text checks (2 points)
- Het — Explanation storage, endpoint (API-65) and AI-labelled display (2 points)
- Manya — day_explanation prompt and evaluation cases (1 points)
- One branch and pull request per part (`feat/IMP-709-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-156; FR-129; NFR-021

**Dependencies:** Prerequisites: IMP-305, IMP-406, IMP-613 · Downstream: IMP-799

**Files**

- apps/api/migrations/sql/0008_day_explanations.sql (create); apps/api/migrations/sql/down/0008_day_explanations.down.sql (create); apps/api/migrations/versions/0008_day_explanations.py (create); apps/api/app/db/models/itinerary.py (modify); apps/api/app/itinerary/router.py (modify); apps/api/app/itinerary/service.py (modify); apps/api/app/itinerary/explanation_check.py (create); apps/api/app/ai/providers/base.py (modify); apps/api/app/ai/providers/gemini.py (modify); apps/api/app/ai/providers/mock.py (modify); apps/api/app/schemas/ai.py (modify); apps/api/app/ai/prompts/templates/day_explanation/v1/system.txt (create); apps/api/app/ai/prompts/templates/day_explanation/v1/user.txt (create); apps/api/app/ai/prompts/templates/day_explanation/v1/meta.json (create); apps/web/components/itinerary/DayExplanation.tsx (create); apps/api/tests/unit/itinerary/test_explanation_check.py (create); apps/api/tests/api/test_day_explanation.py (create); apps/web/tests/unit/itinerary/DayExplanation.test.tsx (create); contracts/openapi.v1.json (modify)

**Implementation**

1. Contract first: on day 1 of the sprint the API part declares this card's endpoints with their final shapes (§6) and regenerates contracts/openapi.v1.json with make openapi; handlers return 501 NOT_IMPLEMENTED until built (IMD-37: allowed for extension routes until SG-7), so the screen part starts against the regenerated web client (Team Contribution Plan v2).
2. Write migration 0008_day_explanations: itinerary_days.explanation (<= 400 chars), explanation_revision, explanation_generated_at; ORM model; drift test green.
3. Add ModelProvider operation explain_day(DayExplanationRequest) -> ProviderResult[DayExplanationOutput] (de-1) to base.py, GEMINI and MOCK; template day_explanation/v1 receives only the saved day: ordered place names, categories, areas and travel minutes; no prices; export contracts/ai/de-1.schema.json.
4. Implement explanation_check.py (pure): reject text over 400 chars, text naming a place not on the day (match against the day's place names and the destination place list), and text containing currency symbols, amounts or clock times (regex); return the reason.
5. Implement API-65 POST .../days/{day_number}/explanation: switch and assist cap check, provider call, check; on pass store explanation with explanation_revision = trips.plan_revision; on rejection store nothing and return 200 with status unavailable and the reason code; log ai_assist_calls; API-24 returns the stored explanation with explanation_current = (explanation_revision equals the current plan_revision); DayExplanation shows a non-current explanation marked out of date with a refresh action (FR-129 AC3, IMD-55).
6. Build DayExplanation under the day header: "Explain this day" button, the text with AiBadge, a "Plan changed - explain again" state when stale, and "Explanation unavailable" on rejection.
7. Add the switch: Guard with the extension switch 'day_explain' (IMD-11, EXT): when FEATURES_DISABLED / NEXT_PUBLIC_FEATURES_DISABLED contains 'day_explain' the routes return 404 NOT_FOUND and the UI entry point is hidden (TC-432).
8. If IMP-613 was switched off before it started, this card creates the ai_assist_calls table (migration 0011_assist_calls) and app/ai/assist_log.py itself, as IMD-60 describes; the first of IMP-708 and IMP-709 to start does it.

**Interfaces**

- API: API-65, API-24 · Tables: itinerary_days, ai_assist_calls, trips, itinerary_items, places · Modules: MOD-B08, MOD-B05, MOD-F04 · Components: DayExplanation, DayColumn, AiBadge · Env: AI_DAILY_ASSIST_CALLS_PER_USER, FEATURES_DISABLED, NEXT_PUBLIC_FEATURES_DISABLED · Other: schema de-1, prompt template day_explanation/v1

**Acceptance criteria**

- FR-129 AC1-AC3 hold (TC-406 to TC-408).
- An explanation naming a place not on the day or stating a price or time is never stored (unit tests on explanation_check).
- After any edit the stored explanation is reported with explanation_current false and shown marked out of date with a refresh action (TC-408).
- The text always carries the AI-written label.
- With day_explain disabled API-65 returns 404 and the button is hidden (TC-432).

**Tests**

- apps/api/tests/unit/itinerary/test_explanation_check.py — TC-406, TC-407 — `make test-unit ARGS='-k explanation'`
- apps/api/tests/api/test_day_explanation.py — TC-408, TC-430, TC-431, TC-432 — `make test-api ARGS='-k day_explanation'`
- apps/web/tests/unit/itinerary/DayExplanation.test.tsx — new cases — `make test-web ARGS='DayExplanation'`

**Completion evidence**

- PR with make check green including the drift test; Screenshot of an explained day with the AI-written label

### IMP-710 Rain-aware day swapping with the Open-Meteo forecast

**Task:** Sprint 7 (week 7) · CODE · 7 points · lead Manal with Malhar, Krrish · release EXT · Extension; switch rain_swap (cut 5 of 9). When disabled no forecast is fetched or shown.

**Objective:** When trip days fall within the 16-day forecast, rainy days are flagged with their probability and, if a rainy outdoor-heavy day can be exchanged with a drier indoor-heavier day without new errors, the traveller is offered that swap and applies it as one edit.

**Owners and parts**

- Manal (lead) — Rain flags, swap suggestion (API-68) and swap edit (API-69) (3 points)
- Malhar — Open-Meteo client and weather cache (2 points)
- Krrish — Forecast banner and swap action (2 points)
- One branch and pull request per part (`feat/IMP-710-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-158; FR-131; NFR-005

**Dependencies:** Prerequisites: IMP-407, IMP-501 · Downstream: IMP-799

**Files**

- apps/api/migrations/sql/0009_weather_cache.sql (create); apps/api/migrations/sql/down/0009_weather_cache.down.sql (create); apps/api/migrations/versions/0009_weather_cache.py (create); apps/api/app/db/models/weather.py (create); apps/api/app/weather/client.py (create); apps/api/app/weather/service.py (create); apps/api/app/weather/repository.py (create); apps/api/app/weather/router.py (create); apps/api/app/itinerary/swap.py (create); apps/api/app/itinerary/router.py (modify); apps/web/components/itinerary/ForecastBanner.tsx (create); apps/web/components/itinerary/SwapDaysDialog.tsx (create); apps/api/tests/unit/weather/test_rain_rules.py (create); apps/api/tests/api/test_weather_swap.py (create); apps/api/.importlinter (modify); apps/web/tests/unit/itinerary/ForecastBanner.test.tsx (create); contracts/openapi.v1.json (modify)

**Implementation**

1. Contract first: on day 1 of the sprint the API part declares this card's endpoints with their final shapes (§6) and regenerates contracts/openapi.v1.json with make openapi; handlers return 501 NOT_IMPLEMENTED until built (IMD-37: allowed for extension routes until SG-7), so the screen part starts against the regenerated web client (Team Contribution Plan v2).
2. Write migration 0009_weather_cache (destination_id, forecast_date PK; precipitation probability max, sum, weather code, temperatures, fetched_at); RLS on, no browser privileges; ORM model; drift test green; add the import-linter rule that only app/weather/client.py makes weather HTTP calls.
3. Implement app/weather/client.py: Open-Meteo forecast for the destination centre (daily precipitation_probability_max, precipitation_sum, weather_code, temperature_2m_max/min, destination timezone), WEATHER_TIMEOUT_S, no key; service caches per destination and date for 3 hours; failure or timeout returns "forecast unavailable" and never blocks the plan; CC BY 4.0 attribution text returned with the data.
4. Implement the rain rules (pure, §9.3.9, IMD-58): outdoor share = share of the day's planned minutes at places with indoor = false (unknown counts as half); a day in the 16-day window is flagged when precipitation probability >= 60 percent and outdoor share >= 50 percent; suggest at most one swap of a flagged day with the in-window day of the lowest rain probability (below 60 percent), only if neither day has a locked item and validating both days on their new dates adds no new error finding; the swap itself is app/itinerary/swap.py.
5. Implement API-68 GET /api/v1/trips/{trip_id}/weather (days outside the 16-day window have in_window false and no forecast) and API-69 POST .../itinerary/swap-days {day_a, day_b, plan_revision} as one edit transaction (recalculate, revalidate, automatic version); locked items -> 422 INVALID_EDIT; stale -> 409 STALE_PLAN.
6. Build ForecastBanner on the itinerary page (probability per day, attribution, "forecast unavailable" state) and SwapDaysDialog showing what moves and the findings after the swap; the traveller decides.
7. Add the switch: Guard with the extension switch 'rain_swap' (IMD-11, EXT): when FEATURES_DISABLED / NEXT_PUBLIC_FEATURES_DISABLED contains 'rain_swap' the routes return 404 NOT_FOUND and the UI entry point is hidden (TC-432). Tests mock Open-Meteo with respx; no live call in CI.

**Interfaces**

- API: API-68, API-69 · Tables: weather_cache, itinerary_days, itinerary_items, places, destinations, trips · Modules: MOD-B16, MOD-B08, MOD-B07, MOD-F04 · Components: ForecastBanner, SwapDaysDialog · Env: WEATHER_TIMEOUT_S, FEATURES_DISABLED, NEXT_PUBLIC_FEATURES_DISABLED · Other: Open-Meteo forecast API (no key, CC BY 4.0)

**Acceptance criteria**

- FR-131 AC1-AC3 hold (TC-413 to TC-416).
- When Open-Meteo times out the itinerary page still loads and shows "forecast unavailable" (respx timeout test).
- A suggested swap never adds an error finding; locked items block the swap with 422 INVALID_EDIT.
- Repeated requests within 3 hours make no new HTTP call (cache test).
- With rain_swap disabled both routes return 404 and the banner is hidden (TC-432).

**Tests**

- apps/api/tests/unit/weather/test_rain_rules.py — TC-413, TC-414 — `make test-unit ARGS='-k rain'`
- apps/api/tests/api/test_weather_swap.py — TC-415, TC-416, TC-431, TC-432 — `make test-api ARGS='-k weather'`
- apps/web/tests/unit/itinerary/ForecastBanner.test.tsx — new cases — `make test-web ARGS='ForecastBanner'`

**Completion evidence**

- PR with make check green including the drift test; Screenshot of a flagged rainy day and the swap preview

### IMP-711 "Today" companion view for trip days

**Task:** Sprint 7 (week 7) · CODE · 3 points · lead Manasvi with Het · release EXT · Extension; switch today_view (cut 4 of 9). When disabled the itinerary page is the only day view.

**Objective:** On a trip day the traveller opens a focused view that shows the current and next stop, the planned departure time and the travel minutes to the next stop, all taken from the stored plan by the backend; no location is tracked.

**Owners and parts**

- Manasvi (lead) — Today view (2 points)
- Het — Today endpoint (API-70) (1 points)
- One branch and pull request per part (`feat/IMP-711-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-159; FR-132; NFR-001

**Dependencies:** Prerequisites: IMP-309, IMP-508 · Downstream: IMP-799

**Files**

- apps/api/app/itinerary/today.py (create); apps/api/app/itinerary/router.py (modify); apps/api/app/itinerary/schemas.py (modify); apps/web/app/(app)/trips/[tripId]/today/page.tsx (create); apps/web/components/itinerary/TodayView.tsx (create); apps/api/tests/unit/itinerary/test_today.py (create); apps/api/tests/api/test_today.py (create); apps/web/tests/unit/itinerary/TodayView.test.tsx (create); contracts/openapi.v1.json (modify)

**Implementation**

1. Contract first: on day 1 of the sprint the API part declares this card's endpoints with their final shapes (§6) and regenerates contracts/openapi.v1.json with make openapi; handlers return 501 NOT_IMPLEMENTED until built (IMD-37: allowed for extension routes until SG-7), so the screen part starts against the regenerated web client (Team Contribution Plan v2).
2. Implement today.py (pure): given the plan of one day and a local date and time, return the current item (start <= time < end), the next item, planned departure = next start minus its travel_from_prev minutes, and status before_first_stop | at_stop | between_stops | day_finished | not_a_trip_day | no_itinerary (TodayOut, §6.5.1).
3. Implement API-70 GET /api/v1/trips/{trip_id}/today?date=&time= (defaults: now in the destination time zone): reads the stored plan only, never recalculates or writes; owned trip else 404.
4. Build /trips/[tripId]/today with TodayView: large current and next stop cards with labelled times, travel label, "Open in map" link from stored coordinates, link back to the full day; refreshes every 60 seconds; phone-first layout; shown as a shortcut on the itinerary page on trip days.
5. The web app displays only values returned by API-70 (no time arithmetic in the browser, CLAUDE.md §4).
6. Add the switch: Guard with the extension switch 'today_view' (IMD-11, EXT): when FEATURES_DISABLED / NEXT_PUBLIC_FEATURES_DISABLED contains 'today_view' the routes return 404 NOT_FOUND and the UI entry point is hidden (TC-432).

**Interfaces**

- API: API-70 · Tables: itinerary_days, itinerary_items, places, trips, destinations · Modules: MOD-B08, MOD-F04, MOD-F05 · Components: TodayView, SourceBadge · Env: FEATURES_DISABLED, NEXT_PUBLIC_FEATURES_DISABLED

**Acceptance criteria**

- FR-132 AC1-AC2 hold (TC-417 to TC-418).
- Outside the trip dates API-70 returns status not_a_trip_day and the view says so.
- No location permission is requested by the page (component test).
- With today_view disabled API-70 returns 404 and the shortcut is hidden (TC-432).

**Tests**

- apps/api/tests/unit/itinerary/test_today.py — TC-417 — `make test-unit ARGS='-k today'`
- apps/api/tests/api/test_today.py — TC-418, TC-431, TC-432 — `make test-api ARGS='-k today'`
- apps/web/tests/unit/itinerary/TodayView.test.tsx — new cases — `make test-web ARGS='TodayView'`

**Completion evidence**

- PR with make check green; Phone-width screenshot of the Today view on a SAMPLE trip with a fixed date and time

### IMP-712 Budget-fit suggestions when a plan is over budget

**Task:** Sprint 7 (week 7) · CODE · 7 points · lead Junaid with Jeel, Krrish · release EXT · Extension; switch budget_fit (cut 3 of 9). When disabled BUDGET_EXCEEDED and the budget alert remain; the traveller edits by hand.

**Objective:** When the estimate is over budget the traveller sees up to three concrete changes (remove or replace items) that bring it under budget while keeping must-visit and locked items, each with the saving and what is lost, and applies one through the ordinary edit endpoints.

**Owners and parts**

- Junaid (lead) — Budget-fit search (3 points)
- Jeel — Budget-fit endpoint (API-71) and apply flow (2 points)
- Krrish — Budget-fit panel (2 points)
- One branch and pull request per part (`feat/IMP-712-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-160; FR-133; NFR-003

**Dependencies:** Prerequisites: IMP-608, IMP-505 · Downstream: IMP-799

**Files**

- apps/api/app/budget/fit.py (create); apps/api/app/budget/router.py (modify); apps/api/app/budget/service.py (modify); apps/api/app/budget/schemas.py (modify); apps/web/components/costs/BudgetFitPanel.tsx (create); apps/api/tests/unit/budget/test_fit.py (create); apps/api/tests/api/test_budget_fit.py (create); apps/web/tests/unit/costs/BudgetFitPanel.test.tsx (create); contracts/openapi.v1.json (modify)

**Implementation**

1. Contract first: on day 1 of the sprint the API part declares this card's endpoints with their final shapes (§6) and regenerates contracts/openapi.v1.json with make openapi; handlers return 501 NOT_IMPLEMENTED until built (IMD-37: allowed for extension routes until SG-7), so the screen part starts against the regenerated web client (Team Contribution Plan v2).
2. Implement fit.py (pure, integer minor units as the budget engine): candidates = removable items (not must-visit, not locked) limited to the 12 costliest by upper price; options = single removal, pair removal, or replacement by a cheaper ranked alternative (reuse the alternatives function of IMP-505); keep suggestions of one or two changes (IMD-59) that bring the estimate (with contingency) at or under budget; order by the smallest loss of ranking score, then the fewest changes, then the largest saving; return at most 3; a two-change suggestion is applied as two edits.
3. Implement API-71 GET /api/v1/trips/{trip_id}/budget-fit: status within_budget (no suggestions) or suggestions with saving (money strings, IMD-05), items affected, ranking loss in words and the edit to apply (API-27 remove or API-29 replace with its payload); nothing is written.
4. Build BudgetFitPanel on the costs page under BudgetAlert: each suggestion with saving, "what you lose" and an Apply button that calls the referenced edit endpoint with plan_revision, then refreshes costs and itinerary queries.
5. Labels: savings computed from curated or estimated ranges carry the same labels as the cost breakdown.
6. Add the switch: Guard with the extension switch 'budget_fit' (IMD-11, EXT): when FEATURES_DISABLED / NEXT_PUBLIC_FEATURES_DISABLED contains 'budget_fit' the routes return 404 NOT_FOUND and the UI entry point is hidden (TC-432).

**Interfaces**

- API: API-71, API-27, API-29, API-33 · Tables: itinerary_items, places, budget_settings, trips, trip_places · Modules: MOD-B09, MOD-B08, MOD-B06, MOD-F06 · Components: BudgetFitPanel, BudgetAlert, CostBreakdown · Env: FEATURES_DISABLED, NEXT_PUBLIC_FEATURES_DISABLED

**Acceptance criteria**

- FR-133 AC1-AC3 hold (TC-419 to TC-421).
- No suggestion removes or replaces a must-visit or locked item.
- Applying a suggestion through API-27 or API-29 brings the API-33 total at or under budget (API test).
- Within budget API-71 returns no suggestions.
- With budget_fit disabled API-71 returns 404 and the panel is hidden (TC-432).

**Tests**

- apps/api/tests/unit/budget/test_fit.py — TC-419, TC-420 — `make test-unit ARGS='-k budget_fit'`
- apps/api/tests/api/test_budget_fit.py — TC-421, TC-431, TC-432 — `make test-api ARGS='-k budget_fit'`
- apps/web/tests/unit/costs/BudgetFitPanel.test.tsx — new cases — `make test-web ARGS='BudgetFitPanel'`

**Completion evidence**

- PR with make check green; Screenshot of an over-budget SAMPLE trip with two suggestions

### IMP-713 Destination and place context cards from Wikivoyage and Wikipedia

**Task:** Sprint 7 (week 7) · CODE · 6 points · lead Malhar with Jeel, Kirtan · release EXT · Extension; switch context_cards (cut 2 of 9). When disabled place details show curated facts only.

**Objective:** Place details and the destination header show a short, attributed introduction from Wikivoyage or Wikipedia, fetched by a background job, cached for 30 days and marked as third-party text that never supplies prices or hours.

**Owners and parts**

- Malhar (lead) — MediaWiki client, attribution and context cache (3 points)
- Jeel — Context endpoints (API-72, API-73) and ContextCard in the drawer (2 points)
- Kirtan — Refresh job schedule, User-Agent and call budget (1 points)
- One branch and pull request per part (`feat/IMP-713-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-161; FR-134; NFR-016

**Dependencies:** Prerequisites: IMP-604 · Downstream: IMP-799

**Files**

- apps/api/migrations/sql/0010_context_cards.sql (create); apps/api/migrations/sql/down/0010_context_cards.down.sql (create); apps/api/migrations/versions/0010_context_cards.py (create); apps/api/app/db/models/context.py (create); apps/api/app/context/client.py (create); apps/api/app/context/service.py (create); apps/api/app/context/repository.py (create); apps/api/app/context/router.py (create); apps/api/app/context/jobs.py (create); apps/api/app/generation/jobs.py (modify); apps/web/components/places/ContextCard.tsx (create); apps/web/components/places/PlaceDetailDrawer.tsx (modify); apps/api/tests/unit/context/test_client.py (create); apps/api/tests/api/test_context.py (create); apps/api/.importlinter (modify); apps/web/tests/unit/places/ContextCard.test.tsx (create); contracts/openapi.v1.json (modify)

**Implementation**

1. Contract first: on day 1 of the sprint the API part declares this card's endpoints with their final shapes (§6) and regenerates contracts/openapi.v1.json with make openapi; handlers return 501 NOT_IMPLEMENTED until built (IMD-37: allowed for extension routes until SG-7), so the screen part starts against the regenerated web client (Team Contribution Plan v2).
2. Write migration 0010_context_cards (subject_type place|destination, subject_id, source wikivoyage|wikipedia, page_title, extract <= 1,200 chars, page_url, licence default CC BY-SA 4.0, retrieved_at, expires_at; unique subject+source); RLS on, no browser privileges; ORM model; drift test green.
3. Implement app/context/client.py (only MediaWiki HTTP here): Wikivoyage page by destination title first, Wikipedia second; places by exact title or GeoData geosearch within 100 m of the stored coordinates; TextExtracts intro as plain text; descriptive WIKI_USER_AGENT header; serial requests; timeout; strip to 1,200 chars on a sentence boundary.
4. Implement jobs.py: refresh cards older than 30 days for active places and destinations, one request at a time, registered in the existing scheduler; on-demand reads never call MediaWiki (cache only).
5. Implement API-72 GET /api/v1/places/{place_id}/context and API-73 GET /api/v1/destinations/{destination_id}/context returning the card with title, extract, source, licence, page_url and retrieved_at, or 404 when none.
6. Build ContextCard in PlaceDetailDrawer and the destination header: "From Wikivoyage/Wikipedia" label, licence and link, retrieved date; never shown in place of curated prices or hours.
7. Add the switch: Guard with the extension switch 'context_cards' (IMD-11, EXT): when FEATURES_DISABLED / NEXT_PUBLIC_FEATURES_DISABLED contains 'context_cards' the routes return 404 NOT_FOUND and the UI entry point is hidden (TC-432). Startup check: WIKI_USER_AGENT must be set in staging and production when the switch is on. Tests mock MediaWiki with respx.

**Interfaces**

- API: API-72, API-73 · Tables: context_cards, places, destinations · Modules: MOD-B17, MOD-B04, MOD-F03 · Components: ContextCard, PlaceDetailDrawer · Env: WIKI_USER_AGENT, FEATURES_DISABLED, NEXT_PUBLIC_FEATURES_DISABLED · Other: MediaWiki API (Wikivoyage, Wikipedia; CC BY-SA 4.0)

**Acceptance criteria**

- FR-134 AC1-AC3 hold (TC-422 to TC-424).
- Every card shows source, licence and link; extracts never contain price or opening-hours fields from the source.
- API-72 and API-73 read the cache only; the refresh job makes serial requests with the configured User-Agent (respx assertion).
- With context_cards disabled both routes return 404 and the card is hidden (TC-432).

**Tests**

- apps/api/tests/unit/context/test_client.py — TC-422, TC-423 — `make test-unit ARGS='-k context'`
- apps/api/tests/api/test_context.py — TC-424, TC-432 — `make test-api ARGS='-k context'`
- apps/web/tests/unit/places/ContextCard.test.tsx — new cases — `make test-web ARGS='ContextCard'`

**Completion evidence**

- PR with make check green including the drift test; Screenshot of a place drawer with an attributed card

### IMP-799 Sprint 7 gate SG-7: release candidate

**Task:** Sprint 7 (week 7) · VERIFY · 2 points · lead Kirtan · release MVP

**Objective:** Sprint 7 gate SG-7 is passed: a release candidate is tagged on a green main, acceptance scenarios ACC-01 to ACC-18 have been re-run on staging, no severity-1 defect is open, and every Sprint 1 to 7 task is done or listed open with an owner.

**Owners and parts:** Kirtan — whole task (2 points); branch `feat/IMP-799-<short>`

**Traces to:** NFR-041, NFR-048

**Dependencies:** Prerequisites: IMP-701, IMP-702, IMP-703, IMP-704, IMP-705, IMP-707, IMP-706, IMP-708, IMP-709, IMP-710, IMP-711, IMP-712, IMP-713 · Downstream: IMP-801

**Files**

- docs/progress/gates.md (modify); docs/acceptance/rc1.md (create); docs/progress/sprint-7.md (modify); docs/test-reports/defects.md (modify)

**Implementation**

1. Check docs/progress/sprint-1.md to sprint-7.md: every IMP task is done with evidence or listed open with owner and due date.
2. Run make check and make e2e on main; confirm the staging deployment of the same commit is green and make smoke URL=<staging> passes.
3. Trigger live-smoke.yml once against staging (Gemini, within cap) and record the outcome; if it fails, record the cause; the gate can pass with the fallback path working (ACC-03) but the failure is listed.
4. Re-run ACC-01 to ACC-18 on staging with the candidate (CHK-21) and record pass/fail per scenario in docs/acceptance/rc1.md; record the High-priority test execution summary (CHK-20).
5. Confirm the final evaluation and cost report (IMP-705) and the document drafts (IMP-707) exist; confirm security items CHK-03 to CHK-05 from IMP-702.
6. If all criteria hold, tag the commit v1.0-rc1 and freeze demo data and prompt version; otherwise record "not passed" with reasons and owners in docs/progress/gates.md.
7. Extension freeze: every extension (IMP-515, IMP-612, IMP-613, IMP-708 to IMP-713) is either done with its tests passing on the candidate commit, or its switch is listed in FEATURES_DISABLED for staging and production; run make e2e ARGS='--grep @ext' with the enabled switches; no extension work merges after the RC tag except severity 1-2 fixes.

**Interfaces**

- API: API-01, API-02 · Modules: MOD-P01 · Env: PROMPT_TEMPLATE_VERSION · Other: .github/workflows/live-smoke.yml, tag v1.0-rc1

**Acceptance criteria**

- docs/progress/gates.md records SG-7 with date, commit SHA and each criterion as met or not met
- ACC-01 to ACC-18 results recorded on staging (CHK-21); no severity-1 defect open (CHK-22)
- Final evaluation report and cost report exist (US-131); document set drafted (US-145, US-146)
- Tag v1.0-rc1 exists on a commit whose CI and staging smoke are green
- No criterion is recorded as met without a linked artefact
- Each extension is recorded as done (tests TC-399 to TC-432 passing) or switched off; the @ext E2E smoke passes for the enabled ones.

**Tests**

- all suites — CHK-13, CHK-20 — `make check`
- apps/web/e2e/*.spec.ts — TC-369, TC-371, TC-375, TC-376 — `make e2e`
- apps/api/tests/smoke/test_deployed.py — E2E-09 — `make smoke URL=<staging API URL>`

**Completion evidence**

- docs/progress/gates.md SG-7 entry; docs/acceptance/rc1.md; Tag v1.0-rc1; CI and staging smoke run links; live-smoke.yml run link

## Sprint 8 (week 8): Release and demonstration — gate SG-8

| Task | Title | Type | Lead | Parts (points) | Prerequisites | Points |
| --- | --- | --- | --- | --- | --- | --- |
| IMP-801 | Production deployment, smoke tests, release-candidate tag, demo script and backup video | VERIFY | Kirtan | Kirtan 4, Nidhi 1 | IMP-799 | 5 |
| IMP-802 | Fix severe defects found in rehearsal (regression-tested) | CODE | Junaid | Junaid 2, Kirtan 1, Nidhi 1, Manasvi 1 | IMP-801 | 5 |
| IMP-803 | Pre-demo checklist | HUMAN | Malhar | Malhar 1, Jeel 1 | IMP-801, IMP-802 | 2 |
| IMP-804 | Final report and presentation | HUMAN | Malhar | Malhar 1, Jeel 1, Manya 1 | IMP-705, IMP-707 | 3 |
| IMP-899 | Sprint 8 gate SG-8: release, demo and submission | VERIFY | Kirtan | Kirtan 1 | IMP-801, IMP-802, IMP-803, IMP-804 | 1 |


### IMP-801 Production deployment, smoke tests, release-candidate tag, demo script and backup video

**Task:** Sprint 8 (week 8) · VERIFY · 5 points · lead Kirtan with Nidhi · release MVP

**Objective:** Production runs the tagged release, production smoke tests pass, and a rehearsed six-minute demo script, a rehearsal log and a backup video exist.

**Amended by A1 (2 November 2026):** production runs on AWS (IMD-99 to IMD-104). Vercel, Render and a hosted Supabase database are not used.

**Owners and parts**

- Kirtan (lead) — Production deployment, smoke tests, RC tag (4 points)
- Nidhi — Demo script and backup video (1 points)
- One branch and pull request per part (`feat/IMP-801-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-147; NFR-005, NFR-009, NFR-021, NFR-035, NFR-037

**Dependencies:** Prerequisites: IMP-799 · Downstream: IMP-802, IMP-803, IMP-899

**Files**

- .github/workflows/deploy-production.yml (modify); docs/demo/demo-script.md (create); docs/demo/rehearsal-log.md (create); docs/demo/README.md (create); docs/release-notes/v1.0-mvp.md (create)

**Implementation**

1. Follow the release routine: check GEMINI_MODEL_ID against the provider model and deprecation pages and record the date (CHK-06); confirm the spending control and daily caps (CHK-07, NFR-037) and the privacy notice (CHK-08).
2. Kirtan takes an RDS manual snapshot of production before migrating and records its name and time (NFR-009, CHK-12; Amendment A1 §5.1).
3. Kirtan creates the production resources on AWS (Amendment A1 §4.1):
   - database travel_production on the RDS instance;
   - SSM parameters under /group12/production/;
   - Express services group12-api-production and group12-web-production;
   - the PRODUCTION_* repository variables;
   - the production web URL in the Supabase Auth redirect list.

   He then deploys from tag v1.0-rc1 with deploy-production.yml (manual approval). The release task runs the auth stub, the migrations, the seed of SEED_DIRS and the RAG index before the services are updated (IMD-103).
4. Run make smoke URL=<production API URL> and make e2e ARGS='--grep @smoke' with BASE_URL=<production web URL>; on failure roll back to the previous release per the deployment guide.
5. Write docs/demo/demo-script.md with the 12 steps of blueprint §31.7 adapted to the features actually shipped (cut-list decisions applied) and the demo accounts and data.
6. Rehearse twice on production after warm-up (TC-377), including the provider-failure path on staging (AI_PROVIDER=MOCK, MOCK_PROVIDER_SCENARIO=timeout, IMD-33) and the rule-based mode on production; log issues with severity in rehearsal-log.md.
7. Nidhi records the backup video of the full flow; docs/demo/README.md records its location and duration (no large binary in Git).
8. Tag v1.0-mvp on the deployed commit and write release notes.

**Interfaces**

- API: API-01, API-02, API-22, API-23 · Modules: MOD-P01, MOD-D01 · Components: FallbackNotice · Env: GEMINI_MODEL_ID, AI_DAILY_GENERATIONS_PER_USER, AI_DAILY_GENERATIONS_GLOBAL, ALLOWED_ORIGINS · Other: AWS ECS Express Mode, RDS travel_production, SSM /group12/production/, auth-only Supabase project (Amendment A1 §4)

**Acceptance criteria**

- Production /health and /health/ready answer with the release version, database ok and provider status (API-01, API-02)
- Production smoke (E2E-09) passes and its output is stored
- The demo runs in about six minutes on the deployed site in rehearsal, with the time measured (US-147 AC1)
- In rehearsal a Gemini failure produces the saved or rule-based plan, and the backup video exists (US-147 AC2, CHK-17)
- A production database export (an RDS manual snapshot) exists from before the deployment (CHK-12)
- Production runs on AWS from the tagged images, budget alerts are active and the task definitions hold no secret values (CHK-24, NFR-049)

**Tests**

- apps/api/tests/smoke/test_deployed.py — E2E-09 — `make smoke URL=<production API URL>`
- apps/web/e2e/smoke.spec.ts — E2E-09, TC-377 — `make e2e ARGS='--grep @smoke'`

**Completion evidence**

- Production smoke output; docs/demo/demo-script.md and rehearsal-log.md with measured times; docs/demo/README.md with video location; Tags v1.0-rc1 and v1.0-mvp; Export location record

### IMP-802 Fix severe defects found in rehearsal (regression-tested)

**Task:** Sprint 8 (week 8) · CODE · 5 points · lead Junaid with Kirtan, Nidhi, Manasvi · release MVP

**Objective:** Every severity-1 and severity-2 defect from the rehearsal log is fixed with a regression test or has a documented workaround, no feature is added, and the journey and smoke tests pass again.

**Owners and parts**

- Junaid (lead) — Triage rehearsal defects and add regression tests (2 points)
- Kirtan — Deployment and configuration fixes (1 points)
- Nidhi — AI pipeline defect fixes (1 points)
- Manasvi — Frontend defect fixes (1 points)
- One branch and pull request per part (`feat/IMP-802-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-150; NFR-006, NFR-048

**Dependencies:** Prerequisites: IMP-801 · Downstream: IMP-803, IMP-899

**Files**

- docs/test-reports/defects.md (modify); apps/api/app/** (modify); apps/web/** (modify); apps/api/tests/** (modify); apps/web/e2e/** (modify)

**Implementation**

1. Triage docs/demo/rehearsal-log.md into docs/test-reports/defects.md with severity 1-4 (§13) and owner.
2. For each severity 1-2 defect: write a failing test that reproduces it first, then fix it in a small PR labelled "fix"; no PR may add a feature or change a contract (feature freeze).
3. Severity 3-4 defects are listed for the final report, not fixed unless trivial and approved by Kirtan.
4. After the last fix, run make check, make e2e ARGS='journey' and make smoke against staging; redeploy production from a new tag only if a fix is needed for the demo, then repeat production smoke.

**Interfaces**

- Modules: MOD-B06, MOD-F04, MOD-P01 · Other: docs/test-reports/defects.md

**Acceptance criteria**

- Every severity 1-2 defect is fixed with a linked regression test or has a documented workaround (US-150 AC1, NFR-006)
- All fix PRs are merged with green CI and none adds a feature (US-150 AC2)
- make check, make e2e ARGS='journey' and staging smoke pass after the last fix
- No severity-1 defect remains open (CHK-22)

**Tests**

- apps/api/tests/** and apps/web/tests/** (new regression tests) — per defect — `make check`
- apps/web/e2e/journey.spec.ts — TC-369 — `make e2e ARGS='journey'`
- apps/api/tests/smoke/test_deployed.py — E2E-09 — `make smoke URL=<staging API URL>`

**Completion evidence**

- docs/test-reports/defects.md with status per defect; PR links with regression tests; Green CI and smoke runs after the last fix

### IMP-803 Pre-demo checklist

**Task:** Sprint 8 (week 8) · HUMAN · 2 points · lead Malhar with Jeel · release MVP

**Objective:** On demo day the pre-demo checklist is completed and recorded with a name and time per step: backend awake, database unpaused, export stored, keys and quotas checked, demo path smoke-tested, local MOCK fallback ready.

**Amended by A1 (2 November 2026):** the RDS instance must be available, an RDS manual snapshot is the export, and CHK-24 and CHK-25 are checked.

**Owners and parts**

- Malhar (lead) — Pre-demo checklist: database reset and fallback drill (1 points)
- Jeel — Pre-demo checklist: data, accounts, sample itineraries (1 points)
- One branch and pull request per part (`feat/IMP-803-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-149; NFR-005, NFR-009

**Dependencies:** Prerequisites: IMP-801, IMP-802 · Downstream: IMP-899

**Files**

- docs/demo/pre-demo-checklist.md (create)

**Implementation**

1. Before demo day, Claude Code may create docs/demo/pre-demo-checklist.md as a template with one row per step and empty "done by / time" columns.
2. On demo day the team: wakes the backend at least 10 minutes before (NFR-005), confirms the RDS instance is available (not stopped), takes an RDS manual snapshot and records its name (NFR-009), checks the Gemini key, model id and remaining quota, and checks the network.
3. Run make smoke URL=<production API URL> and the demo path once; start the local stack with AI_PROVIDER=MOCK on the presenter machine as fallback.
4. Each step is ticked only by the person who did it, with the time; Claude Code must not tick steps or fill times.

**Interfaces**

- API: API-01, API-02 · Modules: MOD-P01, MOD-D01 · Env: AI_PROVIDER · Other: Production deployment, Local stack

**Acceptance criteria**

- The checklist file shows every step with a name and time (US-149 AC2)
- Backend awake, database unpaused and an export stored before the demo (US-149 AC1, CHK-16)
- Production smoke passed on demo day
- CHK-24 and CHK-25 checked: AWS production from the tagged images with budget alerts, and the RAG index built with the retrieval report committed

**Tests**

- apps/api/tests/smoke/test_deployed.py — E2E-09 — `make smoke URL=<production API URL>`

**Completion evidence**

- docs/demo/pre-demo-checklist.md completed on demo day; Smoke output from demo day; Export location

### IMP-804 Final report and presentation

**Task:** Sprint 8 (week 8) · HUMAN · 3 points · lead Malhar with Jeel, Manya · release MVP

**Objective:** The final report and presentation exist, state what was built, cut and not built, and every numeric claim about AI quality, cost or speed links to a recorded run or is removed.

**Owners and parts**

- Malhar (lead) — Final report: data and architecture chapters (1 points)
- Jeel — Presentation slides (1 points)
- Manya — Final report: AI chapter (1 points)
- One branch and pull request per part (`feat/IMP-804-<part>`); the backend, database or AI part merges first

**Traces to:** Stories US-148; NFR-041

**Dependencies:** Prerequisites: IMP-705, IMP-707 · Downstream: IMP-899

**Files**

- docs/final-report.md (create); docs/presentation/ (create); docs/final-report-claims-check.md (create)

**Implementation**

1. Write docs/final-report.md from the document set (IMP-707), the gate records and the test reports; include known limitations, cut-list decisions from SG-4, the manual account-deletion procedure and the Stage 2 position (CHK-19).
2. List every numeric claim in docs/final-report-claims-check.md with the run record or test report it comes from; remove any claim without one (TC-397, NFR-041).
3. Prepare the presentation (Jeel) to fit the slot; it shows the Stage 1 result and states that Stage 2 is conditional and not done.
4. Claude Code may draft sections from repository artefacts and check claims against eval/results/ and docs/test-reports/; it must not invent results, participant feedback or measurements.

**Interfaces**

- Other: eval/reports/, docs/test-reports/, docs/progress/gates.md

**Acceptance criteria**

- Every numeric claim in the report and slides appears in the claims check with a linked record (US-148 AC1, TC-397)
- The presentation fits the time slot in rehearsal and states the Stage 2 position honestly (US-148 AC2)
- Known limitations and what was not built are stated (CHK-19)

**Tests**

- docs/final-report-claims-check.md — TC-397 — `manual review by Junaid (no automated command)`

**Completion evidence**

- docs/final-report.md; Presentation file; docs/final-report-claims-check.md reviewed by Junaid

### IMP-899 Sprint 8 gate SG-8: release, demo and submission

**Task:** Sprint 8 (week 8) · VERIFY · 1 points · lead Kirtan · release MVP

**Objective:** Sprint 8 gate SG-8 is passed: the tagged release is running in production, the demo has been given or is ready with all backups, the final checklist CHK-01 to CHK-23 is closed or has recorded exceptions, and the submission is complete.

**Owners and parts:** Kirtan — whole task (1 points); branch `feat/IMP-899-<short>`

**Traces to:** NFR-005

**Dependencies:** Prerequisites: IMP-801, IMP-802, IMP-803, IMP-804 · Downstream: none

**Files**

- docs/progress/gates.md (modify); docs/acceptance/final-checklist.md (create); docs/progress/sprint-8.md (modify)

**Implementation**

1. Confirm the release candidate was tagged before rehearsal and production runs v1.0-mvp (CHK-02 freeze respected).
2. Confirm the pre-demo checklist (IMP-803) is complete, the backup video exists and the saved sample itineraries and fallback work with the provider switched off (CHK-17).
3. Walk CHK-01 to CHK-23 in docs/acceptance/final-checklist.md: each item done with an evidence link or an exception with owner and note in the final report; a failed security item blocks the release.
4. Confirm submission artefacts: repository tag, final report, presentation, document set, test reports, evaluation report.
5. Record SG-8 in docs/progress/gates.md with date and outcome.

**Interfaces**

- API: API-01, API-02 · Modules: MOD-P01 · Other: tag v1.0-mvp

**Acceptance criteria**

- docs/acceptance/final-checklist.md lists CHK-01 to CHK-23 each with evidence or a recorded exception
- No open severity-1 defect and no failed security item (CHK-03, CHK-04, CHK-05, CHK-22)
- Backup video, saved samples and pre-demo checklist exist (US-147, US-149)
- SG-8 is recorded in docs/progress/gates.md with date and evidence links

**Tests**

- apps/api/tests/smoke/test_deployed.py — E2E-09 — `make smoke URL=<production API URL>`

**Completion evidence**

- docs/acceptance/final-checklist.md; docs/progress/gates.md SG-8 entry; Submission confirmation

## Optional Tier 1 items (not scheduled; a full card is required before any is started)

| ID | Stories | Title | Requirements | Entry condition |
| --- | --- | --- | --- | --- |
| OPT-01 | US-033 | Suggest nearby places | FR-021 | SG-7 passed, no open severity-1/2 defect, team decision recorded |
| OPT-02 | US-096 | Generate a packing checklist | FR-088 | SG-7 passed, no open severity-1/2 defect, team decision recorded |
| OPT-03 | US-098 | Track bookings with a checklist | FR-090 | SG-7 passed, no open severity-1/2 defect, team decision recorded |
| OPT-04 | US-099 | Suggest weather-aware clothing | FR-091 | SG-7 passed, no open severity-1/2 defect, team decision recorded |
| OPT-05 | US-105 | Record booking links and confirmation references | FR-110 | SG-7 passed, no open severity-1/2 defect, team decision recorded |
| OPT-06 | US-106 | Record place feedback | FR-111 | SG-7 passed, no open severity-1/2 defect, team decision recorded |
| OPT-07 | US-107 | Record saved and rejected signals | FR-112 | SG-7 passed, no open severity-1/2 defect, team decision recorded |
| OPT-08 | US-112 | Export to PDF through the print view | FR-097 | SG-7 passed, no open severity-1/2 defect, team decision recorded |
| OPT-09 | US-113 | Share a read-only view | FR-098 | SG-7 passed, no open severity-1/2 defect, team decision recorded |

