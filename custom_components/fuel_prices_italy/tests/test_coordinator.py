from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.fuel_prices_italy.api_client import CannotConnect
from custom_components.fuel_prices_italy.coordinator import FuelPricesCoordinator


@pytest.fixture
def coordinator(hass):
    session = MagicMock()
    return FuelPricesCoordinator(
        hass=hass,
        session=session,
        latitude=41.9,
        longitude=12.48,
        radius_km=10,
        fuel_types=["gasoline", "diesel"],
        show_servito=True,
        update_interval_hours=6,
    )


@pytest.mark.asyncio
async def test_coordinator_first_refresh_success(coordinator, sample_prices, sample_stations):
    with (
        patch.object(coordinator._client, "fetch_prices", AsyncMock(return_value=sample_prices)),
        patch.object(coordinator._client, "fetch_stations", AsyncMock(return_value=sample_stations)),
    ):
        await coordinator.async_refresh()

    assert coordinator.data is not None
    assert ("gasoline", True) in coordinator.data


@pytest.mark.asyncio
async def test_coordinator_raises_update_failed_on_first_error(coordinator):
    with (
        patch.object(coordinator._client, "fetch_prices", AsyncMock(side_effect=CannotConnect("err"))),
        patch.object(coordinator._client, "fetch_stations", AsyncMock(side_effect=CannotConnect("err"))),
        pytest.raises(UpdateFailed),
    ):
        await coordinator._async_update_data()


@pytest.mark.asyncio
async def test_coordinator_uses_stale_cache_on_subsequent_error(
    coordinator, sample_prices, sample_stations
):
    # Prime the cache
    coordinator._prices_cache = sample_prices
    coordinator._stations_cache = sample_stations
    coordinator._prices_cached_at = 1.0
    coordinator._stations_cached_at = 1.0

    with patch.object(
        coordinator._client, "fetch_prices", AsyncMock(side_effect=CannotConnect("net"))
    ):
        # Should not raise; should use stale cache
        result = await coordinator._async_update_data()

    assert result is not None


@pytest.mark.asyncio
async def test_coordinator_no_servito_mode(hass, sample_prices, sample_stations):
    session = MagicMock()
    coord = FuelPricesCoordinator(
        hass=hass,
        session=session,
        latitude=41.9,
        longitude=12.48,
        radius_km=10,
        fuel_types=["gasoline"],
        show_servito=False,
        update_interval_hours=6,
    )
    with (
        patch.object(coord._client, "fetch_prices", AsyncMock(return_value=sample_prices)),
        patch.object(coord._client, "fetch_stations", AsyncMock(return_value=sample_stations)),
    ):
        result = await coord._async_update_data()

    assert ("gasoline", False) not in result
    assert ("gasoline", True) in result
