"""Constants for BB HEMS slim v1."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "bb_hems"
NAME = "BB HEMS"
PANEL_URL = "bb-hems"
CONFIG_ENTRY_VERSION = 2

PLATFORMS = ["sensor", "binary_sensor", "number", "select", "switch"]
SCAN_INTERVAL = timedelta(seconds=10)

CONF_GRID_POWER_SENSOR = "grid_power_sensor"
CONF_GRID_IMPORT_POWER_SENSORS = "grid_import_power_sensors"
CONF_GRID_EXPORT_POWER_SENSORS = "grid_export_power_sensors"
CONF_GRID_SIGNED_IMPORT_POSITIVE_SENSORS = "grid_signed_import_positive_sensors"
CONF_GRID_SIGNED_EXPORT_POSITIVE_SENSORS = "grid_signed_export_positive_sensors"
CONF_PV_POWER_SENSORS = "pv_power_sensors"
CONF_BATTERY_SOC_SENSORS = "battery_soc_sensors"
CONF_BATTERY_DISCHARGE_SENSORS = "battery_discharge_sensors"
CONF_HOUSE_LOAD_SENSORS = "house_load_sensors"
CONF_AC_BATTERY_PROFILES = "ac_battery_profiles"
CONF_POOL_SWITCHES = "pool_switches"
CONF_POOL_POWER_SENSORS = "pool_power_sensors"
CONF_DEHUMIDIFIER_SWITCHES = "dehumidifier_switches"
CONF_DEHUMIDIFIER_POWER_SENSORS = "dehumidifier_power_sensors"
CONF_START_ONLY_APPLIANCE_SWITCHES = "start_only_appliance_switches"
CONF_START_ONLY_APPLIANCE_POWER_SENSORS = "start_only_appliance_power_sensors"

OPT_MODE = "mode"
OPT_AUTO_ENABLED = "auto_enabled"
OPT_DASHBOARD_ENABLED = "dashboard_enabled"
OPT_GRID_TOLERANCE_W = "grid_tolerance_w"
OPT_PV_BATTERY_AC_CHARGE_THRESHOLD_SOC = "pv_battery_ac_charge_threshold_soc"
OPT_MANUAL_PAUSE_HOURS = "manual_pause_hours"
OPT_AC_BATTERY_NIGHT_DISCHARGE_W = "ac_battery_night_discharge_w"
OPT_AC_BATTERY_NIGHT_START = "ac_battery_night_start"
OPT_AC_BATTERY_NIGHT_END = "ac_battery_night_end"
OPT_POOL_POWER = "pool_power"
OPT_DEHUMIDIFIER_POWER = "dehumidifier_power"
OPT_START_ONLY_APPLIANCE_POWER = "start_only_appliance_power"

MODE_AUTO = "auto"
MODE_OFF = "off"
MODES = [MODE_AUTO, MODE_OFF]

DEFAULTS = {
    OPT_MODE: MODE_AUTO,
    OPT_AUTO_ENABLED: True,
    OPT_DASHBOARD_ENABLED: True,
    OPT_GRID_TOLERANCE_W: 50.0,
    OPT_PV_BATTERY_AC_CHARGE_THRESHOLD_SOC: 80.0,
    OPT_MANUAL_PAUSE_HOURS: 4.0,
    OPT_AC_BATTERY_NIGHT_DISCHARGE_W: 120.0,
    OPT_AC_BATTERY_NIGHT_START: "22:00",
    OPT_AC_BATTERY_NIGHT_END: "06:00",
    OPT_POOL_POWER: 1000.0,
    OPT_DEHUMIDIFIER_POWER: 300.0,
    OPT_START_ONLY_APPLIANCE_POWER: 1200.0,
}
