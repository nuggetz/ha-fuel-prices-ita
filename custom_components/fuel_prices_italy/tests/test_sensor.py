from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from custom_components.fuel_prices_italy.sensor import FuelPriceSensor


def _make_sensor(fuel_type="gasoline", is_self=True, stat="min", entry_id="test_entry"):
    coordinator = MagicMock()
    coordinator.radius_km = 5
    coordinator.data = {
        ("gasoline", True): {
            "min": 1.789,
            "avg": 1.799,
            "max": 1.809,
            "stations_count": 2,
            "cheapest_station": "ENI SPA (Agip Eni)",
            "cheapest_station_address": "Via Roma 1, Roma (RM)",
            "cheapest_station_distance_km": 0.5,
            "last_updated": "22/05/2026 08:00:00",
        }
    }
    return FuelPriceSensor(coordinator, entry_id, fuel_type, is_self, "self" if is_self else "servito", stat)


def test_sensor_native_value_present():
    sensor = _make_sensor(stat="min")
    assert sensor.native_value == pytest.approx(1.789)


def test_sensor_native_value_max():
    sensor = _make_sensor(stat="max")
    assert sensor.native_value == pytest.approx(1.809)


def test_sensor_native_value_none_when_no_data():
    sensor = _make_sensor(fuel_type="lpg", is_self=True, stat="min")
    assert sensor.native_value is None


def test_sensor_native_value_none_when_coordinator_data_none():
    sensor = _make_sensor()
    sensor.coordinator.data = None
    assert sensor.native_value is None


def test_sensor_extra_attributes_present():
    sensor = _make_sensor()
    attrs = sensor.extra_state_attributes
    assert attrs["stations_count"] == 2
    assert attrs["radius_km"] == 5
    assert "cheapest_station" in attrs


def test_sensor_extra_attributes_empty_when_no_data():
    sensor = _make_sensor(fuel_type="lpg")
    assert sensor.extra_state_attributes == {}


def test_sensor_enabled_default_gasoline_self_min():
    assert _make_sensor("gasoline", True, "min")._attr_entity_registry_enabled_default is True


def test_sensor_enabled_default_gasoline_self_avg():
    assert _make_sensor("gasoline", True, "avg")._attr_entity_registry_enabled_default is True


def test_sensor_disabled_default_gasoline_self_max():
    assert _make_sensor("gasoline", True, "max")._attr_entity_registry_enabled_default is False


def test_sensor_disabled_default_lpg():
    assert _make_sensor("lpg", True, "min")._attr_entity_registry_enabled_default is False


def test_sensor_unique_id_stable():
    s1 = _make_sensor("gasoline", True, "min", "abc")
    s2 = _make_sensor("gasoline", True, "min", "abc")
    assert s1.unique_id == s2.unique_id


def test_sensor_methane_unit():
    sensor = _make_sensor("methane", True, "min")
    assert sensor.native_unit_of_measurement == "EUR/kg"
