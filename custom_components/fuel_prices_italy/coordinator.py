from __future__ import annotations

import logging
import time
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api_client import CannotConnect, InvalidData, MimitApiClient
from .const import (
    DOMAIN,
    PRICES_TTL_SECONDS,
    STATIONS_TTL_SECONDS,
)
from .geo_utils import aggregate_prices, filter_stations_by_radius, merge_prices_with_stations

_LOGGER = logging.getLogger(__name__)

type CoordinatorData = dict[tuple[str, bool], dict[str, Any] | None]


class FuelPricesCoordinator(DataUpdateCoordinator[CoordinatorData]):
    """Manages dual-TTL caching for MIMIT prices and stations CSVs."""

    def __init__(
        self,
        hass: HomeAssistant,
        session: aiohttp.ClientSession,
        latitude: float,
        longitude: float,
        radius_km: float,
        fuel_types: list[str],
        show_servito: bool,
        update_interval_hours: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=update_interval_hours),
        )
        self._client = MimitApiClient(session)
        self.latitude = latitude
        self.longitude = longitude
        self.radius_km = radius_km
        self._fuel_types = fuel_types
        self._show_servito = show_servito

        self._prices_cache: list[dict[str, Any]] | None = None
        self._prices_cached_at: float = 0.0
        self._stations_cache: list[dict[str, Any]] | None = None
        self._stations_cached_at: float = 0.0

    async def _async_update_data(self) -> CoordinatorData:
        now = time.monotonic()

        try:
            if (
                self._stations_cache is None
                or (now - self._stations_cached_at) > STATIONS_TTL_SECONDS
            ):
                self._stations_cache = await self._client.fetch_stations()
                self._stations_cached_at = now
                _LOGGER.debug(
                    "Stations cache refreshed (%d stations)", len(self._stations_cache)
                )

            if (
                self._prices_cache is None
                or (now - self._prices_cached_at) > PRICES_TTL_SECONDS
            ):
                self._prices_cache = await self._client.fetch_prices()
                self._prices_cached_at = now
                _LOGGER.debug(
                    "Prices cache refreshed (%d records)", len(self._prices_cache)
                )

        except (CannotConnect, InvalidData) as err:
            if self._prices_cache is not None and self._stations_cache is not None:
                _LOGGER.warning(
                    "MIMIT update failed, serving stale cache: %s", err
                )
            else:
                raise UpdateFailed(f"MIMIT data unavailable: {err}") from err

        merged = merge_prices_with_stations(self._prices_cache, self._stations_cache)
        nearby = filter_stations_by_radius(
            merged, self.latitude, self.longitude, self.radius_km
        )

        modes = [True, False] if self._show_servito else [True]
        result: CoordinatorData = {}
        for fuel_type in self._fuel_types:
            for is_self in modes:
                result[(fuel_type, is_self)] = aggregate_prices(
                    nearby, fuel_type, is_self
                )
        return result
