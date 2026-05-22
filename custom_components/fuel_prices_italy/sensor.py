from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_FUEL_TYPES,
    CONF_SHOW_SERVITO,
    DEFAULT_SHOW_SERVITO,
    DOMAIN,
    FUEL_DIESEL,
    FUEL_GASOLINE,
    FUEL_UNITS,
    STAT_AVG,
    STAT_MAX,
    STAT_MIN,
)
from .coordinator import FuelPricesCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from a config entry."""
    coordinator: FuelPricesCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    fuel_types: list[str] = entry.data[CONF_FUEL_TYPES]
    show_servito: bool = entry.options.get(CONF_SHOW_SERVITO, DEFAULT_SHOW_SERVITO)

    modes: list[tuple[bool, str]] = [(True, "self")]
    if show_servito:
        modes.append((False, "servito"))

    entities: list[FuelPriceSensor] = [
        FuelPriceSensor(coordinator, entry.entry_id, fuel_type, is_self, mode_name, stat)
        for fuel_type in fuel_types
        for is_self, mode_name in modes
        for stat in (STAT_MIN, STAT_AVG, STAT_MAX)
    ]
    async_add_entities(entities)


class FuelPriceSensor(CoordinatorEntity[FuelPricesCoordinator], SensorEntity):
    """Price sensor for one fuel type / service mode / statistic combination."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:gas-station"

    def __init__(
        self,
        coordinator: FuelPricesCoordinator,
        entry_id: str,
        fuel_type: str,
        is_self: bool,
        mode_name: str,
        stat: str,
    ) -> None:
        super().__init__(coordinator)
        self._fuel_type = fuel_type
        self._is_self = is_self
        self._stat = stat

        self._attr_unique_id = f"{entry_id}_{fuel_type}_{mode_name}_{stat}"
        self._attr_translation_key = f"{fuel_type}_{mode_name}_{stat}"
        self._attr_native_unit_of_measurement = FUEL_UNITS.get(fuel_type, "EUR/L")
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="Fuel Prices Italy",
            manufacturer="MIMIT Open Data",
            entry_type="service",
        )
        # Only gasoline/diesel self min and avg are enabled by default.
        self._attr_entity_registry_enabled_default = (
            fuel_type in (FUEL_GASOLINE, FUEL_DIESEL)
            and is_self
            and stat in (STAT_MIN, STAT_AVG)
        )

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data is None:
            return None
        agg = self.coordinator.data.get((self._fuel_type, self._is_self))
        return None if agg is None else agg.get(self._stat)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self.coordinator.data is None:
            return {}
        agg = self.coordinator.data.get((self._fuel_type, self._is_self))
        if agg is None:
            return {}
        return {
            "stations_count": agg.get("stations_count"),
            "cheapest_station": agg.get("cheapest_station"),
            "cheapest_station_address": agg.get("cheapest_station_address"),
            "cheapest_station_distance_km": agg.get("cheapest_station_distance_km"),
            "last_updated": agg.get("last_updated"),
            "radius_km": self.coordinator.radius_km,
        }
