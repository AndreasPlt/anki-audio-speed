"""Speed values. No Anki imports."""

from __future__ import annotations

NORMAL = 1.0


def snap(value: float, low: float, high: float, step: float) -> float:
    """Round *value* to the nearest multiple of *step*, then clamp it to [low, high]."""
    stepped = round(round(value / step) * step, 6)  # 6 places: drop float noise (0.8500000001)
    return min(max(stepped, low), high)
