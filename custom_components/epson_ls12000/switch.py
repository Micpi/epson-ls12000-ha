"""Switch entities for Epson EH-LS12000."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import EpsonEntity, EpsonRuntimeData


@dataclass(frozen=True, kw_only=True)
class EpsonSwitchDescription(SwitchEntityDescription):
    """Switch description."""

    command: str
    on_value: str = "ON"
    off_value: str = "OFF"


SWITCHES = [
    EpsonSwitchDescription(key="av_mute", name="A/V Mute", command="MUTE"),
    EpsonSwitchDescription(
        key="on_screen_display",
        name="On-Screen Display",
        command="ONSCREEN",
        on_value="01",
        off_value="00",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switches."""
    async_add_entities(
        EpsonSwitch(entry, entry.runtime_data, description) for description in SWITCHES
    )


class EpsonSwitch(EpsonEntity, SwitchEntity):
    """ESC/VP21 backed switch."""

    entity_description: EpsonSwitchDescription

    def __init__(
        self,
        entry: ConfigEntry,
        runtime: EpsonRuntimeData,
        description: EpsonSwitchDescription,
    ) -> None:
        super().__init__(entry, runtime)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        """Return switch state."""
        value = (self.coordinator.data or {}).get(self.entity_description.command)
        if value is None:
            return None
        return value == self.entity_description.on_value

    async def async_turn_on(self, **kwargs) -> None:
        """Turn switch on."""
        await self.coordinator.client.set_command(
            self.entity_description.command, self.entity_description.on_value
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn switch off."""
        await self.coordinator.client.set_command(
            self.entity_description.command, self.entity_description.off_value
        )
        await self.coordinator.async_request_refresh()
