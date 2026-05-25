"""Binary sensors for JPS HEMS."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import HemsCoordinator, HemsData
from .entity import HemsEntity


@dataclass(frozen=True, kw_only=True)
class HemsBinarySensorDescription(BinarySensorEntityDescription):
    """Describes a HEMS binary sensor."""

    value_fn: Callable[[HemsData], bool]


BINARY_SENSORS: tuple[HemsBinarySensorDescription, ...] = (
    HemsBinarySensorDescription(
        key="surplus_available",
        translation_key="surplus_available",
        device_class=BinarySensorDeviceClass.POWER,
        value_fn=lambda data: data.surplus_available,
    ),
    HemsBinarySensorDescription(
        key="battery_protect",
        translation_key="battery_protect",
        device_class=BinarySensorDeviceClass.SAFETY,
        value_fn=lambda data: data.battery_protect,
    ),
    HemsBinarySensorDescription(
        key="good_weather",
        translation_key="good_weather",
        icon="mdi:weather-sunny",
        value_fn=lambda data: data.good_weather,
    ),
    HemsBinarySensorDescription(
        key="flexible_loads_allowed",
        translation_key="flexible_loads_allowed",
        device_class=BinarySensorDeviceClass.RUNNING,
        value_fn=lambda data: data.flexible_loads_allowed,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensors."""
    coordinator: HemsCoordinator = entry.runtime_data
    async_add_entities(
        HemsBinarySensor(coordinator, description) for description in BINARY_SENSORS
    )


class HemsBinarySensor(HemsEntity, BinarySensorEntity):
    """Computed HEMS binary sensor."""

    entity_description: HemsBinarySensorDescription

    def __init__(
        self, coordinator: HemsCoordinator, description: HemsBinarySensorDescription
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool:
        """Return if this decision is active."""
        return self.entity_description.value_fn(self.coordinator.data)
