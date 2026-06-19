"""Config flow for Epson EH-LS12000."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import callback

from .api import EpsonConnectionError, EpsonWebClient
from .const import (
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USE_SSL,
    CONF_VERIFY_SSL,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SSL_PORT,
    DEFAULT_USE_SSL,
    DEFAULT_VERIFY_SSL,
    DOMAIN,
)


class EpsonConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle Epson EH-LS12000 config flow."""

    VERSION = 1
    CONNECTION_CLASS = "local_polling"

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle initial setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            client = EpsonWebClient(
                hass=self.hass,
                host=user_input[CONF_HOST],
                port=user_input[CONF_PORT],
                use_ssl=user_input[CONF_USE_SSL],
                verify_ssl=user_input[CONF_VERIFY_SSL],
                password=user_input.get(CONF_PASSWORD),
            )
            try:
                await client.test_connection()
            except EpsonConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(f"{DOMAIN}_{user_input[CONF_HOST]}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, DEFAULT_NAME),
                    data=user_input,
                )

        use_ssl = DEFAULT_USE_SSL
        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_SSL_PORT if use_ssl else DEFAULT_PORT): int,
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_USE_SSL, default=DEFAULT_USE_SSL): bool,
                vol.Required(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): bool,
                vol.Optional(CONF_PASSWORD): str,
                vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.Range(
                    min=10, max=3600
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Get options flow."""
        return EpsonOptionsFlow(config_entry)


class EpsonOptionsFlow(OptionsFlow):
    """Handle Epson options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL,
                            self.config_entry.data.get(
                                CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                            ),
                        ),
                    ): vol.Range(min=10, max=3600),
                }
            ),
        )
