"""Config flow for BB HEMS."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_AC_BATTERY_PROFILES,
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
    DEFAULTS,
    DOMAIN,
    NAME,
)


NUMERIC_DOMAINS = ["sensor", "number", "input_number"]
SWITCHABLE_DOMAINS = ["switch", "input_boolean"]
STARTABLE_DOMAINS = ["switch", "input_boolean", "button"]


def _is_german(language: str | None) -> bool:
    """Return whether the Home Assistant UI language should use German text."""
    return bool(language and language.lower().startswith("de"))


def _options_menu_labels(language: str | None) -> dict[str, str]:
    """Return robust labels for the options menu."""
    if _is_german(language):
        return {
            "energy_sources": "Netz, PV und Batterie - wichtige Messwerte",
            "weather_sources": "Sonne - Bewölkung und Sonnenstand",
            "load_flexible": "Flexible Verbraucher - darf HEMS ein- und ausschalten",
            "load_start_only": "Nur starten - Waschmaschine, Geschirrspüler, Trockner",
            "load_heating_rods": "Heizstäbe - mit optionaler Zieltemperatur",
            "load_wallboxes": "Wallboxen - Ladefreigaben",
            "load_heat_pumps": "Wärmepumpen - SG-Ready oder Freigaben",
            "load_advanced": "Erweiterte Geräteprofile - Priorität und Verhalten",
        }
    return {
        "energy_sources": "Grid, PV and battery - important meters",
        "weather_sources": "Sun - clouds and sun position",
        "load_flexible": "Flexible loads - HEMS may turn on and off",
        "load_start_only": "Start only - washing machine, dishwasher, dryer",
        "load_heating_rods": "Heating rods - with optional target temperature",
        "load_wallboxes": "Wallboxes - charge release",
        "load_heat_pumps": "Heat pumps - SG-ready or releases",
        "load_advanced": "Advanced device profiles - priority and behavior",
    }


def _csv(value: str | None) -> list[str]:
    """Convert a comma separated entity list to clean ids."""
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _entity_list(value: Any) -> list[str]:
    """Normalize entity selector or legacy comma separated values."""
    if value is None:
        return []
    if isinstance(value, str):
        return _csv(value)
    return [item for item in value if item]


def _optional_entity(defaults: dict[str, Any], key: str) -> vol.Optional:
    """Return an optional schema key without forcing an empty default."""
    value = defaults.get(key)
    if value:
        return vol.Optional(key, default=value)
    return vol.Optional(key)


def _optional_text(defaults: dict[str, Any], key: str) -> vol.Optional:
    """Return an optional text schema key without forcing a null default."""
    value = defaults.get(key)
    if value:
        return vol.Optional(key, default=value)
    return vol.Optional(key)


class BbHemsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BB HEMS."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Create the first HEMS instance."""
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()

            data = {
                CONF_NAME: user_input.get(CONF_NAME, NAME),
                CONF_GRID_POWER_SENSOR: user_input.get(CONF_GRID_POWER_SENSOR),
                CONF_GRID_IMPORT_POWER_SENSORS: _entity_list(
                    user_input.get(CONF_GRID_IMPORT_POWER_SENSORS)
                ),
                CONF_GRID_EXPORT_POWER_SENSORS: _entity_list(
                    user_input.get(CONF_GRID_EXPORT_POWER_SENSORS)
                ),
                CONF_GRID_SIGNED_IMPORT_POSITIVE_SENSORS: _entity_list(
                    user_input.get(CONF_GRID_SIGNED_IMPORT_POSITIVE_SENSORS)
                ),
                CONF_GRID_SIGNED_EXPORT_POSITIVE_SENSORS: _entity_list(
                    user_input.get(CONF_GRID_SIGNED_EXPORT_POSITIVE_SENSORS)
                ),
                    CONF_PV_POWER_SENSORS: _entity_list(
                        user_input.get(CONF_PV_POWER_SENSORS)
                    ),
                    CONF_PV_SOURCE_PROFILES: user_input.get(CONF_PV_SOURCE_PROFILES),
                    CONF_PV_FORECAST_NEXT_HOUR_SENSOR: user_input.get(
                        CONF_PV_FORECAST_NEXT_HOUR_SENSOR
                    ),
                    CONF_PV_FORECAST_NEXT_3H_SENSOR: user_input.get(
                        CONF_PV_FORECAST_NEXT_3H_SENSOR
                    ),
                CONF_BATTERY_SOC_SENSORS: _entity_list(
                    user_input.get(CONF_BATTERY_SOC_SENSORS)
                ),
                CONF_BATTERY_DISCHARGE_SENSORS: _entity_list(
                    user_input.get(CONF_BATTERY_DISCHARGE_SENSORS)
                ),
                CONF_BATTERY_CHARGE_SENSORS: _entity_list(
                    user_input.get(CONF_BATTERY_CHARGE_SENSORS)
                ),
                CONF_BATTERY_SIGNED_DISCHARGE_POSITIVE_SENSORS: _entity_list(
                    user_input.get(CONF_BATTERY_SIGNED_DISCHARGE_POSITIVE_SENSORS)
                ),
                CONF_BATTERY_SIGNED_CHARGE_POSITIVE_SENSORS: _entity_list(
                    user_input.get(CONF_BATTERY_SIGNED_CHARGE_POSITIVE_SENSORS)
                ),
                CONF_HOUSE_LOAD_SENSORS: _entity_list(
                    user_input.get(CONF_HOUSE_LOAD_SENSORS)
                ),
                CONF_AC_BATTERY_PROFILES: user_input.get(CONF_AC_BATTERY_PROFILES),
                CONF_GRID_IMPORT_PRICE_SENSOR: user_input.get(
                    CONF_GRID_IMPORT_PRICE_SENSOR
                ),
                CONF_GRID_EXPORT_PRICE_SENSOR: user_input.get(
                    CONF_GRID_EXPORT_PRICE_SENSOR
                ),
                CONF_VIRTUAL_BATTERY_CHARGE_SENSOR: user_input.get(
                    CONF_VIRTUAL_BATTERY_CHARGE_SENSOR
                ),
                CONF_VIRTUAL_BATTERY_DISCHARGE_SENSOR: user_input.get(
                    CONF_VIRTUAL_BATTERY_DISCHARGE_SENSOR
                ),
                CONF_CLOUD_SENSOR: user_input.get(CONF_CLOUD_SENSOR),
                CONF_SUN_ENTITY: user_input.get(CONF_SUN_ENTITY),
                CONF_FLEXIBLE_LOAD_SWITCHES: _entity_list(
                    user_input.get(CONF_FLEXIBLE_LOAD_SWITCHES)
                ),
                CONF_FLEXIBLE_LOAD_POWER_SENSORS: _entity_list(
                    user_input.get(CONF_FLEXIBLE_LOAD_POWER_SENSORS)
                ),
                CONF_START_ONLY_APPLIANCE_SWITCHES: _entity_list(
                    user_input.get(CONF_START_ONLY_APPLIANCE_SWITCHES)
                ),
                CONF_START_ONLY_APPLIANCE_POWER_SENSORS: _entity_list(
                    user_input.get(CONF_START_ONLY_APPLIANCE_POWER_SENSORS)
                ),
                CONF_DEVICE_PROFILES: user_input.get(CONF_DEVICE_PROFILES),
                CONF_WALLBOX_SWITCHES: _entity_list(
                    user_input.get(CONF_WALLBOX_SWITCHES)
                ),
                CONF_HEAT_PUMP_SWITCHES: _entity_list(
                    user_input.get(CONF_HEAT_PUMP_SWITCHES)
                ),
                CONF_HEATING_ROD_SWITCHES: _entity_list(
                    user_input.get(CONF_HEATING_ROD_SWITCHES)
                ),
                CONF_HEATING_ROD_POWER_SENSORS: _entity_list(
                    user_input.get(CONF_HEATING_ROD_POWER_SENSORS)
                ),
                CONF_HEATING_ROD_TEMPERATURE_SENSORS: _entity_list(
                    user_input.get(CONF_HEATING_ROD_TEMPERATURE_SENSORS)
                ),
                CONF_HEATING_ROD_TARGET_TEMPERATURES: user_input.get(
                    CONF_HEATING_ROD_TARGET_TEMPERATURES
                ),
            }
            return self.async_create_entry(title=data[CONF_NAME], data=data, options=DEFAULTS)

        return self.async_show_form(
            step_id="user",
            data_schema=self._schema({}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return BbHemsOptionsFlow(config_entry)

    def _schema(self, defaults: dict[str, Any]) -> vol.Schema:
        return _schema(defaults)


class BbHemsOptionsFlow(config_entries.OptionsFlow):
    """Change HEMS sources and thresholds."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        return self.async_show_menu(
            step_id="init",
            menu_options=_options_menu_labels(self.hass.config.language),
        )

    async def async_step_energy_sources(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            self._update_data(
                {
                    CONF_GRID_POWER_SENSOR: user_input.get(CONF_GRID_POWER_SENSOR),
                    CONF_GRID_IMPORT_POWER_SENSORS: _entity_list(
                        user_input.get(CONF_GRID_IMPORT_POWER_SENSORS)
                    ),
                    CONF_GRID_EXPORT_POWER_SENSORS: _entity_list(
                        user_input.get(CONF_GRID_EXPORT_POWER_SENSORS)
                    ),
                    CONF_GRID_SIGNED_IMPORT_POSITIVE_SENSORS: _entity_list(
                        user_input.get(CONF_GRID_SIGNED_IMPORT_POSITIVE_SENSORS)
                    ),
                    CONF_GRID_SIGNED_EXPORT_POSITIVE_SENSORS: _entity_list(
                        user_input.get(CONF_GRID_SIGNED_EXPORT_POSITIVE_SENSORS)
                    ),
                CONF_PV_POWER_SENSORS: _entity_list(
                    user_input.get(CONF_PV_POWER_SENSORS)
                ),
                CONF_PV_SOURCE_PROFILES: user_input.get(CONF_PV_SOURCE_PROFILES),
                CONF_PV_FORECAST_NEXT_HOUR_SENSOR: user_input.get(
                    CONF_PV_FORECAST_NEXT_HOUR_SENSOR
                ),
                CONF_PV_FORECAST_NEXT_3H_SENSOR: user_input.get(
                    CONF_PV_FORECAST_NEXT_3H_SENSOR
                ),
                    CONF_BATTERY_SOC_SENSORS: _entity_list(
                        user_input.get(CONF_BATTERY_SOC_SENSORS)
                    ),
                    CONF_BATTERY_DISCHARGE_SENSORS: _entity_list(
                        user_input.get(CONF_BATTERY_DISCHARGE_SENSORS)
                    ),
                    CONF_BATTERY_CHARGE_SENSORS: _entity_list(
                        user_input.get(CONF_BATTERY_CHARGE_SENSORS)
                    ),
                    CONF_BATTERY_SIGNED_DISCHARGE_POSITIVE_SENSORS: _entity_list(
                        user_input.get(CONF_BATTERY_SIGNED_DISCHARGE_POSITIVE_SENSORS)
                    ),
                    CONF_BATTERY_SIGNED_CHARGE_POSITIVE_SENSORS: _entity_list(
                        user_input.get(CONF_BATTERY_SIGNED_CHARGE_POSITIVE_SENSORS)
                    ),
                    CONF_HOUSE_LOAD_SENSORS: _entity_list(
                        user_input.get(CONF_HOUSE_LOAD_SENSORS)
                    ),
                    CONF_AC_BATTERY_PROFILES: user_input.get(CONF_AC_BATTERY_PROFILES),
                    CONF_GRID_IMPORT_PRICE_SENSOR: user_input.get(
                        CONF_GRID_IMPORT_PRICE_SENSOR
                    ),
                    CONF_GRID_EXPORT_PRICE_SENSOR: user_input.get(
                        CONF_GRID_EXPORT_PRICE_SENSOR
                    ),
                    CONF_VIRTUAL_BATTERY_CHARGE_SENSOR: user_input.get(
                        CONF_VIRTUAL_BATTERY_CHARGE_SENSOR
                    ),
                    CONF_VIRTUAL_BATTERY_DISCHARGE_SENSOR: user_input.get(
                        CONF_VIRTUAL_BATTERY_DISCHARGE_SENSOR
                    ),
                }
            )
            return self.async_create_entry(title="", data=dict(self._entry.options))

        return self.async_show_form(
            step_id="energy_sources",
            data_schema=_energy_sources_schema(self._defaults()),
        )

    async def async_step_weather_sources(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            self._update_data(
                {
                    CONF_CLOUD_SENSOR: user_input.get(CONF_CLOUD_SENSOR),
                    CONF_SUN_ENTITY: user_input.get(CONF_SUN_ENTITY),
                }
            )
            return self.async_create_entry(title="", data=dict(self._entry.options))

        return self.async_show_form(
            step_id="weather_sources",
            data_schema=_weather_sources_schema(self._defaults()),
        )

    async def async_step_load_sources(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            self._update_data(
                {
                    CONF_FLEXIBLE_LOAD_SWITCHES: _entity_list(
                        user_input.get(CONF_FLEXIBLE_LOAD_SWITCHES)
                    ),
                    CONF_FLEXIBLE_LOAD_POWER_SENSORS: _entity_list(
                        user_input.get(CONF_FLEXIBLE_LOAD_POWER_SENSORS)
                    ),
                    CONF_START_ONLY_APPLIANCE_SWITCHES: _entity_list(
                        user_input.get(CONF_START_ONLY_APPLIANCE_SWITCHES)
                    ),
                    CONF_START_ONLY_APPLIANCE_POWER_SENSORS: _entity_list(
                        user_input.get(CONF_START_ONLY_APPLIANCE_POWER_SENSORS)
                    ),
                    CONF_DEVICE_PROFILES: user_input.get(CONF_DEVICE_PROFILES),
                    CONF_WALLBOX_SWITCHES: _entity_list(
                        user_input.get(CONF_WALLBOX_SWITCHES)
                    ),
                    CONF_HEAT_PUMP_SWITCHES: _entity_list(
                        user_input.get(CONF_HEAT_PUMP_SWITCHES)
                    ),
                    CONF_HEATING_ROD_SWITCHES: _entity_list(
                        user_input.get(CONF_HEATING_ROD_SWITCHES)
                    ),
                    CONF_HEATING_ROD_POWER_SENSORS: _entity_list(
                        user_input.get(CONF_HEATING_ROD_POWER_SENSORS)
                    ),
                    CONF_HEATING_ROD_TEMPERATURE_SENSORS: _entity_list(
                        user_input.get(CONF_HEATING_ROD_TEMPERATURE_SENSORS)
                    ),
                    CONF_HEATING_ROD_TARGET_TEMPERATURES: user_input.get(
                        CONF_HEATING_ROD_TARGET_TEMPERATURES
                    ),
                }
            )
            return self.async_create_entry(title="", data=dict(self._entry.options))

        return self.async_show_form(
            step_id="load_sources",
            data_schema=_load_sources_schema(self._defaults()),
        )

    async def async_step_load_flexible(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            self._update_data(
                {
                    CONF_FLEXIBLE_LOAD_SWITCHES: _entity_list(
                        user_input.get(CONF_FLEXIBLE_LOAD_SWITCHES)
                    ),
                    CONF_FLEXIBLE_LOAD_POWER_SENSORS: _entity_list(
                        user_input.get(CONF_FLEXIBLE_LOAD_POWER_SENSORS)
                    ),
                }
            )
            return self.async_create_entry(title="", data=dict(self._entry.options))

        return self.async_show_form(
            step_id="load_flexible",
            data_schema=_load_flexible_schema(self._defaults()),
        )

    async def async_step_load_start_only(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            self._update_data(
                {
                    CONF_START_ONLY_APPLIANCE_SWITCHES: _entity_list(
                        user_input.get(CONF_START_ONLY_APPLIANCE_SWITCHES)
                    ),
                    CONF_START_ONLY_APPLIANCE_POWER_SENSORS: _entity_list(
                        user_input.get(CONF_START_ONLY_APPLIANCE_POWER_SENSORS)
                    ),
                }
            )
            return self.async_create_entry(title="", data=dict(self._entry.options))

        return self.async_show_form(
            step_id="load_start_only",
            data_schema=_load_start_only_schema(self._defaults()),
        )

    async def async_step_load_heating_rods(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            self._update_data(
                {
                    CONF_HEATING_ROD_SWITCHES: _entity_list(
                        user_input.get(CONF_HEATING_ROD_SWITCHES)
                    ),
                    CONF_HEATING_ROD_POWER_SENSORS: _entity_list(
                        user_input.get(CONF_HEATING_ROD_POWER_SENSORS)
                    ),
                    CONF_HEATING_ROD_TEMPERATURE_SENSORS: _entity_list(
                        user_input.get(CONF_HEATING_ROD_TEMPERATURE_SENSORS)
                    ),
                    CONF_HEATING_ROD_TARGET_TEMPERATURES: user_input.get(
                        CONF_HEATING_ROD_TARGET_TEMPERATURES
                    ),
                }
            )
            return self.async_create_entry(title="", data=dict(self._entry.options))

        return self.async_show_form(
            step_id="load_heating_rods",
            data_schema=_load_heating_rods_schema(self._defaults()),
        )

    async def async_step_load_wallboxes(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            self._update_data(
                {
                    CONF_WALLBOX_SWITCHES: _entity_list(
                        user_input.get(CONF_WALLBOX_SWITCHES)
                    ),
                }
            )
            return self.async_create_entry(title="", data=dict(self._entry.options))

        return self.async_show_form(
            step_id="load_wallboxes",
            data_schema=_load_wallboxes_schema(self._defaults()),
        )

    async def async_step_load_heat_pumps(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            self._update_data(
                {
                    CONF_HEAT_PUMP_SWITCHES: _entity_list(
                        user_input.get(CONF_HEAT_PUMP_SWITCHES)
                    ),
                }
            )
            return self.async_create_entry(title="", data=dict(self._entry.options))

        return self.async_show_form(
            step_id="load_heat_pumps",
            data_schema=_load_heat_pumps_schema(self._defaults()),
        )

    async def async_step_load_advanced(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            self._update_data(
                {
                    CONF_DEVICE_PROFILES: user_input.get(CONF_DEVICE_PROFILES),
                }
            )
            return self.async_create_entry(title="", data=dict(self._entry.options))

        return self.async_show_form(
            step_id="load_advanced",
            data_schema=_load_advanced_schema(self._defaults()),
        )

    def _update_data(self, updates: dict[str, Any]) -> None:
        data = dict(self._entry.data)
        data.update(updates)
        self.hass.config_entries.async_update_entry(self._entry, data=data)

    def _defaults(self) -> dict[str, Any]:
        data = self._entry.data
        return {
            CONF_GRID_POWER_SENSOR: data.get(CONF_GRID_POWER_SENSOR),
            CONF_GRID_IMPORT_POWER_SENSORS: _entity_list(
                data.get(CONF_GRID_IMPORT_POWER_SENSORS)
            ),
            CONF_GRID_EXPORT_POWER_SENSORS: _entity_list(
                data.get(CONF_GRID_EXPORT_POWER_SENSORS)
            ),
            CONF_GRID_SIGNED_IMPORT_POSITIVE_SENSORS: _entity_list(
                data.get(CONF_GRID_SIGNED_IMPORT_POSITIVE_SENSORS)
            ),
            CONF_GRID_SIGNED_EXPORT_POSITIVE_SENSORS: _entity_list(
                data.get(CONF_GRID_SIGNED_EXPORT_POSITIVE_SENSORS)
            ),
            CONF_GRID_AVERAGE_SENSOR: data.get(CONF_GRID_AVERAGE_SENSOR),
            CONF_PV_POWER_SENSORS: _entity_list(data.get(CONF_PV_POWER_SENSORS)),
            CONF_PV_SOURCE_PROFILES: data.get(CONF_PV_SOURCE_PROFILES),
            CONF_PV_AVERAGE_SENSOR: data.get(CONF_PV_AVERAGE_SENSOR),
            CONF_PV_FORECAST_TODAY_SENSOR: data.get(CONF_PV_FORECAST_TODAY_SENSOR),
            CONF_PV_FORECAST_NEXT_HOUR_SENSOR: data.get(
                CONF_PV_FORECAST_NEXT_HOUR_SENSOR
            ),
            CONF_PV_FORECAST_NEXT_3H_SENSOR: data.get(CONF_PV_FORECAST_NEXT_3H_SENSOR),
            CONF_PV_ARRAY_SPECS: data.get(CONF_PV_ARRAY_SPECS),
            CONF_BATTERY_SOC_SENSORS: _entity_list(data.get(CONF_BATTERY_SOC_SENSORS)),
            CONF_BATTERY_DISCHARGE_SENSORS: _entity_list(
                data.get(CONF_BATTERY_DISCHARGE_SENSORS)
            ),
            CONF_BATTERY_CHARGE_SENSORS: _entity_list(
                data.get(CONF_BATTERY_CHARGE_SENSORS)
            ),
            CONF_BATTERY_SIGNED_DISCHARGE_POSITIVE_SENSORS: _entity_list(
                data.get(CONF_BATTERY_SIGNED_DISCHARGE_POSITIVE_SENSORS)
            ),
            CONF_BATTERY_SIGNED_CHARGE_POSITIVE_SENSORS: _entity_list(
                data.get(CONF_BATTERY_SIGNED_CHARGE_POSITIVE_SENSORS)
            ),
            CONF_HOUSE_LOAD_SENSORS: _entity_list(data.get(CONF_HOUSE_LOAD_SENSORS)),
            CONF_AC_BATTERY_PROFILES: data.get(CONF_AC_BATTERY_PROFILES),
            CONF_GRID_IMPORT_PRICE_SENSOR: data.get(CONF_GRID_IMPORT_PRICE_SENSOR),
            CONF_GRID_EXPORT_PRICE_SENSOR: data.get(CONF_GRID_EXPORT_PRICE_SENSOR),
            CONF_VIRTUAL_BATTERY_CHARGE_SENSOR: data.get(
                CONF_VIRTUAL_BATTERY_CHARGE_SENSOR
            ),
            CONF_VIRTUAL_BATTERY_DISCHARGE_SENSOR: data.get(
                CONF_VIRTUAL_BATTERY_DISCHARGE_SENSOR
            ),
            CONF_WEATHER_STATE_SENSOR: data.get(CONF_WEATHER_STATE_SENSOR),
            CONF_CLOUD_SENSOR: data.get(CONF_CLOUD_SENSOR),
            CONF_SUNSHINE_SENSOR: data.get(CONF_SUNSHINE_SENSOR),
            CONF_SUN_ENTITY: data.get(CONF_SUN_ENTITY),
            CONF_FLEXIBLE_LOAD_SWITCHES: _entity_list(
                data.get(CONF_FLEXIBLE_LOAD_SWITCHES)
            ),
            CONF_FLEXIBLE_LOAD_POWER_SENSORS: _entity_list(
                data.get(CONF_FLEXIBLE_LOAD_POWER_SENSORS)
            ),
            CONF_START_ONLY_APPLIANCE_SWITCHES: _entity_list(
                data.get(CONF_START_ONLY_APPLIANCE_SWITCHES)
            ),
            CONF_START_ONLY_APPLIANCE_POWER_SENSORS: _entity_list(
                data.get(CONF_START_ONLY_APPLIANCE_POWER_SENSORS)
            ),
            CONF_DEVICE_PROFILES: data.get(CONF_DEVICE_PROFILES),
            CONF_WALLBOX_SWITCHES: _entity_list(data.get(CONF_WALLBOX_SWITCHES)),
            CONF_HEAT_PUMP_SWITCHES: _entity_list(data.get(CONF_HEAT_PUMP_SWITCHES)),
            CONF_HEATING_ROD_SWITCHES: _entity_list(
                data.get(CONF_HEATING_ROD_SWITCHES)
            ),
            CONF_HEATING_ROD_POWER_SENSORS: _entity_list(
                data.get(CONF_HEATING_ROD_POWER_SENSORS)
            ),
            CONF_HEATING_ROD_TEMPERATURE_SENSORS: _entity_list(
                data.get(CONF_HEATING_ROD_TEMPERATURE_SENSORS)
            ),
            CONF_HEATING_ROD_TARGET_TEMPERATURES: data.get(
                CONF_HEATING_ROD_TARGET_TEMPERATURES
            ),
        }


def _energy_source_fields(defaults: dict[str, Any]) -> dict[Any, Any]:
    return {
        vol.Optional(
            CONF_GRID_POWER_SENSOR,
            default=defaults.get(CONF_GRID_POWER_SENSOR),
        ): selector.EntitySelector(selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS)),
        vol.Optional(
            CONF_GRID_IMPORT_POWER_SENSORS,
            default=defaults.get(CONF_GRID_IMPORT_POWER_SENSORS, []),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS, multiple=True)
        ),
        vol.Optional(
            CONF_GRID_EXPORT_POWER_SENSORS,
            default=defaults.get(CONF_GRID_EXPORT_POWER_SENSORS, []),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS, multiple=True)
        ),
        vol.Optional(
            CONF_GRID_SIGNED_IMPORT_POSITIVE_SENSORS,
            default=defaults.get(CONF_GRID_SIGNED_IMPORT_POSITIVE_SENSORS, []),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS, multiple=True)
        ),
        vol.Optional(
            CONF_GRID_SIGNED_EXPORT_POSITIVE_SENSORS,
            default=defaults.get(CONF_GRID_SIGNED_EXPORT_POSITIVE_SENSORS, []),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS, multiple=True)
        ),
        vol.Optional(
            CONF_PV_POWER_SENSORS,
            default=defaults.get(CONF_PV_POWER_SENSORS, []),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS, multiple=True)
        ),
        _optional_text(defaults, CONF_PV_SOURCE_PROFILES): selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
        ),
        _optional_entity(defaults, CONF_PV_FORECAST_NEXT_HOUR_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS)
        ),
        _optional_entity(defaults, CONF_PV_FORECAST_NEXT_3H_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS)
        ),
        vol.Optional(
            CONF_BATTERY_SOC_SENSORS,
            default=defaults.get(CONF_BATTERY_SOC_SENSORS, []),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS, multiple=True)
        ),
        vol.Optional(
            CONF_BATTERY_DISCHARGE_SENSORS,
            default=defaults.get(CONF_BATTERY_DISCHARGE_SENSORS, []),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS, multiple=True)
        ),
        vol.Optional(
            CONF_BATTERY_CHARGE_SENSORS,
            default=defaults.get(CONF_BATTERY_CHARGE_SENSORS, []),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS, multiple=True)
        ),
        vol.Optional(
            CONF_BATTERY_SIGNED_DISCHARGE_POSITIVE_SENSORS,
            default=defaults.get(CONF_BATTERY_SIGNED_DISCHARGE_POSITIVE_SENSORS, []),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS, multiple=True)
        ),
        vol.Optional(
            CONF_BATTERY_SIGNED_CHARGE_POSITIVE_SENSORS,
            default=defaults.get(CONF_BATTERY_SIGNED_CHARGE_POSITIVE_SENSORS, []),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS, multiple=True)
        ),
        vol.Optional(
            CONF_HOUSE_LOAD_SENSORS,
            default=defaults.get(CONF_HOUSE_LOAD_SENSORS, []),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS, multiple=True)
        ),
        _optional_text(defaults, CONF_AC_BATTERY_PROFILES): selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
        ),
        _optional_entity(defaults, CONF_GRID_IMPORT_PRICE_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS)
        ),
        _optional_entity(defaults, CONF_GRID_EXPORT_PRICE_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS)
        ),
        _optional_entity(defaults, CONF_VIRTUAL_BATTERY_CHARGE_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS)
        ),
        _optional_entity(defaults, CONF_VIRTUAL_BATTERY_DISCHARGE_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS)
        ),
    }


def _schema(defaults: dict[str, Any]) -> vol.Schema:
    fields: dict[Any, Any] = {
        vol.Optional(CONF_NAME, default=defaults.get(CONF_NAME, NAME)): str,
        **_energy_source_fields(defaults),
        vol.Optional(
            CONF_CLOUD_SENSOR,
            default=defaults.get(CONF_CLOUD_SENSOR),
        ): selector.EntitySelector(selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS)),
        vol.Optional(
            CONF_SUN_ENTITY,
            default=defaults.get(CONF_SUN_ENTITY),
        ): selector.EntitySelector(selector.EntitySelectorConfig(domain=["sun"])),
        vol.Optional(
            CONF_FLEXIBLE_LOAD_SWITCHES,
            default=defaults.get(CONF_FLEXIBLE_LOAD_SWITCHES, []),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=SWITCHABLE_DOMAINS, multiple=True)
        ),
        vol.Optional(
            CONF_FLEXIBLE_LOAD_POWER_SENSORS,
            default=defaults.get(CONF_FLEXIBLE_LOAD_POWER_SENSORS, []),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS, multiple=True)
        ),
        vol.Optional(
            CONF_START_ONLY_APPLIANCE_SWITCHES,
            default=defaults.get(CONF_START_ONLY_APPLIANCE_SWITCHES, []),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=STARTABLE_DOMAINS, multiple=True)
        ),
        vol.Optional(
            CONF_START_ONLY_APPLIANCE_POWER_SENSORS,
            default=defaults.get(CONF_START_ONLY_APPLIANCE_POWER_SENSORS, []),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS, multiple=True)
        ),
        _optional_text(defaults, CONF_DEVICE_PROFILES): selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
        ),
        vol.Optional(
            CONF_WALLBOX_SWITCHES,
            default=defaults.get(CONF_WALLBOX_SWITCHES, []),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=SWITCHABLE_DOMAINS, multiple=True)
        ),
        vol.Optional(
            CONF_HEAT_PUMP_SWITCHES,
            default=defaults.get(CONF_HEAT_PUMP_SWITCHES, []),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=SWITCHABLE_DOMAINS, multiple=True)
        ),
        vol.Optional(
            CONF_HEATING_ROD_SWITCHES,
            default=defaults.get(CONF_HEATING_ROD_SWITCHES, []),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=SWITCHABLE_DOMAINS, multiple=True)
        ),
        vol.Optional(
            CONF_HEATING_ROD_POWER_SENSORS,
            default=defaults.get(CONF_HEATING_ROD_POWER_SENSORS, []),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS, multiple=True)
        ),
        vol.Optional(
            CONF_HEATING_ROD_TEMPERATURE_SENSORS,
            default=defaults.get(CONF_HEATING_ROD_TEMPERATURE_SENSORS, []),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS, multiple=True)
        ),
        _optional_text(defaults, CONF_HEATING_ROD_TARGET_TEMPERATURES): selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
        ),
    }
    return vol.Schema(fields)


def _energy_sources_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(_energy_source_fields(defaults))


def _weather_sources_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional(
                CONF_CLOUD_SENSOR,
                default=defaults.get(CONF_CLOUD_SENSOR),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS)
            ),
            vol.Optional(
                CONF_SUN_ENTITY,
                default=defaults.get(CONF_SUN_ENTITY),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["sun"])
            ),
        }
    )


def _load_sources_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional(
                CONF_FLEXIBLE_LOAD_SWITCHES,
                default=defaults.get(CONF_FLEXIBLE_LOAD_SWITCHES, []),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=SWITCHABLE_DOMAINS, multiple=True)
            ),
            vol.Optional(
                CONF_FLEXIBLE_LOAD_POWER_SENSORS,
                default=defaults.get(CONF_FLEXIBLE_LOAD_POWER_SENSORS, []),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS, multiple=True)
            ),
            vol.Optional(
                CONF_START_ONLY_APPLIANCE_SWITCHES,
                default=defaults.get(CONF_START_ONLY_APPLIANCE_SWITCHES, []),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=STARTABLE_DOMAINS, multiple=True)
            ),
            vol.Optional(
                CONF_START_ONLY_APPLIANCE_POWER_SENSORS,
                default=defaults.get(CONF_START_ONLY_APPLIANCE_POWER_SENSORS, []),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS, multiple=True)
            ),
            _optional_text(defaults, CONF_DEVICE_PROFILES): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
            ),
            vol.Optional(
                CONF_WALLBOX_SWITCHES,
                default=defaults.get(CONF_WALLBOX_SWITCHES, []),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=SWITCHABLE_DOMAINS, multiple=True)
            ),
            vol.Optional(
                CONF_HEAT_PUMP_SWITCHES,
                default=defaults.get(CONF_HEAT_PUMP_SWITCHES, []),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=SWITCHABLE_DOMAINS, multiple=True)
            ),
            vol.Optional(
                CONF_HEATING_ROD_SWITCHES,
                default=defaults.get(CONF_HEATING_ROD_SWITCHES, []),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=SWITCHABLE_DOMAINS, multiple=True)
            ),
            vol.Optional(
                CONF_HEATING_ROD_POWER_SENSORS,
                default=defaults.get(CONF_HEATING_ROD_POWER_SENSORS, []),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS, multiple=True)
            ),
            vol.Optional(
                CONF_HEATING_ROD_TEMPERATURE_SENSORS,
                default=defaults.get(CONF_HEATING_ROD_TEMPERATURE_SENSORS, []),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS, multiple=True)
            ),
            _optional_text(
                defaults, CONF_HEATING_ROD_TARGET_TEMPERATURES
            ): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
            ),
        }
    )


def _load_flexible_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional(
                CONF_FLEXIBLE_LOAD_SWITCHES,
                default=defaults.get(CONF_FLEXIBLE_LOAD_SWITCHES, []),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=SWITCHABLE_DOMAINS, multiple=True)
            ),
            vol.Optional(
                CONF_FLEXIBLE_LOAD_POWER_SENSORS,
                default=defaults.get(CONF_FLEXIBLE_LOAD_POWER_SENSORS, []),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS, multiple=True)
            ),
        }
    )


def _load_start_only_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional(
                CONF_START_ONLY_APPLIANCE_SWITCHES,
                default=defaults.get(CONF_START_ONLY_APPLIANCE_SWITCHES, []),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=STARTABLE_DOMAINS, multiple=True)
            ),
            vol.Optional(
                CONF_START_ONLY_APPLIANCE_POWER_SENSORS,
                default=defaults.get(CONF_START_ONLY_APPLIANCE_POWER_SENSORS, []),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS, multiple=True)
            ),
        }
    )


def _load_heating_rods_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional(
                CONF_HEATING_ROD_SWITCHES,
                default=defaults.get(CONF_HEATING_ROD_SWITCHES, []),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=SWITCHABLE_DOMAINS, multiple=True)
            ),
            vol.Optional(
                CONF_HEATING_ROD_POWER_SENSORS,
                default=defaults.get(CONF_HEATING_ROD_POWER_SENSORS, []),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS, multiple=True)
            ),
            vol.Optional(
                CONF_HEATING_ROD_TEMPERATURE_SENSORS,
                default=defaults.get(CONF_HEATING_ROD_TEMPERATURE_SENSORS, []),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS, multiple=True)
            ),
            _optional_text(
                defaults, CONF_HEATING_ROD_TARGET_TEMPERATURES
            ): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
            ),
        }
    )


def _load_wallboxes_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional(
                CONF_WALLBOX_SWITCHES,
                default=defaults.get(CONF_WALLBOX_SWITCHES, []),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=SWITCHABLE_DOMAINS, multiple=True)
            ),
        }
    )


def _load_heat_pumps_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional(
                CONF_HEAT_PUMP_SWITCHES,
                default=defaults.get(CONF_HEAT_PUMP_SWITCHES, []),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=SWITCHABLE_DOMAINS, multiple=True)
            ),
        }
    )


def _load_advanced_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            _optional_text(defaults, CONF_DEVICE_PROFILES): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
            ),
        }
    )
