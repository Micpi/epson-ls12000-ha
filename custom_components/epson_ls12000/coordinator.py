"""Data coordinator for Epson EH-LS12000."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EpsonClient, EpsonConnectionError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, QUERY_COMMANDS

_LOGGER = logging.getLogger(__name__)


class EpsonDataUpdateCoordinator(DataUpdateCoordinator[dict[str, str]]):
    """Keep projector state synchronized."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: EpsonClient,
        scan_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, str]:
        """Fetch projector state."""
        try:
            return await self.client.query_many(QUERY_COMMANDS)
        except EpsonConnectionError as exc:
            raise UpdateFailed(str(exc)) from exc
