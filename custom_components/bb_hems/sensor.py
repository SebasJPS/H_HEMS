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
from homeassistant.const import PERCENTAGE, UnitOfEnergy, UnitOfPower, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_BATTERY_CHARGE_SENSORS,
    CONF_BATTERY_DISCHARGE_SENSORS,
    CONF_BATTERY_SIGNED_CHARGE_POSITIVE_SENSORS,
    CONF_BATTERY_SIGNED_DISCHARGE_POSITIVE_SENSORS,
    CONF_BATTERY_SOC_SENSORS,
    CONF_CLOUD_SENSOR,
    CONF_DEVICE_PROFILES,
    CONF_FLEXIBLE_LOAD_POWER_SENSORS,
    CONF_FLEXIBLE_LOAD_SWITCHES,
    CONF_GRID_AVERAGE_SENSOR,
    CONF_GRID_EXPORT_PRICE_SENSOR,
    CONF_GRID_EXPORT_POWER_SENSORS,
    CONF_GRID_IMPORT_PRICE_SENSOR,
    CONF_GRID_IMPORT_POWER_SENSORS,
    CONF_GRID_POWER_SENSOR,
    CONF_GRID_SIGNED_EXPORT_POSITIVE_SENSORS,
    CONF_GRID_SIGNED_IMPORT_POSITIVE_SENSORS,
    CONF_HEAT_PUMP_SWITCHES,
    CONF_HEATING_ROD_POWER_SENSORS,
    CONF_HEATING_ROD_SWITCHES,
    CONF_HEATING_ROD_TARGET_TEMPERATURES,
    CONF_HEATING_ROD_TEMPERATURE_SENSORS,
    CONF_HOUSE_LOAD_SENSORS,
    CONF_PV_ARRAY_SPECS,
    CONF_PV_AVERAGE_SENSOR,
    CONF_PV_FORECAST_NEXT_3H_SENSOR,
    CONF_PV_FORECAST_NEXT_HOUR_SENSOR,
    CONF_PV_FORECAST_TODAY_SENSOR,
    CONF_PV_POWER_SENSORS,
    CONF_PV_SOURCE_PROFILES,
    CONF_START_ONLY_APPLIANCE_POWER_SENSORS,
    CONF_START_ONLY_APPLIANCE_SWITCHES,
    CONF_SUN_ENTITY,
    CONF_SUNSHINE_SENSOR,
    CONF_WALLBOX_SWITCHES,
    CONF_WEATHER_STATE_SENSOR,
    CONF_VIRTUAL_BATTERY_CHARGE_SENSOR,
    CONF_VIRTUAL_BATTERY_DISCHARGE_SENSOR,
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
        key="grid_average",
        translation_key="grid_average",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: round(data.grid_average, 1),
    ),
    HemsSensorDescription(
        key="grid_import_price",
        translation_key="grid_import_price",
        native_unit_of_measurement="EUR/kWh",
        icon="mdi:cash-minus",
        value_fn=lambda data: round(data.grid_import_price, 4),
    ),
    HemsSensorDescription(
        key="grid_export_price",
        translation_key="grid_export_price",
        native_unit_of_measurement="EUR/kWh",
        icon="mdi:cash-plus",
        value_fn=lambda data: round(data.grid_export_price, 4),
    ),
    HemsSensorDescription(
        key="savings_price",
        translation_key="savings_price",
        native_unit_of_measurement="EUR/kWh",
        icon="mdi:cash-sync",
        value_fn=lambda data: round(data.savings_price, 4),
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
        key="pv_window",
        translation_key="pv_window",
        icon="mdi:solar-power-variant",
        value_fn=lambda data: data.pv_window,
    ),
    HemsSensorDescription(
        key="pv_forecast_next_3h",
        translation_key="pv_forecast_next_3h",
        icon="mdi:weather-sunny-alert",
        value_fn=lambda data: None
        if data.pv_forecast_next_3h is None
        else round(data.pv_forecast_next_3h, 1),
    ),
    HemsSensorDescription(
        key="sun_elevation",
        translation_key="sun_elevation",
        icon="mdi:weather-sunny",
        value_fn=lambda data: None
        if data.sun_elevation is None
        else round(data.sun_elevation, 1),
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
        key="battery_charge_total",
        translation_key="battery_charge_total",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: round(data.battery_charge, 1),
    ),
    HemsSensorDescription(
        key="usable_battery_charge",
        translation_key="usable_battery_charge",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: round(data.usable_battery_charge, 1),
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
        key="virtual_battery_soc",
        translation_key="virtual_battery_soc",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: None
        if data.virtual_battery_soc is None
        else round(data.virtual_battery_soc, 1),
    ),
    HemsSensorDescription(
        key="virtual_battery_energy",
        translation_key="virtual_battery_energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: None
        if data.virtual_battery_energy is None
        else round(data.virtual_battery_energy, 3),
    ),
    HemsSensorDescription(
        key="virtual_battery_usable_energy",
        translation_key="virtual_battery_usable_energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: None
        if data.virtual_battery_usable_energy is None
        else round(data.virtual_battery_usable_energy, 3),
    ),
    HemsSensorDescription(
        key="virtual_battery_confidence",
        translation_key="virtual_battery_confidence",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:shield-check",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: round(data.virtual_battery_confidence, 1),
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
    HemsSensorDescription(
        key="shifted_energy_today",
        translation_key="shifted_energy_today",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda data: round(data.shifted_energy_today, 3),
    ),
    HemsSensorDescription(
        key="estimated_savings_today",
        translation_key="estimated_savings_today",
        native_unit_of_measurement="EUR",
        icon="mdi:cash",
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda data: round(data.estimated_savings_today, 2),
    ),
    HemsSensorDescription(
        key="shifted_energy_total",
        translation_key="shifted_energy_total",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda data: round(data.shifted_energy_total, 3),
    ),
    HemsSensorDescription(
        key="learning_samples",
        translation_key="learning_samples",
        icon="mdi:brain",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.learning_samples,
    ),
    HemsSensorDescription(
        key="seasonal_success_rate",
        translation_key="seasonal_success_rate",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:calendar-sync",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.seasonal_success_rate,
    ),
    HemsSensorDescription(
        key="configured_assets",
        translation_key="configured_assets",
        icon="mdi:counter",
        value_fn=lambda data: (
            data.configured_pv_sources
            + data.configured_batteries
            + data.configured_flexible_loads
            + data.configured_start_only_appliances
            + data.configured_wallboxes
            + data.configured_heat_pumps
            + data.configured_heating_rods
            + data.configured_profile_loads
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
            "pv_forecast_today": data.pv_forecast_today,
            "pv_forecast_next_hour": data.pv_forecast_next_hour,
            "pv_forecast_next_3h": data.pv_forecast_next_3h,
            "sun_elevation": data.sun_elevation,
            "sun_azimuth": data.sun_azimuth,
            "pv_array_count": data.pv_array_count,
            "pv_best_array": data.pv_best_array,
            "pv_orientation_score": data.pv_orientation_score,
            "pv_source_details": data.pv_source_details,
            "pv_window": data.pv_window,
            "pv_window_reason": data.pv_window_reason,
            "weather_reason": data.weather_reason,
            "surplus_reason": data.surplus_reason,
            "battery_reason": data.battery_reason,
            "grid_import": data.grid_import,
            "grid_export": data.grid_export,
            "grid_power": data.grid_power,
            "pv_power": data.pv_power,
            "battery_charge": data.battery_charge,
            "battery_discharge": data.battery_discharge,
            "battery_soc_min": data.battery_soc_min,
            "house_load": data.house_load,
            "usable_battery_charge": data.usable_battery_charge,
            "grid_import_price": data.grid_import_price,
            "grid_export_price": data.grid_export_price,
            "savings_price": data.savings_price,
            "price_reason": data.price_reason,
            "virtual_battery_enabled": data.virtual_battery_enabled,
            "virtual_battery_used": data.virtual_battery_used,
            "virtual_battery_soc": data.virtual_battery_soc,
            "virtual_battery_energy": data.virtual_battery_energy,
            "virtual_battery_usable_energy": data.virtual_battery_usable_energy,
            "virtual_battery_confidence": data.virtual_battery_confidence,
            "virtual_battery_reason": data.virtual_battery_reason,
            "load_reason": data.load_reason,
            "action_history": data.action_history,
            "configured_pv_sources": data.configured_pv_sources,
            "configured_batteries": data.configured_batteries,
            "configured_flexible_loads": data.configured_flexible_loads,
            "configured_start_only_appliances": data.configured_start_only_appliances,
            "configured_wallboxes": data.configured_wallboxes,
            "configured_heat_pumps": data.configured_heat_pumps,
            "configured_heating_rods": data.configured_heating_rods,
            "configured_profile_loads": data.configured_profile_loads,
            "blocked_heating_rods": data.blocked_heating_rods,
            "response_profile": data.response_profile,
            "switch_on_delay_seconds": data.switch_on_delay_seconds,
            "switch_off_delay_seconds": data.switch_off_delay_seconds,
            "available_surplus_budget": data.available_surplus_budget,
            "scheduled_surplus_loads": data.scheduled_surplus_loads,
            "scheduled_surplus_power": data.scheduled_surplus_power,
            "temperature_blocked_loads": data.temperature_blocked_loads,
            "shifted_energy_today": data.shifted_energy_today,
            "estimated_savings_today": data.estimated_savings_today,
            "shifted_energy_total": data.shifted_energy_total,
            "daily_history": data.daily_history,
            "learning_bucket": data.learning_bucket,
            "learning_samples": data.learning_samples,
            "seasonal_success_rate": data.seasonal_success_rate,
            "seasonal_average_shifted_energy": data.seasonal_average_shifted_energy,
            "seasonal_average_budget": data.seasonal_average_budget,
            "seasonal_grid_adjustment": data.seasonal_grid_adjustment,
            "seasonal_recommendation": data.seasonal_recommendation,
            "scheduler_reason": data.scheduler_reason,
            "grid_power_sensor": config.get(CONF_GRID_POWER_SENSOR),
            "grid_import_power_sensors": config.get(
                CONF_GRID_IMPORT_POWER_SENSORS, []
            ),
            "grid_export_power_sensors": config.get(
                CONF_GRID_EXPORT_POWER_SENSORS, []
            ),
            "grid_signed_import_positive_sensors": config.get(
                CONF_GRID_SIGNED_IMPORT_POSITIVE_SENSORS, []
            ),
            "grid_signed_export_positive_sensors": config.get(
                CONF_GRID_SIGNED_EXPORT_POSITIVE_SENSORS, []
            ),
            "grid_average_sensor": config.get(CONF_GRID_AVERAGE_SENSOR),
            "grid_import_price_sensor": config.get(CONF_GRID_IMPORT_PRICE_SENSOR),
            "grid_export_price_sensor": config.get(CONF_GRID_EXPORT_PRICE_SENSOR),
            "pv_power_sensors": config.get(CONF_PV_POWER_SENSORS, []),
            "pv_source_profiles": config.get(CONF_PV_SOURCE_PROFILES),
            "pv_average_sensor": config.get(CONF_PV_AVERAGE_SENSOR),
            "pv_forecast_today_sensor": config.get(CONF_PV_FORECAST_TODAY_SENSOR),
            "pv_forecast_next_hour_sensor": config.get(
                CONF_PV_FORECAST_NEXT_HOUR_SENSOR
            ),
            "pv_forecast_next_3h_sensor": config.get(CONF_PV_FORECAST_NEXT_3H_SENSOR),
            "pv_array_specs": config.get(CONF_PV_ARRAY_SPECS),
            "battery_soc_sensors": config.get(CONF_BATTERY_SOC_SENSORS, []),
            "battery_discharge_sensors": config.get(
                CONF_BATTERY_DISCHARGE_SENSORS, []
            ),
            "battery_charge_sensors": config.get(CONF_BATTERY_CHARGE_SENSORS, []),
            "battery_signed_discharge_positive_sensors": config.get(
                CONF_BATTERY_SIGNED_DISCHARGE_POSITIVE_SENSORS, []
            ),
            "battery_signed_charge_positive_sensors": config.get(
                CONF_BATTERY_SIGNED_CHARGE_POSITIVE_SENSORS, []
            ),
            "house_load_sensors": config.get(CONF_HOUSE_LOAD_SENSORS, []),
            "virtual_battery_charge_sensor": config.get(
                CONF_VIRTUAL_BATTERY_CHARGE_SENSOR
            ),
            "virtual_battery_discharge_sensor": config.get(
                CONF_VIRTUAL_BATTERY_DISCHARGE_SENSOR
            ),
            "weather_state_sensor": config.get(CONF_WEATHER_STATE_SENSOR),
            "cloud_sensor": config.get(CONF_CLOUD_SENSOR),
            "sunshine_sensor": config.get(CONF_SUNSHINE_SENSOR),
            "sun_entity": config.get(CONF_SUN_ENTITY),
            "flexible_load_switches": config.get(CONF_FLEXIBLE_LOAD_SWITCHES, []),
            "flexible_load_power_sensors": config.get(
                CONF_FLEXIBLE_LOAD_POWER_SENSORS, []
            ),
            "start_only_appliance_switches": config.get(
                CONF_START_ONLY_APPLIANCE_SWITCHES, []
            ),
            "start_only_appliance_power_sensors": config.get(
                CONF_START_ONLY_APPLIANCE_POWER_SENSORS, []
            ),
            "device_profiles": config.get(CONF_DEVICE_PROFILES),
            "wallbox_switches": config.get(CONF_WALLBOX_SWITCHES, []),
            "heat_pump_switches": config.get(CONF_HEAT_PUMP_SWITCHES, []),
            "heating_rod_switches": config.get(CONF_HEATING_ROD_SWITCHES, []),
            "heating_rod_power_sensors": config.get(
                CONF_HEATING_ROD_POWER_SENSORS, []
            ),
            "heating_rod_temperature_sensors": config.get(
                CONF_HEATING_ROD_TEMPERATURE_SENSORS, []
            ),
            "heating_rod_target_temperatures": config.get(
                CONF_HEATING_ROD_TARGET_TEMPERATURES
            ),
        }
