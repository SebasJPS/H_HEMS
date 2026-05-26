"""Sensors for BB HEMS."""

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
from homeassistant.const import PERCENTAGE, UnitOfPower, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_BATTERY_DISCHARGE_SENSORS,
    CONF_BATTERY_SOC_SENSORS,
    CONF_CLOUD_SENSOR,
    CONF_FLEXIBLE_LOAD_SWITCHES,
    CONF_GRID_AVERAGE_SENSOR,
    CONF_GRID_POWER_SENSOR,
    CONF_HEAT_PUMP_SWITCHES,
    CONF_PV_AVERAGE_SENSOR,
    CONF_PV_POWER_SENSORS,
    CONF_SUNSHINE_SENSOR,
    CONF_WALLBOX_SWITCHES,
    CONF_WEATHER_STATE_SENSOR,
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
        key="grid_average",
        translation_key="grid_average",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: round(data.grid_average, 1),
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
        key="pv_average",
        translation_key="pv_average",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: round(data.pv_average, 1),
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
        key="grid_tolerance",
        translation_key="grid_tolerance",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: round(data.grid_tolerance, 1),
    ),
    HemsSensorDescription(
        key="cloud_coverage",
        translation_key="cloud_coverage",
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda data: None
        if data.cloud_coverage is None
        else round(data.cloud_coverage, 1),
    ),
    HemsSensorDescription(
        key="sunshine_minutes",
        translation_key="sunshine_minutes",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        value_fn=lambda data: None
        if data.sunshine_minutes is None
        else round(data.sunshine_minutes, 1),
    ),
    HemsSensorDescription(
        key="active_flexible_loads",
        translation_key="active_flexible_loads",
        icon="mdi:power-plug",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.active_flexible_loads,
    ),
    HemsSensorDescription(
        key="configured_assets",
        translation_key="configured_assets",
        icon="mdi:counter",
        value_fn=lambda data: (
            data.configured_pv_sources
            + data.configured_batteries
            + data.configured_flexible_loads
            + data.configured_wallboxes
            + data.configured_heat_pumps
        ),
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
        """Return the computed state."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return useful dashboard attributes."""
        data = self.coordinator.data
        config = self.coordinator.config_entry.data
        if self.entity_description.key != "energy_mode":
            return {}
        return {
            "good_weather": data.good_weather,
            "bad_weather": data.bad_weather,
            "surplus_available": data.surplus_available,
            "battery_protect": data.battery_protect,
            "flexible_loads_allowed": data.flexible_loads_allowed,
            "weather_state": data.weather_state,
            "cloud_coverage": data.cloud_coverage,
            "sunshine_minutes": data.sunshine_minutes,
            "weather_reason": data.weather_reason,
            "surplus_reason": data.surplus_reason,
            "battery_reason": data.battery_reason,
            "load_reason": data.load_reason,
            "action_history": data.action_history,
            "configured_pv_sources": data.configured_pv_sources,
            "configured_batteries": data.configured_batteries,
            "configured_flexible_loads": data.configured_flexible_loads,
            "configured_wallboxes": data.configured_wallboxes,
            "configured_heat_pumps": data.configured_heat_pumps,
            "grid_power_sensor": config.get(CONF_GRID_POWER_SENSOR),
            "grid_average_sensor": config.get(CONF_GRID_AVERAGE_SENSOR),
            "pv_power_sensors": config.get(CONF_PV_POWER_SENSORS, []),
            "pv_average_sensor": config.get(CONF_PV_AVERAGE_SENSOR),
            "battery_soc_sensors": config.get(CONF_BATTERY_SOC_SENSORS, []),
            "battery_discharge_sensors": config.get(
                CONF_BATTERY_DISCHARGE_SENSORS, []
            ),
            "weather_state_sensor": config.get(CONF_WEATHER_STATE_SENSOR),
            "cloud_sensor": config.get(CONF_CLOUD_SENSOR),
            "sunshine_sensor": config.get(CONF_SUNSHINE_SENSOR),
            "flexible_load_switches": config.get(CONF_FLEXIBLE_LOAD_SWITCHES, []),
            "wallbox_switches": config.get(CONF_WALLBOX_SWITCHES, []),
            "heat_pump_switches": config.get(CONF_HEAT_PUMP_SWITCHES, []),
        }
