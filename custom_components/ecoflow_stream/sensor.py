"""EcoFlow Stream Sensoren."""
import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_DEFINITIONS, CONF_MAIN_SN
from .coordinator import EcoFlowCoordinator, ENERGY_CODES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: EcoFlowCoordinator = hass.data[DOMAIN][entry.entry_id]
    main_sn = entry.data[CONF_MAIN_SN]

    entities = []

    # Echtzeit-Sensoren aus SENSOR_DEFINITIONS
    for key, definition in SENSOR_DEFINITIONS.items():
        entities.append(
            EcoFlowRealtimeSensor(
                coordinator=coordinator,
                entry=entry,
                main_sn=main_sn,
                mqtt_key=key,
                definition=definition,
            )
        )

    # Berechneter PV-Gesamt-Sensor
    entities.append(EcoFlowPvTotalSensor(coordinator, entry, main_sn))

    # Berechneter Hausstrom-Gesamt (Shelly)
    entities.append(EcoFlowSmartMeterTotalSensor(coordinator, entry, main_sn))

    # Energie-Tagesdaten-Sensoren
    energy_sensor_defs = {
        "solar_energy_wh": ("Solarenergie Heute", "mdi:solar-power", SensorDeviceClass.ENERGY),
        "load_energy_wh": ("Verbrauch Heute", "mdi:home-lightning-bolt", SensorDeviceClass.ENERGY),
        "grid_energy_wh": ("Netzbezug Heute", "mdi:transmission-tower", SensorDeviceClass.ENERGY),
        "battery_energy_wh": ("Batterieenergie Heute", "mdi:battery-charging", SensorDeviceClass.ENERGY),
        "independence_pct": ("Autarkie Heute", "mdi:home-battery", None),
    }
    for key, (name, icon, device_class) in energy_sensor_defs.items():
        entities.append(
            EcoFlowEnergySensor(
                coordinator=coordinator,
                entry=entry,
                main_sn=main_sn,
                energy_key=key,
                name=name,
                icon=icon,
                device_class=device_class,
            )
        )

    async_add_entities(entities)


class EcoFlowBaseSensor(CoordinatorEntity, SensorEntity):
    """Basis-Klasse für alle EcoFlow Sensoren."""

    def __init__(self, coordinator: EcoFlowCoordinator, entry: ConfigEntry, main_sn: str) -> None:
        super().__init__(coordinator)
        self._main_sn = main_sn
        self._entry = entry

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._main_sn)},
            name=f"EcoFlow Stream Ultra X ({self._main_sn[-4:]})",
            manufacturer="EcoFlow",
            model="STREAM Ultra X",
            serial_number=self._main_sn,
        )


class EcoFlowRealtimeSensor(EcoFlowBaseSensor):
    """Echtzeit-Sensor aus MQTT-Daten."""

    def __init__(
        self,
        coordinator: EcoFlowCoordinator,
        entry: ConfigEntry,
        main_sn: str,
        mqtt_key: str,
        definition: dict,
    ) -> None:
        super().__init__(coordinator, entry, main_sn)
        self._mqtt_key = mqtt_key
        self._definition = definition
        self._attr_unique_id = f"{main_sn}_{mqtt_key}"
        self._attr_name = definition["name"]
        self._attr_native_unit_of_measurement = definition["unit"]
        self._attr_device_class = definition["device_class"]
        self._attr_state_class = definition["state_class"]
        self._attr_icon = definition["icon"]

    @property
    def native_value(self) -> Any:
        realtime = self.coordinator.data.get("realtime", {}) if self.coordinator.data else {}
        raw = realtime.get(self._mqtt_key)
        if raw is None:
            return None
        try:
            factor = self._definition.get("factor", 1)
            return round(float(raw) * factor, 3)
        except (ValueError, TypeError):
            return raw

    @property
    def available(self) -> bool:
        realtime = self.coordinator.data.get("realtime", {}) if self.coordinator.data else {}
        return self._mqtt_key in realtime


class EcoFlowPvTotalSensor(EcoFlowBaseSensor):
    """Berechnete PV-Gesamtleistung (MPPT1+2+3+4)."""

    def __init__(self, coordinator, entry, main_sn):
        super().__init__(coordinator, entry, main_sn)
        self._attr_unique_id = f"{main_sn}_pv_total"
        self._attr_name = "PV Gesamtleistung"
        self._attr_native_unit_of_measurement = "W"
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:solar-panel-large"

    @property
    def native_value(self) -> float | None:
        realtime = self.coordinator.data.get("realtime", {}) if self.coordinator.data else {}
        values = []
        for key in ["powGetPv", "powGetPv2", "powGetPv3", "powGetPv4"]:
            v = realtime.get(key)
            if v is not None:
                try:
                    values.append(float(v))
                except (ValueError, TypeError):
                    pass
        return round(sum(values), 1) if values else None


class EcoFlowSmartMeterTotalSensor(EcoFlowBaseSensor):
    """Berechneter Gesamtverbrauch aus Shelly 3EM (alle 3 Phasen)."""

    def __init__(self, coordinator, entry, main_sn):
        super().__init__(coordinator, entry, main_sn)
        self._attr_unique_id = f"{main_sn}_smart_meter_total"
        self._attr_name = "Hausverbrauch Gesamt (Shelly)"
        self._attr_native_unit_of_measurement = "W"
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:home-lightning-bolt"

    @property
    def native_value(self) -> float | None:
        realtime = self.coordinator.data.get("realtime", {}) if self.coordinator.data else {}
        total = 0
        found = False
        for key in ["cloudMetter_phaseAPower", "cloudMetter_phaseBPower", "cloudMetter_phaseCPower"]:
            v = realtime.get(key)
            if v is not None:
                try:
                    total += float(v)
                    found = True
                except (ValueError, TypeError):
                    pass
        return round(total, 1) if found else None


class EcoFlowEnergySensor(EcoFlowBaseSensor):
    """Energie-Tagesdaten-Sensor."""

    def __init__(
        self,
        coordinator,
        entry,
        main_sn,
        energy_key: str,
        name: str,
        icon: str,
        device_class,
    ):
        super().__init__(coordinator, entry, main_sn)
        self._energy_key = energy_key
        self._attr_unique_id = f"{main_sn}_energy_{energy_key}"
        self._attr_name = name
        self._attr_icon = icon
        self._attr_device_class = device_class
        if device_class:
            self._attr_native_unit_of_measurement = "Wh"
            self._attr_state_class = SensorStateClass.TOTAL
        else:
            self._attr_native_unit_of_measurement = "%"
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        energy = self.coordinator.data.get("energy_today", {}) if self.coordinator.data else {}
        v = energy.get(self._energy_key)
        if v is None:
            return None
        try:
            return round(float(v), 1)
        except (ValueError, TypeError):
            return None

    @property
    def extra_state_attributes(self) -> dict:
        return {"last_reset": "daily"}
