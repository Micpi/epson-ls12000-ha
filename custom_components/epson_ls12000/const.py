"""Constants for the Epson EH-LS12000 integration."""

from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "epson_ls12000"
MANUFACTURER = "Epson"
MODEL = "EH-LS12000"

CONF_USE_SSL = "use_ssl"
CONF_VERIFY_SSL = "verify_ssl"
CONF_PASSWORD = "password"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_CONNECTION_TYPE = "connection_type"

CONNECTION_TCP = "tcp"
CONNECTION_WEB_API = "web_api"
CONNECTION_TYPES = [CONNECTION_TCP, CONNECTION_WEB_API]

DEFAULT_NAME = "Epson EH-LS12000"
DEFAULT_PORT = 3629
DEFAULT_WEB_API_PORT = 80
DEFAULT_SSL_PORT = 443
DEFAULT_TIMEOUT = 5.0
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_USE_SSL = False
DEFAULT_VERIFY_SSL = True
AUTH_USERNAME = "EPSONWEB"

PLATFORMS: list[Platform] = [
    Platform.MEDIA_PLAYER,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.SELECT,
    Platform.NUMBER,
    Platform.BUTTON,
]

POWER_STATES = {
    "00": "standby",
    "01": "on",
    "02": "warmup",
    "03": "cooldown",
    "04": "standby_network",
    "05": "abnormal_standby",
}

SOURCE_OPTIONS = {
    "HDMI1": "30",
    "HDMI2": "A0",
}
SOURCE_NAMES = {value: key for key, value in SOURCE_OPTIONS.items()}

MUTE_OPTIONS = {"Off": "OFF", "On": "ON"}
ONSCREEN_OPTIONS = {"Off": "00", "On": "01"}

COLOR_MODE_OPTIONS = {
    "Dynamic": "07",
    "Vivid": "0B",
    "Bright Cinema": "0C",
    "Cinema": "15",
    "Natural": "17",
    "B&W Cinema": "18",
    "Digital Cinema": "19",
}
COLOR_MODE_NAMES = {value: key for key, value in COLOR_MODE_OPTIONS.items()}

ASPECT_OPTIONS = {
    "Auto": "00",
    "Normal": "10",
    "Full": "20",
    "Zoom": "30",
    "Anamorphic Wide": "40",
    "Horiz. Squeeze": "50",
}
ASPECT_NAMES = {value: key for key, value in ASPECT_OPTIONS.items()}

LIGHT_SOURCE_MODE_OPTIONS = {
    "Dynamic": "00",
    "Quiet": "01",
    "Extended": "03",
    "Custom": "05",
}
LIGHT_SOURCE_MODE_NAMES = {
    value: key for key, value in LIGHT_SOURCE_MODE_OPTIONS.items()
}

QUERY_COMMANDS = [
    "PWR",
    "SOURCE",
    "MUTE",
    "ONSCREEN",
    "CMODE",
    "ASPECT",
    "LUMINANCE",
    "LUMLEVEL",
    "LAMP",
    "LENS",
    "HLENS",
]
