from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.fuel_prices_italy.const import (
    CONF_FUEL_TYPES,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_RADIUS_KM,
    CONF_SHOW_SERVITO,
    CONF_UPDATE_INTERVAL_HOURS,
    DOMAIN,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests in this package."""
    return


@pytest.fixture
def prices_csv_text() -> str:
    return (FIXTURES_DIR / "prezzi_latest.csv").read_text(encoding="utf-8")


@pytest.fixture
def stations_csv_text() -> str:
    return (FIXTURES_DIR / "anagrafica_latest.csv").read_text(encoding="utf-8")


@pytest.fixture
def sample_prices() -> list[dict]:
    return [
        {"id": 1001, "fuel": "Benzina", "price": 1.789, "is_self": True, "dt_comu": "22/05/2026 08:00:00"},
        {"id": 1001, "fuel": "Gasolio", "price": 1.699, "is_self": True, "dt_comu": "22/05/2026 08:00:00"},
        {"id": 1002, "fuel": "Benzina", "price": 1.809, "is_self": True, "dt_comu": "22/05/2026 08:00:00"},
        {"id": 1002, "fuel": "Gasolio", "price": 1.729, "is_self": True, "dt_comu": "22/05/2026 08:00:00"},
        {"id": 9999, "fuel": "Benzina", "price": 1.750, "is_self": True, "dt_comu": "22/05/2026 08:00:00"},
    ]


@pytest.fixture
def sample_stations() -> list[dict]:
    return [
        {"id": 1001, "manager": "ENI SPA", "brand": "Agip Eni", "address": "Via Roma 1",
         "city": "Roma", "province": "RM", "lat": 41.9, "lon": 12.48},
        {"id": 1002, "manager": "IP SPA", "brand": "IP", "address": "Via Milano 5",
         "city": "Roma", "province": "RM", "lat": 41.92, "lon": 12.50},
    ]


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_LATITUDE: 41.9,
            CONF_LONGITUDE: 12.48,
            CONF_RADIUS_KM: 10,
            CONF_FUEL_TYPES: ["gasoline", "diesel"],
        },
        options={
            CONF_UPDATE_INTERVAL_HOURS: 6,
            CONF_SHOW_SERVITO: True,
        },
        entry_id="test_entry_id",
    )


@pytest.fixture
def mock_coordinator_data(sample_prices, sample_stations):
    """Realistic coordinator data dict for sensor tests."""
    return {
        ("gasoline", True): {
            "min": 1.789, "avg": 1.799, "max": 1.809,
            "stations_count": 2,
            "cheapest_station": "ENI SPA (Agip Eni)",
            "cheapest_station_address": "Via Roma 1, Roma (RM)",
            "cheapest_station_distance_km": 0.5,
            "last_updated": "22/05/2026 08:00:00",
        },
        ("gasoline", False): None,
        ("diesel", True): {
            "min": 1.699, "avg": 1.714, "max": 1.729,
            "stations_count": 2,
            "cheapest_station": "ENI SPA (Agip Eni)",
            "cheapest_station_address": "Via Roma 1, Roma (RM)",
            "cheapest_station_distance_km": 0.5,
            "last_updated": "22/05/2026 08:00:00",
        },
        ("diesel", False): None,
    }
