# Sprint 1 index (week 1): Foundation and contracts — gate SG-1

One line per task part of Sprint 1 (task register). Evidence lives in the part records under `docs/progress/parts/`; the gate card IMP-199 compiles this index from them. Status values: todo, in progress, PR open, draft PR open, merged, done, blocked.

Compiled by IMP-199 (RUN-017) on 2 November 2026 from the part records on `main` at `887e25e`. Gate result: see [gates.md, SG-1](gates.md#sg-1-end-of-week-1-runnable-skeleton-and-contracts-in-place-imp-199).

| Task | Title | Part | Owner | Points | Part record | Status | Points credited | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IMP-101 | Repository skeleton, toolchain, Makefile, CLAUDE.md and docs/progress folders | Repo tree, Makefile, toolchain pins, CLAUDE.md, progress folders (repo-tree-makefile) | Kirtan (lead) | 2 | IMP-101-repo-tree-makefile.md | merged (PR #1, RUN-001) | 2 | [record](parts/IMP-101-repo-tree-makefile.md) |
| IMP-101 | Repository skeleton, toolchain, Makefile, CLAUDE.md and docs/progress folders | API pyproject (ruff, mypy, pytest) and test socket guard (api-pyproject-guard) | Het | 1 | IMP-101-api-pyproject-guard.md | merged (PR #2, RUN-002) | 1 | [record](parts/IMP-101-api-pyproject-guard.md) |
| IMP-102 | CI workflow (lint, types, imports, unit, guards, audit), branch protection, PR template, CODEOWNERS | Whole task | Kirtan | 2 | IMP-102-whole-task.md | merged (PR #3, RUN-003 and RUN-003b) | 2 | [record](parts/IMP-102-whole-task.md) |
| IMP-103 | Backend skeleton: app factory, typed settings with start-up checks, error envelope, basic GET /health | Whole task | Manal | 2 | IMP-103-whole-task.md | merged (PR #190, RUN-004) | 2 | [record](parts/IMP-103-whole-task.md) |
| IMP-104 | Web skeleton: Next.js app, Tailwind and shadcn/ui, responsive AppShell, query provider, state components | Whole task | Manasvi | 5 | IMP-104-whole-task.md | merged (PR #192, RUN-006) | 5 | [record](parts/IMP-104-whole-task.md) |
| IMP-105 | Local environments: Supabase CLI stack, docker compose db, .env.example and env templates | Whole task | Malhar | 1 | IMP-105-whole-task.md | merged (PR #191, RUN-005); TC-335 measured: about 100 minutes, target 60 (NFR-032 target not met) | 1 | [record](parts/IMP-105-whole-task.md); TC-335 below |
| IMP-106 | MVP migrations 0001-0006 through Alembic, ORM models, schema-drift test, test database fixture | SQL migrations 0001-0006 through Alembic, constraints and indexes (sql-migrations) | Malhar (lead) | 3 | IMP-106-sql-migrations.md | merged (PR #193, RUN-007) | 3 | [record](parts/IMP-106-sql-migrations.md) |
| IMP-106 | MVP migrations 0001-0006 through Alembic, ORM models, schema-drift test, test database fixture | ORM models, schema-drift test, test database fixture (orm-drift-fixture) | Jeel | 2 | IMP-106-orm-drift-fixture.md | merged (PR #193, RUN-007) | 2 | [record](parts/IMP-106-orm-drift-fixture.md) |
| IMP-107 | SAMPLE fixture destination and minimal seed command | Whole task | Jeel | 2 | IMP-107-whole-task.md | merged (PR #197, RUN-011) | 2 | [record](parts/IMP-107-whole-task.md) |
| IMP-108 | Backend token verification and CurrentUser dependency, test token helper | Whole task | Het | 2 | IMP-108-whole-task.md | merged (PR #196, RUN-010) | 2 | [record](parts/IMP-108-whole-task.md) |
| IMP-109 | Sign-up, sign-in, sign-out and AuthGuard with Supabase Auth | Whole task | Krrish | 4 | IMP-109-whole-task.md | merged (PR #194, RUN-008 and RUN-008b) | 4 | [record](parts/IMP-109-whole-task.md) |
| IMP-110 | ModelProvider interface, shared AI schemas gr-1 and io-1, provider error types | Whole task | Nidhi | 5 | IMP-110-whole-task.md | merged (PR #195, RUN-009) | 5 | [record](parts/IMP-110-whole-task.md) |
| IMP-111 | Versioned prompt-template registry | Whole task | Manya | 2 | IMP-111-whole-task.md | merged (PR #198, RUN-012) | 2 | [record](parts/IMP-111-whole-task.md) |
| IMP-112 | Hello-world deployment to Vercel, Render and Supabase staging with deploy workflows | Whole task | Kirtan | 5 | IMP-112-whole-task.md | merged (PR #202, RUN-016): local half (image, smoke, workflows that skip) done; **hosted half blocked by IMP-113, owner Kirtan, 2026-11-02** | 5 provisional (hosted acceptance criteria AC1, AC3 and the staging half of AC2 not verified) | [record](parts/IMP-112-whole-task.md) |
| IMP-113 | Provision accounts, keys and email sender with named owners | GitHub, Vercel, Render, Supabase accounts and secrets register (accounts-secrets-register) | Kirtan (lead) | 1 | IMP-113-accounts-secrets-register.md | merged as template (PR #200, RUN-014, merged 2026-11-02 08:51 UTC); outcome pending member (Kirtan) | 0 (pending outcome) | [record](parts/IMP-113-accounts-secrets-register.md) |
| IMP-113 | Provision accounts, keys and email sender with named owners | OpenRouteService key and email sender (ors-email-sender) | Junaid | 1 | IMP-113-ors-email-sender.md | merged as template (PR #200, RUN-014); outcome pending member (Junaid) | 0 (pending outcome) | [record](parts/IMP-113-ors-email-sender.md) |
| IMP-113 | Provision accounts, keys and email sender with named owners | Gemini API key, model ID and data-use terms (gemini-key-terms) | Nidhi | 1 | IMP-113-gemini-key-terms.md | merged as template (PR #200, RUN-014); outcome pending member (Nidhi) | 0 (pending outcome) | [record](parts/IMP-113-gemini-key-terms.md) |
| IMP-114 | Stakeholder interviews round 1 and recorded findings | Run stakeholder interviews round 1 | Junaid (lead) | 2 | | draft PR open (#201), pending member | 0 | PR #201 |
| IMP-114 | Stakeholder interviews round 1 and recorded findings | Interview guide and recorded findings | Krrish | 1 | | draft PR open (#201), pending member | 0 | PR #201 |
| IMP-115 | Seed-data plan and choice of the two demo destinations | Whole task | Malhar | 3 | | draft PR open (#199), pending member | 0 | PR #199 |
| IMP-199 | Sprint 1 gate SG-1: runnable skeleton and contracts in place | Whole task | Kirtan | 0 | IMP-199-whole-task.md | PR open (RUN-017) | 0 | [record](parts/IMP-199-whole-task.md) |

**Points.** Sprint 1 plans 47 points over 21 parts. Credited at this gate: 38 (including IMP-112's 5, provisional). Pending: IMP-113 3, IMP-114 3, IMP-115 3.

## Human results recorded by the operator

- **IMP-105 TC-335 (setup-guide walkthrough):** Nidhi followed `docs/guides/local-setup.md` on 1 November 2026 and took about 100 minutes. Target 60 minutes (NFR-032): **target not met**; result recorded as measured. Carry-over to the guide owner (Malhar), see gates.md SG-1.

## Board and branch protection (IMP-102 follow-up)

- Board: 183 issues (one per part) on https://github.com/users/het-lathiya/projects/1. After this gate: 141 open, 42 closed; the 26 extension issues were closed as "not planned" under IMD-65.
- Branch protection on `main`: saved but not enforced on this plan (PD-K). The working agreement of IMD-68 applies instead; the SG-1 audit is in gates.md.
