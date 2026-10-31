# Local setup

From a fresh machine to the API and the web app running on your computer, in about 60 minutes (NFR-032). No account and no key is needed: the local Supabase stack provides auth and Postgres, and the AI provider runs as `MOCK` (IMD-03, specification §4.5).

Supported setups (IMP-101):

- Linux (Ubuntu 24.04 or similar)
- macOS
- Windows with WSL2: Ubuntu 24.04 in WSL2 and Docker Desktop with WSL integration switched on for that distribution. Run every command below inside the Ubuntu terminal, and clone into your Linux home directory (for example `~/Group12`), not under `/mnt/c`, where file access is much slower.

Run every command from the repository root unless a step says otherwise. Times are rough guides for a first run on a normal home connection.

## 1. Install the tools (about 15 minutes)

| Tool | Version | Check |
| --- | --- | --- |
| Git | any recent | `git --version` |
| GNU Make | 4.x | `make --version` |
| Docker with Docker Compose | Docker 24 or later, Compose 2.24 or later | `docker info --format '{{.ServerVersion}}'` and `docker compose version` |
| Supabase CLI | 2.x | `supabase --version` |
| Python | 3.12 (pinned in `.python-version`) | `python3.12 --version` |
| Node.js with npm | the LTS pinned in `.nvmrc` | `node --version` |

The versions the team uses are recorded in [docs/decisions/versions.md](../decisions/versions.md).

- **Docker.** Linux: Docker Engine with the Compose plugin, and add yourself to the `docker` group so `docker` runs without `sudo`. macOS and Windows: Docker Desktop (on Windows: Settings → Resources → WSL integration → switch on Ubuntu-24.04). Docker must be running before steps 4 and 5.
- **Supabase CLI.** macOS or Linux with Homebrew: `brew install supabase/tap/supabase`. Linux or WSL2 without Homebrew: install the `.deb` package from the Supabase CLI releases page on GitHub (`sudo apt install ./supabase_<version>_linux_amd64.deb`).
- **Python 3.12.** Ubuntu 24.04 ships it; also install the venv module: `sudo apt install python3.12 python3.12-venv`. macOS: `brew install python@3.12`.
- **Node.js.** With nvm: `nvm install` in the repository root reads `.nvmrc`.

## 2. Clone and install (about 10 minutes)

```bash
git clone <repository URL> Group12
cd Group12
make setup
```

`make setup` creates `apps/api/.venv`, installs the API package with its dev tools, runs `npm ci` for the web app and points git at the tracked hooks in `.githooks`. Add `ARGS=--with-browsers` to also install Playwright Chromium (needed only for `make e2e`).

## 3. Create your env files (about 2 minutes)

Variable names and placeholders live only in `.env.example`. Copy the templates to the two untracked files that hold your real values:

```bash
cp .env.example apps/api/.env
cp apps/web/.env.local.example apps/web/.env.local
```

Both copies are ignored by git; never commit them or paste their values anywhere (see [docs/secrets.md](../secrets.md)). The defaults already point at the local stack (`DATABASE_URL` on port 54322) and at `AI_PROVIDER=MOCK`. Leave `GEMINI_API_KEY`, `GEMINI_MODEL_ID` and `ORS_API_KEY` as they are for local work: MOCK needs no key, and routing falls back to a distance estimate. Do not set `GOOGLE_API_KEY`.

## 4. Start the local Supabase stack (about 20 minutes the first time)

```bash
make stack-up
```

This runs `supabase start` with `supabase/config.toml`. The first run downloads the Supabase images; later starts take under a minute. When it finishes, `supabase status` shows the API URL `http://127.0.0.1:54321` and the database URL on `127.0.0.1:54322`. Studio is on `http://127.0.0.1:54323` and the local mail inbox, which catches sign-up and password emails, is on `http://127.0.0.1:54324`.

Now copy the local keys into your env files. Print them with:

```bash
supabase status -o env
```

| From `supabase status -o env` | Into |
| --- | --- |
| `JWT_SECRET` | `SUPABASE_JWT_SECRET` in `apps/api/.env` |
| `ANON_KEY` | `NEXT_PUBLIC_SUPABASE_ANON_KEY` in `apps/web/.env.local` (the API does not read the `NEXT_PUBLIC_*` lines of its copy) |
| `SERVICE_ROLE_KEY` | `SUPABASE_SERVICE_ROLE_KEY` in `apps/api/.env`, only if you run `make e2e` |

Replace the whole `<placeholder>`, angle brackets included. These keys are created by your local stack and only work against it, but treat them like any other secret: they stay in the untracked files.

## 5. Start the test database (about 2 minutes)

```bash
make db-up
docker compose ps
```

`make db-up` starts the `db` service of `docker-compose.yml` (postgres:16 on port 5432, database `travel_test`) and returns once it is healthy; `docker compose ps` shows `db` as `(healthy)`. This is the database the backend test suites use (`TEST_DATABASE_URL`). It is blank on every start, because the tests migrate it themselves. The running app uses the stack database from step 4.

## 6. Migrate and seed (about 2 minutes)

```bash
make db-migrate
make seed
```

These build the tables in the stack database and load the SAMPLE fixture destination. Until IMP-106 and IMP-107 are merged, they print `not yet implemented (IMP-106)` or `(IMP-107)` and exit 0; carry on.

## 7. Run the API and the web app (about 5 minutes)

Terminal 1:

```bash
make api
```

Wait for `Application startup complete.`, then check the API from another terminal:

```bash
curl -s http://localhost:8000/health
```

You should get `{"status":"ok","version":"dev","environment":"local","provider":"MOCK"}`.

Terminal 2:

```bash
make web
```

Open `http://localhost:3000` in your browser. The web app talks to the API at `NEXT_PUBLIC_API_BASE_URL` (`http://localhost:8000/api/v1`) and to the local Supabase auth at `NEXT_PUBLIC_SUPABASE_URL`.

You are done when `/health` answers and the web page loads.

## 8. Check your setup and stop the services

```bash
make check        # everything a pull request needs; the test database from step 5 must be up
make stack-down   # stops the Supabase stack (your local auth users and data are kept)
make db-down      # stops and removes the test database container
```

Stop `make api` and `make web` with Ctrl+C.

## Troubleshooting

| Symptom | Cause and fix |
| --- | --- |
| `make api` exits with `configuration error: DATABASE_URL is not set` | `apps/api/.env` is missing or has no `DATABASE_URL`. Repeat step 3. |
| `port is already allocated` or `address already in use` on 5432 or 54321 to 54324 | Another Postgres or Supabase project is running. Find it with `ss -ltnp \| grep -E ':5432'` (macOS: `lsof -i :5432`), stop it, and run the target again. Do not change the ports: the env defaults and the team rely on them. |
| `Cannot connect to the Docker daemon` | Start Docker (Desktop) and wait until it reports running. On WSL2, check that WSL integration is on for your Ubuntu distribution. |
| `permission denied` on `/var/run/docker.sock` (Linux) | Add yourself to the `docker` group (`sudo usermod -aG docker $USER`), then log out and back in. |
| `supabase start` stops part-way | Run `make stack-down`, then `make stack-up` again; a partial image download resumes. |
| Sign-in in the web app fails with an invalid key | `NEXT_PUBLIC_SUPABASE_ANON_KEY` still holds the placeholder, or the stack was recreated. Copy the key again from `supabase status -o env` and restart `make web`. |
| `make setup` cannot find `python3.12` | Install Python 3.12 (step 1); on Ubuntu also `python3.12-venv`. |

## Record your setup time

For TC-335, note when you started step 1 and when `/health` and the web page both worked, and send both times to the integration lead. The Sprint 1 gate records them.
