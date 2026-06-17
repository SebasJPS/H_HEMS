"""Number settings for BB HEMS."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    OPT_AC_BATTERY_NIGHT_DISCHARGE_W,
    OPT_BATTERY_DISCHARGE_LIMIT,
    OPT_BATTERY_CHARGE_RESERVE_CLOUDY,
    OPT_BATTERY_CHARGE_RESERVE_GOOD,
    OPT_BATTERY_CHARGE_SHARE_SOC,
    OPT_FLEXIBLE_LOAD_POWER,
    OPT_GRID_TOLERANCE_W,
    OPT_GRID_EXPORT_PRICE,
    OPT_GRID_HARD_IMPORT_LIMIT,
    OPT_GRID_IMPORT_LIMIT,
    OPT_GRID_IMPORT_PRICE,
    OPT_HEATING_ROD_POWER,
    OPT_HEATING_ROD_TEMPERATURE_HYSTERESIS,
    OPT_MANUAL_PAUSE_HOURS,
    OPT_MIN_BATTERY_SOC,
    OPT_PROTECT_BATTERY_SOC,
    OPT_PV_BATTERY_AC_CHARGE_THRESHOLD_SOC,
    OPT_PV_AVG_THRESHOLD,
    OPT_PV_THRESHOLD,
    OPT_START_ONLY_APPLIANCE_POWER,
    OPT_VIRTUAL_BATTERY_CAPACITY,
    OPT_VIRTUAL_BATTERY_CHARGE_EFFICIENCY,
    OPT_VIRTUAL_BATTERY_DISCHARGE_EFFICIENCY,
    OPT_VIRTUAL_BATTERY_MANUAL_SOC,
    OPT_VIRTUAL_BATTERY_MAX_SOC,
    OPT_VIRTUAL_BATTERY_MIN_SOC,
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
        key="battery_charge_share_soc",
        translation_key="battery_charge_share_soc",
        option_key=OPT_BATTERY_CHARGE_SHARE_SOC,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:battery-clock",
    ),
    HemsNumberDescription(
        key="battery_charge_reserve_good",
        translation_key="battery_charge_reserve_good",
        option_key=OPT_BATTERY_CHARGE_RESERVE_GOOD,
        native_min_value=0,
        native_max_value=100,
        native_step=5,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:battery-plus",
    ),
    HemsNumberDescription(
        key="battery_charge_reserve_cloudy",
        translation_key="battery_charge_reserve_cloudy",
        option_key=OPT_BATTERY_CHARGE_RESERVE_CLOUDY,
        native_min_value=0,
        native_max_value=100,
        native_step=5,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:weather-cloudy",
    ),
    HemsNumberDescription(
        key="grid_import_price",
        translation_key="grid_import_price",
        option_key=OPT_GRID_IMPORT_PRICE,
        native_min_value=0,
        native_max_value=5,
        native_step=0.01,
        native_unit_of_measurement="EUR/kWh",
        icon="mdi:cash-minus",
    ),
    HemsNumberDescription(
        key="grid_export_price",
        translation_key="grid_export_price",
        option_key=OPT_GRID_EXPORT_PRICE,
        native_min_value=0,
        native_max_value=5,
        native_step=0.01,
        native_unit_of_measurement="EUR/kWh",
        icon="mdi:cash-plus",
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
        key="start_only_appliance_power",
        translation_key="start_only_appliance_power",
        option_key=OPT_START_ONLY_APPLIANCE_POWER,
        native_min_value=0,
        native_max_value=10000,
        native_step=10,
        native_unit_of_measurement=UnitOfPower.WATT,
        icon="mdi:dishwasher",
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
        key="heating_rod_temperature_hysteresis",
        translation_key="heating_rod_temperature_hysteresis",
        option_key=OPT_HEATING_ROD_TEMPERATURE_HYSTERESIS,
        native_min_value=0,
        native_max_value=20,
        native_step=0.5,
        native_unit_of_measurement="°C",
        icon="mdi:thermometer-lines",
    ),
    HemsNumberDescription(
        key="virtual_battery_capacity",
        translation_key="virtual_battery_capacity",
        option_key=OPT_VIRTUAL_BATTERY_CAPACITY,
        native_min_value=0.1,
        native_max_value=500,
        native_step=0.1,
        native_unit_of_measurement="kWh",
        icon="mdi:battery-high",
    ),
    HemsNumberDescription(
        key="virtual_battery_min_soc",
        translation_key="virtual_battery_min_soc",
        option_key=OPT_VIRTUAL_BATTERY_MIN_SOC,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:battery-lock",
    ),
    HemsNumberDescription(
        key="virtual_battery_max_soc",
        translation_key="virtual_battery_max_soc",
        option_key=OPT_VIRTUAL_BATTERY_MAX_SOC,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:battery-lock-open",
    ),
    HemsNumberDescription(
        key="virtual_battery_manual_soc",
        translation_key="virtual_battery_manual_soc",
        option_key=OPT_VIRTUAL_BATTERY_MANUAL_SOC,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:battery-sync",
    ),
    HemsNumberDescription(
        key="virtual_battery_charge_efficiency",
        translation_key="virtual_battery_charge_efficiency",
        option_key=OPT_VIRTUAL_BATTERY_CHARGE_EFFICIENCY,
        native_min_value=50,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:battery-plus",
    ),
    HemsNumberDescription(
        key="virtual_battery_discharge_efficiency",
        translation_key="virtual_battery_discharge_efficiency",
        option_key=OPT_VIRTUAL_BATTERY_DISCHARGE_EFFICIENCY,
        native_min_value=50,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:battery-minus",
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
