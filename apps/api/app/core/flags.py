"""Feature switches (IMD-11): FEATURES_DISABLED is a comma-separated list of switch names.

A listed switch turns its feature off: its routes return 404 NOT_FOUND and its tests skip with a
reason. The cards that build the switched features check them with ``is_enabled``.
"""

from app.core.config import Settings


def parse_features_disabled(raw: str) -> frozenset[str]:
    """`"versions, Packing,,"` -> {"versions", "packing"}."""
    return frozenset(name.strip().lower() for name in raw.split(",") if name.strip())


def disabled_features(settings: Settings) -> frozenset[str]:
    return parse_features_disabled(settings.features_disabled)


def is_enabled(settings: Settings, name: str) -> bool:
    return name.lower() not in disabled_features(settings)
