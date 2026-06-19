"""Shared Epson EH-LS12000 entity helpers."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import EpsonDataUpdateCoordinator


@dataclass(frozen=True)
class EpsonRuntimeData:
    """Runtime data stored on a config entry."""

    coordinator: EpsonDataUpdateCoordinator
    name: str


class EpsonEntity(CoordinatorEntity[EpsonDataUpdateCoordinator]):
    """Base class for Epson entities."""

    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry, runtime: EpsonRuntimeData) -> None:
        super().__init__(runtime.coordinator)
        self.entry = entry
        self.runtime = runtime

    @property
    def device_info(self) -> DeviceInfo:
        """Return projector device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.unique_id or self.entry.entry_id)},
            name=self.runtime.name,
            manufacturer=MANUFACTURER,
            model=MODEL,
        )
