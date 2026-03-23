"""EcoFlow Stream Integration für Home Assistant."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import EcoFlowApiClient
from .const import DOMAIN, CONF_ACCESS_KEY, CONF_SECRET_KEY, CONF_MAIN_SN, CONF_SECONDARY_SN
from .coordinator import EcoFlowCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Integration einrichten."""
    api = EcoFlowApiClient(
        entry.data[CONF_ACCESS_KEY],
        entry.data[CONF_SECRET_KEY],
    )

    secondary_sn = entry.data.get(CONF_SECONDARY_SN) or None
    if secondary_sn == "":
        secondary_sn = None

    coordinator = EcoFlowCoordinator(
        hass=hass,
        api=api,
        main_sn=entry.data[CONF_MAIN_SN],
        secondary_sn=secondary_sn,
    )

    # Erster Datenabruf
    await coordinator.async_config_entry_first_refresh()

    # MQTT starten
    await coordinator.setup_mqtt()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _LOGGER.info(
        "EcoFlow Stream eingerichtet: Hauptgerät=%s, Sekundärgerät=%s",
        entry.data[CONF_MAIN_SN],
        secondary_sn,
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Integration entfernen."""
    coordinator: EcoFlowCoordinator = hass.data[DOMAIN][entry.entry_id]
    coordinator.stop()

    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded
