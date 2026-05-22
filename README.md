<img src="assets/header.png" alt="ha-fuel-prices" width="100%"/>

A Home Assistant custom component that exposes sensors with **fuel prices across Italy**, powered by the open data published daily by the Italian Ministry of Enterprises and Made in Italy (MIMIT). Public data, updated every morning, no authentication required.

---

## Features

- Asynchronously downloads MIMIT CSV files (prices + station registry)
- Filters stations within a configurable radius from your HA home location
- Exposes **minimum, average, and maximum** price sensors per fuel type
- **Self-service** and **full-service** modes handled separately
- Automatic refresh every 6 hours (configurable: 1 / 3 / 6 / 12 h)
- Zero external Python dependencies — only libraries already bundled with HA

## Supported fuel types

| Fuel | Unit | Enabled by default |
| --- | --- | --- |
| Gasoline (Benzina) | EUR/L | ✅ |
| Diesel (Gasolio) | EUR/L | ✅ |
| LPG (GPL) | EUR/L | — |
| Methane / CNG (Metano) | EUR/kg | — |
| HVO / Biodiesel | EUR/L | — |
| Blue Diesel | EUR/L | — |

## Installation

### HACS (recommended)

1. Open HACS → **Integrations** → top-right menu → **Custom repositories**
2. Add `https://github.com/nuggetz/ha-fuel-prices-ita` as type **Integration**
3. Search for "Fuel Prices Italy" and install it
4. Restart Home Assistant

### Manual

1. Copy the `custom_components/fuel_prices_italy/` folder into your `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **Fuel Prices Italy**
3. Set the search radius (default 5 km) and the fuel types to monitor

> If your HA home location is not configured, you will be asked for an Italian address or city name to find nearby stations.

## Sensors

Up to 6 entities are created per selected fuel type:

```
sensor.fuel_gasoline_self_min       # Gasoline self-service — minimum price
sensor.fuel_gasoline_self_avg       # Gasoline self-service — average price
sensor.fuel_gasoline_self_max       # Gasoline self-service — maximum price
sensor.fuel_gasoline_servito_min    # Gasoline full service — minimum price
...
```

Each sensor exposes the following extra attributes:

| Attribute | Description |
|-----------|-------------|
| `stations_count` | Number of stations found within the radius |
| `cheapest_station` | Manager / brand of the cheapest station |
| `cheapest_station_address` | Address of the cheapest station |
| `cheapest_station_distance_km` | Distance in km |
| `last_updated` | Timestamp of the latest MIMIT data |
| `radius_km` | Search radius in use |

## Automation example — alert when price drops below threshold

```yaml
automation:
  alias: "Cheap gasoline alert"
  trigger:
    - platform: numeric_state
      entity_id: sensor.fuel_gasoline_self_min
      below: 1.80
  action:
    - service: notify.mobile_app
      data:
        title: "Cheap fuel nearby!"
        message: >
          Min price: {{ states('sensor.fuel_gasoline_self_min') }} EUR/L
          at {{ state_attr('sensor.fuel_gasoline_self_min', 'cheapest_station') }}
          ({{ state_attr('sensor.fuel_gasoline_self_min', 'cheapest_station_distance_km') }} km away)
```

## Data source

Data is sourced from the **Ministero delle Imprese e del Made in Italy (MIMIT)** open data portal, licensed under [IODL 2.0](https://www.dati.gov.it/iodl/2.0/).

- Price CSV: updated every morning at 08:00 Italian time
- Station registry CSV: updated when active stations change

## Requirements

- Home Assistant **2024.1+**
- Python **3.12+**

## License

MIT

---

---

## 🇮🇹 Versione italiana

### Descrizione

Custom component per Home Assistant che espone sensori con i **prezzi del carburante in Italia** usando i dati open del Ministero delle Imprese e del Made in Italy (MIMIT). Dati pubblici, aggiornati ogni mattina, senza autenticazione.

### Caratteristiche

- Scarica i CSV MIMIT (prezzi + anagrafica impianti) in modo asincrono
- Filtra le stazioni nel raggio configurato dalla posizione di casa HA
- Espone sensori con prezzo **minimo, medio e massimo** per ogni carburante
- Modalità **self-service** e **servito** gestite separatamente
- Aggiornamento automatico ogni 6 ore (configurabile: 1 / 3 / 6 / 12 h)
- Nessuna dipendenza Python esterna

### Installazione

#### HACS (consigliato)

1. Apri HACS → **Integrazioni** → menu in alto a destra → **Repository personalizzati**
2. Aggiungi `https://github.com/nuggetz/ha-fuel-prices-ita` come tipo **Integration**
3. Cerca "Fuel Prices Italy" e installala
4. Riavvia Home Assistant

#### Manuale

1. Copia la cartella `custom_components/fuel_prices_italy/` nella tua directory `config/custom_components/`
2. Riavvia Home Assistant

### Configurazione

1. Vai in **Impostazioni → Dispositivi e servizi → Aggiungi integrazione**
2. Cerca **Fuel Prices Italy**
3. Configura il raggio di ricerca (default 5 km) e i tipi di carburante

> Se la posizione di casa in HA non è configurata, verrà chiesto un indirizzo o città italiana.

### Sensori

Per ogni carburante selezionato vengono create fino a 6 entità (min / media / max × self / servito). Ogni sensore include attributi extra: stazione più economica, indirizzo, distanza, numero stazioni nel raggio.

### Fonte dati

Dati dal portale open data **MIMIT**, licenza [IODL 2.0](https://www.dati.gov.it/iodl/2.0/). CSV prezzi aggiornato ogni mattina alle 08:00.
