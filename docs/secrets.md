# Secrets register

Which secret values exist, who owns each, where it is stored and when it is rotated. **This file never holds a value**, not even a local one. Variable names come from `.env.example` (specification §4.5); a new secret variable gets a row here in the same pull request that adds it. IMP-113 adds the hosted accounts (Supabase, Vercel, Render, Google AI Studio, OpenRouteService, email sender), each with its owner, and confirms the owners below.

## Where values live

| Environment | Store |
| --- | --- |
| Local (each member) | Untracked `apps/api/.env` and `apps/web/.env.local`, copied from `.env.example` and `apps/web/.env.local.example`; local Supabase keys come from `supabase status -o env` |
| Pull-request CI | No secret except the built-in `GITHUB_TOKEN`; `AI_PROVIDER=MOCK` and fixed local values in `.github/workflows/ci.yml` |
| Staging and production | Render environment settings (API) and Vercel environment settings (web); deploy secrets in the GitHub Actions secret store |
| Team copy | The team password manager, one entry per hosted value, shared only with the owner and the integration lead |

## Register

"Local stack" values are created by `supabase start` on each member's machine, only work against that machine's stack and never leave it.

| Variable | Secret? | Owner role | Where stored | Rotation rule |
| --- | --- | --- | --- | --- |
| `DATABASE_URL` | Yes in staging and production (holds the database password); local default is not secret | Database Engineer (Malhar), with the DevOps Engineer and Integration Lead (Kirtan) for the hosted values | Local: `apps/api/.env`. Staging, production: Render settings, deploy workflow secret, password manager | Reset the Supabase database password and update every store when exposed or when a member with access leaves |
| `TEST_DATABASE_URL` | No (fixed local and CI value `travel_test`) | Database Engineer (Malhar) | `.env.example` default, `ci.yml` | None; never point it at a hosted database |
| `SUPABASE_JWT_SECRET` | Yes | Backend Engineer, Auth (Het), with the Integration Lead for hosted values | Local: `apps/api/.env` (local stack). Staging, production: Render settings, password manager | Hosted: rotate in the Supabase dashboard when exposed (this signs out every user); local: `make stack-down` and a fresh stack |
| `SUPABASE_JWKS_URL` | No (public URL) | Backend Engineer, Auth (Het) | Render settings | None (OD-06 decides whether it is used) |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes (bypasses row-level security) | Frontend and QA Engineer, E2E (Krrish) | Local only: `apps/api/.env` for `make e2e` | Never set outside the local stack; if a hosted service-role key is ever exposed, rotate it in the Supabase dashboard at once |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | No (public by design; row-level security protects data) | Frontend Engineer, Web App Lead (Manasvi), with the Integration Lead for hosted values | Local: `apps/web/.env.local`. Staging, production: Vercel settings | Rotate together with the JWT secret |
| `GEMINI_API_KEY` | Yes (billed; spending control in production) | AI Engineer, Provider Layer (Nidhi) | Staging, production: Render settings, password manager. Local: only for `make live-smoke`, a personal key in `apps/api/.env` | Revoke and replace at once when exposed; replace when a member with access leaves; never in pull-request CI |
| `ORS_API_KEY` | Yes | Backend and QA Engineer, Routing (Junaid) | Staging, production: Render settings, password manager. Local: optional, `apps/api/.env` | Revoke and replace when exposed or when a member with access leaves |
| `FINETUNED_API_KEY` | Yes when used | AI Engineer, Provider Layer (Nidhi) | Empty in Stage 1 | Defined by the Stage 2 decision that enables the adapter |

Non-secret settings (`APP_ENV`, `ALLOWED_ORIGINS`, caps, timeouts, `WIKI_USER_AGENT`, `FEATURES_DISABLED` and the other `NEXT_PUBLIC_*` names) are listed only in `.env.example`.

## Rules for every secret

- Never commit, print, log or paste a value: not in code, tests, fixtures, issues, pull requests, progress records or chat. Redact keys in any pasted command output.
- CI fails when a real env file is tracked (the `guards` job; only the two templates are allowed) and when gitleaks finds a secret pattern.
- Do not set `GOOGLE_API_KEY`: the Gemini SDK would prefer it to `GEMINI_API_KEY`.
- **When a value is exposed**: tell the owner and the integration lead at once, rotate it first, then remove it from where it leaked. Removing a commit does not un-expose a value that was pushed.
