"""EcoFlow API Client für REST und MQTT."""
import asyncio
import hashlib
import hmac
import json
import logging
import random
import ssl
import time
from typing import Any, Callable

import aiohttp
import paho.mqtt.client as mqtt

from .const import API_HOST, MQTT_HOST, MQTT_PORT

_LOGGER = logging.getLogger(__name__)


def _build_sign(access_key: str, secret_key: str, body_data: dict | None = None) -> dict:
    """HMAC-SHA256 Signatur nach EcoFlow-Doku.
    
    Für GET-Requests: body_data=None → nur accessKey/nonce/timestamp signieren.
    Für POST-Requests: body_data=dict → Felder flattened + sortiert in Signatur.
    Query-Parameter (z.B. sn bei GET) fließen NICHT in die Signatur ein!
    """
    nonce = str(random.randint(100000, 999999))
    timestamp = str(int(time.time() * 1000))

    data_str = ""
    if body_data:
        def flatten(obj: dict, prefix: str = "") -> dict:
            result = {}
            for k, v in obj.items():
                key = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    result.update(flatten(v, key))
                else:
                    result[key] = v
            return result
        flat = flatten(body_data)
        data_str = "&".join(f"{k}={flat[k]}" for k in sorted(flat.keys())) + "&"

    sign_str = f"{data_str}accessKey={access_key}&nonce={nonce}&timestamp={timestamp}"
    signature = hmac.new(secret_key.encode(), sign_str.encode(), hashlib.sha256).hexdigest()

    return {
        "accessKey": access_key,
        "nonce": nonce,
        "timestamp": timestamp,
        "sign": signature,
    }


class EcoFlowApiClient:
    """REST API Client."""

    def __init__(self, access_key: str, secret_key: str) -> None:
        self._access_key = access_key
        self._secret_key = secret_key
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    def _headers(self, body_data: dict | None = None) -> dict:
        """Headers mit Signatur. body_data nur für POST angeben, nie für GET-Query-Params!"""
        headers = _build_sign(self._access_key, self._secret_key, body_data)
        headers["Content-Type"] = "application/json;charset=UTF-8"
        return headers

    async def get_device_list(self) -> list[dict]:
        session = await self._get_session()
        async with session.get(
            f"{API_HOST}/iot-open/sign/device/list",
            headers=self._headers(None),
        ) as resp:
            data = await resp.json()
            if data.get("code") == "0":
                return data.get("data", [])
            _LOGGER.error("Geräteliste Fehler: %s", data)
            return []

    async def get_all_quota(self, sn: str) -> dict:
        session = await self._get_session()
        async with session.get(
            f"{API_HOST}/iot-open/sign/device/quota/all",
            params={"sn": sn},
            headers=self._headers(None),  # SN nicht in Signatur!
        ) as resp:
            data = await resp.json()
            if data.get("code") == "0":
                return data.get("data", {})
            _LOGGER.error("Quota Fehler: %s", data)
            return {}

    async def get_mqtt_credentials(self) -> dict | None:
        session = await self._get_session()
        async with session.get(
            f"{API_HOST}/iot-open/sign/certification",
            headers=self._headers(None),
        ) as resp:
            data = await resp.json()
            if data.get("code") == "0":
                return data.get("data")
            _LOGGER.error("MQTT Credentials Fehler: %s", data)
            return None

    async def validate_credentials(self) -> bool:
        try:
            devices = await self.get_device_list()
            return isinstance(devices, list)
        except Exception as ex:
            _LOGGER.error("Credentials ungültig: %s", ex)
            return False

    async def get_historical_data(self, sn: str, code: str, begin: str, end: str) -> list:
        """Historische Tagesdaten abrufen."""
        session = await self._get_session()
        payload = {
            "sn": sn,
            "params": {
                "beginTime": begin,
                "endTime": end,
                "code": code,
            },
        }
        async with session.post(
            f"{API_HOST}/iot-open/sign/device/quota/data",
            json=payload,
            headers=self._headers(payload),  # POST → body in Signatur
        ) as resp:
            data = await resp.json()
            if data.get("code") == "0":
                inner = data.get("data", {})
                if isinstance(inner, dict):
                    return inner.get("data", [])
            return []

    async def close(self) -> None:
        if self._session:
            await self._session.close()


class EcoFlowMqttClient:
    """MQTT Client für Echtzeit-Updates."""

    def __init__(
        self,
        cert_account: str,
        cert_password: str,
        sn_list: list[str],
        on_message_callback: Callable[[str, dict], None],
    ) -> None:
        self._cert_account = cert_account
        self._cert_password = cert_password
        self._sn_list = sn_list
        self._on_message = on_message_callback
        self._client: mqtt.Client | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

    def _on_connect(self, client, userdata, flags, rc, props=None):
        if rc == 0 or str(rc) == "Success":
            _LOGGER.info("EcoFlow MQTT verbunden")
            for sn in self._sn_list:
                for topic_type in ["quota", "status"]:
                    topic = f"/open/{self._cert_account}/{sn}/{topic_type}"
                    client.subscribe(topic)
                    _LOGGER.debug("Abonniert: %s", topic)
        else:
            _LOGGER.error("MQTT Verbindungsfehler: %s", rc)

    def _on_disconnect(self, client, userdata, rc, props=None, reason=None):
        _LOGGER.warning("MQTT getrennt (rc=%s), reconnect...", rc)

    def _on_mqtt_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            # SN aus Topic extrahieren: /open/{account}/{sn}/quota
            parts = msg.topic.split("/")
            sn = parts[3] if len(parts) >= 4 else "unknown"
            params = payload.get("params", payload)
            if isinstance(params, dict) and self._loop:
                asyncio.run_coroutine_threadsafe(
                    self._async_dispatch(sn, params), self._loop
                )
        except Exception as ex:
            _LOGGER.error("MQTT Parse-Fehler: %s", ex)

    async def _async_dispatch(self, sn: str, params: dict) -> None:
        self._on_message(sn, params)

    def start(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop
        client_id = f"ha_ecoflow_{random.randint(10000, 99999)}"
        self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
        self._client.username_pw_set(self._cert_account, self._cert_password)
        self._client.tls_set(cert_reqs=ssl.CERT_NONE)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_mqtt_message
        self._client.on_disconnect = self._on_disconnect
        self._client.reconnect_delay_set(min_delay=5, max_delay=60)
        try:
            self._client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
            self._client.loop_start()
            _LOGGER.info("MQTT Client gestartet")
        except Exception as ex:
            _LOGGER.error("MQTT Start-Fehler: %s", ex)

    def stop(self) -> None:
        if self._client:
            self._client.loop_stop()
            self._client.disconnect()
            _LOGGER.info("MQTT Client gestoppt")
