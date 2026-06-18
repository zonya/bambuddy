"""Binarni senzori za Bambuddy (povezanost, vrata komore)."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import BambuddyCoordinator
from .entity import BambuddyEntity


@dataclass(frozen=True, kw_only=True)
class BambuddyBinaryDescription(BinarySensorEntityDescription):
    """Opis binarnog senzora sa funkcijom za vrednost."""

    value_fn: Callable[[dict], bool | None]


BINARY_SENSORS: tuple[BambuddyBinaryDescription, ...] = (
    BambuddyBinaryDescription(
        key="connected",
        translation_key="connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda p: p.get("status", {}).get("connected"),
    ),
    BambuddyBinaryDescription(
        key="door_open",
        translation_key="door_open",
        device_class=BinarySensorDeviceClass.DOOR,
        value_fn=lambda p: p.get("status", {}).get("door_open"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: BambuddyCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        BambuddyBinarySensor(coordinator, pid, desc)
        for pid in coordinator.data
        for desc in BINARY_SENSORS
    ]
    async_add_entities(entities)


class BambuddyBinarySensor(BambuddyEntity, BinarySensorEntity):
    """Binarni senzor štampača."""

    entity_description: BambuddyBinaryDescription

    def __init__(
        self,
        coordinator: BambuddyCoordinator,
        printer_id: int,
        description: BambuddyBinaryDescription,
    ) -> None:
        super().__init__(coordinator, printer_id)
        self.entity_description = description
        self._attr_unique_id = f"{self._serial}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        return self.entity_description.value_fn(self._printer)
