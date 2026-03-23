# EcoFlow Stream HA Integration

Home Assistant Custom Component für **EcoFlow Stream Ultra X** + **Stream AC Pro**.

## Features

- 🔆 **PV Leistung** – Alle 4 MPPTs einzeln + Gesamtleistung
- 🔋 **Batterie** – SOC, SOH, Leistung, Spannung, Temperatur, Zyklen
- ⚡ **Netz** – Einspeisung/Bezug, Spannung, Frequenz
- 🏠 **Hausverbrauch** – via Shelly 3EM (alle 3 Phasen)
- 📊 **Tagesdaten** – Solar, Verbrauch, Netz, Batterie, Autarkie
- 🔌 **AC Steckdosen** – Status + Leistung
- 🌡️ **Temperaturen** – Inverter, Batterie, MOS
- 🔍 **Unbekannte Parameter** – werden automatisch in `ecoflow_stream_unknown_params.json` gespeichert

## Installation

1. Ordner `custom_components/ecoflow_stream` nach `/config/custom_components/` kopieren
2. Home Assistant neu starten
3. **Einstellungen → Integrationen → EcoFlow Stream** hinzufügen
4. Access Key, Secret Key und Seriennummer des Ultra X eingeben

## API Keys

Developer-Portal: https://developer-eu.ecoflow.com

## Geräte

| Gerät | Seriennummer |
|-------|-------------|
| Stream Ultra X | Hauptgerät |
| Stream AC Pro | Optional (Sekundärgerät) |

## Dateien

| Datei | Beschreibung |
|-------|-------------|
| `const.py` | Alle Sensor-Definitionen – hier neue Sensoren hinzufügen |
| `api.py` | REST + MQTT Client |
| `coordinator.py` | Datenkoordinator, unbekannte Parameter-Erkennung |
| `sensor.py` | Sensor-Entitäten |
| `binary_sensor.py` | Binary Sensor-Entitäten |
| `config_flow.py` | Setup-Dialog |

## Neue Parameter hinzufügen

Unbekannte Parameter werden in `/config/ecoflow_stream_unknown_params.json` gespeichert.
Um einen neuen Sensor hinzuzufügen, einfach in `const.py` unter `SENSOR_DEFINITIONS` eintragen:

```python
"mqtt_key": {
    "name": "Anzeigename",
    "unit": UnitOfPower.WATT,
    "device_class": SensorDeviceClass.POWER,
    "state_class": SensorStateClass.MEASUREMENT,
    "factor": 1,
    "icon": "mdi:solar-panel",
},
```
