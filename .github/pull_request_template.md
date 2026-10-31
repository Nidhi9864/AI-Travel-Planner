<!-- Title: IMP-NNN · <part-slug> part (for a single-owner card: IMP-NNN · whole task). -->

## Linked IDs

- Task and part: IMP-NNN · <part-slug>
- Requirements and stories (FR, NFR, US, TC): <IDs from the card's "Traces to" row>

## What changed

- <one line per change; name the files or modules>

## Tests run

| Command | Result line (quoted exactly) |
| --- | --- |
| `make check` | |
| `<the card's test command>` | |

Not run, with the reason: <none, or the command and why>

## Screenshots (UI changes)

<desktop and mobile screenshots, or "no UI change">

## Contract and migration

- [ ] Contract changed (OpenAPI, AI schema, table, error or finding code, environment variable name); `make openapi` was run and the specification registers are updated in this pull request
- [ ] Migration added (one `migrations/sql/NNNN_name.sql` + `versions/NNNN_name.py` pair; ORM models and the drift test updated)
- [ ] Neither

## Ownership and review

- Part owner: <member> (@<github user>), assigned to this pull request
- Reviewer: <member> (@<github user>), named in the run prompt; never the account that opened this pull request
- Part record: `docs/progress/parts/IMP-NNN-<part-slug>.md`
- Prerequisite parts merged on main: <IMP-NNN parts, or none>

## Checklist

- [ ] Every commit is authored and committed as the part owner, one author per commit, Conventional Commits starting with the task ID
- [ ] The required checks are green: lint-types, unit, guards, attribution, audit, api
- [ ] No secret, key, token, connection string or personal data in code, tests, fixtures or logs
- [ ] Merge with Rebase and merge only
