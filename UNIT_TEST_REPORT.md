# Unit Test Report — AI Travel Planner API

- **Date:** 2026-11-03
- **Commit tested:** `2053abf` (main)
- **Tool:** pytest 9 on Python 3.12, run from `apps/api`
- **Command:** `.venv/bin/pytest tests/unit -q`

## Summary

| Run | Tests | Passed | Failed |
| --- | ---: | ---: | ---: |
| Existing unit tests (before) | 374 | 374 | 0 |
| New test cases | 107 | 100 | **7** |
| **Whole unit suite (after)** | **481** | **474** | **7** |

The 7 failing tests are marked `@pytest.mark.xfail(strict=True)` with a reason that names F-1, F-2 or F-3 below, so CI stays green while the defects stay recorded. pytest reports them as `474 passed, 7 xfailed`. Once a defect is fixed, its test passes, and strict mode turns that into a failure until the marker is removed.

## New test files

| File | Module under test | Tests | Result |
| --- | --- | ---: | --- |
| `apps/api/tests/unit/generation/test_records.py` | `app/generation/records.py`: status machine, scope, outcome, failure reason, request hash, settings, token usage | 62 | 62 passed |
| `apps/api/tests/unit/places/test_vocabulary.py` | `app/places/vocabulary.py`: categories, labels, statuses and flags compared with migration 0002 | 9 | 9 passed |
| `apps/api/tests/unit/core/test_money_types.py` | `app/schemas/common.py`: Money, MoneyAmount, UtcTimestamp, Page | 17 | 12 passed, **5 failed** |
| `apps/api/tests/unit/budget/test_budget_schemas.py` | `app/budget/schemas.py`: BudgetSettingsPatch, AmountRange, BudgetStatus | 19 | 17 passed, **2 failed** |

## Failures

### F-1 — Money accepts an invalid currency code (5 failures)

- **Test:** `test_money_types.py::test_money_rejects_currency_that_is_not_three_upper_case_letters` (line 50), with inputs `inr`, `IN`, `INRR`, `12A` and `""`
- **Failed at:** `apps/api/tests/unit/core/test_money_types.py:53`, `Failed: DID NOT RAISE ValidationError`
- **Expected:** a `ValidationError`. The field description says "ISO 4217 code, three upper-case letters", and the database requires `char(3) ~ '^[A-Z]{3}$'` (migration 0002).
- **Actual:** every value is accepted.
- **Cause:** `apps/api/app/schemas/common.py:43`. `currency: str` has a description but no `pattern`, so nothing enforces the format. A bad code would only be caught later by the database, as an internal error instead of a 422.
- **Suggested fix:** `currency: str = Field(pattern=r"^[A-Z]{3}$", description=...)`

### F-2 — AmountRange accepts min greater than max (1 failure)

- **Test:** `test_budget_schemas.py::test_amount_range_rejects_min_above_max` (line 66)
- **Failed at:** `apps/api/tests/unit/budget/test_budget_schemas.py:69`, `Failed: DID NOT RAISE ValidationError`
- **Input:** `AmountRange(min="500", max="100")`
- **Expected:** a `ValidationError`, because a cost range whose minimum is above its maximum is meaningless. The places table has the same rule (`price_max >= price_min`, migration 0002).
- **Actual:** accepted.
- **Cause:** `apps/api/app/budget/schemas.py:17`. `AmountRange` has no cross-field check.
- **Note:** this is a response shape built by the budget engine, so the risk is low. The expectation comes from the tester's reading of §9.3.1, not from explicit wording in the spec.

### F-3 — BudgetStatus accepts an excess when the status is not "exceeded" (1 failure)

- **Test:** `test_budget_schemas.py::test_budget_status_excess_only_when_exceeded` (line 72)
- **Failed at:** `apps/api/tests/unit/budget/test_budget_schemas.py:76`, `Failed: DID NOT RAISE ValidationError`
- **Input:** `BudgetStatus(amount="1000", status="near", ratio_pct=90, excess="200")`
- **Expected:** a `ValidationError`. The field's own description says "Null unless the status is exceeded".
- **Actual:** accepted.
- **Cause:** `apps/api/app/budget/schemas.py:37`. The rule is only in the description, and there is no model validator.

## What passed (highlights)

- Every allowed generation status change passes, and every illegal one (skipping steps, leaving `completed` or `failed`) raises `IllegalTransitionError`.
- The status, outcome and failure-reason lists in the code match migration 0004 exactly.
- The request hash ignores key order, changes with content and is a valid SHA-256 digest.
- Generation settings refuse `prompt` or `text` keys, non-scalar values and values longer than 64 characters.
- The place vocabulary matches migration 0002 exactly (categories, price and hours labels, verification statuses, suitability columns).
- Money always serialises with two decimals and rejects a third decimal and more than 12 digits. Timestamps are converted to UTC.
- BudgetSettingsPatch enforces non-negative amounts, contingency between 0 and 50, two decimals and no unknown fields.

## Not covered

- The frontend unit tests (Vitest) were not run in this pass.
- API, authorization and contract tests were not run. They need Docker for PostgreSQL, which is not installed on this machine.
