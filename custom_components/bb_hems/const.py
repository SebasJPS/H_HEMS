"""Constants for BB HEMS."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "bb_hems"
NAME = "BB HEMS"
PANEL_URL = "bb-hems"
PLATFORMS = ["sensor", "binary_sensor", "number", "select", "switch"]
SCAN_INTERVAL = timedelta(seconds=30)

CONF_GRID_POWER_SENSOR = "grid_power_sensor"
CONF_GRID_AVERAGE_SENSOR = "grid_average_sensor"
CONF_PV_POWER_SENSORS = "pv_power_sensors"
CONF_PV_AVERAGE_SENSOR = "pv_average_sensor"
CONF_BATTERY_SOC_SENSORS = "battery_soc_sensors"
CONF_BATTERY_DISCHARGE_SENSORS = "battery_discharge_sensors"
CONF_WEATHER_STATE_SENSOR = "weather_state_sensor"
CONF_CLOUD_SENSOR = "cloud_sensor"
CONF_SUNSHINE_SENSOR = "sunshine_sensor"
CONF_FLEXIBLE_LOAD_SWITCHES = "flexible_load_switches"
CONF_WALLBOX_SWITCHES = "wallbox_switches"
CONF_HEAT_PUMP_SWITCHES = "heat_pump_switches"

OPT_MODE = "mode"
OPT_AUTO_ENABLED = "auto_enabled"
OPT_MIN_BATTERY_SOC = "min_battery_soc"
OPT_PROTECT_BATTERY_SOC = "protect_battery_soc"
OPT_PV_THRESHOLD = "pv_threshold"
OPT_PV_AVG_THRESHOLD = "pv_avg_threshold"
OPT_GRID_IMPORT_LIMIT = "grid_import_limit"
OPT_GRID_HARD_IMPORT_LIMIT = "grid_hard_import_limit"
OPT_BATTERY_DISCHARGE_LIMIT = "battery_discharge_limit"

MODE_AUTO = "auto"
MODE_ECO = "eco"
MODE_COMFORT = "comfort"
MODE_FORCE_SURPLUS = "force_surplus"
MODE_OFF = "off"
MODES = [MODE_AUTO, MODE_ECO, MODE_COMFORT, MODE_FORCE_SURPLUS, MODE_OFF]

DEFAULTS = {
    OPT_MODE: MODE_AUTO,
    OPT_AUTO_ENABLED: True,
    OPT_MIN_BATTERY_SOC: 50.0,
    OPT_PROTECT_BATTERY_SOC: 45.0,
    OPT_PV_THRESHOLD: 180.0,
    OPT_PV_AVG_THRESHOLD: 120.0,
    OPT_GRID_IMPORT_LIMIT: 100.0,
    OPT_GRID_HARD_IMPORT_LIMIT: 350.0,
    OPT_BATTERY_DISCHARGE_LIMIT: 250.0,
}

GOOD_WEATHER = {"sunny", "partlycloudy", "clear", "cloudy", "leicht bewölkt", "bewölkt", "sonnig"}
BAD_WEATHER = {"rainy", "pouring", "fog", "snowy", "hail", "lightning"}
