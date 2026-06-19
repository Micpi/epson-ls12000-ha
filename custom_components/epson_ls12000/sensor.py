"""Sensor entities for Epson EH-LS12000."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ASPECT_NAMES,
    COLOR_MODE_NAMES,
    LIGHT_SOURCE_MODE_NAMES,
    POWER_STATES,
    QUERY_COMMANDS,
    SOURCE_NAMES,
)
from .entity import EpsonEntity, EpsonRuntimeData


@dataclass(frozen=True, kw_only=True)
class EpsonSensorDescription(SensorEntityDescription):
    """Sensor description."""

    command: str


SENSORS = [
    EpsonSensorDescription(key=command.lower(), name=command, command=command)
    for command in QUERY_COMMANDS
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors."""
    async_add_entities(
        EpsonSensor(entry, entry.runtime_data, description) for description in SENSORS
    )


class EpsonSensor(EpsonEntity, SensorEntity):
    """Raw command value sensor."""

    entity_description: EpsonSensorDescription

    def __init__(
        self,
        entry: ConfigEntry,
        runtime: EpsonRuntimeData,
        description: EpsonSensorDescription,
    ) -> None:
        super().__init__(entry, runtime)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> str | None:
        """Return command value."""
        value = (self.coordinator.data or {}).get(self.entity_description.command)
        if self.entity_description.command == "PWR":
            return POWER_STATES.get(value, value)
        if self.entity_description.command == "SOURCE":
            return SOURCE_NAMES.get(value, value)
        if self.entity_description.command == "CMODE":
            return COLOR_MODE_NAMES.get(value, value)
        if self.entity_description.command == "ASPECT":
            return ASPECT_NAMES.get(value, value)
        if self.entity_description.command == "LUMINANCE":
            return LIGHT_SOURCE_MODE_NAMES.get(value, value)
        return value
