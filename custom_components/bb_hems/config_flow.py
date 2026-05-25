"""Config flow for BB HEMS."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import *


def _csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _csv_string(values: list[str] | None) -> str:
    return ", ".join(values or [])


class BbHemsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BB HEMS."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            data = _data_from_input(user_input)
            return self.async_create_entry(title=data[CONF_NAME], data=data, options=DEFAULTS)
        return self.async_show_form(step_id="user", data_schema=_schema({}))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        return BbHemsOptionsFlow(config_entry)


class BbHemsOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            data = dict(self.config_entry.data)
            data.update(_data_from_input(user_input))
            self.hass.config_entries.async_update_entry(self.config_entry, data=data)
            return self.async_create_entry(title="", data=dict(self.config_entry.options))
        data = self.config_entry.data
        defaults = dict(data)
        defaults[CONF_PV_POWER_SENSORS] = _csv_string(data.get(CONF_PV_POWER_SENSORS))
        defaults[CONF_BATTERY_SOC_SENSORS] = _csv_string(data.get(CONF_BATTERY_SOC_SENSORS))
        defaults[CONF_BATTERY_DISCHARGE_SENSORS] = _csv_string(data.get(CONF_BATTERY_DISCHARGE_SENSORS))
        defaults[CONF_FLEXIBLE_LOAD_SWITCHES] = _csv_string(data.get(CONF_FLEXIBLE_LOAD_SWITCHES))
        defaults[CONF_WALLBOX_SWITCHES] = _csv_string(data.get(CONF_WALLBOX_SWITCHES))
        defaults[CONF_HEAT_PUMP_SWITCHES] = _csv_string(data.get(CONF_HEAT_PUMP_SWITCHES))
        return self.async_show_form(step_id="init", data_schema=_schema(defaults))


def _data_from_input(user_input: dict[str, Any]) -> dict[str, Any]:
    return {
        CONF_NAME: user_input.get(CONF_NAME, NAME),
        CONF_GRID_POWER_SENSOR: user_input.get(CONF_GRID_POWER_SENSOR),
        CONF_GRID_AVERAGE_SENSOR: user_input.get(CONF_GRID_AVERAGE_SENSOR),
        CONF_PV_POWER_SENSORS: _csv(user_input.get(CONF_PV_POWER_SENSORS)),
        CONF_PV_AVERAGE_SENSOR: user_input.get(CONF_PV_AVERAGE_SENSOR),
        CONF_BATTERY_SOC_SENSORS: _csv(user_input.get(CONF_BATTERY_SOC_SENSORS)),
        CONF_BATTERY_DISCHARGE_SENSORS: _csv(user_input.get(CONF_BATTERY_DISCHARGE_SENSORS)),
        CONF_WEATHER_STATE_SENSOR: user_input.get(CONF_WEATHER_STATE_SENSOR),
        CONF_CLOUD_SENSOR: user_input.get(CONF_CLOUD_SENSOR),
        CONF_SUNSHINE_SENSOR: user_input.get(CONF_SUNSHINE_SENSOR),
        CONF_FLEXIBLE_LOAD_SWITCHES: _csv(user_input.get(CONF_FLEXIBLE_LOAD_SWITCHES)),
        CONF_WALLBOX_SWITCHES: _csv(user_input.get(CONF_WALLBOX_SWITCHES)),
        CONF_HEAT_PUMP_SWITCHES: _csv(user_input.get(CONF_HEAT_PUMP_SWITCHES)),
    }


def _schema(defaults: dict[str, Any]) -> vol.Schema:
    sensor = selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor"))
    return vol.Schema({
        vol.Optional(CONF_NAME, default=defaults.get(CONF_NAME, NAME)): str,
        vol.Required(CONF_GRID_POWER_SENSOR, default=defaults.get(CONF_GRID_POWER_SENSOR)): sensor,
        vol.Optional(CONF_GRID_AVERAGE_SENSOR, default=defaults.get(CONF_GRID_AVERAGE_SENSOR)): sensor,
        vol.Optional(CONF_PV_POWER_SENSORS, default=defaults.get(CONF_PV_POWER_SENSORS, "")): str,
        vol.Optional(CONF_PV_AVERAGE_SENSOR, default=defaults.get(CONF_PV_AVERAGE_SENSOR)): sensor,
        vol.Optional(CONF_BATTERY_SOC_SENSORS, default=defaults.get(CONF_BATTERY_SOC_SENSORS, "")): str,
        vol.Optional(CONF_BATTERY_DISCHARGE_SENSORS, default=defaults.get(CONF_BATTERY_DISCHARGE_SENSORS, "")): str,
        vol.Optional(CONF_WEATHER_STATE_SENSOR, default=defaults.get(CONF_WEATHER_STATE_SENSOR)): selector.EntitySelector(selector.EntitySelectorConfig(domain=["sensor", "weather"])),
        vol.Optional(CONF_CLOUD_SENSOR, default=defaults.get(CONF_CLOUD_SENSOR)): sensor,
        vol.Optional(CONF_SUNSHINE_SENSOR, default=defaults.get(CONF_SUNSHINE_SENSOR)): sensor,
        vol.Optional(CONF_FLEXIBLE_LOAD_SWITCHES, default=defaults.get(CONF_FLEXIBLE_LOAD_SWITCHES, "")): str,
        vol.Optional(CONF_WALLBOX_SWITCHES, default=defaults.get(CONF_WALLBOX_SWITCHES, "")): str,
        vol.Optional(CONF_HEAT_PUMP_SWITCHES, default=defaults.get(CONF_HEAT_PUMP_SWITCHES, "")): str,
    })
