# Deployment: staging and production (IMP-112)

- **Card:** IMP-112 · Hello-world deployment to Vercel, Render and Supabase staging with deploy workflows (US-002; FR-123; NFR-005, NFR-015, NFR-035)
- **Owner:** Kirtan (DevOps Engineer and Integration Lead)
- **Status:**
  - The local container path works.
  - The hosted steps (sections 3 to 5 and 7) are **blocked by IMP-113 (owner Kirtan)**: the Supabase staging project and the Render account do not exist yet (as of 2026-11-02).
  - Both deploy workflows skip until their secrets exist.

| Part | Where it runs | How it is deployed |
| --- | --- | --- |
| Web app (`apps/web`) | Vercel: production, staging and pull-request previews | Vercel's GitHub integration builds every push |
| API (`apps/api/Dockerfile`) | Render web service (Docker), staging and production | Render deploy hook, called by `deploy-staging.yml` and `deploy-production.yml` |
| Database and Auth | Supabase staging project; production per OD-15 | Migrations from the deploy workflows (`make db-migrate`), never on container start (IMD-38) |

## 1. The API image

`apps/api/Dockerfile` builds the production image:

- **Base and install:** `python:3.12-slim` with a normal (non-editable) wheel install of `apps/api`, so the prompt templates ship as package data (IMP-111).
- **Contents:** no dev extras, tests or migrations.
- **User:** a non-root user (`app`, uid 10001).
- **Command:** `uvicorn app.main:app` on `${PORT:-8000}`. Render sets `PORT`.
- **Version:** `/health` reports `BUILD_VERSION`. When that is not set, the start command uses Render's `RENDER_GIT_COMMIT`, the deployed commit, and locally it falls back to `dev`. The deploy workflows wait for this value.
- **No migrations on start:** the container never runs migrations (IMD-38).
- **Bad configuration:** the API refuses to start on a bad configuration and names the variable, never its value (FR-124).

### Local container run (the card's path while the accounts are missing)

From the repository root:

```sh
make db-up
psql "postgresql://postgres:postgres@localhost:5432/travel_test" -v ON_ERROR_STOP=1 \
  -f apps/api/migrations/sql/test_auth_stub.sql      # plain PostgreSQL only, never Supabase
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/travel_test make db-migrate
```

The `api` service of `docker-compose.yml` sits behind the `api` profile, and its `apps/api/.env` file is optional (IMP-105). To pass non-secret local values without an env file, use a compose override file outside the repository:

```yaml
services:
  api:
    environment:
      APP_ENV: local
      AI_PROVIDER: MOCK
      DATABASE_URL: postgresql+psycopg://postgres:postgres@db:5432/travel_test
      ALLOWED_ORIGINS: http://localhost:3000
    depends_on:
      db:
        condition: service_healthy
```

Then run:

```sh
docker compose -f docker-compose.yml -f <override file> --profile api up -d --build api
make smoke URL=http://localhost:8000 ARGS='--web-origin http://localhost:3000'
docker compose --profile api down   # stops api and db
```

## 2. Deploy secrets (GitHub Actions secrets store)

The deploy workflows read only these repository secrets. GitHub masks them in logs, and the workflows never print them. Their rows in `docs/secrets.md` are added by IMP-113's follow-up run (owner, store and rotation rule). This file never holds a value.

| Secret | Purpose | Used by |
| --- | --- | --- |
| `STAGING_DATABASE_URL` | Connection string of the Supabase staging database, for `make db-migrate` before each deploy | `deploy-staging.yml` |
| `STAGING_RENDER_DEPLOY_HOOK_URL` | Deploy hook URL of the Render staging service (from Render: Settings, Deploy Hook) | `deploy-staging.yml` |
| `STAGING_API_URL` | Base URL of the staging API on Render, for the version wait and `make smoke` | `deploy-staging.yml` |
| `STAGING_WEB_ORIGIN` | Origin of the staging web app on Vercel (scheme and host, no path), for the CORS allow check in `make smoke` | `deploy-staging.yml` |
| `PRODUCTION_DATABASE_URL` | Connection string of the production database (OD-15) | `deploy-production.yml` |
| `PRODUCTION_RENDER_DEPLOY_HOOK_URL` | Deploy hook URL of the Render production service | `deploy-production.yml` |
| `PRODUCTION_API_URL` | Base URL of the production API | `deploy-production.yml` |
| `PRODUCTION_WEB_ORIGIN` | Origin of the production web app | `deploy-production.yml` |

`STAGING_API_URL`, `STAGING_WEB_ORIGIN` and their production pairs are not secret. They are kept in the secrets store so that each workflow checks a single set of four values.

## 3. Render web service (card step 2), blocked by IMP-113 (owner Kirtan)

When the Render account exists:

1. **GitHub access:** ask the repository owner (het-lathiya) to approve Render's GitHub access to `het-lathiya/Group12`. Only the owner can approve it (`docs/decisions/accounts.md`).
2. **Create the service:** a **Web Service** from the repository, with:
   - runtime **Docker**;
   - root directory `apps/api` and Dockerfile path `apps/api/Dockerfile`;
   - branch `main`;
   - health check path `/health`.
3. **Auto-deploy: off.** The deploy workflow triggers each deploy through the hook after the migrations, so the schema is always ahead of the code (IMD-38).
4. **Environment variables** in the Render dashboard (values from the password manager, never from this repository):
   - `APP_ENV=staging`;
   - `DATABASE_URL`: the staging Supabase connection string;
   - `SUPABASE_URL`;
   - `SUPABASE_JWKS_URL` or `SUPABASE_JWT_SECRET`, per OD-06 (both are implemented, IMD-04);
   - `ALLOWED_ORIGINS`: the exact staging web origin (NFR-015);
   - `AI_PROVIDER=MOCK` until Sprint 3;
   - leave `BUILD_VERSION` unset, so `/health` reports the deployed commit.
5. **Store the four staging secrets** of section 2 in the GitHub Actions secrets store: the deploy hook URL, the API URL, the web origin and the staging database connection string.

## 4. Vercel project (card step 3), blocked by IMP-113 (owner Kirtan)

The Vercel account exists, but the API URL and the Supabase staging values it needs do not yet.

1. **GitHub access:** the Vercel GitHub app's access to `het-lathiya/Group12` is approved by het-lathiya.
2. **Import the project:** import `het-lathiya/Group12` with root directory `apps/web` and framework preset Next.js. The production branch is `main`, and preview deployments for pull requests are on.
3. **Environment variables:** set the browser-safe variables only (CLAUDE.md §6) for Production and Preview:
   - `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` (the staging project);
   - `NEXT_PUBLIC_API_BASE_URL` (`<staging API URL>/api/v1`);
   - `NEXT_PUBLIC_FEATURES_DISABLED` (the same list as the API's `FEATURES_DISABLED`).
4. **Record the origin:** put the staging web origin in Render's `ALLOWED_ORIGINS` and in `STAGING_WEB_ORIGIN`.

Preview deployments have their own origins, which the staging API does not allow (exact origins only, NFR-015). A preview can show its pages, but its API calls are refused by CORS.

## 5. Supabase staging project, blocked by IMP-113 (owner Kirtan)

- **The project:** created under IMP-113 (OD-15). The connection string goes into `STAGING_DATABASE_URL` and Render's `DATABASE_URL`.
- **The auth stub:** never applied here. Supabase already has the `auth` schema, and the stub is for plain PostgreSQL only.
- **Auth settings:** email confirmation on or off per IMP-113 section 2. The site URL and the redirect allow list include the staging web origin, so that the confirmation link reaches `/auth/callback` (IMP-109).

## 6. Deploy workflows (card step 4)

### `deploy-staging.yml`

- **Trigger:** runs after the **CI** workflow completes successfully on a push to `main`. It never runs on pull requests.
- **Configuration check:** the job first checks the four staging secrets.
  - If one is missing, it prints `staging not configured (blocked by IMP-113)` with the missing names and ends successfully.
  - Otherwise it checks out the commit CI tested and then runs four steps in order:
    1. `make db-migrate` with `DATABASE_URL` from `STAGING_DATABASE_URL`;
    2. a POST to the Render deploy hook with `ref=<commit>`;
    3. a poll of `GET /health` every 15 s, for up to 20 minutes, until `version` equals the commit (this also covers a cold start);
    4. `make smoke URL=<staging API URL> ARGS='--web-origin <staging web origin>'`.

### `deploy-production.yml`

- **Trigger:** "Run workflow" by hand, with a release tag `vMAJOR.MINOR.PATCH` (Kirtan, §4.5).
- **Checks and steps:** the same configuration check with the `PRODUCTION_*` secrets. When configured:
  1. checks that the tag is on `main`;
  2. runs the same four steps against production.

### Not yet verified

These two points are first checked on the first configured deploy:

- that Render's deploy hook honours the `ref` query parameter;
- that `RENDER_GIT_COMMIT` is set in the running container.

If either fails, the wait step times out and the run fails visibly. The fix is to set `BUILD_VERSION` from the deploy, or to drop `ref` and let Render deploy the head of `main`.

## 7. Cold start (card step 6, NFR-005), blocked by IMP-113 (owner Kirtan)

Measure after at least 15 minutes without requests, three times, with `curl -s -o /dev/null -w '%{time_total}\n' <staging API URL>/health`.

| Measurement | Date (YYYY-MM-DD) | Idle time before (minutes) | First `/health` response time (s) |
| --- | --- | --- | --- |
| 1 | | | |
| 2 | | | |
| 3 | | | |

**Wake-up routine before a demo or a test session:** to be written with the measurements.
