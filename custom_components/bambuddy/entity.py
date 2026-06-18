"""Zajednička bazna klasa za Bambuddy entitete."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_HOST, DOMAIN, MANUFACTURER
from .coordinator import BambuddyCoordinator


class BambuddyEntity(CoordinatorEntity[BambuddyCoordinator]):
    """Bazni entitet vezan za jedan štampač na Bambuddy serveru."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: BambuddyCoordinator, printer_id: int) -> None:
        super().__init__(coordinator)
        self._printer_id = printer_id
        info = self._info
        serial = info.get("serial_number") or f"printer_{printer_id}"
        self._serial = serial
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            name=info.get("name") or f"Bambuddy {printer_id}",
            manufacturer=MANUFACTURER,
            model=info.get("model"),
            serial_number=serial,
            configuration_url=coordinator._entry.data.get(CONF_HOST),
        )

    @property
    def _printer(self) -> dict:
        return self.coordinator.data.get(self._printer_id, {})

    @property
    def _info(self) -> dict:
        return self._printer.get("info", {})

    @property
    def _status(self) -> dict:
        return self._printer.get("status", {})

    @property
    def available(self) -> bool:
        return super().available and self._printer_id in self.coordinator.data
