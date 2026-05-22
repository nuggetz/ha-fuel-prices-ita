from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


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
        # id 9999 intentionally absent — simulates a defunct station
    ]
