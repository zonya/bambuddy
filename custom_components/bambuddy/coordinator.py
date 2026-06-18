"""DataUpdateCoordinator za Bambuddy — povlači sve štampače sa servera."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import BambuddyApi, BambuddyApiError, BambuddyAuthError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class BambuddyCoordinator(DataUpdateCoordinator[dict[int, dict]]):
    """Jedan koordinator po Bambuddy serveru; ključ podataka je printer_id."""

    def __init__(self, hass: HomeAssistant, api: BambuddyApi, entry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self._api = api
        self._entry = entry

    async def _async_update_data(self) -> dict[int, dict]:
        try:
            printers = await self._api.list_printers()
            result: dict[int, dict] = {}
            for info in printers:
                pid = info.get("id")
                if pid is None:
                    continue
                try:
                    status = await self._api.get_status(pid)
                except BambuddyApiError as err:
                    _LOGGER.debug("Status štampača %s nije dostupan: %s", pid, err)
                    status = {}
                result[pid] = {"info": info, "status": status}
            if not result:
                raise UpdateFailed("Bambuddy nije vratio nijedan štampač")
            return result
        except BambuddyAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except BambuddyApiError as err:
            raise UpdateFailed(str(err)) from err
