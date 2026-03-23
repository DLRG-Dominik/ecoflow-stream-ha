"""Konstanten für EcoFlow Stream Integration."""
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    UnitOfPower,
    UnitOfEnergy,
    UnitOfElectricPotential,
    UnitOfFrequency,
    UnitOfTemperature,
    PERCENTAGE,
    UnitOfTime,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
)

DOMAIN = "ecoflow_stream"
CONF_ACCESS_KEY = "access_key"
CONF_SECRET_KEY = "secret_key"
CONF_MAIN_SN = "main_sn"
CONF_SECONDARY_SN = "secondary_sn"

API_HOST = "https://api.ecoflow.com"
MQTT_HOST = "mqtt-e.ecoflow.com"
MQTT_PORT = 8883

UNKNOWN_PARAMS_FILE = "ecoflow_stream_unknown_params.json"

# ─────────────────────────────────────────────────────────────────────────────
# SENSOR-DEFINITIONEN
# Format: "mqtt_key": (name, unit, device_class, state_class, factor, icon)
#   factor = Multiplikator um auf die richtige Einheit zu kommen (z.B. mV→V: 0.001)
#   state_class = "measurement" für Echtzeit, "total_increasing" für Energie-Zähler
# ─────────────────────────────────────────────────────────────────────────────

SENSOR_DEFINITIONS = {
    # ── PV EINGANG ────────────────────────────────────────────────────────────
    "powGetPv": {
        "name": "PV Leistung MPPT1",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:solar-panel",
    },
    "powGetPv2": {
        "name": "PV Leistung MPPT2",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:solar-panel",
    },
    "powGetPv3": {
        "name": "PV Leistung MPPT3",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:solar-panel",
    },
    "powGetPv4": {
        "name": "PV Leistung MPPT4",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:solar-panel",
    },
    "plugInInfoPvVol": {
        "name": "PV Spannung MPPT1",
        "unit": UnitOfElectricPotential.VOLT,
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:solar-panel",
    },
    "plugInInfoPv2Vol": {
        "name": "PV Spannung MPPT2",
        "unit": UnitOfElectricPotential.VOLT,
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:solar-panel",
    },
    "plugInInfoPv3Vol": {
        "name": "PV Spannung MPPT3",
        "unit": UnitOfElectricPotential.VOLT,
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:solar-panel",
    },
    "plugInInfoPv4Vol": {
        "name": "PV Spannung MPPT4",
        "unit": UnitOfElectricPotential.VOLT,
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:solar-panel",
    },

    # ── SYSTEM GESAMT (vom AC Pro als Master) ────────────────────────────────
    "powGetPvSum": {
        "name": "PV Gesamtleistung (System)",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:solar-panel-large",
    },
    "sysGridConnectionPower": {
        "name": "Netzleistung System",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:transmission-tower",
    },
    "lanSysMeterValue": {
        "name": "LAN Smart Meter",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:meter-electric",
    },
    "cmsBattFullEnergy": {
        "name": "System Gesamtkapazität",
        "unit": UnitOfEnergy.WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY_STORAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:battery-high",
    },
    "cascadeSysSoc": {
        "name": "System SOC gesamt",
        "unit": PERCENTAGE,
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:battery",
    },
    "offgrid1ActivePower": {
        "name": "Offgrid Ausgang 1",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:power-socket-de",
    },
    "offgrid2ActivePower": {
        "name": "Offgrid Ausgang 2",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:power-socket-de",
    },
    "dcTemp1Ntc": {
        "name": "DC Temperatur 1",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:thermometer",
    },
    "dcTemp2Ntc": {
        "name": "DC Temperatur 2",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:thermometer",
    },
    "dcTemp3Ntc": {
        "name": "DC Temperatur 3",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:thermometer",
    },


    "gridConnectionPower": {
        "name": "Netz Leistung",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:transmission-tower",
    },
    "gridConnectionVol": {
        "name": "Netzspannung",
        "unit": UnitOfElectricPotential.VOLT,
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:sine-wave",
    },
    "gridConnectionFreq": {
        "name": "Netzfrequenz",
        "unit": UnitOfFrequency.HERTZ,
        "device_class": SensorDeviceClass.FREQUENCY,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:sine-wave",
    },
    "acTotalActivePower": {
        "name": "AC Gesamtleistung",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:lightning-bolt",
    },
    "powGetSysLoad": {
        "name": "Systemlast",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:home-lightning-bolt",
    },
    "powGetSysGrid": {
        "name": "Netzbezug",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:transmission-tower",
    },
    "powGetSysLoadFromGrid": {
        "name": "Last aus Netz",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:home-import-outline",
    },
    "powGetSysLoadFromPv": {
        "name": "Last aus PV",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:solar-power",
    },
    "powGetSysLoadFromBp": {
        "name": "Last aus Batterie",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:battery-arrow-down",
    },

    # ── AC STECKDOSEN ─────────────────────────────────────────────────────────
    "powGetSchuko1": {
        "name": "Schuko 1 Leistung",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:power-socket-de",
    },
    "powGetSchuko2": {
        "name": "Schuko 2 Leistung",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:power-socket-de",
    },

    # ── BATTERIE ECHTZEIT ─────────────────────────────────────────────────────
    "bmsBattSoc": {
        "name": "Batterie SOC",
        "unit": PERCENTAGE,
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:battery",
    },
    "bmsBattSoh": {
        "name": "Batterie Gesundheit (SOH)",
        "unit": PERCENTAGE,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:battery-heart",
    },
    "powGetBpCms": {
        "name": "Batterie Leistung",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:battery-charging",
    },
    "bmsChgRemTime": {
        "name": "Restladezeit",
        "unit": UnitOfTime.MINUTES,
        "device_class": SensorDeviceClass.DURATION,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:timer-outline",
    },
    "bmsDsgRemTime": {
        "name": "Restentladezeit",
        "unit": UnitOfTime.MINUTES,
        "device_class": SensorDeviceClass.DURATION,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:timer-outline",
    },
    "vBat": {
        "name": "Batteriespannung",
        "unit": UnitOfElectricPotential.VOLT,
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 0.001,
        "icon": "mdi:battery",
    },
    "cycles": {
        "name": "Ladezyklen",
        "unit": None,
        "device_class": None,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "factor": 1,
        "icon": "mdi:battery-sync",
    },
    "calendarSoh": {
        "name": "Kalender-SOH",
        "unit": PERCENTAGE,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:battery-heart-variant",
    },

    # ── ENERGIE-ZÄHLER (total_increasing → HA Energy Dashboard) ──────────────
    "pv_energy_total_wh": {
        "name": "PV Energie Gesamt",
        "unit": UnitOfEnergy.WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "factor": 1,
        "icon": "mdi:solar-power",
    },
    "accuChgEnergy": {
        "name": "Gesamt Ladeenergie",
        "unit": UnitOfEnergy.WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "factor": 1,
        "icon": "mdi:battery-plus",
    },
    "accuDsgEnergy": {
        "name": "Gesamt Entladeenergie",
        "unit": UnitOfEnergy.WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "factor": 1,
        "icon": "mdi:battery-minus",
    },

    # ── TEMPERATUREN ──────────────────────────────────────────────────────────
    "invTempNtc": {
        "name": "Inverter Temperatur",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:thermometer",
    },
    "bmsMaxCellTemp": {
        "name": "Max Zelltemperatur",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:thermometer-high",
    },
    "bmsMinCellTemp": {
        "name": "Min Zelltemperatur",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:thermometer-low",
    },
    "bmsMaxMosTemp": {
        "name": "MOS Temperatur",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:thermometer",
    },
    "dabHighTempNtc": {
        "name": "DAB Temperatur",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:thermometer",
    },

    # ── NETZWERK ──────────────────────────────────────────────────────────────
    "moduleWifiRssi": {
        "name": "WLAN Signal",
        "unit": SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        "device_class": SensorDeviceClass.SIGNAL_STRENGTH,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:wifi",
    },

    # ── SHELLY 3EM PHASENDATEN (aus cloudMetter) ──────────────────────────────
    "cloudMetter_phaseAPower": {
        "name": "Smart Meter Phase A",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:meter-electric",
    },
    "cloudMetter_phaseBPower": {
        "name": "Smart Meter Phase B",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:meter-electric",
    },
    "cloudMetter_phaseCPower": {
        "name": "Smart Meter Phase C",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "factor": 1,
        "icon": "mdi:meter-electric",
    },
}

# Binary Sensors
BINARY_SENSOR_DEFINITIONS = {
    "relay2Onoff": {
        "name": "AC1 Steckdose",
        "device_class": "outlet",
        "icon_on": "mdi:power-socket-de",
        "icon_off": "mdi:power-socket-de",
    },
    "relay3Onoff": {
        "name": "AC2 Steckdose",
        "device_class": "outlet",
        "icon_on": "mdi:power-socket-de",
        "icon_off": "mdi:power-socket-de",
    },
    "bmsBattHeating": {
        "name": "Batterie Heizung",
        "device_class": "heat",
        "icon_on": "mdi:heat-wave",
        "icon_off": "mdi:heat-wave",
    },
    "sysOffgrid": {
        "name": "Offgrid Modus",
        "device_class": "power",
        "icon_on": "mdi:home-off",
        "icon_off": "mdi:home-lightning-bolt",
    },
}

# Felder die nie als "unbekannt" gespeichert werden sollen (interne/Debug-Werte)
IGNORED_PARAMS = {
    "iotMemHeapSize", "iotMemInternalFreeSize", "iotLan1FsmState",
    "iotLan2LastRecvDataTime", "invStateMonitor1", "invStateMonitor2", "invStateMonitor3",
    "dabStateMonitor1", "dabStateMonitor2", "dabStateMonitor3",
    "bqSysStatReg", "mcuPinInStatus", "mcuPinOutStatus",
    "bsmSysEvent", "afeSysStatus", "bmsHeartbeatVer",
    "sysLoaderVer", "sysVer", "hwVer", "updateBanFlag",
    "pfcVbusTag", "vBusPidRef", "vBus", "vBusHv",
    "iDabLv", "pvIoutFilt", "dcvFilt", "dciFilt",
    "voltFreqfilter", "invIl1Rms", "invVcapRms",
    "ongridIinRms", "ongridVinRms", "ongridVoutRms",
    "ongridInActivePower", "ongridInReactivePower", "ongridActivePowerRef",
    "iinPv1", "iinPv2", "iinPv3", "iinPv4",
    "ioutBat", "pinPv1", "pinPv2", "pinPv3", "pinPv4",
    "vinPv1", "vinPv2", "vinPv3", "vinPv4", "pvIoutFilt",
    "bmsChgReqCurr", "bmsChgReqVolt",
    "tagChgAmp", "amp", "vol", "pwr12v",
    # AC Pro interne Felder
    "pvStateMonitor1", "pvStateMonitor2",
    "pv1InsRx", "pv2InsRx", "pv3InsRx", "pv4InsRx",
    "pv1GndInsRy", "pv2GndInsRy", "pv3GndInsRy", "pv4GndInsRy",
    "mpptPv1Fault", "mpptPv2Fault", "mpptPv3Fault", "mpptPv4Fault",
    "mpptFaultComm", "invCommFault", "invFault", "invFaultLock",
    "dabFault", "dabFaultLock", "pfcFault", "gridFault",
    "ref1P65", "ref2P5", "mosVolt",
    "dcToInvData", "invTodcData",
    "actPwrByUfip", "actPwrByFreqDroop", "actPwrByOfdp", "actPwrByOvdp",
    "actPwrByRampUp", "actPwrByPerc", "addPwrActLimit",
    "iotGatewayAddress", "iotIpAddress", "iotWifiBssid",
    "iotLan1MeshIdSummary", "iotLan2IdSummary", "iotLan2EncKeySummary",
    "iotLan1PlugCounts", "iotLan1PlugConsPwr", "iotLan1LastRecvDataTime",
    "iotLan2FsmState", "iotLan2DevOnlineCounts",
    "iotMqttState", "iotMqttErrType", "iotMqttErrReason",
    "iotBleState", "iotBleAuthState", "iotWifiState", "iotVersion",
    "iotShellyOnlineCounts", "iotShellyLastRecvDataTime", "iotShellyCfgDevCounts",
    "displayPropertyIncrementalUploadPeriod", "displayPropertyFullUploadPeriod",
    "runtimePropertyIncrementalUploadPeriod", "runtimePropertyFullUploadPeriod",
    "chgOverCurOffCnt", "chgPowerLoopRef", "emsPfcChgPwrTag",
    "reactPwrRefDelta", "cascadeSysOutputPwrDiff",
}
