from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
)

from .api_client import CannotConnect, InvalidData, MimitApiClient
from .const import (
    CONF_FUEL_TYPES,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_RADIUS_KM,
    CONF_SHOW_SERVITO,
    CONF_UPDATE_INTERVAL_HOURS,
    DEFAULT_FUEL_TYPES,
    DEFAULT_RADIUS_KM,
    DEFAULT_SHOW_SERVITO,
    DEFAULT_UPDATE_INTERVAL_HOURS,
    DOMAIN,
    FUEL_DISPLAY_NAMES,
    NOMINATIM_URL,
    NOMINATIM_USER_AGENT,
)

_LOGGER = logging.getLogger(__name__)

# HA stores 0.0/0.0 when the user has never set a home location.
_UNSET_COORD_THRESHOLD = 0.001


def _home_location_is_set(hass: HomeAssistant) -> bool:
    return not (
        abs(hass.config.latitude) < _UNSET_COORD_THRESHOLD
        and abs(hass.config.longitude) < _UNSET_COORD_THRESHOLD
    )


async def _geocode_address(
    session: aiohttp.ClientSession, address: str
) -> tuple[float, float] | None:
    """Resolve a free-text address to (lat, lon) via Nominatim OSM."""
    try:
        async with session.get(
            NOMINATIM_URL,
            params={"q": address, "format": "json", "limit": "1", "countrycodes": "it"},
            headers={"User-Agent": NOMINATIM_USER_AGENT},
            timeout=aiohttp.ClientTimeout(total=10),
        ) as resp:
            resp.raise_for_status()
            results = await resp.json()
            if results:
                return float(results[0]["lat"]), float(results[0]["lon"])
    except Exception as err:
        _LOGGER.warning("Geocoding failed for '%s': %s", address, err)
    return None


def _fuel_selector() -> SelectSelector:
    return SelectSelector(
        SelectSelectorConfig(
            options=[
                {"value": k, "label": v} for k, v in FUEL_DISPLAY_NAMES.items()
            ],
            multiple=True,
            mode=SelectSelectorMode.LIST,
        )
    )


def _radius_selector() -> NumberSelector:
    return NumberSelector(
        NumberSelectorConfig(
            min=1,
            max=50,
            mode=NumberSelectorMode.SLIDER,
            unit_of_measurement="km",
        )
    )


class FuelPricesConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for Fuel Prices Italy."""

    VERSION = 1

    def __init__(self) -> None:
        self._resolved_lat: float | None = None
        self._resolved_lon: float | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Entry point. Redirects to location step when HA home is not configured."""
        if not _home_location_is_set(self.hass) and self._resolved_lat is None:
            return await self.async_step_location()

        errors: dict[str, str] = {}

        if user_input is not None:
            lat = self._resolved_lat or self.hass.config.latitude
            lon = self._resolved_lon or self.hass.config.longitude

            session = async_get_clientsession(self.hass)
            try:
                await MimitApiClient(session).fetch_stations()
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidData:
                errors["base"] = "invalid_data"
            else:
                return self.async_create_entry(
                    title=f"Prezzi carburante ({user_input[CONF_RADIUS_KM]} km)",
                    data={
                        CONF_LATITUDE: lat,
                        CONF_LONGITUDE: lon,
                        CONF_RADIUS_KM: user_input[CONF_RADIUS_KM],
                        CONF_FUEL_TYPES: user_input[CONF_FUEL_TYPES],
                    },
                    options={
                        CONF_UPDATE_INTERVAL_HOURS: DEFAULT_UPDATE_INTERVAL_HOURS,
                        CONF_SHOW_SERVITO: DEFAULT_SHOW_SERVITO,
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_RADIUS_KM, default=DEFAULT_RADIUS_KM): _radius_selector(),
                vol.Required(
                    CONF_FUEL_TYPES, default=DEFAULT_FUEL_TYPES
                ): _fuel_selector(),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_location(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Shown when HA home location is not set. Resolves address via Nominatim."""
        errors: dict[str, str] = {}

        if user_input is not None:
            session = async_get_clientsession(self.hass)
            coords = await _geocode_address(session, user_input["address"])
            if coords is None:
                errors["address"] = "geocode_failed"
            else:
                self._resolved_lat, self._resolved_lon = coords
                return await self.async_step_user()

        schema = vol.Schema({vol.Required("address"): TextSelector()})
        return self.async_show_form(
            step_id="location", data_schema=schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> FuelPricesOptionsFlow:
        return FuelPricesOptionsFlow()


class FuelPricesOptionsFlow(OptionsFlow):
    """Options flow — reconfigure radius, fuel types, interval, and servito toggle."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            # update_interval_hours arrives as str from SelectSelector
            user_input[CONF_UPDATE_INTERVAL_HOURS] = int(
                user_input[CONF_UPDATE_INTERVAL_HOURS]
            )
            return self.async_create_entry(data=user_input)

        current_opts = self.config_entry.options
        current_data = self.config_entry.data

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_RADIUS_KM,
                    default=current_data.get(CONF_RADIUS_KM, DEFAULT_RADIUS_KM),
                ): _radius_selector(),
                vol.Required(
                    CONF_FUEL_TYPES,
                    default=current_data.get(CONF_FUEL_TYPES, DEFAULT_FUEL_TYPES),
                ): _fuel_selector(),
                vol.Required(
                    CONF_UPDATE_INTERVAL_HOURS,
                    default=str(
                        current_opts.get(
                            CONF_UPDATE_INTERVAL_HOURS, DEFAULT_UPDATE_INTERVAL_HOURS
                        )
                    ),
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            {"value": "1", "label": "1 ora"},
                            {"value": "3", "label": "3 ore"},
                            {"value": "6", "label": "6 ore"},
                            {"value": "12", "label": "12 ore"},
                        ],
                        mode=SelectSelectorMode.LIST,
                    )
                ),
                vol.Required(
                    CONF_SHOW_SERVITO,
                    default=current_opts.get(CONF_SHOW_SERVITO, DEFAULT_SHOW_SERVITO),
                ): bool,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
