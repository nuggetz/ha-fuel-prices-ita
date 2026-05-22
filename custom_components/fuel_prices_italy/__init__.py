from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_FUEL_TYPES,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_RADIUS_KM,
    CONF_SHOW_SERVITO,
    CONF_UPDATE_INTERVAL_HOURS,
    DEFAULT_SHOW_SERVITO,
    DEFAULT_UPDATE_INTERVAL_HOURS,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import FuelPricesCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Fuel Prices Italy from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = FuelPricesCoordinator(
        hass=hass,
        session=async_get_clientsession(hass),
        latitude=entry.data[CONF_LATITUDE],
        longitude=entry.data[CONF_LONGITUDE],
        radius_km=entry.data[CONF_RADIUS_KM],
        fuel_types=entry.data[CONF_FUEL_TYPES],
        show_servito=entry.options.get(CONF_SHOW_SERVITO, DEFAULT_SHOW_SERVITO),
        update_interval_hours=entry.options.get(
            CONF_UPDATE_INTERVAL_HOURS, DEFAULT_UPDATE_INTERVAL_HOURS
        ),
    )

    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator}
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload_on_options_update))
    return True


async def _async_reload_on_options_update(
    hass: HomeAssistant, entry: ConfigEntry
) -> None:
    """Reload the config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unloaded
