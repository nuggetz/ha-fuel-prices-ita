from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries

from custom_components.fuel_prices_italy.const import DOMAIN


@pytest.mark.asyncio
async def test_config_flow_creates_entry(hass):
    hass.config.latitude = 41.9
    hass.config.longitude = 12.48

    with patch(
        "custom_components.fuel_prices_italy.config_flow.MimitApiClient.fetch_stations",
        AsyncMock(return_value=[{"id": 1}]),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] == "form"
        assert result["step_id"] == "user"

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={"radius_km": 10, "fuel_types": ["gasoline", "diesel"]},
        )

    assert result2["type"] == "create_entry"
    data = result2["data"]
    assert data["latitude"] == pytest.approx(41.9)
    assert data["radius_km"] == 10
    assert "gasoline" in data["fuel_types"]


@pytest.mark.asyncio
async def test_config_flow_cannot_connect_shows_error(hass):
    from custom_components.fuel_prices_italy.api_client import CannotConnect

    hass.config.latitude = 41.9
    hass.config.longitude = 12.48

    with patch(
        "custom_components.fuel_prices_italy.config_flow.MimitApiClient.fetch_stations",
        AsyncMock(side_effect=CannotConnect("timeout")),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={"radius_km": 5, "fuel_types": ["gasoline"]},
        )

    assert result2["type"] == "form"
    assert result2["errors"]["base"] == "cannot_connect"


@pytest.mark.asyncio
async def test_config_flow_location_step_when_home_unset(hass):
    hass.config.latitude = 0.0
    hass.config.longitude = 0.0

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["step_id"] == "location"


@pytest.mark.asyncio
async def test_config_flow_geocode_failure_shows_error(hass):
    hass.config.latitude = 0.0
    hass.config.longitude = 0.0

    with patch(
        "custom_components.fuel_prices_italy.config_flow._geocode_address",
        AsyncMock(return_value=None),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={"address": "fdjskfjdsk nonsense"},
        )

    assert result2["type"] == "form"
    assert result2["errors"]["address"] == "geocode_failed"
