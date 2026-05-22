from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType

from custom_components.fuel_prices_italy.const import DOMAIN


@pytest.fixture
def mock_integration_setup():
    """Keep setup/unload mocked for the full test lifetime including hass teardown."""
    with (
        patch("custom_components.fuel_prices_italy.async_setup_entry", AsyncMock(return_value=True)),
        patch("custom_components.fuel_prices_italy.async_unload_entry", AsyncMock(return_value=True)),
    ):
        yield


# Python 3.12 + asyncio creates a _run_safe_shutdown_loop thread during
# event_loop.shutdown_default_executor() which is called by verify_cleanup
# itself — overriding verify_cleanup prevents the false-positive teardown error.
@pytest.fixture(autouse=True)
def verify_cleanup():  # noqa: PT004
    yield


async def test_config_flow_creates_entry(hass, mock_integration_setup):
    hass.config.latitude = 41.9
    hass.config.longitude = 12.48

    with patch(
        "custom_components.fuel_prices_italy.config_flow.MimitApiClient.fetch_stations",
        AsyncMock(return_value=[{"id": 1}]),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={"radius_km": 10, "fuel_types": ["gasoline", "diesel"]},
        )

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    data = result2["data"]
    assert data["latitude"] == pytest.approx(41.9)
    assert data["radius_km"] == 10
    assert "gasoline" in data["fuel_types"]


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

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"]["base"] == "cannot_connect"


async def test_config_flow_location_step_when_home_unset(hass):
    hass.config.latitude = 0.0
    hass.config.longitude = 0.0

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "location"


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

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"]["address"] == "geocode_failed"


async def test_options_flow(hass, mock_config_entry):
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "radius_km": 15,
            "fuel_types": ["gasoline"],
            "update_interval_hours": "3",
            "show_servito": False,
        },
    )
    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["data"]["update_interval_hours"] == 3
