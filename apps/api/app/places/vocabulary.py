"""The one vocabulary of place categories, tags, suitability flags and labels (MOD-B04, IMP-205).

The import quality gate and the API enums both read these values; nothing else defines them.
Categories, labels and verification statuses equal the CHECK lists of migration 0002. ``stay`` is a
category of the data model but is not offered in the MVP (no filter or interest offers it, IMD-40).
Suitability flags are true, false or unknown; unknown is stored as NULL and never as false (FR-019).
"""

from enum import StrEnum


class Category(StrEnum):
    SIGHT = "sight"
    MUSEUM = "museum"
    NATURE = "nature"
    FOOD = "food"
    SHOPPING = "shopping"
    ENTERTAINMENT = "entertainment"
    RELIGIOUS = "religious"
    ACTIVITY = "activity"
    STAY = "stay"


class OfferedCategory(StrEnum):
    """The categories the MVP offers in filters and interests: every Category except stay."""

    SIGHT = Category.SIGHT.value
    MUSEUM = Category.MUSEUM.value
    NATURE = Category.NATURE.value
    FOOD = Category.FOOD.value
    SHOPPING = Category.SHOPPING.value
    ENTERTAINMENT = Category.ENTERTAINMENT.value
    RELIGIOUS = Category.RELIGIOUS.value
    ACTIVITY = Category.ACTIVITY.value


class Tag(StrEnum):
    """Allowed place tags (PD-IMP-205-2): the descriptive tags of the SAMPLE fixture plus the
    pricing tags the budget engine reads (§9.3.1 BF-01, BF-02)."""

    ARCHITECTURE = "architecture"
    ART = "art"
    BOOKS = "books"
    BREAKFAST = "breakfast"
    CAFE = "cafe"
    CRAFTS = "crafts"
    CYCLING = "cycling"
    DINNER = "dinner"
    EVENING = "evening"
    FAMILY = "family"
    GAMES = "games"
    GARDEN = "garden"
    HISTORY = "history"
    INDOOR = "indoor"
    LATE = "late"
    LOCAL = "local"
    LUNCH = "lunch"
    MARITIME = "maritime"
    MARKET = "market"
    MUSIC = "music"
    OUTDOOR = "outdoor"
    QUIET = "quiet"
    SEAFOOD = "seafood"
    SPORT = "sport"
    STREET_FOOD = "street-food"
    TEA = "tea"
    THEATRE = "theatre"
    VEGETARIAN = "vegetarian"
    VIEWS = "views"
    WALKING = "walking"
    WATER = "water"
    WILDLIFE = "wildlife"
    # Pricing tags (§9.3.1): a child pays half or nothing; the price is for the whole group.
    CHILD_HALF = "child_half"
    CHILD_FREE = "child_free"
    PRICE_PER_GROUP = "price_per_group"


class SuitabilityFlag(StrEnum):
    STEP_FREE = "step_free"
    CHILD_FRIENDLY = "child_friendly"
    INDOOR = "indoor"


class SourceLabel(StrEnum):
    """price_label and hours_label (§6.1 Labels)."""

    CURATED = "curated"
    ESTIMATE = "estimate"
    UNAVAILABLE = "unavailable"


class VerificationStatus(StrEnum):
    UNVERIFIED = "unverified"
    CURATED_CHECKED = "curated_checked"
    IMPORTED_OSM = "imported_osm"
    ESTIMATED = "estimated"


CATEGORIES: frozenset[str] = frozenset(category.value for category in Category)
OFFERED_CATEGORIES: frozenset[str] = frozenset(category.value for category in OfferedCategory)
TAGS: frozenset[str] = frozenset(tag.value for tag in Tag)
SUITABILITY_FLAGS: tuple[str, ...] = tuple(flag.value for flag in SuitabilityFlag)
SOURCE_LABELS: frozenset[str] = frozenset(label.value for label in SourceLabel)
VERIFICATION_STATUSES: frozenset[str] = frozenset(status.value for status in VerificationStatus)
