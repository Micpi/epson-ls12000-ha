"""Number entities for Epson EH-LS12000."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import EpsonEntity, EpsonRuntimeData


@dataclass(frozen=True, kw_only=True)
class EpsonNumberDescription(NumberEntityDescription):
    """Number description."""

    command: str


NUMBERS = [
    EpsonNumberDescription(
        key="brightness_level",
        name="Brightness Level",
        command="LUMLEVEL",
        native_min_value=0,
        native_max_value=100,
        native_step=1,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up numbers."""
    async_add_entities(
        EpsonNumber(entry, entry.runtime_data, description) for description in NUMBERS
    )


class EpsonNumber(EpsonEntity, NumberEntity):
    """ESC/VP21 backed number."""

    entity_description: EpsonNumberDescription

    def __init__(
        self,
        entry: ConfigEntry,
        runtime: EpsonRuntimeData,
        description: EpsonNumberDescription,
    ) -> None:
        super().__init__(entry, runtime)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> float | None:
        """Return current number value."""
        value = (self.coordinator.data or {}).get(self.entity_description.command)
        try:
            return float(value) if value is not None else None
        except ValueError:
            return None

    async def async_set_native_value(self, value: float) -> None:
        """Set value."""
        await self.coordinator.client.set_command(
            self.entity_description.command, int(value)
        )
        await self.coordinator.async_request_refresh()
