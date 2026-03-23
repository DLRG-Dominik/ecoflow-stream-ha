"""EcoFlow Stream Datenkoordinator."""
import asyncio
import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EcoFlowApiClient, EcoFlowMqttClient
from .const import (
    DOMAIN,
    SENSOR_DEFINITIONS,
    BINARY_SENSOR_DEFINITIONS,
    IGNORED_PARAMS,
    UNKNOWN_PARAMS_FILE,
)

_LOGGER = logging.getLogger(__name__)

# Historische Energie-Codes (BKW = Balkonkraftwerk)
ENERGY_CODES = {
    "solar_energy_wh": "BK621-App-HOME-SOLAR-ENERGY-FLOW-solor-line-NOTDISTINGUISH-MASTER_DATA",
    "load_energy_wh": "BK621-App-HOME-LOAD-ENERGY-FLOW-consumption-prop_arc-NOTDISTINGUISH-MASTER_DATA",
    "grid_energy_wh": "BK621-App-HOME-GRID-ENERGY-FLOW-grid_prop_bar-NOTDISTINGUISH-MASTER_DATA",
    "battery_energy_wh": "BK621-App-HOME-SOC-ENERGY-FLOW-battery-prop_bar-NOTDISTINGUISH-MASTER_DATA",
    "independence_pct": "BK621-App-HOME-INDEPENDENCE-PERCENT-FLOW-indep-progress_bar-NOTDISTINGUISH-MASTER_DATA",
}


class EcoFlowCoordinator(DataUpdateCoordinator):
    """Koordiniert REST-Polling + MQTT-Push."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: EcoFlowApiClient,
        main_sn: str,
        secondary_sn: str | None,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        self.api = api
        self.main_sn = main_sn
        self.secondary_sn = secondary_sn
        self.mqtt_client: EcoFlowMqttClient | None = None

        # Echtzeit-Daten (MQTT)
        self.realtime_data: dict[str, Any] = {}
        # Tagesdaten (REST historical)
        self.energy_today: dict[str, Any] = {}
        # Alle unbekannten Parameter speichern
        self._unknown_params: dict[str, Any] = {}
        self._unknown_params_path = hass.config.path(UNKNOWN_PARAMS_FILE)
        self._load_unknown_params()

        # Kumulativer PV-Energiezähler
        self._pv_energy_path = hass.config.path("ecoflow_stream_pv_energy.json")
        self._pv_energy_wh: float = 0.0
        self._last_pv_update: datetime | None = None
        self._load_pv_energy()

    def _load_pv_energy(self) -> None:
        """Kumulativen PV-Energiezähler laden."""
        try:
            if os.path.exists(self._pv_energy_path):
                with open(self._pv_energy_path, "r") as f:
                    data = json.load(f)
                    self._pv_energy_wh = float(data.get("pv_energy_wh", 0.0))
                _LOGGER.debug("PV-Energiezähler geladen: %.1f Wh", self._pv_energy_wh)
        except Exception as ex:
            _LOGGER.warning("PV-Energiezähler konnte nicht geladen werden: %s", ex)

    def _save_pv_energy(self) -> None:
        """Kumulativen PV-Energiezähler speichern."""
        try:
            with open(self._pv_energy_path, "w") as f:
                json.dump({"pv_energy_wh": self._pv_energy_wh}, f)
        except Exception as ex:
            _LOGGER.warning("PV-Energiezähler konnte nicht gespeichert werden: %s", ex)

    def _update_pv_energy(self, params: dict) -> None:
        """PV-Energie aus aktueller MQTT-Nachricht hochzählen."""
        # PV-Gesamtleistung aus powGetPvSum (AC Pro Master) oder Summe der MPPTs
        pv_power = 0.0
        if "powGetPvSum" in params:
            pv_power = float(params["powGetPvSum"])
        else:
            for key in ["powGetPv", "powGetPv2", "powGetPv3", "powGetPv4"]:
                if key in params:
                    pv_power += float(params[key])

        if pv_power <= 0:
            return

        now = datetime.now()
        if self._last_pv_update is not None:
            elapsed_seconds = (now - self._last_pv_update).total_seconds()
            # Maximal 120 Sekunden berücksichtigen (verhindert Sprünge nach Verbindungsabbruch)
            elapsed_seconds = min(elapsed_seconds, 120)
            energy_delta_wh = pv_power * elapsed_seconds / 3600
            self._pv_energy_wh += energy_delta_wh
            self._save_pv_energy()

        self._last_pv_update = now
        self.realtime_data["pv_energy_total_wh"] = round(self._pv_energy_wh, 1)

    def _load_unknown_params(self) -> None:
        """Gespeicherte unbekannte Parameter laden."""
        try:
            if os.path.exists(self._unknown_params_path):
                with open(self._unknown_params_path, "r") as f:
                    self._unknown_params = json.load(f)
                _LOGGER.debug("Unbekannte Parameter geladen: %d", len(self._unknown_params))
        except Exception as ex:
            _LOGGER.warning("Unbekannte Parameter konnten nicht geladen werden: %s", ex)

    def _save_unknown_params(self) -> None:
        """Unbekannte Parameter speichern."""
        try:
            with open(self._unknown_params_path, "w") as f:
                json.dump(self._unknown_params, f, indent=2, default=str)
        except Exception as ex:
            _LOGGER.warning("Unbekannte Parameter konnten nicht gespeichert werden: %s", ex)

    def _process_mqtt_params(self, sn: str, params: dict) -> None:
        """MQTT-Nachricht verarbeiten und unbekannte Parameter erkennen."""
        known_keys = set(SENSOR_DEFINITIONS.keys()) | set(BINARY_SENSOR_DEFINITIONS.keys()) | IGNORED_PARAMS
        # cloudMetter Unterfelder
        known_keys |= {"cloudMetter_phaseAPower", "cloudMetter_phaseBPower", "cloudMetter_phaseCPower"}

        new_unknown = False
        for key, value in params.items():
            # cloudMetter aufdröseln
            if key == "cloudMetter" and isinstance(value, dict):
                self.realtime_data["cloudMetter_phaseAPower"] = value.get("phaseAPower", 0)
                self.realtime_data["cloudMetter_phaseBPower"] = value.get("phaseBPower", 0)
                self.realtime_data["cloudMetter_phaseCPower"] = value.get("phaseCPower", 0)
                continue

            # Normalen Wert speichern
            self.realtime_data[key] = value

            # Unbekannte Parameter erkennen
            if key not in known_keys and not isinstance(value, (dict, list)):
                if key not in self._unknown_params:
                    _LOGGER.info("Neuer unbekannter Parameter entdeckt: %s = %s", key, value)
                    new_unknown = True
                self._unknown_params[key] = {
                    "value": value,
                    "sn": sn,
                    "last_seen": datetime.now().isoformat(),
                }

        if new_unknown:
            self._save_unknown_params()

        # PV-Energiezähler aktualisieren
        self._update_pv_energy(params)

        # HA Update anstoßen
        self.hass.loop.call_soon_threadsafe(
            lambda: self.hass.async_create_task(self._async_update_listeners())
        )

    async def _async_update_listeners(self) -> None:
        """Alle Listener über neue Daten informieren."""
        self.async_set_updated_data(self._get_combined_data())

    def _get_combined_data(self) -> dict:
        return {
            "realtime": self.realtime_data,
            "energy_today": self.energy_today,
        }

    async def setup_mqtt(self) -> None:
        """MQTT Client einrichten und starten."""
        try:
            creds = await self.api.get_mqtt_credentials()
            if not creds:
                _LOGGER.error("Keine MQTT Credentials erhalten")
                return

            sn_list = [self.main_sn]
            if self.secondary_sn:
                sn_list.append(self.secondary_sn)

            self.mqtt_client = EcoFlowMqttClient(
                cert_account=creds["certificateAccount"],
                cert_password=creds["certificatePassword"],
                sn_list=sn_list,
                on_message_callback=self._process_mqtt_params,
            )
            self.mqtt_client.start(self.hass.loop)
            _LOGGER.info("MQTT für %d Gerät(e) gestartet", len(sn_list))
        except Exception as ex:
            _LOGGER.error("MQTT Setup Fehler: %s", ex)

    async def _async_update_data(self) -> dict:
        """REST-Polling: Quota + historische Tagesdaten."""
        try:
            # Quota abrufen (15 offizielle Felder)
            quota = await self.api.get_all_quota(self.main_sn)
            for key, value in quota.items():
                self.realtime_data[key] = value

            # Historische Tagesdaten abrufen
            await self._fetch_energy_today()

            return self._get_combined_data()
        except Exception as ex:
            raise UpdateFailed(f"EcoFlow Update Fehler: {ex}") from ex

    async def _fetch_energy_today(self) -> None:
        """Energie-Tagesdaten abrufen."""
        now = datetime.now(timezone.utc)
        begin = now.strftime("%Y-%m-%d 00:00:00")
        end = now.strftime("%Y-%m-%d 23:59:59")

        for metric_key, code in ENERGY_CODES.items():
            try:
                result = await self.api.get_historical_data(
                    self.main_sn, code, begin, end
                )
                if result:
                    # Summiere alle indexValues des Tages
                    total = sum(
                        float(item.get("indexValue", 0))
                        for item in result
                        if item.get("indexValue") is not None
                    )
                    self.energy_today[metric_key] = total
            except Exception as ex:
                _LOGGER.debug("Tagesdaten für %s nicht verfügbar: %s", metric_key, ex)

    def get_unknown_params(self) -> dict:
        """Alle unbekannten Parameter zurückgeben."""
        return self._unknown_params.copy()

    def stop(self) -> None:
        if self.mqtt_client:
            self.mqtt_client.stop()
