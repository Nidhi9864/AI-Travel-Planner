# Contributing

How the ten members turn task parts into merged code, following the Team Contribution Plan (specification §14.3 and §14.4) and decisions IMD-61, IMD-62 and IMD-63. The working rules for code are in [CLAUDE.md](../../CLAUDE.md); the cards are in [docs/spec/TASK_REGISTER.md](../spec/TASK_REGISTER.md).

## 1. One part, one branch, one pull request

- Every card names its lead and its parts in the "Owners and parts" row. Build only your part and use other parts through their contracts.
- Before starting, check that the card's prerequisites are merged on `main` (their part records exist in `docs/progress/parts/`).
- Branch name: `feat|fix|chore/IMP-NNN-<part-slug>`, one branch per part, for example `feat/IMP-409-move-api` (Het) and `feat/IMP-409-move-controls` (Manasvi). A single-owner card uses the slug `whole-task` or a short slug.
- The backend, database or AI part merges first; the screen part that uses it merges after it. Screen parts can start earlier against the generated client and stub endpoints.
- At most one migration per pull request (a `migrations/sql/NNNN_name.sql` and `versions/NNNN_name.py` pair).

## 2. Commits

- Conventional Commits starting with the task ID, for example `feat(itinerary): IMP-409 keyboard move controls`.
- Every commit is authored **and** committed as the part owner, with the name and email of the team table, also when the operator runs the part on the owner's behalf (IMD-61). Pass the identity on each command that writes history instead of setting it in git config:

  ```bash
  git -c user.name="<name>" -c user.email="<email>" commit -m "feat(itinerary): IMP-409 keyboard move controls"
  ```

  Use the same `-c` pair for `commit --amend`, `rebase`, `cherry-pick` and `revert`.
- One author per commit: no `Co-authored-by:` line. Commit messages, branch names, pull-request titles and bodies, and code comments do not name an AI tool or its vendor; the product's own AI features (Gemini, ModelProvider, "AI-written" labels) are product content and are fine. Mentioning the paths `CLAUDE.md` and `.claude/` is allowed.
- Never rewrite commits on `main` or commits made by another member. Rebase your own branch on `main` with your `-c` pair and push with `git push --force-with-lease`, only before the pull request is approved.

### The commit-msg hook

`make setup` sets `core.hooksPath` to `.githooks`, so `.githooks/commit-msg` checks every commit message locally. It removes the path texts `CLAUDE.md` and `.claude/` (any case), then refuses the message and names the rule when:

- rule `co-authored-by`: a line starts with `Co-authored-by:` (any case), or
- rule `tool-word`: the message names an AI coding tool or its vendor as a whole word (the exact words are in the hook).

If you cloned before the hook existed, run `make setup` again or `git config core.hooksPath .githooks`.

### Before pushing

Run both checks from CLAUDE.md §12 and repair only your own new commits if one fails:

```bash
git log origin/main..HEAD --format='%h|%an|%ae|%cn|%ce|%s'   # only your name and email, as author and committer
git log origin/main..HEAD --format='%B' | perl -ne 's/CLAUDE\.md|\.claude\///gi; print if /co-authored-by|anthropic|\bclaude\b/i'   # prints nothing
```

## 3. Pull requests

- Opened with `gh pr create` from the operator's account, using the template in `.github/pull_request_template.md`: linked task, part and requirement IDs, what changed, tests run with their result lines, screenshots for UI changes, the contract and migration questions, part owner and reviewer.
- Title names the part, for example `IMP-409 · move-controls part` (single-owner card: `IMP-409 · whole task`).
- Assigned to the part owner; the reviewer is the one named in the run prompt. The reviewer is never the account that opened the pull request and never the part owner. Review across the seam: the API owner reviews the screen part and the screen owner reviews the API part.
- Write the body to a temporary file outside the repository and pass it with `--body-file`.
- Every pull request adds its part record, `docs/progress/parts/IMP-NNN-<part-slug>.md` (IMD-62; fields in [docs/progress/parts/README.md](../progress/parts/README.md)). `docs/progress/sprint-N.md` is compiled from the records by the sprint's gate card.

## 4. Required checks (`.github/workflows/ci.yml`)

| Job | Runs | Fails when |
| --- | --- | --- |
| `lint-types` | `make lint`, `make typecheck`, `make imports` | ruff, Prettier, ESLint, mypy, tsc or an import-linter contract reports a problem |
| `unit` | `make test-unit`, `make test-contract`, `make test-web` | a test fails |
| `guards` | gitleaks over the pull request's commits (full history on `main`) | a secret pattern is found |
| `attribution` | `scripts/check_attribution.sh` (pull requests only) | a commit's author email is not in the repository variable `TEAM_EMAILS`, its committer differs from its author, its message breaks a commit-msg rule, or the pull-request body breaks a commit-msg rule |
| `audit` | `pip-audit` of the API dependencies, `npm audit --audit-level=critical` | pip-audit finds any known vulnerability, or npm finds a critical one |
| `api` | PostgreSQL 16 service, `make db-migrate`, `make test-api`, `make test-authz` | a migration or test fails |

All jobs run with `AI_PROVIDER=MOCK` and `APP_ENV=test`; no provider key exists in pull-request jobs. Run `make check` locally before pushing.

## 5. Review and merge

- One approval from the named reviewer's own account. CODEOWNERS (`.github/CODEOWNERS`) requests Kirtan for `contracts/`, `apps/api/migrations/` and `apps/api/app/schemas/`, and Nidhi for `apps/api/app/ai/`.
- Merge with **Rebase and merge** only (IMD-63); merge commits and squash merging are disabled. Rebasing keeps each commit's author, so every merged part stays credited to its owner. On `main`, GitHub records its own committer, which is expected.
- Kirtan, as integration lead, merges in dependency order, keeps `main` green and resolves migration heads and contract conflicts. A red `main` stops merges until it is fixed.

## 6. When a part counts as done

A part is done, and its points are credited to its owner, when its pull request merges to `main` with every required check green and its share of the card's acceptance criteria is shown by tests. The card's lead marks the card done when all its parts are merged and the card's acceptance criteria are verified.
