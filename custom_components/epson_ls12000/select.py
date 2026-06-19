"""Select entities for Epson EH-LS12000."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ASPECT_NAMES,
    ASPECT_OPTIONS,
    COLOR_MODE_NAMES,
    COLOR_MODE_OPTIONS,
    LIGHT_SOURCE_MODE_NAMES,
    LIGHT_SOURCE_MODE_OPTIONS,
    SOURCE_NAMES,
    SOURCE_OPTIONS,
)
from .entity import EpsonEntity, EpsonRuntimeData


@dataclass(frozen=True, kw_only=True)
class EpsonSelectDescription(SelectEntityDescription):
    """Select description."""

    command: str
    options_to_values: dict[str, str]
    values_to_options: dict[str, str]


SELECTS = [
    EpsonSelectDescription(
        key="source",
        name="Source",
        command="SOURCE",
        options_to_values=SOURCE_OPTIONS,
        values_to_options=SOURCE_NAMES,
    ),
    EpsonSelectDescription(
        key="color_mode",
        name="Color Mode",
        command="CMODE",
        options_to_values=COLOR_MODE_OPTIONS,
        values_to_options=COLOR_MODE_NAMES,
    ),
    EpsonSelectDescription(
        key="aspect",
        name="Aspect",
        command="ASPECT",
        options_to_values=ASPECT_OPTIONS,
        values_to_options=ASPECT_NAMES,
    ),
    EpsonSelectDescription(
        key="light_source_mode",
        name="Light Source Mode",
        command="LUMINANCE",
        options_to_values=LIGHT_SOURCE_MODE_OPTIONS,
        values_to_options=LIGHT_SOURCE_MODE_NAMES,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up selects."""
    async_add_entities(
        EpsonSelect(entry, entry.runtime_data, description) for description in SELECTS
    )


class EpsonSelect(EpsonEntity, SelectEntity):
    """ESC/VP21 backed select."""

    entity_description: EpsonSelectDescription

    def __init__(
        self,
        entry: ConfigEntry,
        runtime: EpsonRuntimeData,
        description: EpsonSelectDescription,
    ) -> None:
        super().__init__(entry, runtime)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_options = list(description.options_to_values)

    @property
    def current_option(self) -> str | None:
        """Return selected option."""
        value = (self.coordinator.data or {}).get(self.entity_description.command)
        return self.entity_description.values_to_options.get(value or "")

    async def async_select_option(self, option: str) -> None:
        """Select option."""
        await self.coordinator.client.set_command(
            self.entity_description.command,
            self.entity_description.options_to_values[option],
        )
        await self.coordinator.async_request_refresh()
