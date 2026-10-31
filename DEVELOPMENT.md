# AI Travel Planner

A web app where a signed-in traveller describes a trip and gets a day-wise, costed, editable itinerary. The plan is proposed from a shortlist of curated places, then every place, time, travel gap and price is validated and recalculated by the backend; a rule-based planner takes over when the AI provider fails.

The binding details are in [docs/spec/IMPLEMENTATION_SPEC.md](docs/spec/IMPLEMENTATION_SPEC.md); the working rules for contributors are in [CLAUDE.md](CLAUDE.md).

## Prerequisites

- Git
- Docker (with Docker Compose)
- Supabase CLI
- Python 3.12 (pinned in `.python-version`)
- Node LTS (pinned in `.nvmrc`) with npm
- GNU Make

Exact versions in use are recorded in [docs/decisions/versions.md](docs/decisions/versions.md).

## Quick start

Run everything from the repository root:

```bash
make setup        # API virtual environment and web packages (ARGS=--with-browsers also installs Playwright Chromium)
make stack-up     # local Supabase stack: auth and Postgres
make db-up        # plain Postgres for backend tests
make db-migrate   # apply the migrations
make seed         # load the SAMPLE fixture destination
make api          # API on http://localhost:8000
make web          # web app on http://localhost:3000
```

Before opening a pull request, run `make check`. `make help` lists every target. A target whose code has not been built yet prints `not yet implemented (IMP-xxx)` naming the task that adds it, and exits 0.

Environment variable names and placeholders live only in `.env.example`; real values go in untracked `apps/api/.env` and `apps/web/.env.local`.

## Layout

| Path | Contents |
| --- | --- |
| `apps/api/` | FastAPI backend: `app/` modules, `tests/` suites, migrations |
| `apps/web/` | Next.js web app (App Router in `app/`) |
| `contracts/` | Generated OpenAPI contract and AI JSON Schemas |
| `data/` | SAMPLE fixture destination and curated destinations |
| `docs/` | Specification, progress records, decisions, guides, test reports, acceptance |
| `eval/` | Evaluation datasets, results and reports |
| `.github/` | CI and deployment workflows, pull request template, CODEOWNERS |
