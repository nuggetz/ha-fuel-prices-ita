# ha-fuel-prices-ita — Product & Technical Spec

## 1. Overview

### Problema
Non esiste un custom component HA serio e mantenuto per monitorare i prezzi del
carburante in Italia. Le soluzioni esistenti sono workaround YAML con `rest` sensor
artigianali, fragili e senza logica geografica. L'utente deve sapere a mano quali
stazioni esistono vicino a casa.

### Soluzione
Un custom component (`fuel_prices_italy`) che scarica i CSV open data del MIMIT,
filtra le stazioni nel raggio configurato dall'utente, e espone sensori con i prezzi
aggregati (minimo, massimo, media) per ogni tipo di carburante, sia in modalità
self-service che servito.

### Fonte dati
- **Ministero MIMIT** — portale open data prezzi carburanti
- CSV giornaliero prezzi: aggiornato ogni mattina alle 8:00
- CSV anagrafica impianti: aggiornato quando cambiano le stazioni attive
- Licenza: Open Data Italia (IODL 2.0) — uso libero

### Utenti target
- Automobilisti italiani con HA che vogliono sapere quando il prezzo scende sotto soglia
- Chi vuole notifiche "benzina sotto X euro/litro nel raggio di Y km"
- Homelab HA user italiani

---

## 2. Tipi di carburante supportati

| Chiave interna | Nome display | Note |
|---------------|--------------|------|
| `gasoline` | Benzina | |
| `diesel` | Gasolio | |
| `lpg` | GPL | |
| `methane` | Metano | |
| `hvo` | HVO (biodiesel) | Meno diffuso, includere |
| `blue_diesel` | Gasolio Blue+ | Variante premium |

Mapping da `descCarburante` nel CSV ai tipi interni in `const.py`.
Il CSV MIMIT usa nomi non standardizzati (es. "Benzina", "BENZINA", "Gasolio",
"Gasolio BTZ") — normalizzare con mapping case-insensitive.

> **Nota accuratezza tipi carburante**: benzina, gasolio, GPL e metano sono tipi
> ufficiali con obbligo di comunicazione (L. 99/2009). HVO e Gasolio Blue+ sono
> **varianti di bandiera** con nomi liberi — il mapping è best-effort e potrebbe
> non coprire tutte le denominazioni usate dai gestori. Considerarli meno affidabili.

---

## 3. Sensori esposti

Per ogni tipo di carburante × modalità (self / servito) vengono create fino a 3 entità:

| Pattern entità | Esempio | Descrizione |
|---------------|---------|-------------|
| `sensor.fuel_{tipo}_{modalita}_min` | `sensor.fuel_gasoline_self_min` | Prezzo minimo nel raggio |
| `sensor.fuel_{tipo}_{modalita}_avg` | `sensor.fuel_gasoline_self_avg` | Prezzo medio nel raggio |
| `sensor.fuel_{tipo}_{modalita}_max` | `sensor.fuel_gasoline_self_max` | Prezzo massimo nel raggio |

**Unità**: `EUR/L` (o `EUR/kg` per metano)

**Attributi extra di ogni sensore**:
- `stations_count`: numero stazioni nel raggio che hanno quel carburante
- `cheapest_station`: nome/gestore della stazione col prezzo minore
- `cheapest_station_address`: indirizzo
- `cheapest_station_distance_km`: distanza in km
- `last_updated`: timestamp dell'ultimo dato MIMIT
- `radius_km`: raggio di ricerca usato

**Sensori abilitati di default**: solo gasoline e diesel (self + servito)
**Sensori disabilitati di default**: GPL, metano, HVO, blue_diesel (l'utente li abilita)

---

## 4. Moduli

### M1 — `api_client.py` — MIMIT CSV Downloader

**Descrizione**: scarica e decodifica i CSV MIMIT.

**Responsabilità**:
- Download asincrono CSV prezzi (latin-1, separatore `|`)
- Download asincrono CSV anagrafica (stesso encoding e separatore)
- Parse CSV con `csv.DictReader`
- Restituire lista di dict tipizzati

**Metodi**:
- `fetch_prices() -> list[dict]` — scarica e parsa CSV prezzi
- `fetch_stations() -> list[dict]` — scarica e parsa CSV anagrafica

**Edge case**:
- Encoding errato (UTF-8 invece di latin-1): tentare fallback
- Righe con prezzo non numerico: skip + log debug
- Colonne mancanti rispetto al formato atteso: log warning + skip riga
- HTTP timeout / 4xx / 5xx: eccezione `CannotConnect`
- CSV vuoto o con solo header: eccezione `InvalidData`
- Stazioni senza coordinate o con coordinate `0.0, 0.0`: skip + log warning
- Stazioni con coordinate fuori dal bounding box Italia (lat 35–48, lon 6–19): skip + log warning

---

### M2 — `geo_utils.py` — Filtraggio geografico

**Descrizione**: funzioni pure per calcolo distanze e filtraggio stazioni.

**Funzioni**:

`haversine(lat1, lon1, lat2, lon2) -> float`
- Implementazione formula haversine, risultato in km
- Nessuna dipendenza esterna

`filter_stations_by_radius(stations, center_lat, center_lon, radius_km) -> list[dict]`
- Aggiunge campo `distance_km` a ogni stazione filtrata
- Ordina per distanza crescente

`merge_prices_with_stations(prices, stations) -> list[dict]`
- Join su `idImpianto` tra CSV prezzi e CSV anagrafica
- Scarta prezzi senza anagrafica corrispondente (impianti cessati)

`aggregate_prices(merged, fuel_type, is_self) -> dict | None`
- Calcola min/max/mean per un tipo carburante + modalità
- Restituisce anche stazione più economica (nome, indirizzo, distanza)
- Restituisce `None` se nessuna stazione ha quel carburante nel raggio

---

### M3 — `coordinator.py` — FuelPricesCoordinator

**Descrizione**: gestisce aggiornamenti e caching differenziato dei due CSV.

**Responsabilità**:
- CSV prezzi: TTL **6 ore** (aggiornamento MIMIT mattutino)
- CSV anagrafica: TTL **24 ore**
- Salva cache in `self._prices_cache` e `self._stations_cache` con timestamp
- A ogni update verifica TTL: se scaduto ri-scarica, altrimenti usa cache
- Espone `self.data` come dict `{(fuel_type, is_self): aggregated_dict}`

**Logica update**:
```
1. Verifica TTL stazioni → ri-scarica se necessario
2. Verifica TTL prezzi → ri-scarica se necessario
3. merge_prices_with_stations()
4. filter_stations_by_radius() con coordinate e raggio da config
5. Per ogni (fuel_type, is_self) abilitato → aggregate_prices()
6. Aggiorna self.data
```

**Gestione errori**:
- Primo avvio fallito → `ConfigEntryNotReady`
- Update fallito con dati in cache → log warning, dati vecchi restano validi
- Update fallito senza cache → `UpdateFailed`

---

### M4 — `config_flow.py` — Configurazione

**Descrizione**: wizard UI configurazione e opzioni.

**Step configurazione iniziale** (unico step `user`):

| Campo | Tipo | Default | Validazione |
|-------|------|---------|-------------|
| `name` | string | "Fuel Prices" | non vuoto |
| `use_home_location` | bool | True | — |
| `latitude` | float | — | -90 / +90, visibile solo se use_home_location=False |
| `longitude` | float | — | -180 / +180, visibile solo se use_home_location=False |
| `radius_km` | int | 5 | range 1–50 |
| `fuel_types` | multi-select | [gasoline, diesel] | almeno 1 |

Al submit: test download CSV MIMIT; se fallisce → errore `cannot_connect`.
Se CSV ok ma 0 stazioni nel raggio → warning (non errore bloccante, HA non sempre è a casa).

**OptionsFlow**:
- `radius_km`: modifica raggio
- `fuel_types`: aggiungi/rimuovi tipi carburante
- `update_interval_hours`: 1 / 3 / 6 / 12 (default 6)
- `show_servito`: toggle per includere/escludere modalità servito (default True)

---

### M5 — `sensor.py` — Entità Sensor

**Descrizione**: crea entità sensor per ogni combinazione (tipo, modalità, statistica).

**Logica creazione entità**:
```
per ogni fuel_type in config.fuel_types:
  per ogni is_self in [True, False] (se show_servito abilitato):
    per ogni stat in [min, avg, max]:
      crea OutdoorFuelSensor(fuel_type, is_self, stat)
```

**Proprietà sensore**:
- `state_class`: `SensorStateClass.MEASUREMENT`
- `device_class`: `SensorDeviceClass.MONETARY`
- `native_unit_of_measurement`: `EUR/L` (o `EUR/kg` per metano)
- `entity_registry_enabled_default`:
  - `gasoline` e `diesel` self min/avg → True
  - tutto il resto → False (l'utente abilita quello che vuole)
- `icon`: `mdi:gas-station`

**Valore `None`**: se nessuna stazione ha quel carburante → stato `unknown`

---

### M6 — Infrastruttura HACS / manifest

**`manifest.json`**:
```json
{
  "domain": "fuel_prices_italy",
  "name": "Fuel Prices Italy",
  "version": "1.0.0",
  "documentation": "https://github.com/...",
  "issue_tracker": "https://github.com/.../issues",
  "codeowners": ["@<username>"],
  "requirements": [],
  "dependencies": [],
  "iot_class": "cloud_polling",
  "config_flow": true
}
```

**File obbligatori**:
- `hacs.json`
- `README.md` con esempi automazione (notifica prezzo sotto soglia)
- `translations/en.json` e `translations/it.json`

---

## 5. Stack e architettura tecnica

### Layer applicativo
- **Runtime**: Python 3.12+ in Home Assistant
- **HTTP**: `aiohttp` via `async_get_clientsession`
- **CSV parsing**: stdlib `csv.DictReader`
- **Geo**: formula haversine implementata internamente
- **Config storage**: HA `ConfigEntry`
- **Deploy**: custom_components o HACS

### Integrazioni esterne

| Servizio | Modulo | Scopo | Note |
|----------|--------|-------|------|
| MIMIT CSV prezzi | M1, M3 | Prezzi giornalieri | URL stabile, no auth |
| MIMIT CSV anagrafica | M1, M3 | Coordinate stazioni | URL stabile, no auth |

### Sicurezza e dati
- Nessun dato personale trasmesso — solo download pubblico
- Le coordinate home sono usate solo localmente per il filtraggio
- Nessun secret / token / credenziali

### Requisiti non funzionali
- Startup: primo download entro 45s; failover su `ConfigEntryNotReady`
- Compatibilità HA: >= 2024.1
- Zero dipendenze Python esterne
- CSV MIMIT può contenere fino a ~70.000 righe: parsing deve completarsi in < 5s

---

## 6. Decisioni aperte

| # | Decisione | Opzioni | Note |
|---|-----------|---------|------|
| D1 | Supportare anche prezzi di altri paesi EU? | ~~Multi-paese~~ **Solo IT — chiuso** | Le fonti extra-IT hanno qualità, granularità e formati troppo eterogenei. Scope fisso: solo MIMIT Italia. |
| D2 | Mostrare storico prezzi (attributo o entità separata)? | Solo current / + 7gg history | Richiede storage locale, rimandare a v1.1 |
| D3 | Mappa/lista stazioni come attributo? | Sì (lista dict) / No | Attributo lista su sensore min con top-5 stazioni |
| D4 | Notifica automatica integrata o solo via automazione? | Solo sensor + automazione utente | Preferire sensor puro, l'utente configura la sua automazione |
| D5 | Gestione stazioni senza coordinate nell'anagrafica? | **Skip con bounding box** | Le coordinate sono volontarie e non verificate dal MIMIT. Skip se mancanti, `0.0/0.0`, o fuori dal bounding box Italia (lat 35–48, lon 6–19). Log warning. No geocoding esterno. |

---

## 7. Roadmap build order

### Sprint 1 — Download e parsing
1. `const.py` con URL MIMIT, mapping tipi carburante, defaults
2. `api_client.py` — download CSV + parse latin-1
3. `geo_utils.py` — haversine + filter + merge + aggregate
4. Test unitari puri (no HA) per geo_utils con fixture CSV

### Sprint 2 — Coordinator e sensori base
5. `coordinator.py` con doppio TTL cache
6. `sensor.py` — benzina e gasolio self (subset iniziale)
7. `__init__.py` — setup base
8. Test coordinator con mock HTTP

### Sprint 3 — Config flow completo
9. `config_flow.py` — step user + validazione
10. OptionsFlow
11. `translations/en.json` + `it.json` + `strings.json`
12. Test config flow

### Sprint 4 — Tutti i carburanti + release
13. Tutti i tipi carburante + modalità servito
14. `entity_registry_enabled_default` logic
15. `README.md` con esempi automazione blueprint
16. `hacs.json` + CI validation
17. Tag v1.0.0
