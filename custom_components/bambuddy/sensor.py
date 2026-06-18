"""Senzori stanja štampača za Bambuddy."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    EntityCategory,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, PRINTER_STATES
from .coordinator import BambuddyCoordinator
from .entity import BambuddyEntity


def _temp(field: str) -> Callable[[dict], Any]:
    return lambda s: (s.get("temperatures") or {}).get(field)


@dataclass(frozen=True, kw_only=True)
class BambuddySensorDescription(SensorEntityDescription):
    """Opis senzora sa funkcijom za izvlačenje vrednosti iz statusa."""

    value_fn: Callable[[dict], Any]


SENSORS: tuple[BambuddySensorDescription, ...] = (
    BambuddySensorDescription(
        key="state",
        translation_key="state",
        icon="mdi:printer-3d",
        value_fn=lambda s: PRINTER_STATES.get(s.get("state"), s.get("state")),
    ),
    BambuddySensorDescription(
        key="subtask_name",
        translation_key="subtask_name",
        icon="mdi:file-document-outline",
        value_fn=lambda s: s.get("subtask_name"),
    ),
    BambuddySensorDescription(
        key="progress",
        translation_key="progress",
        icon="mdi:progress-clock",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: (
            round(s["progress"]) if s.get("progress") is not None else None
        ),
    ),
    BambuddySensorDescription(
        key="remaining_time",
        translation_key="remaining_time",
        icon="mdi:timer-sand",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        value_fn=lambda s: s.get("remaining_time"),
    ),
    BambuddySensorDescription(
        key="layer",
        translation_key="layer",
        icon="mdi:layers-triple",
        value_fn=lambda s: s.get("layer_num"),
    ),
    BambuddySensorDescription(
        key="total_layers",
        translation_key="total_layers",
        icon="mdi:layers-triple-outline",
        entity_registry_enabled_default=False,
        value_fn=lambda s: s.get("total_layers"),
    ),
    BambuddySensorDescription(
        key="nozzle_temp",
        translation_key="nozzle_temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_temp("nozzle"),
    ),
    BambuddySensorDescription(
        key="bed_temp",
        translation_key="bed_temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_temp("bed"),
    ),
    BambuddySensorDescription(
        key="chamber_temp",
        translation_key="chamber_temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_temp("chamber"),
    ),
    BambuddySensorDescription(
        key="wifi_signal",
        translation_key="wifi_signal",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda s: s.get("wifi_signal"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: BambuddyCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        BambuddySensor(coordinator, pid, desc)
        for pid in coordinator.data
        for desc in SENSORS
    ]
    async_add_entities(entities)


class BambuddySensor(BambuddyEntity, SensorEntity):
    """Pojedinačni senzor štampača."""

    entity_description: BambuddySensorDescription

    def __init__(
        self,
        coordinator: BambuddyCoordinator,
        printer_id: int,
        description: BambuddySensorDescription,
    ) -> None:
        super().__init__(coordinator, printer_id)
        self.entity_description = description
        self._attr_unique_id = f"{self._serial}_{description.key}"

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self._status)
