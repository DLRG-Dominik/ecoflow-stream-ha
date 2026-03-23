"""EcoFlow Stream Binary Sensoren."""
import logging
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, BINARY_SENSOR_DEFINITIONS, CONF_MAIN_SN
from .coordinator import EcoFlowCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: EcoFlowCoordinator = hass.data[DOMAIN][entry.entry_id]
    main_sn = entry.data[CONF_MAIN_SN]

    entities = [
        EcoFlowBinarySensor(coordinator, entry, main_sn, key, definition)
        for key, definition in BINARY_SENSOR_DEFINITIONS.items()
    ]

    # Dynamischer "Einspeisung aktiv" Sensor
    entities.append(EcoFlowFeedingGridSensor(coordinator, entry, main_sn))
    entities.append(EcoFlowChargingSensor(coordinator, entry, main_sn))

    async_add_entities(entities)


class EcoFlowBinarySensor(CoordinatorEntity, BinarySensorEntity):

    def __init__(self, coordinator, entry, main_sn, key, definition):
        super().__init__(coordinator)
        self._key = key
        self._definition = definition
        self._attr_unique_id = f"{main_sn}_{key}_binary"
        self._attr_name = definition["name"]
        self._attr_device_class = definition["device_class"]

    @property
    def device_info(self) -> DeviceInfo:
        main_sn = self._attr_unique_id.split("_")[0] + "_" + self._attr_unique_id.split("_")[1]
        return DeviceInfo(
            identifiers={(DOMAIN, self._attr_unique_id.rsplit("_", 2)[0])},
            name="EcoFlow Stream Ultra X",
            manufacturer="EcoFlow",
            model="STREAM Ultra X",
        )

    @property
    def is_on(self) -> bool | None:
        realtime = self.coordinator.data.get("realtime", {}) if self.coordinator.data else {}
        v = realtime.get(self._key)
        if v is None:
            return None
        if isinstance(v, bool):
            return v
        return str(v).lower() in ("true", "1", "on")

    @property
    def icon(self) -> str:
        return self._definition["icon_on"] if self.is_on else self._definition["icon_off"]

    @property
    def available(self) -> bool:
        realtime = self.coordinator.data.get("realtime", {}) if self.coordinator.data else {}
        return self._key in realtime


class EcoFlowFeedingGridSensor(CoordinatorEntity, BinarySensorEntity):
    """Zeigt ob das System gerade ins Netz einspeist."""

    def __init__(self, coordinator, entry, main_sn):
        super().__init__(coordinator)
        self._main_sn = main_sn
        self._attr_unique_id = f"{main_sn}_feeding_grid"
        self._attr_name = "Einspeisung aktiv"
        self._attr_device_class = "power"
        self._attr_icon = "mdi:transmission-tower-export"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._main_sn)},
            name=f"EcoFlow Stream Ultra X ({self._main_sn[-4:]})",
            manufacturer="EcoFlow",
            model="STREAM Ultra X",
        )

    @property
    def is_on(self) -> bool | None:
        realtime = self.coordinator.data.get("realtime", {}) if self.coordinator.data else {}
        status = realtime.get("gridConnectionSta")
        if status is None:
            return None
        return status == "PANEL_FEED_GRID"


class EcoFlowChargingSensor(CoordinatorEntity, BinarySensorEntity):
    """Zeigt ob die Batterie gerade lädt."""

    def __init__(self, coordinator, entry, main_sn):
        super().__init__(coordinator)
        self._main_sn = main_sn
        self._attr_unique_id = f"{main_sn}_charging"
        self._attr_name = "Batterie lädt"
        self._attr_device_class = "battery_charging"
        self._attr_icon = "mdi:battery-charging"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._main_sn)},
            name=f"EcoFlow Stream Ultra X ({self._main_sn[-4:]})",
            manufacturer="EcoFlow",
            model="STREAM Ultra X",
        )

    @property
    def is_on(self) -> bool | None:
        realtime = self.coordinator.data.get("realtime", {}) if self.coordinator.data else {}
        state = realtime.get("bmsChgDsgState")
        if state is None:
            return None
        # 1 = lädt, 2 = entlädt, 0 = idle
        return int(state) == 1
