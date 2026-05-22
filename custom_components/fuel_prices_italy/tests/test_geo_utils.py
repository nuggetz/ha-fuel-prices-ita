from __future__ import annotations

import math

import pytest

from custom_components.fuel_prices_italy.geo_utils import (
    aggregate_prices,
    filter_stations_by_radius,
    haversine,
    merge_prices_with_stations,
)


def test_haversine_same_point():
    assert haversine(41.9, 12.48, 41.9, 12.48) == pytest.approx(0.0, abs=1e-9)


def test_haversine_rome_milan():
    dist = haversine(41.9, 12.48, 45.46, 9.19)
    assert 470 < dist < 490


def test_haversine_symmetry():
    a = haversine(41.9, 12.48, 45.46, 9.19)
    b = haversine(45.46, 9.19, 41.9, 12.48)
    assert a == pytest.approx(b)


def test_filter_stations_by_radius_includes_nearby(sample_stations):
    # Both stations are within 10 km of the same Rome area
    result = filter_stations_by_radius(sample_stations, 41.90, 12.48, radius_km=10)
    assert len(result) == 2


def test_filter_stations_by_radius_excludes_distant(sample_stations):
    result = filter_stations_by_radius(sample_stations, 41.90, 12.48, radius_km=0.5)
    assert len(result) == 0


def test_filter_stations_sorted_by_distance(sample_stations):
    result = filter_stations_by_radius(sample_stations, 41.90, 12.48, radius_km=10)
    distances = [s["distance_km"] for s in result]
    assert distances == sorted(distances)


def test_filter_stations_rejects_zero_coords():
    bad_stations = [
        {"id": 1, "manager": "X", "brand": "X", "address": "", "city": "", "province": "",
         "lat": 0.0, "lon": 0.0},
    ]
    result = filter_stations_by_radius(bad_stations, 41.9, 12.48, radius_km=50)
    assert result == []


def test_filter_stations_rejects_out_of_italy():
    out = [
        {"id": 2, "manager": "X", "brand": "X", "address": "", "city": "", "province": "",
         "lat": 51.5, "lon": 0.12},
    ]
    result = filter_stations_by_radius(out, 41.9, 12.48, radius_km=50000)
    assert result == []


def test_merge_drops_unknown_stations(sample_prices, sample_stations):
    merged = merge_prices_with_stations(sample_prices, sample_stations)
    ids = {r["id"] for r in merged}
    assert 9999 not in ids


def test_merge_joins_on_id(sample_prices, sample_stations):
    merged = merge_prices_with_stations(sample_prices, sample_stations)
    for record in merged:
        assert "manager" in record
        assert "lat" in record


def test_aggregate_prices_basic(sample_prices, sample_stations):
    merged = merge_prices_with_stations(sample_prices, sample_stations)
    nearby = filter_stations_by_radius(merged, 41.90, 12.48, radius_km=10)
    result = aggregate_prices(nearby, "gasoline", is_self=True)
    assert result is not None
    assert result["min"] == pytest.approx(1.789)
    assert result["max"] == pytest.approx(1.809)
    assert result["avg"] == pytest.approx((1.789 + 1.809) / 2, rel=1e-3)
    assert result["stations_count"] == 2


def test_aggregate_prices_no_match(sample_prices, sample_stations):
    merged = merge_prices_with_stations(sample_prices, sample_stations)
    nearby = filter_stations_by_radius(merged, 41.90, 12.48, radius_km=10)
    result = aggregate_prices(nearby, "lpg", is_self=True)
    assert result is None
