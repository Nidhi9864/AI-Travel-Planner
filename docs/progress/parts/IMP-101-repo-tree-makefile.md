# IMP-101 · repo-tree-makefile part

- Run id: RUN-001
- Owner: Kirtan (kirtan-S111)
- Status: PR_OPEN
- Base commit: 19072f2
- Branch: feat/IMP-101-repo-tree-makefile
- Reviewer: Junaid (Junaid-Kureshi)
- Traces to: US-001; NFR-032, NFR-033
- Card steps built: 1, 2, 4, 5, 7, 8, 10. Steps 3, 6 and 9 belong to Het's api-pyproject-guard part, which is built on top of this one.

## Changed files

- `docs/spec/` (created): the operator's set, committed unchanged: IMPLEMENTATION_SPEC.md, TASK_REGISTER.md, DECISION_REGISTER.md, TRACEABILITY_MATRIX.md, SPRINT_EXECUTION_GUIDE.md, ORCHESTRATOR_PROMPT.md, FRONTEND_UI_BUILDER_ADDENDUM.md, `sql/0001`–`0010`, `sql/test_auth_stub.sql`, `sql/down/0001`–`0010` (29 files with CLAUDE.md)
- `CLAUDE.md` (created, unchanged)
- `Makefile` (created)
- `README.md` (modified: the initial commit held only the title line; replaced by the quick start of step 8)
- `.editorconfig`, `.gitignore`, `.pre-commit-config.yaml`, `.nvmrc`, `.python-version` (created)
- `.claude/settings.json`, `.claude/README.md` (created)
- `docs/decisions/versions.md` (created)
- Purpose notes (created): `apps/README.md`, `apps/api/README.md`, `apps/api/tests/README.md`, `apps/api/tests/{unit,contract,api,authz,smoke,fixtures}/README.md`, `contracts/README.md`, `data/README.md`, `data/fixtures/README.md`, `data/places/README.md`, `docs/README.md`, `docs/{progress,decisions,guides,test-reports,acceptance}/README.md`, `eval/README.md`, `eval/{datasets,results,reports}/README.md`, `.github/workflows/README.md`
- Python packages with a one-line docstring (created): `apps/api/app/__init__.py` and `apps/api/app/{core,auth,trips,places,ai,generation,validation,itinerary,budget,routing,evaluation,schemas}/__init__.py`
- `apps/web/` (created): `package.json`, `package-lock.json`, `tsconfig.json`, `next.config.ts`, `eslint.config.mjs`, `.gitignore`, `README.md`, `app/{layout.tsx,page.tsx,globals.css,favicon.ico}`, `public/*.svg`
- `docs/progress/sprint-1.md`, `docs/progress/gates.md`, `docs/progress/parts/README.md`, this record (created)

## Commands run

| Command | Result line (quoted exactly) |
| --- | --- |
| `sha256sum --quiet -c <saved sums>` (CLAUDE.md and the 28 docs/spec files, after the commits; also compared against the committed blobs) | no output, exit 0 (no mismatch) |
| `diff` of CLAUDE.md against the §12.1 block of IMPLEMENTATION_SPEC.md (extracted from the line after the heading text to the closing fence) | `1,2d0` — only the blank line and the opening `~~~~markdown` fence differ; the 165 lines of the file are identical |
| `make setup && make lint && make typecheck && make imports` (TC-335, after deleting apps/web/node_modules) | `imports: not yet implemented (IMP-101 api-pyproject-guard part)`; exit 0 |
| `for t in <26 targets of §4.7>; do make -n $t >/dev/null 2>&1 \|\| echo "FAIL $t"; done` | no `FAIL` line printed (26 targets) |
| `make test` | `No test files found, exiting with code 0` (vitest); exit 0 |
| `make check` | `No test files found, exiting with code 0` (vitest); exit 0 |
| `make web`, then `curl -w '%{http_code}' http://localhost:3000/` | `200`; dev log `✓ Ready in 474ms` |
| key-pattern grep over the 63 added files outside docs/spec (Gemini, OpenAI-style, GitHub, AWS, Slack, JWT, private key, credentialed connection string, quoted secret assignments) | no match |
| `npm audit` (apps/web) | `16 moderate severity vulnerabilities`; `npm audit --omit=dev`: `found 0 vulnerabilities` |

## Not run

| Command | Reason |
| --- | --- |
| API half of `make setup`, `make lint`, `make typecheck`, `make imports` | Prints `not yet implemented (IMP-101 api-pyproject-guard part)`; runs once Het's `apps/api/pyproject.toml` and `.importlinter` land |
| `make test-unit`, `make test-contract`, `make test-api`, `make test-authz`, `make live-smoke` | Same message (pytest arrives with Het's part) |
| `make stack-up`, `make stack-down`, `make db-up`, `make db-down` | `not yet implemented (IMP-105)` |
| `make db-migrate`, `make db-reset` | `not yet implemented (IMP-106)` |
| `make seed` | `not yet implemented (IMP-107)` |
| `make api` | `not yet implemented (IMP-103)` |
| `make e2e` | `not yet implemented (IMP-216)` |
| `make openapi` / `make openapi-check` | `not yet implemented (IMP-110, IMP-214)` / `not yet implemented (IMP-214)` |
| `make eval` | `not yet implemented (IMP-413)` |
| `make smoke` | `not yet implemented (IMP-112)` |
| `make setup ARGS=--with-browsers` | Playwright browser install is optional and not run in this part (narrowing note c) |
| `pre-commit install` / `pre-commit run` | Not installed on purpose: hooks belong to IMP-102 and installing would replace the local commit-msg guard (note f) |

## Acceptance criteria

| Criterion | Status | How |
| --- | --- | --- |
| Card 1 (web half): `make setup` exits 0 and creates apps/web/node_modules | verified | TC-335 run above from a deleted node_modules; directory present afterwards |
| Card 1 (API half): `make setup` creates apps/api/.venv | not verified | Belongs to Het's api-pyproject-guard part |
| Card 2 (web half): `make lint`, `make typecheck`, `make imports` exit 0 | verified | TC-335 exit 0; ESLint, Prettier and `next typegen && tsc --noEmit` ran |
| Card 2 (API half): ruff, mypy, lint-imports | not verified | Belongs to Het's part; the targets print the pending message |
| Card 3: every §4.7 target exists | verified | `make -n` loop over the 26 targets printed no `FAIL` line |
| Card 4: CLAUDE.md equals §12.1; sprint-1.md lists IMP-101..IMP-199 | verified | sha256 match and diff against §12.1; sprint-1.md has one todo line per part of IMP-101 to IMP-115 and IMP-199 |
| Card 5: no real secret or non-placeholder key | not verified | Key-pattern grep found nothing; the full check is TC-354 in IMP-102 |
| Card 6: socket guard | not verified | Belongs to Het's part |
| Card 7: attribution empty; core.hooksPath guarded by a .githooks check | verified | `.claude/settings.json` has `"commit": ""` and `"pr": ""`; `make -n setup` prints `if [ -d .githooks ]; then git config core.hooksPath .githooks ...` |
| NFR-033: every created directory has its one-line purpose | verified | README.md or package docstring in each directory listed above; see open issues for `.github/` and the generator folders |

## Blockers

None.

## Proposed decisions

- PD-A (Makefile working directory): the API commands run from `apps/api` (`cd apps/api && .venv/bin/<tool> ...`) instead of passing `apps/api` paths from the root, so that ruff, mypy, pytest and lint-imports find `apps/api/pyproject.toml` and `.importlinter`. The behaviour matches §4.7; only the working directory differs.
- PD-B (optional browser flag): §4.7 names an optional flag for the Playwright browser install without naming it. This part uses `make setup ARGS=--with-browsers`, so no new Make or environment variable name is introduced.
- PD-C (web typecheck script): the card names `tsc --noEmit`; the script is `next typegen && tsc --noEmit`, because Next.js 16 declares global route types (`LayoutProps`) only in generated files, and `tsc` alone fails on a clean clone.

## Open issues

- `@types/node` was raised from the generator's `^20` to `^22` (Node 22 is the pinned runtime) because vitest 5 requires `@types/node` 22 or newer.
- `apps/web/next.config.ts` sets `agentRules: false`: without it `next dev` writes an `apps/web/AGENTS.md` instruction file (note b: the root CLAUDE.md is the only instruction file).
- The generator's `apps/web/.gitignore` ignored `.env*`, which would also hide an `.env.example`; it now ignores `.env` and `.env.*` and keeps `.env.example`, like the root `.gitignore`.
- `.github/` has no README.md of its own, because GitHub would show `.github/README.md` as the repository front page in place of the root README; `.github/workflows/README.md` and the root README layout table describe the folder.
- `apps/web/app/` and `apps/web/public/` are generator folders and are described in `apps/web/README.md`; a README inside `public/` would be served as a static file.
- `npm audit`: 16 moderate advisories, all in the dev-only `minimatch` pulled in by ESLint; production dependencies have none. IMP-102 sets the audit threshold.
- Make targets added beyond §4.7: `help` (default goal, prints the target list). No §4.7 target was renamed.
- The PR is opened from the operator's GitHub account (`het-lathiya`); the commits are authored and committed by Kirtan.
