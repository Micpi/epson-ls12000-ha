"""Button entities for Epson EH-LS12000."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import EpsonEntity, EpsonRuntimeData


@dataclass(frozen=True, kw_only=True)
class EpsonButtonDescription(ButtonEntityDescription):
    """Button description."""

    command: str


BUTTONS = [
    EpsonButtonDescription(key="lens_shift_up", name="Lens Shift Up", command="LENS INC"),
    EpsonButtonDescription(key="lens_shift_down", name="Lens Shift Down", command="LENS DEC"),
    EpsonButtonDescription(key="lens_shift_center", name="Lens Shift Center", command="LENS INIT"),
    EpsonButtonDescription(
        key="horizontal_lens_left", name="Horizontal Lens Left", command="HLENS DEC"
    ),
    EpsonButtonDescription(
        key="horizontal_lens_right", name="Horizontal Lens Right", command="HLENS INC"
    ),
    EpsonButtonDescription(
        key="horizontal_lens_center", name="Horizontal Lens Center", command="HLENS INIT"
    ),
]

for memory in range(1, 11):
    code = f"{memory:02d}"
    BUTTONS.append(
        EpsonButtonDescription(
            key=f"recall_lens_memory_{memory}",
            name=f"Recall Lens Memory {memory}",
            command=f"POPLP {code}",
        )
    )
    BUTTONS.append(
        EpsonButtonDescription(
            key=f"recall_memory_{memory}",
            name=f"Recall Memory {memory}",
            command=f"POPMEM 01 {code}",
        )
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up buttons."""
    async_add_entities(
        EpsonButton(entry, entry.runtime_data, description) for description in BUTTONS
    )


class EpsonButton(EpsonEntity, ButtonEntity):
    """ESC/VP21 backed button."""

    entity_description: EpsonButtonDescription

    def __init__(
        self,
        entry: ConfigEntry,
        runtime: EpsonRuntimeData,
        description: EpsonButtonDescription,
    ) -> None:
        super().__init__(entry, runtime)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

    async def async_press(self) -> None:
        """Send button command."""
        await self.coordinator.client.send_raw(self.entity_description.command)
        await self.coordinator.async_request_refresh()
