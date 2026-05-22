# Fuel Prices Italy

![ha-fuel-prices](assets/header.png)

Monitor real-time Italian fuel prices in Home Assistant using official open data from the Ministry of Enterprises and Made in Italy (MIMIT). Zero authentication, zero cost.

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/github/license/nuggetz/ha-fuel-prices-ita)](LICENSE)
[![Release](https://img.shields.io/github/v/release/nuggetz/ha-fuel-prices-ita?display_name=tag)](https://github.com/nuggetz/ha-fuel-prices-ita/releases)
[![Issues](https://img.shields.io/github/issues/nuggetz/ha-fuel-prices-ita)](https://github.com/nuggetz/ha-fuel-prices-ita/issues)
[![Last commit](https://img.shields.io/github/last-commit/nuggetz/ha-fuel-prices-ita)](https://github.com/nuggetz/ha-fuel-prices-ita/commits/main)

---

## What it does

| Feature | Detail |
| --- | --- |
| Data source | MIMIT open data CSV (daily update at 08:00 IT) |
| API key required | No |
| Geo filtering | Stations within a configurable radius from your HA home location |
| Fuel types | Gasoline, Diesel, LPG, Methane (CNG), HVO, Blue Diesel |
| Modes | Self-service and full service (servito) separately |
| Statistics | Minimum, average, maximum price per fuel type / mode |
| Update interval | Configurable: 1 / 3 / 6 / 12 h (default 6 h) |
| HA minimum | 2024.1 |
| Python minimum | 3.12 |

---

## Installation

### HACS (recommended)

1. Open HACS → **Integrations**
2. Click the three-dot menu (top right) → **Custom repositories**
3. Add `https://github.com/nuggetz/ha-fuel-prices-ita` — category **Integration**
4. Search for **Fuel Prices Italy** and click **Download**
5. Restart Home Assistant
6. Go to **Settings → Devices & Services → Add Integration**
7. Search for **Fuel Prices Italy** and follow the setup wizard

> **Reconfigure tip:** After setup, go to the integration options to change the search radius, add or remove fuel types, adjust the update interval, or toggle full-service prices.

### Manual

1. Download the latest release from the [Releases page](https://github.com/nuggetz/ha-fuel-prices-ita/releases)
2. Copy `custom_components/fuel_prices_italy/` into your `config/custom_components/` directory
3. Restart Home Assistant
4. Add the integration from **Settings → Devices & Services**

---

## Sensors

The integration creates up to **6 sensors per fuel type** (min / avg / max × self-service / full-service). Only gasoline and diesel self-service min and avg are **enabled by default**; all others can be enabled individually in the entity registry.

### Entity pattern

```text
sensor.fuel_prices_italy_{fuel}_{mode}_{stat}
```

Where `{fuel}` = `gasoline | diesel | lpg | methane | hvo | blue_diesel`, `{mode}` = `self_service | full_service`, `{stat}` = `min | avg | max`.

### Full entity list

| Entity ID | Unit | Enabled by default | Description |
| --- | --- | --- | --- |
| `sensor.fuel_prices_italy_gasoline_self_service_min` | EUR/L | ✅ | Cheapest gasoline self-service in radius |
| `sensor.fuel_prices_italy_gasoline_self_service_avg` | EUR/L | ✅ | Average gasoline self-service in radius |
| `sensor.fuel_prices_italy_gasoline_self_service_max` | EUR/L | — | Most expensive gasoline self-service |
| `sensor.fuel_prices_italy_gasoline_full_service_min` | EUR/L | — | Cheapest gasoline full service |
| `sensor.fuel_prices_italy_gasoline_full_service_avg` | EUR/L | — | Average gasoline full service |
| `sensor.fuel_prices_italy_gasoline_full_service_max` | EUR/L | — | Most expensive gasoline full service |
| `sensor.fuel_prices_italy_diesel_self_service_min` | EUR/L | ✅ | Cheapest diesel self-service in radius |
| `sensor.fuel_prices_italy_diesel_self_service_avg` | EUR/L | ✅ | Average diesel self-service in radius |
| `sensor.fuel_prices_italy_diesel_self_service_max` | EUR/L | — | Most expensive diesel self-service |
| `sensor.fuel_prices_italy_diesel_full_service_min` | EUR/L | — | Cheapest diesel full service |
| `sensor.fuel_prices_italy_diesel_full_service_avg` | EUR/L | — | Average diesel full service |
| `sensor.fuel_prices_italy_diesel_full_service_max` | EUR/L | — | Most expensive diesel full service |
| `sensor.fuel_prices_italy_lpg_self_service_min` | EUR/L | — | Cheapest LPG self-service |
| `sensor.fuel_prices_italy_lpg_self_service_avg` | EUR/L | — | Average LPG self-service |
| `sensor.fuel_prices_italy_lpg_self_service_max` | EUR/L | — | Most expensive LPG self-service |
| `sensor.fuel_prices_italy_lpg_full_service_min` | EUR/L | — | Cheapest LPG full service |
| `sensor.fuel_prices_italy_lpg_full_service_avg` | EUR/L | — | Average LPG full service |
| `sensor.fuel_prices_italy_lpg_full_service_max` | EUR/L | — | Most expensive LPG full service |
| `sensor.fuel_prices_italy_methane_self_service_min` | EUR/kg | — | Cheapest CNG self-service |
| `sensor.fuel_prices_italy_methane_self_service_avg` | EUR/kg | — | Average CNG self-service |
| `sensor.fuel_prices_italy_methane_self_service_max` | EUR/kg | — | Most expensive CNG self-service |
| `sensor.fuel_prices_italy_methane_full_service_min` | EUR/kg | — | Cheapest CNG full service |
| `sensor.fuel_prices_italy_methane_full_service_avg` | EUR/kg | — | Average CNG full service |
| `sensor.fuel_prices_italy_methane_full_service_max` | EUR/kg | — | Most expensive CNG full service |
| `sensor.fuel_prices_italy_hvo_self_service_min` | EUR/L | — | Cheapest HVO/biodiesel self-service |
| `sensor.fuel_prices_italy_hvo_self_service_avg` | EUR/L | — | Average HVO/biodiesel self-service |
| `sensor.fuel_prices_italy_hvo_self_service_max` | EUR/L | — | Most expensive HVO/biodiesel self-service |
| `sensor.fuel_prices_italy_hvo_full_service_min` | EUR/L | — | Cheapest HVO/biodiesel full service |
| `sensor.fuel_prices_italy_hvo_full_service_avg` | EUR/L | — | Average HVO/biodiesel full service |
| `sensor.fuel_prices_italy_hvo_full_service_max` | EUR/L | — | Most expensive HVO/biodiesel full service |
| `sensor.fuel_prices_italy_blue_diesel_self_service_min` | EUR/L | — | Cheapest Blue Diesel self-service |
| `sensor.fuel_prices_italy_blue_diesel_self_service_avg` | EUR/L | — | Average Blue Diesel self-service |
| `sensor.fuel_prices_italy_blue_diesel_self_service_max` | EUR/L | — | Most expensive Blue Diesel self-service |
| `sensor.fuel_prices_italy_blue_diesel_full_service_min` | EUR/L | — | Cheapest Blue Diesel full service |
| `sensor.fuel_prices_italy_blue_diesel_full_service_avg` | EUR/L | — | Average Blue Diesel full service |
| `sensor.fuel_prices_italy_blue_diesel_full_service_max` | EUR/L | — | Most expensive Blue Diesel full service |

### Sensor attributes

Every sensor exposes these extra attributes:

| Attribute | Type | Description |
| --- | --- | --- |
| `stations_count` | int | Number of stations in radius reporting this fuel type |
| `cheapest_station` | string | Manager / brand of the cheapest station |
| `cheapest_station_address` | string | Full address of the cheapest station |
| `cheapest_station_distance_km` | float | Distance in km to the cheapest station |
| `last_updated` | string | Timestamp of the MIMIT data (`dd/MM/yyyy HH:mm:ss`) |
| `radius_km` | float | Search radius currently in use |

---

## Configuration

### Setup options (initial wizard)

| Field | Default | Range | Notes |
| --- | --- | --- | --- |
| Search radius | 5 km | 1 – 50 km | Slider |
| Fuel types | Gasoline, Diesel | All types | Multi-select |

> If your HA home location is not configured (latitude/longitude = 0), an extra step asks for an Italian address or city name. The address is resolved via [Nominatim / OpenStreetMap](https://nominatim.openstreetmap.org) — no API key required.

### Options (reconfigure at any time)

| Field | Default | Notes |
| --- | --- | --- |
| Search radius | 5 km | 1 – 50 km slider |
| Fuel types | Gasoline, Diesel | Multi-select; changes take effect on next update |
| Update interval | 6 h | 1 / 3 / 6 / 12 hours |
| Include full-service prices | On | Toggle to hide all _full_service_ entities |

---

## Dashboard card examples

### Markdown card — quick price overview

```yaml
type: markdown
content: >
  ## ⛽ Carburante vicino a te

  | Tipo | Self min | Self avg |
  |------|----------|----------|
  | Benzina | {{ states('sensor.fuel_prices_italy_gasoline_self_service_min') }} €/L | {{ states('sensor.fuel_prices_italy_gasoline_self_service_avg') }} €/L |
  | Gasolio | {{ states('sensor.fuel_prices_italy_diesel_self_service_min') }} €/L | {{ states('sensor.fuel_prices_italy_diesel_self_service_avg') }} €/L |

  📍 Stazione più economica (benzina):
  {{ state_attr('sensor.fuel_prices_italy_gasoline_self_service_min', 'cheapest_station') }}
  — {{ state_attr('sensor.fuel_prices_italy_gasoline_self_service_min', 'cheapest_station_address') }}
  ({{ state_attr('sensor.fuel_prices_italy_gasoline_self_service_min', 'cheapest_station_distance_km') }} km)
```

### Entities card — all default sensors

```yaml
type: entities
title: Fuel Prices
entities:
  - entity: sensor.fuel_prices_italy_gasoline_self_service_min
    name: Gasoline min
  - entity: sensor.fuel_prices_italy_gasoline_self_service_avg
    name: Gasoline avg
  - entity: sensor.fuel_prices_italy_diesel_self_service_min
    name: Diesel min
  - entity: sensor.fuel_prices_italy_diesel_self_service_avg
    name: Diesel avg
```

---

## Automation examples

### Alert when gasoline drops below a threshold

```yaml
automation:
  alias: "Gasoline price alert"
  trigger:
    - platform: numeric_state
      entity_id: sensor.fuel_prices_italy_gasoline_self_service_min
      below: 1.75
  action:
    - service: notify.mobile_app
      data:
        title: "Cheap fuel nearby!"
        message: >
          Gasoline at {{ states('sensor.fuel_prices_italy_gasoline_self_service_min') }} EUR/L
          at {{ state_attr('sensor.fuel_prices_italy_gasoline_self_service_min', 'cheapest_station') }}
          ({{ state_attr('sensor.fuel_prices_italy_gasoline_self_service_min', 'cheapest_station_distance_km') }} km away)
```

### Daily price report at a fixed time

```yaml
automation:
  alias: "Daily fuel price report"
  trigger:
    - platform: time
      at: "08:30:00"
  action:
    - service: notify.mobile_app
      data:
        title: "Today's fuel prices"
        message: >
          ⛽ Benzina self: {{ states('sensor.fuel_prices_italy_gasoline_self_service_min') }} – {{ states('sensor.fuel_prices_italy_gasoline_self_service_max') }} EUR/L
          🛢️ Gasolio self: {{ states('sensor.fuel_prices_italy_diesel_self_service_min') }} – {{ states('sensor.fuel_prices_italy_diesel_self_service_max') }} EUR/L
          ({{ state_attr('sensor.fuel_prices_italy_gasoline_self_service_min', 'stations_count') }} stazioni nel raggio)
```

### Notify when prices rise above a warning level

```yaml
automation:
  alias: "Fuel price high warning"
  trigger:
    - platform: numeric_state
      entity_id: sensor.fuel_prices_italy_gasoline_self_service_avg
      above: 2.00
  action:
    - service: notify.mobile_app
      data:
        title: "Fuel prices are high"
        message: >
          Average gasoline in your area reached
          {{ states('sensor.fuel_prices_italy_gasoline_self_service_avg') }} EUR/L.
```

---

## Automation blueprints

> **Coming soon.** Importable blueprints for the most common use cases:
>
> - Price-drop alert (configurable fuel type, threshold, and notification target)
> - Daily morning price digest
> - High-price warning with cooldown

---

## Development status

| Milestone | Description | Status |
| --- | --- | --- |
| v0.1.0 | Core integration: CSV download, geo filter, sensors, config flow | ✅ Done |
| v0.1.0 | HACS compliance, CI/CD, full test suite | ✅ Done |
| v1.1.0 | Automation blueprints | ⏳ In progress |
| v1.1.0 | 7-day price history attribute on min sensors | 🔲 Planned |
| v1.2.0 | Top-5 cheapest stations list as sensor attribute | 🔲 Planned |
| v2.0.0 | Multi-location support (e.g., home + workplace) | 🔲 Planned |

---

## Data source

Prices are sourced from the **Ministero delle Imprese e del Made in Italy (MIMIT)** open data portal, licensed under [IODL 2.0](https://www.dati.gov.it/iodl/2.0/).

- Price CSV: updated every morning at **08:00 Italian time**
- Station registry CSV: updated when active stations change
- Coordinates in the station registry are provided voluntarily by operators and are not verified by MIMIT. Stations with missing, zero, or out-of-Italy coordinates are automatically excluded.

---

## 🇮🇹 Versione italiana

Custom component per Home Assistant che espone sensori con i **prezzi del carburante in Italia** usando i dati open del MIMIT. Dati pubblici, aggiornati ogni mattina, senza autenticazione.

### Installazione rapida

1. HACS → **Integrazioni** → menu ⋮ → **Repository personalizzati**
2. Aggiungi `https://github.com/nuggetz/ha-fuel-prices-ita` come **Integration**
3. Cerca **Fuel Prices Italy** e scarica
4. Riavvia HA → Impostazioni → Dispositivi e servizi → Aggiungi integrazione

### Configurazione

Imposta raggio di ricerca e tipi di carburante. Se la posizione di casa in HA non è configurata, viene chiesto un indirizzo italiano per trovare le stazioni vicine (geocoding via OpenStreetMap, nessuna API key).

### Sensori

Per ogni carburante selezionato vengono create fino a 6 entità (min / media / max × self / servito). Di default sono attivi solo benzina e gasolio self min/media. Ogni sensore espone: stazione più economica, indirizzo, distanza, numero stazioni nel raggio.

### Fonte dati

**MIMIT** open data, licenza [IODL 2.0](https://www.dati.gov.it/iodl/2.0/). CSV prezzi aggiornato ogni mattina alle 08:00.
