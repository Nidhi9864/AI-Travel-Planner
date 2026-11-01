# Decision: hosted accounts, keys and email sender (IMP-113)

- Card: IMP-113 · Provision accounts, keys and email sender with named owners (US-004; NFR-013, NFR-037)
- Status: **template; outcome pending** (TO BE FILLED BY KIRTAN, JUNAID AND NIDHI)
- Parts:
  - section 1: accounts and secrets register (Kirtan, lead);
  - section 2: OpenRouteService key and email sender (Junaid);
  - section 3: Gemini key, model ID and data-use terms (Nidhi).
- Secrets register: [docs/secrets.md](../secrets.md)
- Open decisions touched: OD-04, OD-06, OD-14, OD-15 (specification §1.9 and Appendix B.3; `docs/spec/DECISION_REGISTER.md`, "Unresolved decisions")

Every field marked **TO BE FILLED BY &lt;member&gt;** is filled in by that member from the account itself.

**This file never holds a value.** That covers:

- key values;
- passwords;
- connection strings;
- login e-mail addresses;
- recovery codes;
- personal data.

Write only yes/no answers, roles, member names, dates and the facts the card asks for. Keys live in the team password manager and the hosting dashboards only (CLAUDE.md §6; [docs/secrets.md](../secrets.md)).

## 1. Accounts (Kirtan)

One row per hosted account (card step 1). Each account uses a team-owned login, never a member's personal address, and its credentials are kept in the team password manager (US-004 AC1).

| Account | Purpose | Owner role | Owner member | Team-owned login (yes/no) | Password-manager entry (yes/no) | Created on (YYYY-MM-DD) |
| --- | --- | --- | --- | --- | --- | --- |
| GitHub repository `het-lathiya/Group12` | Code, pull requests, CI, the GitHub Actions secret store for the deploy workflows | Repository owner; DevOps Engineer and Integration Lead for settings and secrets | TO BE FILLED BY KIRTAN | TO BE FILLED BY KIRTAN | TO BE FILLED BY KIRTAN | TO BE FILLED BY KIRTAN |
| Vercel | Web app hosting: staging, production and pull-request previews (IMP-112) | DevOps Engineer and Integration Lead | TO BE FILLED BY KIRTAN | TO BE FILLED BY KIRTAN | TO BE FILLED BY KIRTAN | TO BE FILLED BY KIRTAN |
| Render | API container hosting, staging and production (IMP-112) | DevOps Engineer and Integration Lead | TO BE FILLED BY KIRTAN | TO BE FILLED BY KIRTAN | TO BE FILLED BY KIRTAN | TO BE FILLED BY KIRTAN |
| Supabase staging project | Hosted Postgres and Auth for staging (§4.5) | DevOps Engineer and Integration Lead; Database Engineer for the schema | TO BE FILLED BY KIRTAN | TO BE FILLED BY KIRTAN | TO BE FILLED BY KIRTAN | TO BE FILLED BY KIRTAN |
| Supabase production project (OD-15: a second project, or the staging project after SG-7) | Hosted Postgres and Auth for production (IMP-801) | DevOps Engineer and Integration Lead | TO BE FILLED BY KIRTAN | TO BE FILLED BY KIRTAN | TO BE FILLED BY KIRTAN | TO BE FILLED BY KIRTAN |
| Google AI Studio (Gemini) | `GEMINI_API_KEY` for staging, production and `make live-smoke` (section 3) | AI Engineer, Provider Layer | TO BE FILLED BY KIRTAN | TO BE FILLED BY KIRTAN | TO BE FILLED BY KIRTAN | TO BE FILLED BY KIRTAN |
| OpenRouteService | `ORS_API_KEY` for staging and production (section 2) | Backend and QA Engineer, Routing | TO BE FILLED BY KIRTAN | TO BE FILLED BY KIRTAN | TO BE FILLED BY KIRTAN | TO BE FILLED BY KIRTAN |
| Email sender (optional) | Sign-up confirmation e-mail for hosted Supabase Auth, if a sender other than the Supabase default is used (section 2) | Backend and QA Engineer, Routing (card part: Junaid) | TO BE FILLED BY KIRTAN | TO BE FILLED BY KIRTAN | TO BE FILLED BY KIRTAN | TO BE FILLED BY KIRTAN |

Record "not created" in "Created on" for the optional email sender if it is not used, and for the production project if OD-15 ends with one project.

**GitHub access for Render and Vercel.** Render and Vercel deploy from `het-lathiya/Group12` through their GitHub apps. Only the repository owner (het-lathiya) can approve that access. Whoever creates the Render and Vercel projects asks the repository owner to approve it.

### Supabase projects (OD-15, OD-06)

| Item | Result |
| --- | --- |
| OD-15: one or two Supabase projects (staging and production) | TO BE FILLED BY KIRTAN |
| Whether the plan in use allows two active projects, as the Supabase pages show it, with the date checked | TO BE FILLED BY KIRTAN |
| OD-06: hosted token verification mode (JWKS through `SUPABASE_JWKS_URL`, or HS256 through `SUPABASE_JWT_SECRET`; both are implemented, IMD-04). The OD-06 owner is Het | TO BE FILLED BY KIRTAN |
| Rows of [docs/secrets.md](../secrets.md) checked against the stores, with the date | TO BE FILLED BY KIRTAN |
