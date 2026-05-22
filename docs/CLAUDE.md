# ha-fuel-prices-ita — Istruzioni per Claude Code

## Contesto progetto
Custom component Home Assistant che espone sensori con i prezzi del carburante
locali in Italia, usando i dati open del Ministero delle Imprese e del Made in
Italy (MIMIT). Dati pubblici, aggiornati quotidianamente, zero autenticazione.

## Stack
- **Linguaggio**: Python 3.12+
- **Framework HA**: Home Assistant integration (custom_component)
- **Sorgente dati**: MIMIT Open Data prezzi carburanti (CSV giornaliero)
- **HTTP client**: `aiohttp` (già disponibile in HA)
- **Parsing CSV**: `csv` stdlib Python (nessuna dipendenza aggiuntiva)
- **Pattern aggiornamento dati**: `DataUpdateCoordinator` di HA
- **Config flow**: UI-based (`config_flow.py`), niente `configuration.yaml`
- **Test**: `pytest` + `pytest-homeassistant-custom-component`

## Struttura del progetto
```
custom_components/fuel_prices_italy/
├── __init__.py              # setup, unload, forward entry setup
├── manifest.json            # domain, version, iot_class
├── config_flow.py           # ConfigFlow + OptionsFlow
├── const.py                 # URL CSV MIMIT, tipi carburante, defaults
├── coordinator.py           # FuelPricesCoordinator (DataUpdateCoordinator)
├── api_client.py            # downloader + parser CSV MIMIT
├── geo_utils.py             # calcolo distanza haversine, filtraggio stazioni
├── sensor.py                # entità SensorEntity per ogni tipo carburante
├── strings.json
├── translations/
│   ├── en.json
│   └── it.json
└── tests/
    ├── conftest.py
    ├── test_config_flow.py
    ├── test_coordinator.py
    ├── test_geo_utils.py
    ├── test_sensor.py
    └── fixtures/
        ├── prezzi_latest.csv        # mock subset CSV MIMIT prezzi (separatore |, latin-1)
        └── anagrafica_latest.csv    # mock subset CSV MIMIT anagrafica (separatore |, latin-1)
```

## Convenzioni codice
- **Lingua**: codice e commenti in inglese, docstring su ogni classe e metodo pubblico
- **Type hints**: obbligatori ovunque, usa `from __future__ import annotations`
- **Async**: tutti i metodi I/O sono `async`
- **Costanti**: tutte in `const.py`, mai stringhe hardcoded
- **Logging**: `DEBUG` per payload CSV, `WARNING` per stazioni non parsabili, `ERROR` per download fallito
- **Naming sensori**: `sensor.fuel_<tipo>_<modalita>` es. `sensor.fuel_gasoline_self_min`
- **Unique ID**: `{entry_id}_{tipo_carburante}_{modalita}_{statistica}`

## URL dati MIMIT
```
# File prezzi aggiornato giornalmente (URL stabile):
https://www.mimit.gov.it/images/exportCSV/prezzo_alle_8.csv

# File anagrafica impianti (aggiornato meno frequentemente):
https://www.mimit.gov.it/images/exportCSV/anagrafica_impianti_attivi.csv
```

Il CSV prezzi ha encoding **latin-1** (non UTF-8). Gestire esplicitamente.
Il separatore è **barra verticale `|`** (pipe), NON punto e virgola. Prima riga è header.
Le variabili numeriche usano il **punto `.`** come separatore decimale (formato internazionale).

> ⚠️ Fonte: metadati ufficiali MIMIT aggiornati al 28/01/2026 — qualsiasi documentazione
> precedente che indica `;` come separatore è da considerarsi errata.

## Struttura CSV prezzi (colonne chiave)
```
idImpianto | descCarburante | prezzo | isSelf | dtComu
```
- `isSelf`: 1 = self-service, 0 = servito
- `dtComu`: data comunicazione prezzo (formato gg/MM/AAAA HH:mm:ss)

## Struttura CSV anagrafica (colonne chiave)
```
idImpianto | Gestore | Bandiera | Indirizzo | Comune | Provincia | Latitudine | Longitudine
```

## Regole importanti
- Il coordinator scarica **entrambi i CSV** una volta e li tiene in memoria/cache
- Il CSV anagrafica cambia raramente: aggiornarlo ogni 24h, il CSV prezzi ogni 6h
- Il filtraggio geografico (stazioni nel raggio configurato) avviene **dopo** il download, in `geo_utils.py`
- La distanza si calcola con la formula **haversine** (implementazione interna, no librerie)
- I prezzi vengono aggregati per tipo carburante: `min`, `max`, `mean` delle stazioni nel raggio
- La posizione di riferimento viene letta da `hass.config.latitude/longitude` di default
- Gestire CSV malformati: righe con campo prezzo non numerico → skip con log debug
- `manifest.json` deve dichiarare `"iot_class": "cloud_polling"`
- Nessuna dipendenza Python aggiuntiva
- **Coordinate nell'anagrafica**: sono inserite su base **volontaria** dai gestori e non sempre verificate dal MIMIT. Stazioni senza coordinate o con coordinate palesemente errate (es. `0.0, 0.0` o fuori dal bounding box Italia) vanno scartate con log warning — NON usare API di geocoding esterne

## Cosa NON fare
- Non usare `pandas` o `numpy` per il CSV — stdlib `csv` è sufficiente
- Non scaricare il CSV ad ogni update del coordinator se non è scaduto il TTL
- Non creare un'entità per ogni singola stazione (possono essere centinaia nel raggio)
- Non usare `requests` o librerie sincrone
- Non leggere coordinate da `configuration.yaml`
- Non hardcodare prezzi o tipi di carburante: tutto in `const.py`
- Non targetare versioni HA < 2024.1
