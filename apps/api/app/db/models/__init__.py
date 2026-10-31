"""ORM models of the 15 MVP tables, one file per owning module (§5.2), and their metadata.

The SQL migrations are the schema (IMD-01); these classes mirror them for queries only, and
``tests/api/test_schema_drift.py`` fails on any difference. Importing this package registers every
table on ``metadata``.
"""

from sqlalchemy import MetaData

from app.db.models.base import Base
from app.db.models.budget import BudgetSettings
from app.db.models.generation import AiGeneration
from app.db.models.itinerary import (
    ItineraryDay,
    ItineraryItem,
    ItineraryVersion,
    ItineraryWarning,
)
from app.db.models.places import DataSource, Destination, Place, PlaceOpeningHours, TripPlace
from app.db.models.profiles import Profile
from app.db.models.routing import RouteCache
from app.db.models.trips import Trip, TripPreferences

metadata: MetaData = Base.metadata

__all__ = [
    "AiGeneration",
    "Base",
    "BudgetSettings",
    "DataSource",
    "Destination",
    "ItineraryDay",
    "ItineraryItem",
    "ItineraryVersion",
    "ItineraryWarning",
    "Place",
    "PlaceOpeningHours",
    "Profile",
    "RouteCache",
    "Trip",
    "TripPlace",
    "TripPreferences",
    "metadata",
]
