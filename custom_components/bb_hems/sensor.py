"""Sensors for BB HEMS slim v1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_AC_BATTERY_PROFILES,
    CONF_BATTERY_DISCHARGE_SENSORS,
    CONF_BATTERY_SOC_SENSORS,
    CONF_DEHUMIDIFIER_POWER_SENSORS,
    CONF_DEHUMIDIFIER_SWITCHES,
    CONF_GRID_EXPORT_POWER_SENSORS,
    CONF_GRID_IMPORT_POWER_SENSORS,
    CONF_GRID_POWER_SENSOR,
    CONF_GRID_SIGNED_EXPORT_POSITIVE_SENSORS,
    CONF_GRID_SIGNED_IMPORT_POSITIVE_SENSORS,
    CONF_HOUSE_LOAD_SENSORS,
    CONF_POOL_POWER_SENSORS,
    CONF_POOL_SWITCHES,
    CONF_PV_POWER_SENSORS,
    CONF_START_ONLY_APPLIANCE_POWER_SENSORS,
    CONF_START_ONLY_APPLIANCE_SWITCHES,
)
from .coordinator import HemsCoordinator, HemsData
from .entity import HemsEntity


@dataclass(frozen=True, kw_only=True)
class HemsSensorDescription(SensorEntityDescription):
    """Describes a computed HEMS sensor."""

    value_fn: Callable[[HemsData], Any]


SENSORS: tuple[HemsSensorDescription, ...] = (
    HemsSensorDescription(
        key="energy_mode",
        translation_key="energy_mode",
        icon="mdi:home-lightning-bolt",
        value_fn=lambda data: data.energy_mode,
    ),
    HemsSensorDescription(
        key="grid_power",
        translation_key="grid_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: round(data.grid_power, 1),
    ),
    HemsSensorDescription(
        key="grid_import_power",
        translation_key="grid_import_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: round(data.grid_import, 1),
    ),
    HemsSensorDescription(
        key="grid_export_power",
        translation_key="grid_export_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: round(data.grid_export, 1),
    ),
    HemsSensorDescription(
        key="pv_power_total",
        translation_key="pv_power_total",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: round(data.pv_power, 1),
    ),
    HemsSensorDescription(
        key="battery_soc_min",
        translation_key="battery_soc_min",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: None
        if data.battery_soc_min is None
        else round(data.battery_soc_min, 1),
    ),
    HemsSensorDescription(
        key="battery_discharge_total",
        translation_key="battery_discharge_total",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: round(data.battery_discharge, 1),
    ),
    HemsSensorDescription(
        key="house_load_total",
        translation_key="house_load_total",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: round(data.house_load, 1),
    ),
    HemsSensorDescription(
        key="available_surplus_budget",
        translation_key="available_surplus_budget",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: round(data.available_surplus_budget, 1),
    ),
    HemsSensorDescription(
        key="scheduled_surplus_power",
        translation_key="scheduled_surplus_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: round(data.scheduled_surplus_power, 1),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HEMS sensors."""
    coordinator: HemsCoordinator = entry.runtime_data
    async_add_entities(HemsSensor(coordinator, description) for description in SENSORS)


class HemsSensor(HemsEntity, SensorEntity):
    """Computed HEMS sensor."""

    entity_description: HemsSensorDescription

    def __init__(
        self, coordinator: HemsCoordinator, description: HemsSensorDescription
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data
        config = self.coordinator.config_entry.data
        if self.entity_description.key != "energy_mode":
            return {}
        return {
            "surplus_available": data.surplus_available,
            "flexible_loads_allowed": data.flexible_loads_allowed,
            "grid_import": data.grid_import,
            "grid_export": data.grid_export,
            "grid_power": data.grid_power,
            "pv_power": data.pv_power,
            "battery_soc_min": data.battery_soc_min,
            "battery_discharge": data.battery_discharge,
            "house_load": data.house_load,
            "grid_tolerance": data.grid_tolerance,
            "available_surplus_budget": data.available_surplus_budget,
            "scheduled_surplus_loads": data.scheduled_surplus_loads,
            "scheduled_surplus_power": data.scheduled_surplus_power,
            "manually_paused_loads": data.manually_paused_loads,
            "pool_loads": data.pool_loads,
            "dehumidifier_loads": data.dehumidifier_loads,
            "start_only_loads": data.start_only_loads,
            "active_loads": data.active_loads,
            "ac_battery_details": data.ac_battery_details,
            "ac_battery_reason": data.ac_battery_reason,
            "surplus_reason": data.surplus_reason,
            "scheduler_reason": data.scheduler_reason,
            "load_reason": data.load_reason,
            "action_history": data.action_history,
            "grid_power_sensor": config.get(CONF_GRID_POWER_SENSOR),
            "grid_import_power_sensors": config.get(CONF_GRID_IMPORT_POWER_SENSORS, []),
            "grid_export_power_sensors": config.get(CONF_GRID_EXPORT_POWER_SENSORS, []),
            "grid_signed_import_positive_sensors": config.get(
                CONF_GRID_SIGNED_IMPORT_POSITIVE_SENSORS, []
            ),
            "grid_signed_export_positive_sensors": config.get(
                CONF_GRID_SIGNED_EXPORT_POSITIVE_SENSORS, []
            ),
            "pv_power_sensors": config.get(CONF_PV_POWER_SENSORS, []),
            "battery_soc_sensors": config.get(CONF_BATTERY_SOC_SENSORS, []),
            "battery_discharge_sensors": config.get(CONF_BATTERY_DISCHARGE_SENSORS, []),
            "house_load_sensors": config.get(CONF_HOUSE_LOAD_SENSORS, []),
            "pool_switches": config.get(CONF_POOL_SWITCHES, []),
            "pool_power_sensors": config.get(CONF_POOL_POWER_SENSORS, []),
            "dehumidifier_switches": config.get(CONF_DEHUMIDIFIER_SWITCHES, []),
            "dehumidifier_power_sensors": config.get(CONF_DEHUMIDIFIER_POWER_SENSORS, []),
            "start_only_appliance_switches": config.get(
                CONF_START_ONLY_APPLIANCE_SWITCHES, []
            ),
            "start_only_appliance_power_sensors": config.get(
                CONF_START_ONLY_APPLIANCE_POWER_SENSORS, []
            ),
            "ac_battery_profiles": config.get(CONF_AC_BATTERY_PROFILES),
        }
