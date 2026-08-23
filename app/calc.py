"""Pure calculation logic for cable-reel winding.

Callers pass plain objects/attrs so this module is unit-testable without
the ORM. Every public function raises :class:`CalculationError` (never a
raw ``ValueError``/``TypeError``/``ZeroDivisionError``) on bad input, so
the view can turn any failure into a user-facing error message.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


class CalculationError(ValueError):
    """Raised when a cable line cannot be placed on any reel."""


@dataclass
class LineResult:
    reel_pk: int | None
    reel_name: str
    reel_len: float          # m wound on one reel
    reel_num: int            # number of reels needed (>=1)
    netto_1: float           # kg, cable on one reel
    brutto_1: float          # kg, cable + one reel
    netto_all: float         # kg, all cable in the line
    brutto_all: float        # kg, all cable + all reels
    bending_radius: float    # mm
    warning: str | None = None


def winding_length(reel, cable_diameter, margin_mm, packing) -> float:
    """Length (m) of cable that fits on ``reel``.

    ``L = packing * B * (D_wind^2 - d_core^2) / (4 * d_cable^2) * pi / 1000``
    where ``D_wind = reel.diameter - 2 * margin``, ``B = reel.length_neck``,
    ``d_core = reel.diameter_neck``. All dimensions in mm; result in metres.
    """
    try:
        d_cable = float(cable_diameter)
        b = float(reel.length_neck)
        d_wind = float(reel.diameter) - 2.0 * float(margin_mm)
        d_core = float(reel.diameter_neck)
        packing_f = float(packing)
    except (ValueError, TypeError, AttributeError) as exc:
        raise CalculationError(f"Invalid reel/cable dimension: {exc}") from exc

    if d_cable <= 0:
        raise CalculationError("Cable diameter must be positive")
    if d_cable > b:
        raise CalculationError("Cable diameter exceeds reel barrel width")
    if d_wind <= d_core:
        raise CalculationError("Winding diameter not greater than core diameter")

    try:
        return (
            packing_f
            * b
            * (d_wind ** 2 - d_core ** 2)
            / (4.0 * d_cable ** 2)
            * math.pi
            / 1000.0
        )
    except (TypeError, ZeroDivisionError) as exc:
        raise CalculationError(f"Cannot compute winding length: {exc}") from exc


def reel_count_and_len(order_len, l_per_reel) -> tuple[int, float]:
    """Number of reels (ceil, never 0) and actual metres wound per reel."""
    try:
        order = float(order_len)
        per = float(l_per_reel)
    except (ValueError, TypeError) as exc:
        raise CalculationError(f"Invalid length value: {exc}") from exc

    if per <= 0:
        raise CalculationError("Length per reel must be positive")

    try:
        count = max(1, math.ceil(order / per))
        return count, round(order / count, 3)
    except (TypeError, ZeroDivisionError) as exc:
        raise CalculationError(f"Cannot compute reel count: {exc}") from exc


def compute_line(line, reels, settings, transport) -> LineResult:
    """Pick the best reel for one cable line; return results + warnings.

    ``line`` exposes: cod, name, con_num, order_len, max_len, mass, diameter.
    ``reels`` is a list of reel-like objects with: pk, name, diameter,
    diameter_neck, length_neck, width, mass, max_load.
    ``settings`` exposes: winding_margin_mm, packing_factor,
    bending_radius_multiplier.
    ``transport`` exposes max_load (or None).
    """
    try:
        order_len = float(line.order_len)
        max_len = float(line.max_len)
        mass = float(line.mass)
        cable_d = float(line.diameter)
        margin = float(settings.winding_margin_mm)
        packing = float(settings.packing_factor)
        bend_mult = float(settings.bending_radius_multiplier)
    except (ValueError, TypeError, AttributeError) as exc:
        raise CalculationError(f"Invalid line/settings value: {exc}") from exc

    candidates: list[tuple[float, Any]] = []  # (length, reel)
    for reel in reels:
        try:
            length = winding_length(reel, cable_d, margin, packing)
        except CalculationError:
            continue
        if 0 < length <= max_len:
            candidates.append((length, reel))

    if not candidates:
        raise CalculationError(
            "No reel can hold this cable within the max production length"
        )

    try:
        best_len, reel = max(candidates, key=lambda t: t[0])
        reel_num, reel_len = reel_count_and_len(order_len, best_len)
        reel_mass = float(reel.mass)
        reel_max_load = float(reel.max_load)
        reel_width = float(reel.width)
        transport_max_load = float(transport.max_load) if transport is not None else 0.0
        netto_1 = round(reel_len * mass, 2)
        brutto_1 = round(netto_1 + reel_mass, 2)
        netto_all = round(order_len * mass, 2)
        brutto_all = round(netto_all + reel_mass * reel_num, 2)
        bending = round(cable_d * bend_mult, 2)
    except CalculationError:
        raise
    except (ValueError, TypeError, AttributeError, ZeroDivisionError) as exc:
        raise CalculationError(f"Cannot compute line results: {exc}") from exc

    warnings: list[str] = []
    if reel_max_load > 0 and brutto_1 > reel_max_load:
        warnings.append("Reel max load exceeded")
    if transport_max_load > 0 and brutto_all > transport_max_load:
        warnings.append("Transport max load exceeded")
    if cable_d > reel_width:
        warnings.append("Cable wider than reel flange width")

    return LineResult(
        reel_pk=reel.pk,
        reel_name=reel.name,
        reel_len=reel_len,
        reel_num=reel_num,
        netto_1=netto_1,
        brutto_1=brutto_1,
        netto_all=netto_all,
        brutto_all=brutto_all,
        bending_radius=bending,
        warning="; ".join(warnings) if warnings else None,
    )