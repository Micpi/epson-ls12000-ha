"""Media player entity for Epson EH-LS12000."""

from __future__ import annotations

from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.components.media_player.const import MediaPlayerEntityFeature, MediaPlayerState
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import POWER_STATES, SOURCE_NAMES, SOURCE_OPTIONS
from .entity import EpsonEntity, EpsonRuntimeData


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Epson media player."""
    async_add_entities([EpsonProjectorMediaPlayer(entry, entry.runtime_data)])


class EpsonProjectorMediaPlayer(EpsonEntity, MediaPlayerEntity):
    """Media player for core projector controls."""

    _attr_name = None
    _attr_supported_features = (
        MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.SELECT_SOURCE
    )

    def __init__(self, entry: ConfigEntry, runtime: EpsonRuntimeData) -> None:
        super().__init__(entry, runtime)
        self._attr_unique_id = f"{entry.entry_id}_projector"
        self._attr_source_list = list(SOURCE_OPTIONS)

    @property
    def state(self) -> MediaPlayerState | None:
        """Return media player state."""
        power = (self.coordinator.data or {}).get("PWR")
        if power == "01":
            return MediaPlayerState.ON
        if power in {"00", "04", "05"}:
            return MediaPlayerState.OFF
        if power in {"02", "03"}:
            return MediaPlayerState.IDLE
        return None

    @property
    def source(self) -> str | None:
        """Return active source."""
        return SOURCE_NAMES.get((self.coordinator.data or {}).get("SOURCE", ""))

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return additional power details."""
        power = (self.coordinator.data or {}).get("PWR")
        return {"power_detail": POWER_STATES.get(power, power or "unknown")}

    async def async_turn_on(self) -> None:
        """Turn projector on."""
        await self.coordinator.client.set_command("PWR", "ON")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn projector off."""
        await self.coordinator.client.set_command("PWR", "OFF")
        await self.coordinator.async_request_refresh()

    async def async_select_source(self, source: str) -> None:
        """Select input source."""
        await self.coordinator.client.set_command("SOURCE", SOURCE_OPTIONS[source])
        await self.coordinator.async_request_refresh()
