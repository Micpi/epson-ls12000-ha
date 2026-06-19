"""Diagnostics for Epson EH-LS12000."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_PASSWORD


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    data = dict(entry.data)
    if CONF_PASSWORD in data:
        data[CONF_PASSWORD] = "**REDACTED**"
    runtime = getattr(entry, "runtime_data", None)
    return {
        "entry": data,
        "options": dict(entry.options),
        "state": runtime.coordinator.data if runtime else {},
    }
