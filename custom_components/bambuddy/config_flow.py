"""Config flow za Bambuddy."""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import BambuddyApi, BambuddyApiError, BambuddyAuthError
from .const import CONF_API_KEY, CONF_HOST, DEFAULT_HOST, DOMAIN

_LOGGER = logging.getLogger(__name__)

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_API_KEY): str,
    }
)


class BambuddyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].rstrip("/")
            session = async_get_clientsession(self.hass)
            api = BambuddyApi(session, host, user_input[CONF_API_KEY])
            try:
                printers = await api.list_printers()
            except BambuddyAuthError:
                errors["base"] = "invalid_auth"
            except BambuddyApiError as err:
                _LOGGER.error("Bambuddy cannot_connect: %s", err)
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Bambuddy neočekivana greška pri konekciji")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured()
                count = len(printers)
                suffix = "štampač" if count == 1 else "štampača"
                return self.async_create_entry(
                    title=f"Bambuddy ({count} {suffix})",
                    data={CONF_HOST: host, CONF_API_KEY: user_input[CONF_API_KEY]},
                )

        return self.async_show_form(
            step_id="user", data_schema=USER_SCHEMA, errors=errors
        )
