"""Number settings for BB HEMS."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import *
from .coordinator import HemsCoordinator
from .entity import HemsEntity


@dataclass(frozen=True, kw_only=True)
class HemsNumberDescription(NumberEntityDescription):
    option_key: str


NUMBERS = (
    HemsNumberDescription(key="min_battery_soc", translation_key="min_battery_soc", option_key=OPT_MIN_BATTERY_SOC, native_min_value=0, native_max_value=100, native_step=1, native_unit_of_measurement=PERCENTAGE),
    HemsNumberDescription(key="protect_battery_soc", translation_key="protect_battery_soc", option_key=OPT_PROTECT_BATTERY_SOC, native_min_value=0, native_max_value=100, native_step=1, native_unit_of_measurement=PERCENTAGE),
    HemsNumberDescription(key="pv_threshold", translation_key="pv_threshold", option_key=OPT_PV_THRESHOLD, native_min_value=0, native_max_value=10000, native_step=10, native_unit_of_measurement=UnitOfPower.WATT),
    HemsNumberDescription(key="pv_avg_threshold", translation_key="pv_avg_threshold", option_key=OPT_PV_AVG_THRESHOLD, native_min_value=0, native_max_value=10000, native_step=10, native_unit_of_measurement=UnitOfPower.WATT),
    HemsNumberDescription(key="grid_import_limit", translation_key="grid_import_limit", option_key=OPT_GRID_IMPORT_LIMIT, native_min_value=-2000, native_max_value=5000, native_step=10, native_unit_of_measurement=UnitOfPower.WATT),
    HemsNumberDescription(key="grid_hard_import_limit", translation_key="grid_hard_import_limit", option_key=OPT_GRID_HARD_IMPORT_LIMIT, native_min_value=0, native_max_value=10000, native_step=10, native_unit_of_measurement=UnitOfPower.WATT),
    HemsNumberDescription(key="battery_discharge_limit", translation_key="battery_discharge_limit", option_key=OPT_BATTERY_DISCHARGE_LIMIT, native_min_value=0, native_max_value=10000, native_step=10, native_unit_of_measurement=UnitOfPower.WATT),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: HemsCoordinator = entry.runtime_data
    async_add_entities(HemsNumber(coordinator, description) for description in NUMBERS)


class HemsNumber(HemsEntity, NumberEntity):
    entity_description: HemsNumberDescription

    def __init__(self, coordinator: HemsCoordinator, description: HemsNumberDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float:
        return float(self.coordinator.opts[self.entity_description.option_key])

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_option(self.entity_description.option_key, float(value))
