"""Number settings for BB HEMS."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    OPT_BATTERY_DISCHARGE_LIMIT,
    OPT_FLEXIBLE_LOAD_POWER,
    OPT_GRID_HARD_IMPORT_LIMIT,
    OPT_GRID_IMPORT_LIMIT,
    OPT_HEATING_ROD_POWER,
    OPT_MIN_BATTERY_SOC,
    OPT_PROTECT_BATTERY_SOC,
    OPT_PV_AZIMUTH,
    OPT_PV_AVG_THRESHOLD,
    OPT_PV_TILT,
    OPT_PV_THRESHOLD,
)
from .coordinator import HemsCoordinator
from .entity import HemsEntity


@dataclass(frozen=True, kw_only=True)
class HemsNumberDescription(NumberEntityDescription):
    """Describes a writable HEMS number."""

    option_key: str


NUMBERS: tuple[HemsNumberDescription, ...] = (
    HemsNumberDescription(
        key="min_battery_soc",
        translation_key="min_battery_soc",
        option_key=OPT_MIN_BATTERY_SOC,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
    ),
    HemsNumberDescription(
        key="protect_battery_soc",
        translation_key="protect_battery_soc",
        option_key=OPT_PROTECT_BATTERY_SOC,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
    ),
    HemsNumberDescription(
        key="pv_threshold",
        translation_key="pv_threshold",
        option_key=OPT_PV_THRESHOLD,
        native_min_value=0,
        native_max_value=10000,
        native_step=10,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    HemsNumberDescription(
        key="pv_avg_threshold",
        translation_key="pv_avg_threshold",
        option_key=OPT_PV_AVG_THRESHOLD,
        native_min_value=0,
        native_max_value=10000,
        native_step=10,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    HemsNumberDescription(
        key="grid_import_limit",
        translation_key="grid_import_limit",
        option_key=OPT_GRID_IMPORT_LIMIT,
        native_min_value=-2000,
        native_max_value=5000,
        native_step=10,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    HemsNumberDescription(
        key="grid_hard_import_limit",
        translation_key="grid_hard_import_limit",
        option_key=OPT_GRID_HARD_IMPORT_LIMIT,
        native_min_value=0,
        native_max_value=10000,
        native_step=10,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    HemsNumberDescription(
        key="battery_discharge_limit",
        translation_key="battery_discharge_limit",
        option_key=OPT_BATTERY_DISCHARGE_LIMIT,
        native_min_value=0,
        native_max_value=10000,
        native_step=10,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    HemsNumberDescription(
        key="flexible_load_power",
        translation_key="flexible_load_power",
        option_key=OPT_FLEXIBLE_LOAD_POWER,
        native_min_value=0,
        native_max_value=10000,
        native_step=10,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    HemsNumberDescription(
        key="heating_rod_power",
        translation_key="heating_rod_power",
        option_key=OPT_HEATING_ROD_POWER,
        native_min_value=0,
        native_max_value=10000,
        native_step=10,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    HemsNumberDescription(
        key="pv_azimuth",
        translation_key="pv_azimuth",
        option_key=OPT_PV_AZIMUTH,
        native_min_value=0,
        native_max_value=360,
        native_step=1,
        icon="mdi:compass",
    ),
    HemsNumberDescription(
        key="pv_tilt",
        translation_key="pv_tilt",
        option_key=OPT_PV_TILT,
        native_min_value=0,
        native_max_value=90,
        native_step=1,
        icon="mdi:angle-acute",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HEMS number settings."""
    coordinator: HemsCoordinator = entry.runtime_data
    async_add_entities(HemsNumber(coordinator, description) for description in NUMBERS)


class HemsNumber(HemsEntity, NumberEntity):
    """Writable HEMS number setting."""

    entity_description: HemsNumberDescription

    def __init__(
        self, coordinator: HemsCoordinator, description: HemsNumberDescription
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float:
        """Return the stored option."""
        return float(self.coordinator.opts[self.entity_description.option_key])

    async def async_set_native_value(self, value: float) -> None:
        """Persist a new setting."""
        await self.coordinator.async_set_option(
            self.entity_description.option_key, float(value)
        )
