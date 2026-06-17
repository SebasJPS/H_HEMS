"""Number settings for BB HEMS slim v1."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    OPT_AC_BATTERY_NIGHT_DISCHARGE_W,
    OPT_DEHUMIDIFIER_POWER,
    OPT_GRID_TOLERANCE_W,
    OPT_MANUAL_PAUSE_HOURS,
    OPT_POOL_POWER,
    OPT_PV_BATTERY_AC_CHARGE_THRESHOLD_SOC,
    OPT_START_ONLY_APPLIANCE_POWER,
)
from .coordinator import HemsCoordinator
from .entity import HemsEntity


@dataclass(frozen=True, kw_only=True)
class HemsNumberDescription(NumberEntityDescription):
    """Describes a writable HEMS number."""

    option_key: str


NUMBERS: tuple[HemsNumberDescription, ...] = (
    HemsNumberDescription(
        key="grid_tolerance_w",
        translation_key="grid_tolerance_w",
        option_key=OPT_GRID_TOLERANCE_W,
        native_min_value=0,
        native_max_value=1000,
        native_step=10,
        native_unit_of_measurement=UnitOfPower.WATT,
        icon="mdi:transmission-tower-import",
    ),
    HemsNumberDescription(
        key="pv_battery_ac_charge_threshold_soc",
        translation_key="pv_battery_ac_charge_threshold_soc",
        option_key=OPT_PV_BATTERY_AC_CHARGE_THRESHOLD_SOC,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:battery-arrow-up",
    ),
    HemsNumberDescription(
        key="manual_pause_hours",
        translation_key="manual_pause_hours",
        option_key=OPT_MANUAL_PAUSE_HOURS,
        native_min_value=0.5,
        native_max_value=24,
        native_step=0.5,
        native_unit_of_measurement="h",
        icon="mdi:pause-circle",
    ),
    HemsNumberDescription(
        key="ac_battery_night_discharge_w",
        translation_key="ac_battery_night_discharge_w",
        option_key=OPT_AC_BATTERY_NIGHT_DISCHARGE_W,
        native_min_value=0,
        native_max_value=2000,
        native_step=10,
        native_unit_of_measurement=UnitOfPower.WATT,
        icon="mdi:weather-night",
    ),
    HemsNumberDescription(
        key="pool_power",
        translation_key="pool_power",
        option_key=OPT_POOL_POWER,
        native_min_value=0,
        native_max_value=10000,
        native_step=10,
        native_unit_of_measurement=UnitOfPower.WATT,
        icon="mdi:pool",
    ),
    HemsNumberDescription(
        key="dehumidifier_power",
        translation_key="dehumidifier_power",
        option_key=OPT_DEHUMIDIFIER_POWER,
        native_min_value=0,
        native_max_value=5000,
        native_step=10,
        native_unit_of_measurement=UnitOfPower.WATT,
        icon="mdi:air-humidifier-off",
    ),
    HemsNumberDescription(
        key="start_only_appliance_power",
        translation_key="start_only_appliance_power",
        option_key=OPT_START_ONLY_APPLIANCE_POWER,
        native_min_value=0,
        native_max_value=10000,
        native_step=10,
        native_unit_of_measurement=UnitOfPower.WATT,
        icon="mdi:dishwasher",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: HemsCoordinator = entry.runtime_data
    async_add_entities(HemsNumber(coordinator, description) for description in NUMBERS)


class HemsNumber(HemsEntity, NumberEntity):
    """Writable HEMS option."""

    entity_description: HemsNumberDescription

    def __init__(
        self, coordinator: HemsCoordinator, description: HemsNumberDescription
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float:
        return float(self.coordinator.opts[self.entity_description.option_key])

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_option(
            self.entity_description.option_key,
            round(float(value), 3),
        )
