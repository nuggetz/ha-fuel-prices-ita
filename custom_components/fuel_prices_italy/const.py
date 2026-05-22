from __future__ import annotations

DOMAIN = "fuel_prices_italy"

# --- MIMIT CSV endpoints ---
URL_PRICES = "https://www.mimit.gov.it/images/exportCSV/prezzo_alle_8.csv"
URL_STATIONS = "https://www.mimit.gov.it/images/exportCSV/anagrafica_impianti_attivi.csv"

CSV_ENCODING = "latin-1"
CSV_DELIMITER = "|"

# --- Italy bounding box for coordinate validation ---
ITALY_LAT_MIN = 35.0
ITALY_LAT_MAX = 48.0
ITALY_LON_MIN = 6.0
ITALY_LON_MAX = 19.0

# --- Cache TTLs (seconds) ---
PRICES_TTL_SECONDS = 6 * 3600
STATIONS_TTL_SECONDS = 24 * 3600

# --- Config entry keys ---
CONF_RADIUS_KM = "radius_km"
CONF_FUEL_TYPES = "fuel_types"
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_UPDATE_INTERVAL_HOURS = "update_interval_hours"
CONF_SHOW_SERVITO = "show_servito"

# --- Defaults ---
DEFAULT_RADIUS_KM = 5
DEFAULT_FUEL_TYPES = ["gasoline", "diesel"]
DEFAULT_UPDATE_INTERVAL_HOURS = 6
DEFAULT_SHOW_SERVITO = True

# --- Fuel type identifiers ---
FUEL_GASOLINE = "gasoline"
FUEL_DIESEL = "diesel"
FUEL_LPG = "lpg"
FUEL_METHANE = "methane"
FUEL_HVO = "hvo"
FUEL_BLUE_DIESEL = "blue_diesel"

ALL_FUEL_TYPES = [
    FUEL_GASOLINE,
    FUEL_DIESEL,
    FUEL_LPG,
    FUEL_METHANE,
    FUEL_HVO,
    FUEL_BLUE_DIESEL,
]

FUEL_DISPLAY_NAMES: dict[str, str] = {
    FUEL_GASOLINE: "Benzina",
    FUEL_DIESEL: "Gasolio",
    FUEL_LPG: "GPL",
    FUEL_METHANE: "Metano",
    FUEL_HVO: "HVO / Biodiesel",
    FUEL_BLUE_DIESEL: "Blue Diesel",
}

# Methane (CNG) is sold by kg in Italy; all others by litre.
FUEL_UNITS: dict[str, str] = {
    FUEL_GASOLINE: "EUR/L",
    FUEL_DIESEL: "EUR/L",
    FUEL_LPG: "EUR/L",
    FUEL_METHANE: "EUR/kg",
    FUEL_HVO: "EUR/L",
    FUEL_BLUE_DIESEL: "EUR/L",
}

# --- Mapping: lowercase descCarburante → internal fuel type ---
# Built from live MIMIT CSV (verified 2026-05-22). Case-insensitive lookup at runtime.
FUEL_TYPE_MAPPING: dict[str, str] = {
    # Benzina / Gasoline
    "benzina": FUEL_GASOLINE,
    "benzina 100 ottani": FUEL_GASOLINE,
    "benzina 102 ottani": FUEL_GASOLINE,
    "benzina energy 98 ottani": FUEL_GASOLINE,
    "benzina plus 98": FUEL_GASOLINE,
    "benzina shell v power": FUEL_GASOLINE,
    "benzina speciale 98 ottani": FUEL_GASOLINE,
    "benzina wr 100": FUEL_GASOLINE,
    "benzina speciale": FUEL_GASOLINE,
    "verde speciale": FUEL_GASOLINE,
    "v-power": FUEL_GASOLINE,
    # Gasolio / Diesel
    "gasolio": FUEL_DIESEL,
    "gasolio alpino": FUEL_DIESEL,
    "gasolio artico": FUEL_DIESEL,
    "gasolio artico igloo": FUEL_DIESEL,
    "gasolio ecoplus": FUEL_DIESEL,
    "gasolio energy d": FUEL_DIESEL,
    "gasolio gelo": FUEL_DIESEL,
    "gasolio oro diesel": FUEL_DIESEL,
    "gasolio plus": FUEL_DIESEL,
    "gasolio premium": FUEL_DIESEL,
    "gasolio prestazionale": FUEL_DIESEL,
    "gasolio speciale": FUEL_DIESEL,
    "dieselmax": FUEL_DIESEL,
    "e-diesel": FUEL_DIESEL,
    "excellium diesel": FUEL_DIESEL,
    "gp diesel": FUEL_DIESEL,
    "s-diesel": FUEL_DIESEL,
    "supreme diesel": FUEL_DIESEL,
    "v-power diesel": FUEL_DIESEL,
    "hi-q diesel": FUEL_DIESEL,
    "hiq perform+": FUEL_DIESEL,
    "diesel shell v power": FUEL_DIESEL,
    # GPL / LPG
    "gpl": FUEL_LPG,
    # Metano / CNG — sold by kg in Italy (~1.50–1.75 EUR/kg)
    "metano": FUEL_METHANE,
    "l-gnc": FUEL_METHANE,
    # HVO / Biodiesel — best-effort, brand names vary widely
    "hvo": FUEL_HVO,
    "hvo100": FUEL_HVO,
    "hvolution": FUEL_HVO,
    "hvovolution": FUEL_HVO,
    "diesel hvo": FUEL_HVO,
    "diesel hvo energy": FUEL_HVO,
    "gasolio hvo": FUEL_HVO,
    "gasolio bio hvo": FUEL_HVO,
    "hvo energy diesel": FUEL_HVO,
    "hvo future": FUEL_HVO,
    "hvo eco diesel": FUEL_HVO,
    "bchvo": FUEL_HVO,
    "rehvo": FUEL_HVO,
    "f-101": FUEL_HVO,
    "f101": FUEL_HVO,
    # Blue Diesel — premium additive blends (best-effort)
    "blue diesel": FUEL_BLUE_DIESEL,
    "blu diesel alpino": FUEL_BLUE_DIESEL,
    "blue super": FUEL_BLUE_DIESEL,
}

# --- Statistics ---
STAT_MIN = "min"
STAT_AVG = "avg"
STAT_MAX = "max"
ALL_STATS = [STAT_MIN, STAT_AVG, STAT_MAX]

# --- HA platforms ---
PLATFORMS = ["sensor"]

# --- Nominatim geocoding (used when HA home location is not configured) ---
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_USER_AGENT = "ha-fuel-prices-italy/1.0.0 (https://github.com/nuggetz/ha-fuel-prices-ita)"
