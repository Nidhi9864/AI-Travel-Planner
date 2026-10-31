# Part records

One record per task part (IMD-62), added in the same pull request as the part's code. The gate card of each sprint compiles `docs/progress/sprint-N.md` from these files, and a RESYNC run rebuilds the planner's ledger from them.

**File name:** `IMP-NNN-<part-slug>.md`, for example `IMP-409-move-controls.md`; a single-owner card uses the slug `whole-task`.

**Base commit, not head commit.** The record names the commit of `origin/main` the part was built on. It never names its own head commit: Rebase and merge rewrites commit IDs, so the head commit of the branch does not exist on `main` after merging.

## Fields (CLAUDE.md §11 item 5)

```markdown
# IMP-NNN · <part-slug> part

- Run id: RUN-…
- Owner: <member>
- Status: PR_OPEN | BLOCKED | TESTS_FAILING | PARTIAL | NO_CHANGE
- Base commit: <sha of origin/main the branch started from>
- Branch: <feat|fix|chore/IMP-NNN-<part-slug>>

## Changed files
- <path> (created | modified | deleted)

## Commands run
| Command | Result line (quoted exactly) |
| --- | --- |

## Not run
| Command | Reason |
| --- | --- |

## Acceptance criteria
| Criterion | Status (verified / not verified) | How |
| --- | --- | --- |

## Blockers
## Proposed decisions
## Open issues
```

A test counts as passing only if it ran in that run or in CI and passed; a command that cannot run is listed under "Not run" with the reason.
