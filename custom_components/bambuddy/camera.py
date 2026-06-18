"""Kamera štampača za Bambuddy (MJPEG live + JPEG snapshot preko stream-tokena)."""
from __future__ import annotations

import time

from aiohttp import web
from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import BambuddyApiError
from .const import DOMAIN
from .coordinator import BambuddyCoordinator
from .entity import BambuddyEntity

# Token važi 60 min na serveru; obnavljamo ga malo ranije.
_TOKEN_TTL = 3000.0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: BambuddyCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        BambuddyCamera(coordinator, pid) for pid in coordinator.data
    )


class BambuddyCamera(BambuddyEntity, Camera):
    """Kamera jednog štampača."""

    _attr_translation_key = "camera"

    def __init__(self, coordinator: BambuddyCoordinator, printer_id: int) -> None:
        super().__init__(coordinator, printer_id)
        Camera.__init__(self)
        self._attr_unique_id = f"{self._serial}_camera"
        self._token: str | None = None
        self._token_exp = 0.0

    async def _token_value(self) -> str:
        now = time.monotonic()
        if self._token and now < self._token_exp:
            return self._token
        self._token = await self.coordinator._api.create_stream_token()
        self._token_exp = now + _TOKEN_TTL
        return self._token

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        try:
            token = await self._token_value()
            return await self.coordinator._api.get_snapshot(self._printer_id, token)
        except BambuddyApiError:
            self._token = None
            return None

    async def handle_async_mjpeg_stream(self, request: web.Request) -> web.StreamResponse:
        """Proksiraj MJPEG stream sa Bambuddy-ja ka HA frontendu."""
        try:
            token = await self._token_value()
        except BambuddyApiError:
            self._token = None
            return web.Response(status=502)

        url = self.coordinator._api.stream_url(self._printer_id, token)
        session = self.coordinator._api.session
        upstream = await session.get(url)
        if upstream.status >= 400:
            upstream.close()
            self._token = None
            return web.Response(status=upstream.status)

        response = web.StreamResponse(
            status=200,
            headers={
                "Content-Type": upstream.headers.get(
                    "Content-Type", "multipart/x-mixed-replace; boundary=frame"
                )
            },
        )
        await response.prepare(request)
        try:
            async for chunk in upstream.content.iter_any():
                await response.write(chunk)
        except (ConnectionResetError, ConnectionError):
            pass
        finally:
            upstream.close()
        return response
