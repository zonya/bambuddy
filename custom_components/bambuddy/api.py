"""Tanki async klijent za Bambuddy REST API."""
from __future__ import annotations

import logging

import aiohttp

_LOGGER = logging.getLogger(__name__)


class BambuddyApiError(Exception):
    """Opšta greška u komunikaciji sa Bambuddy-jem."""


class BambuddyAuthError(BambuddyApiError):
    """Nevažeći / odbijen API ključ (401/403)."""


class BambuddyApi:
    """Čita podatke sa Bambuddy servera preko X-API-Key ključa."""

    def __init__(self, session: aiohttp.ClientSession, host: str, api_key: str) -> None:
        self._session = session
        self._base = host.rstrip("/")
        self._headers = {"X-API-Key": api_key}

    async def _get(self, path: str):
        url = f"{self._base}/api/v1{path}"
        try:
            async with self._session.get(
                url,
                headers=self._headers,
                timeout=aiohttp.ClientTimeout(total=20),
            ) as resp:
                if resp.status in (401, 403):
                    raise BambuddyAuthError(f"Odbijen API ključ (HTTP {resp.status})")
                if resp.status >= 400:
                    raise BambuddyApiError(f"HTTP {resp.status} za {path}")
                return await resp.json()
        except aiohttp.ClientError as err:
            raise BambuddyApiError(f"Mrežna greška: {err}") from err

    async def list_printers(self) -> list[dict]:
        """Vrati listu štampača definisanih na Bambuddy serveru."""
        data = await self._get("/printers/")
        return data if isinstance(data, list) else []

    async def get_status(self, printer_id: int) -> dict:
        """Vrati real-time status jednog štampača."""
        data = await self._get(f"/printers/{printer_id}/status")
        return data if isinstance(data, dict) else {}
