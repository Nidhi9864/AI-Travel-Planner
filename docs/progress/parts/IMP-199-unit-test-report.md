# IMP-199 · unit-test-report part

- Owner: Kirtan (kirtan-S111)
- Status: PR_OPEN
- Base commit: 2053abf
- Branch: chore/IMP-199-unit-test-report
- Reviewer: Het (het-lathiya)

## Changed files

- `apps/api/tests/unit/generation/test_records.py` (created, 62 tests): the status machine of `app/generation/records.py`, scope, outcome, failure reason, request hash, generation settings and token usage; statuses, outcomes and failure reasons are compared with the CHECK lists of migration 0004.
- `apps/api/tests/unit/places/test_vocabulary.py` (created, 9 tests): categories, price and hours labels, verification statuses and suitability flags of `app/places/vocabulary.py` compared with migration 0002.
- `apps/api/tests/unit/core/test_money_types.py` (created, 17 tests): Money, MoneyAmount, UtcTimestamp and Page of `app/schemas/common.py`.
- `apps/api/tests/unit/budget/test_budget_schemas.py` (created, 19 tests): BudgetSettingsPatch, AmountRange and BudgetStatus of `app/budget/schemas.py`.
- `UNIT_TEST_REPORT.md` (created): results and the three defects found, with input, expected and actual result, cause and suggested fix.

No production code, contract or migration is changed.

## Defects found (tests marked `xfail(strict=True)`)

| ID | Where | Tests |
| --- | --- | ---: |
| F-1 | `app/schemas/common.py`: `Money.currency` has no `^[A-Z]{3}$` check | 5 |
| F-2 | `app/budget/schemas.py`: `AmountRange` accepts min above max | 1 |
| F-3 | `app/budget/schemas.py`: `BudgetStatus` accepts an excess when the status is not exceeded | 1 |

## Commands run

| Command | Result |
| --- | --- |
| `cd apps/api && .venv/bin/pytest tests/unit -q` | `474 passed, 7 xfailed, 1 warning` |
| `cd apps/api && .venv/bin/ruff check` and `ruff format --check` on the four new files | `All checks passed!` |

## Not run

- `make check`, `make test-api`, `make test-authz`: Docker is not installed on this machine, so there is no test PostgreSQL.
- `make test-web`: the frontend screens are not built yet.

## Open issues

- F-1 to F-3 need a fix by the owners of `app/schemas/common.py` and `app/budget/`; each fix should remove the matching `xfail` marker.
