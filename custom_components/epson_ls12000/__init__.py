"""Epson EH-LS12000 integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .api import EpsonWebClient
from .const import (
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USE_SSL,
    CONF_VERIFY_SSL,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_USE_SSL,
    DEFAULT_VERIFY_SSL,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import EpsonDataUpdateCoordinator
from .entity import EpsonRuntimeData

SERVICE_SEND_COMMAND = "send_command"
SERVICE_QUERY_COMMAND = "query_command"
SERVICE_SET_COMMAND = "set_command"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Epson EH-LS12000 from a config entry."""
    client = EpsonWebClient(
        hass=hass,
        host=entry.data[CONF_HOST],
        port=entry.data.get(CONF_PORT, DEFAULT_PORT),
        use_ssl=entry.data.get(CONF_USE_SSL, DEFAULT_USE_SSL),
        verify_ssl=entry.data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
        password=entry.data.get(CONF_PASSWORD),
    )
    coordinator = EpsonDataUpdateCoordinator(
        hass,
        client,
        entry.options.get(
            CONF_SCAN_INTERVAL,
            entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        ),
    )
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = EpsonRuntimeData(
        coordinator=coordinator,
        name=entry.data.get(CONF_NAME, DEFAULT_NAME),
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    _async_register_services(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Epson EH-LS12000 config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload entry after options changed."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


def _matching_runtimes(hass: HomeAssistant, entry_id: str | None) -> list[EpsonRuntimeData]:
    runtimes: list[EpsonRuntimeData] = []
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry_id and entry.entry_id != entry_id:
            continue
        runtime = getattr(entry, "runtime_data", None)
        if runtime is not None:
            runtimes.append(runtime)
    return runtimes


def _async_register_services(hass: HomeAssistant) -> None:
    """Register domain services once."""
    if hass.services.has_service(DOMAIN, SERVICE_SEND_COMMAND):
        return

    async def send_command(call: ServiceCall) -> None:
        for runtime in _matching_runtimes(hass, call.data.get("entry_id")):
            await runtime.coordinator.client.send_raw(call.data["command"])
            await runtime.coordinator.async_request_refresh()

    async def query_command(call: ServiceCall) -> None:
        for runtime in _matching_runtimes(hass, call.data.get("entry_id")):
            await runtime.coordinator.client.query(call.data["command"])
            await runtime.coordinator.async_request_refresh()

    async def set_command(call: ServiceCall) -> None:
        for runtime in _matching_runtimes(hass, call.data.get("entry_id")):
            await runtime.coordinator.client.set_command(
                call.data["command"], call.data["value"]
            )
            await runtime.coordinator.async_request_refresh()

    base_schema: dict[Any, Any] = {vol.Optional("entry_id"): cv.string}
    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_COMMAND,
        send_command,
        schema=vol.Schema({**base_schema, vol.Required("command"): cv.string}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_QUERY_COMMAND,
        query_command,
        schema=vol.Schema({**base_schema, vol.Required("command"): cv.string}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_COMMAND,
        set_command,
        schema=vol.Schema(
            {
                **base_schema,
                vol.Required("command"): cv.string,
                vol.Required("value"): cv.string,
            }
        ),
    )
