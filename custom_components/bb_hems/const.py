"""Constants for BB HEMS."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "bb_hems"
NAME = "BB HEMS"
PANEL_URL = "bb-hems"

PLATFORMS = ["sensor", "binary_sensor", "number", "select", "switch"]
SCAN_INTERVAL = timedelta(seconds=10)

CONF_GRID_POWER_SENSOR = "grid_power_sensor"
CONF_GRID_AVERAGE_SENSOR = "grid_average_sensor"
CONF_PV_POWER_SENSORS = "pv_power_sensors"
CONF_PV_AVERAGE_SENSOR = "pv_average_sensor"
CONF_PV_FORECAST_TODAY_SENSOR = "pv_forecast_today_sensor"
CONF_PV_FORECAST_NEXT_HOUR_SENSOR = "pv_forecast_next_hour_sensor"
CONF_PV_FORECAST_NEXT_3H_SENSOR = "pv_forecast_next_3h_sensor"
CONF_PV_ARRAY_SPECS = "pv_array_specs"
CONF_BATTERY_SOC_SENSORS = "battery_soc_sensors"
CONF_BATTERY_DISCHARGE_SENSORS = "battery_discharge_sensors"
CONF_BATTERY_CHARGE_SENSORS = "battery_charge_sensors"
CONF_GRID_IMPORT_PRICE_SENSOR = "grid_import_price_sensor"
CONF_GRID_EXPORT_PRICE_SENSOR = "grid_export_price_sensor"
CONF_WEATHER_STATE_SENSOR = "weather_state_sensor"
CONF_CLOUD_SENSOR = "cloud_sensor"
CONF_SUNSHINE_SENSOR = "sunshine_sensor"
CONF_SUN_ENTITY = "sun_entity"
CONF_FLEXIBLE_LOAD_SWITCHES = "flexible_load_switches"
CONF_FLEXIBLE_LOAD_POWER_SENSORS = "flexible_load_power_sensors"
CONF_DEVICE_PROFILES = "device_profiles"
CONF_WALLBOX_SWITCHES = "wallbox_switches"
CONF_HEAT_PUMP_SWITCHES = "heat_pump_switches"
CONF_HEATING_ROD_SWITCHES = "heating_rod_switches"
CONF_HEATING_ROD_POWER_SENSORS = "heating_rod_power_sensors"
CONF_HEATING_ROD_TEMPERATURE_SENSORS = "heating_rod_temperature_sensors"
CONF_HEATING_ROD_TARGET_TEMPERATURES = "heating_rod_target_temperatures"
CONF_VIRTUAL_BATTERY_CHARGE_SENSOR = "virtual_battery_charge_sensor"
CONF_VIRTUAL_BATTERY_DISCHARGE_SENSOR = "virtual_battery_discharge_sensor"

OPT_MODE = "mode"
OPT_RESPONSE_PROFILE = "response_profile"
OPT_AUTO_ENABLED = "auto_enabled"
OPT_DASHBOARD_ENABLED = "dashboard_enabled"
OPT_BATTERY_PROTECTION_ENABLED = "battery_protection_enabled"
OPT_GRID_IMPORT_PRICE = "grid_import_price"
OPT_GRID_EXPORT_PRICE = "grid_export_price"
OPT_VIRTUAL_BATTERY_ENABLED = "virtual_battery_enabled"
OPT_USE_VIRTUAL_BATTERY = "use_virtual_battery"
OPT_VIRTUAL_BATTERY_CAPACITY = "virtual_battery_capacity"
OPT_VIRTUAL_BATTERY_MIN_SOC = "virtual_battery_min_soc"
OPT_VIRTUAL_BATTERY_MAX_SOC = "virtual_battery_max_soc"
OPT_VIRTUAL_BATTERY_MANUAL_SOC = "virtual_battery_manual_soc"
OPT_VIRTUAL_BATTERY_CHARGE_EFFICIENCY = "virtual_battery_charge_efficiency"
OPT_VIRTUAL_BATTERY_DISCHARGE_EFFICIENCY = "virtual_battery_discharge_efficiency"
OPT_HEATING_ROD_TEMPERATURE_HYSTERESIS = "heating_rod_temperature_hysteresis"
OPT_MIN_BATTERY_SOC = "min_battery_soc"
OPT_PROTECT_BATTERY_SOC = "protect_battery_soc"
OPT_PV_THRESHOLD = "pv_threshold"
OPT_PV_AVG_THRESHOLD = "pv_avg_threshold"
OPT_GRID_IMPORT_LIMIT = "grid_import_limit"
OPT_GRID_HARD_IMPORT_LIMIT = "grid_hard_import_limit"
OPT_BATTERY_DISCHARGE_LIMIT = "battery_discharge_limit"
OPT_FLEXIBLE_LOAD_POWER = "flexible_load_power"
OPT_HEATING_ROD_POWER = "heating_rod_power"

MODE_AUTO = "auto"
MODE_ECO = "eco"
MODE_COMFORT = "comfort"
MODE_FORCE_SURPLUS = "force_surplus"
MODE_OFF = "off"
MODES = [MODE_AUTO, MODE_ECO, MODE_COMFORT, MODE_FORCE_SURPLUS, MODE_OFF]

RESPONSE_AUTO = "auto"
RESPONSE_REALTIME = "realtime"
RESPONSE_SECONDS = "seconds"
RESPONSE_MINUTES = "minutes"
RESPONSE_PROFILES = [
    RESPONSE_AUTO,
    RESPONSE_REALTIME,
    RESPONSE_SECONDS,
    RESPONSE_MINUTES,
]

DEFAULTS = {
    OPT_MODE: MODE_AUTO,
    OPT_RESPONSE_PROFILE: RESPONSE_AUTO,
    OPT_AUTO_ENABLED: True,
    OPT_DASHBOARD_ENABLED: True,
    OPT_BATTERY_PROTECTION_ENABLED: True,
    OPT_GRID_IMPORT_PRICE: 0.32,
    OPT_GRID_EXPORT_PRICE: 0.08,
    OPT_VIRTUAL_BATTERY_ENABLED: False,
    OPT_USE_VIRTUAL_BATTERY: False,
    OPT_VIRTUAL_BATTERY_CAPACITY: 5.0,
    OPT_VIRTUAL_BATTERY_MIN_SOC: 10.0,
    OPT_VIRTUAL_BATTERY_MAX_SOC: 90.0,
    OPT_VIRTUAL_BATTERY_MANUAL_SOC: 50.0,
    OPT_VIRTUAL_BATTERY_CHARGE_EFFICIENCY: 95.0,
    OPT_VIRTUAL_BATTERY_DISCHARGE_EFFICIENCY: 95.0,
    OPT_HEATING_ROD_TEMPERATURE_HYSTERESIS: 2.0,
    OPT_MIN_BATTERY_SOC: 50.0,
    OPT_PROTECT_BATTERY_SOC: 45.0,
    OPT_PV_THRESHOLD: 180.0,
    OPT_PV_AVG_THRESHOLD: 120.0,
    OPT_GRID_IMPORT_LIMIT: 100.0,
    OPT_GRID_HARD_IMPORT_LIMIT: 350.0,
    OPT_BATTERY_DISCHARGE_LIMIT: 250.0,
    OPT_FLEXIBLE_LOAD_POWER: 250.0,
    OPT_HEATING_ROD_POWER: 1000.0,
}

GOOD_WEATHER = {
    "sunny",
    "partlycloudy",
    "clear",
    "cloudy",
    "leicht bewölkt",
    "bewölkt",
    "sonnig",
}

BAD_WEATHER = {"rainy", "pouring", "fog", "snowy", "hail", "lightning"}
