from __future__ import annotations

import logging
import math
from typing import Any

from .const import (
    FUEL_TYPE_MAPPING,
    ITALY_LAT_MAX,
    ITALY_LAT_MIN,
    ITALY_LON_MAX,
    ITALY_LON_MIN,
    STAT_AVG,
    STAT_MAX,
    STAT_MIN,
)

_LOGGER = logging.getLogger(__name__)
_EARTH_RADIUS_KM = 6371.0


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the great-circle distance in km between two (lat, lon) points."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return 2 * _EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def _is_valid_italy_coord(lat: float, lon: float) -> bool:
    return (
        ITALY_LAT_MIN <= lat <= ITALY_LAT_MAX
        and ITALY_LON_MIN <= lon <= ITALY_LON_MAX
    )


def filter_stations_by_radius(
    stations: list[dict[str, Any]],
    center_lat: float,
    center_lon: float,
    radius_km: float,
) -> list[dict[str, Any]]:
    """Return stations within radius_km of center, sorted by distance ascending.

    Stations with missing, zero, or out-of-Italy-bbox coordinates are discarded.
    Each returned record gains a ``distance_km`` field.
    """
    result: list[dict[str, Any]] = []
    for station in stations:
        lat, lon = station["lat"], station["lon"]
        if not _is_valid_italy_coord(lat, lon):
            _LOGGER.warning(
                "Station %s has out-of-bounds coordinates (%.4f, %.4f), skipping",
                station["id"],
                lat,
                lon,
            )
            continue
        dist = haversine(center_lat, center_lon, lat, lon)
        if dist <= radius_km:
            result.append({**station, "distance_km": round(dist, 2)})

    result.sort(key=lambda s: s["distance_km"])
    return result


def merge_prices_with_stations(
    prices: list[dict[str, Any]],
    stations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Join price records with station metadata on idImpianto.

    Prices for unknown or defunct stations are silently dropped.
    """
    station_map: dict[int, dict[str, Any]] = {s["id"]: s for s in stations}
    merged: list[dict[str, Any]] = []
    for price in prices:
        station = station_map.get(price["id"])
        if station is not None:
            merged.append({**price, **station})
    return merged


def aggregate_prices(
    merged: list[dict[str, Any]],
    fuel_type: str,
    is_self: bool,
) -> dict[str, Any] | None:
    """Compute min/max/mean price for one fuel_type + mode combination.

    Returns None when no matching records exist in the dataset.
    """
    matching = [
        r
        for r in merged
        if FUEL_TYPE_MAPPING.get(r["fuel"].lower()) == fuel_type
        and r["is_self"] == is_self
    ]
    if not matching:
        return None

    prices = [r["price"] for r in matching]
    cheapest = min(matching, key=lambda r: r["price"])

    brand = cheapest["brand"]
    manager = cheapest["manager"]
    station_label = f"{manager} ({brand})" if brand and brand != manager else manager

    return {
        STAT_MIN: min(prices),
        STAT_MAX: max(prices),
        STAT_AVG: round(sum(prices) / len(prices), 4),
        "stations_count": len(matching),
        "cheapest_station": station_label,
        "cheapest_station_address": (
            f"{cheapest['address']}, {cheapest['city']} ({cheapest['province']})"
        ),
        "cheapest_station_distance_km": cheapest.get("distance_km"),
        "last_updated": max(r["dt_comu"] for r in matching),
    }
