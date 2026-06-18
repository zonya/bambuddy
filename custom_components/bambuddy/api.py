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

    @property
    def session(self) -> aiohttp.ClientSession:
        return self._session

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

    # --- Kamera (preko reusable stream-tokena, važi 60 min) ---

    async def create_stream_token(self) -> str:
        """Mintuj token za pristup kameri (snapshot/stream)."""
        url = f"{self._base}/api/v1/printers/camera/stream-token"
        try:
            async with self._session.post(
                url, headers=self._headers, timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                if resp.status in (401, 403):
                    raise BambuddyAuthError(f"Odbijen API ključ (HTTP {resp.status})")
                resp.raise_for_status()
                return (await resp.json())["token"]
        except aiohttp.ClientError as err:
            raise BambuddyApiError(f"Mrežna greška (stream-token): {err}") from err

    def snapshot_url(self, printer_id: int, token: str) -> str:
        return f"{self._base}/api/v1/printers/{printer_id}/camera/snapshot?token={token}"

    def stream_url(self, printer_id: int, token: str, fps: int = 10) -> str:
        return (
            f"{self._base}/api/v1/printers/{printer_id}/camera/stream"
            f"?token={token}&fps={fps}"
        )

    async def get_snapshot(self, printer_id: int, token: str) -> bytes | None:
        """Vrati JPEG snimak kamere, ili None ako nije dostupan."""
        try:
            async with self._session.get(
                self.snapshot_url(printer_id, token),
                timeout=aiohttp.ClientTimeout(total=20),
            ) as resp:
                if resp.status >= 400:
                    return None
                return await resp.read()
        except aiohttp.ClientError:
            return None
