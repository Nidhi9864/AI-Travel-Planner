# Toolchain versions

Recorded on 2026-10-31 for IMP-101 (repo-tree-makefile part) from the commands below, run on the development machine (Linux, WSL2). `.python-version` and `.nvmrc` pin the interpreter and runtime; `apps/web/package-lock.json` pins every web package.

| Tool | Version | Command |
| --- | --- | --- |
| Python | 3.12.3 | `python3.12 --version` |
| Node.js | v22.23.4 | `node --version` |
| npm | 10.9.9 | `npm --version` |
| Next.js | 16.4.3 | `apps/web/node_modules/next/package.json` (scaffolded with `create-next-app@16.4.3`) |
| React / React DOM | 19.3.0 | `apps/web/node_modules/react/package.json` |
| TypeScript | 5.9.3 | `apps/web/node_modules/typescript/package.json` |
| ESLint | 9.39.5 | `apps/web/node_modules/eslint/package.json` |
| Prettier | 3.9.10 | `npx prettier --version` |
| Vitest | 5.0.5 | `npx vitest --version` |
| Tailwind CSS | 4.3.3 | `apps/web/node_modules/tailwindcss/package.json` |
| GNU Make | 4.3 | `make --version` |
| Docker | 29.9.2 (build a82e528) | `docker --version` |
| Docker Compose | v5.6.1 | `docker compose version` |
| Supabase CLI | 2.122.0 | `supabase --version` |
| git | 2.43.0 | `git --version` |
| GitHub CLI (gh) | 2.45.0 | `gh --version` |

Python package versions are pinned by the API part (`apps/api/pyproject.toml`, IMP-101 api-pyproject-guard part) and recorded here when it lands.
