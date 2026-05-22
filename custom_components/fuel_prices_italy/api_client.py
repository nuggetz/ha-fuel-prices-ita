from __future__ import annotations

import csv
import logging
from typing import Any

import aiohttp

from .const import CSV_DELIMITER, CSV_ENCODING, URL_PRICES, URL_STATIONS

_LOGGER = logging.getLogger(__name__)


class CannotConnect(Exception):
    """HTTP request failed or timed out."""


class InvalidData(Exception):
    """CSV is empty, missing headers, or contains no parsable rows."""


class MimitApiClient:
    """Downloads and parses MIMIT open-data fuel price CSV files."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session

    async def fetch_prices(self) -> list[dict[str, Any]]:
        """Download and parse the daily prices CSV."""
        raw = await self._download(URL_PRICES)
        return self._parse_prices(raw)

    async def fetch_stations(self) -> list[dict[str, Any]]:
        """Download and parse the stations registry CSV."""
        raw = await self._download(URL_STATIONS)
        return self._parse_stations(raw)

    async def _download(self, url: str) -> str:
        try:
            async with self._session.get(
                url, timeout=aiohttp.ClientTimeout(total=45)
            ) as resp:
                resp.raise_for_status()
                raw_bytes = await resp.read()
        except (aiohttp.ClientError, TimeoutError) as err:
            raise CannotConnect(f"Failed to download {url}: {err}") from err

        for encoding in (CSV_ENCODING, "utf-8", "utf-8-sig"):
            try:
                return raw_bytes.decode(encoding)
            except UnicodeDecodeError:
                continue

        raise InvalidData(f"Cannot decode response from {url} with any known encoding")

    def _parse_prices(self, text: str) -> list[dict[str, Any]]:
        """Parse prices CSV, skipping the MIMIT preamble line before the header."""
        lines = text.splitlines()
        header_idx = next(
            (i for i, line in enumerate(lines) if "idImpianto" in line), None
        )
        if header_idx is None:
            raise InvalidData("Prices CSV is missing the expected header row")

        reader = csv.DictReader(lines[header_idx:], delimiter=CSV_DELIMITER)
        records: list[dict[str, Any]] = []
        for row in reader:
            try:
                records.append(
                    {
                        "id": int(row["idImpianto"].strip()),
                        "fuel": row["descCarburante"].strip(),
                        "price": float(row["prezzo"].strip()),
                        "is_self": row["isSelf"].strip() == "1",
                        "dt_comu": row["dtComu"].strip(),
                    }
                )
            except (KeyError, ValueError):
                _LOGGER.debug("Skipping malformed price row: %s", row)

        if not records:
            raise InvalidData("Prices CSV contained no parsable rows")
        return records

    def _parse_stations(self, text: str) -> list[dict[str, Any]]:
        """Parse stations registry CSV, discarding entries without valid coordinates."""
        lines = text.splitlines()
        header_idx = next(
            (i for i, line in enumerate(lines) if "idImpianto" in line), None
        )
        if header_idx is None:
            raise InvalidData("Stations CSV is missing the expected header row")

        reader = csv.DictReader(lines[header_idx:], delimiter=CSV_DELIMITER)
        records: list[dict[str, Any]] = []
        for row in reader:
            try:
                lat = float(row["Latitudine"].strip().replace(",", "."))
                lon = float(row["Longitudine"].strip().replace(",", "."))
            except (KeyError, ValueError):
                _LOGGER.warning(
                    "Station %s has missing or non-numeric coordinates, skipping",
                    row.get("idImpianto", "?"),
                )
                continue

            records.append(
                {
                    "id": int(row["idImpianto"].strip()),
                    "manager": row.get("Gestore", "").strip(),
                    "brand": row.get("Bandiera", "").strip(),
                    "address": row.get("Indirizzo", "").strip(),
                    "city": row.get("Comune", "").strip(),
                    "province": row.get("Provincia", "").strip(),
                    "lat": lat,
                    "lon": lon,
                }
            )

        if not records:
            raise InvalidData("Stations CSV contained no parsable rows")
        return records
