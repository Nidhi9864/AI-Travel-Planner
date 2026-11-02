"""The budget_settings table (migration 0003). MOD-B09 is its only writer (§3, §5.2).

Other modules create or change a trip's settings only through these functions.
"""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import BudgetSettings


async def upsert_settings(
    session: AsyncSession,
    trip_id: UUID,
    *,
    transport_allowance_per_day: Decimal | None = None,
    stay_budget_per_night: Decimal | None = None,
    contingency_pct: Decimal | None = None,
) -> None:
    """Insert the trip's settings row, or update the values given on an existing one.

    With no values (API-07) the row gets the table defaults, and an existing row is left as it is.
    The caller owns the transaction and has already checked that the trip is the user's.
    """
    values = {
        name: value
        for name, value in (
            ("transport_allowance_per_day", transport_allowance_per_day),
            ("stay_budget_per_night", stay_budget_per_night),
            ("contingency_pct", contingency_pct),
        )
        if value is not None
    }
    statement = insert(BudgetSettings).values(trip_id=trip_id, **values)
    if values:
        statement = statement.on_conflict_do_update(
            index_elements=["trip_id"], set_={**values, "updated_at": func.now()}
        )
    else:
        statement = statement.on_conflict_do_nothing(index_elements=["trip_id"])
    await session.execute(statement)
