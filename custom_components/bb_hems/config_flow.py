"""Config flow for BB HEMS."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_BATTERY_CHARGE_SENSORS,
    CONF_BATTERY_DISCHARGE_SENSORS,
    CONF_BATTERY_SOC_SENSORS,
    CONF_CLOUD_SENSOR,
    CONF_FLEXIBLE_LOAD_POWER_SENSORS,
    CONF_FLEXIBLE_LOAD_SWITCHES,
    CONF_GRID_AVERAGE_SENSOR,
    CONF_GRID_POWER_SENSOR,
    CONF_HEAT_PUMP_SWITCHES,
    CONF_HEATING_ROD_POWER_SENSORS,
    CONF_HEATING_ROD_SWITCHES,
    CONF_PV_ARRAY_SPECS,
    CONF_PV_AVERAGE_SENSOR,
    CONF_PV_FORECAST_NEXT_3H_SENSOR,
    CONF_PV_FORECAST_NEXT_HOUR_SENSOR,
    CONF_PV_FORECAST_TODAY_SENSOR,
    CONF_PV_POWER_SENSORS,
    CONF_SUN_ENTITY,
    CONF_SUNSHINE_SENSOR,
    CONF_WALLBOX_SWITCHES,
    CONF_WEATHER_STATE_SENSOR,
    DEFAULTS,
    DOMAIN,
    NAME,
)


NUMERIC_DOMAINS = ["sensor", "number", "input_number"]
SWITCHABLE_DOMAINS = ["switch", "input_boolean"]


def _is_german(language: str | None) -> bool:
    """Return whether the Home Assistant UI language should use German text."""
    return bool(language and language.lower().startswith("de"))


def _options_menu_labels(language: str | None) -> dict[str, str]:
    """Return robust labels for the options menu."""
    if _is_german(language):
        return {
            "energy_sources": "Netz, PV und Batterie - Messwerte und Forecasts",
            "weather_sources": "Wetter und Sonne - Wetterzustand, Bewölkung, Sonnenstand",
            "load_sources": "Verbraucher - Schalter und Leistungssensoren",
        }
    return {
        "energy_sources": "Grid, PV and battery - meters and forecasts",
        "weather_sources": "Weather and sun - state, clouds and sun position",
        "load_sources": "Loads - switches and power sensors",
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
                CONF_GRID_AVERAGE_SENSOR: user_input.get(CONF_GRID_AVERAGE_SENSOR),
                CONF_PV_POWER_SENSORS: _entity_list(
                    user_input.get(CONF_PV_POWER_SENSORS)
                ),
                CONF_PV_AVERAGE_SENSOR: user_input.get(CONF_PV_AVERAGE_SENSOR),
                CONF_PV_FORECAST_TODAY_SENSOR: user_input.get(
                    CONF_PV_FORECAST_TODAY_SENSOR
                ),
                CONF_PV_FORECAST_NEXT_HOUR_SENSOR: user_input.get(
                    CONF_PV_FORECAST_NEXT_HOUR_SENSOR
                ),
                CONF_PV_FORECAST_NEXT_3H_SENSOR: user_input.get(
                    CONF_PV_FORECAST_NEXT_3H_SENSOR
                ),
                CONF_PV_ARRAY_SPECS: user_input.get(CONF_PV_ARRAY_SPECS),
                CONF_BATTERY_SOC_SENSORS: _entity_list(
                    user_input.get(CONF_BATTERY_SOC_SENSORS)
                ),
                CONF_BATTERY_DISCHARGE_SENSORS: _entity_list(
                    user_input.get(CONF_BATTERY_DISCHARGE_SENSORS)
                ),
                CONF_BATTERY_CHARGE_SENSORS: _entity_list(
                    user_input.get(CONF_BATTERY_CHARGE_SENSORS)
                ),
                CONF_WEATHER_STATE_SENSOR: user_input.get(CONF_WEATHER_STATE_SENSOR),
                CONF_CLOUD_SENSOR: user_input.get(CONF_CLOUD_SENSOR),
                CONF_SUNSHINE_SENSOR: user_input.get(CONF_SUNSHINE_SENSOR),
                CONF_SUN_ENTITY: user_input.get(CONF_SUN_ENTITY),
                CONF_FLEXIBLE_LOAD_SWITCHES: _entity_list(
                    user_input.get(CONF_FLEXIBLE_LOAD_SWITCHES)
                ),
                CONF_FLEXIBLE_LOAD_POWER_SENSORS: _entity_list(
                    user_input.get(CONF_FLEXIBLE_LOAD_POWER_SENSORS)
                ),
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
                    CONF_GRID_AVERAGE_SENSOR: user_input.get(CONF_GRID_AVERAGE_SENSOR),
                    CONF_PV_POWER_SENSORS: _entity_list(
                        user_input.get(CONF_PV_POWER_SENSORS)
                    ),
                    CONF_PV_AVERAGE_SENSOR: user_input.get(CONF_PV_AVERAGE_SENSOR),
                    CONF_PV_FORECAST_TODAY_SENSOR: user_input.get(
                        CONF_PV_FORECAST_TODAY_SENSOR
                    ),
                    CONF_PV_FORECAST_NEXT_HOUR_SENSOR: user_input.get(
                        CONF_PV_FORECAST_NEXT_HOUR_SENSOR
                    ),
                    CONF_PV_FORECAST_NEXT_3H_SENSOR: user_input.get(
                        CONF_PV_FORECAST_NEXT_3H_SENSOR
                    ),
                    CONF_PV_ARRAY_SPECS: user_input.get(CONF_PV_ARRAY_SPECS),
                    CONF_BATTERY_SOC_SENSORS: _entity_list(
                        user_input.get(CONF_BATTERY_SOC_SENSORS)
                    ),
                    CONF_BATTERY_DISCHARGE_SENSORS: _entity_list(
                        user_input.get(CONF_BATTERY_DISCHARGE_SENSORS)
                    ),
                    CONF_BATTERY_CHARGE_SENSORS: _entity_list(
                        user_input.get(CONF_BATTERY_CHARGE_SENSORS)
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
                    CONF_WEATHER_STATE_SENSOR: user_input.get(
                        CONF_WEATHER_STATE_SENSOR
                    ),
                    CONF_CLOUD_SENSOR: user_input.get(CONF_CLOUD_SENSOR),
                    CONF_SUNSHINE_SENSOR: user_input.get(CONF_SUNSHINE_SENSOR),
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
                }
            )
            return self.async_create_entry(title="", data=dict(self._entry.options))

        return self.async_show_form(
            step_id="load_sources",
            data_schema=_load_sources_schema(self._defaults()),
        )

    def _update_data(self, updates: dict[str, Any]) -> None:
        data = dict(self._entry.data)
        data.update(updates)
        self.hass.config_entries.async_update_entry(self._entry, data=data)

    def _defaults(self) -> dict[str, Any]:
        data = self._entry.data
        return {
            CONF_GRID_POWER_SENSOR: data.get(CONF_GRID_POWER_SENSOR),
            CONF_GRID_AVERAGE_SENSOR: data.get(CONF_GRID_AVERAGE_SENSOR),
            CONF_PV_POWER_SENSORS: _entity_list(data.get(CONF_PV_POWER_SENSORS)),
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
            CONF_WALLBOX_SWITCHES: _entity_list(data.get(CONF_WALLBOX_SWITCHES)),
            CONF_HEAT_PUMP_SWITCHES: _entity_list(data.get(CONF_HEAT_PUMP_SWITCHES)),
            CONF_HEATING_ROD_SWITCHES: _entity_list(
                data.get(CONF_HEATING_ROD_SWITCHES)
            ),
            CONF_HEATING_ROD_POWER_SENSORS: _entity_list(
                data.get(CONF_HEATING_ROD_POWER_SENSORS)
            ),
        }


def _schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional(CONF_NAME, default=defaults.get(CONF_NAME, NAME)): str,
            vol.Required(
                CONF_GRID_POWER_SENSOR,
                default=defaults.get(CONF_GRID_POWER_SENSOR),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS)
            ),
            vol.Optional(
                CONF_GRID_AVERAGE_SENSOR,
                default=defaults.get(CONF_GRID_AVERAGE_SENSOR),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS)
            ),
            vol.Optional(
                CONF_PV_POWER_SENSORS,
                default=defaults.get(CONF_PV_POWER_SENSORS, []),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS, multiple=True)
            ),
            vol.Optional(
                CONF_PV_AVERAGE_SENSOR,
                default=defaults.get(CONF_PV_AVERAGE_SENSOR),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS)
            ),
            _optional_entity(
                defaults, CONF_PV_FORECAST_TODAY_SENSOR
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS)
            ),
            _optional_entity(
                defaults, CONF_PV_FORECAST_NEXT_HOUR_SENSOR
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS)
            ),
            _optional_entity(
                defaults, CONF_PV_FORECAST_NEXT_3H_SENSOR
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS)
            ),
            _optional_text(defaults, CONF_PV_ARRAY_SPECS): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
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
                CONF_WEATHER_STATE_SENSOR,
                default=defaults.get(CONF_WEATHER_STATE_SENSOR),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["sensor", "weather"])
            ),
            vol.Optional(
                CONF_CLOUD_SENSOR,
                default=defaults.get(CONF_CLOUD_SENSOR),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS)
            ),
            vol.Optional(
                CONF_SUNSHINE_SENSOR,
                default=defaults.get(CONF_SUNSHINE_SENSOR),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS)
            ),
            vol.Optional(
                CONF_SUN_ENTITY,
                default=defaults.get(CONF_SUN_ENTITY),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["sun"])
            ),
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
        }
    )


def _energy_sources_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_GRID_POWER_SENSOR,
                default=defaults.get(CONF_GRID_POWER_SENSOR),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS)
            ),
            vol.Optional(
                CONF_GRID_AVERAGE_SENSOR,
                default=defaults.get(CONF_GRID_AVERAGE_SENSOR),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS)
            ),
            vol.Optional(
                CONF_PV_POWER_SENSORS,
                default=defaults.get(CONF_PV_POWER_SENSORS, []),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS, multiple=True)
            ),
            vol.Optional(
                CONF_PV_AVERAGE_SENSOR,
                default=defaults.get(CONF_PV_AVERAGE_SENSOR),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS)
            ),
            _optional_entity(
                defaults, CONF_PV_FORECAST_TODAY_SENSOR
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS)
            ),
            _optional_entity(
                defaults, CONF_PV_FORECAST_NEXT_HOUR_SENSOR
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS)
            ),
            _optional_entity(
                defaults, CONF_PV_FORECAST_NEXT_3H_SENSOR
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS)
            ),
            _optional_text(defaults, CONF_PV_ARRAY_SPECS): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
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
        }
    )


def _weather_sources_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional(
                CONF_WEATHER_STATE_SENSOR,
                default=defaults.get(CONF_WEATHER_STATE_SENSOR),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["sensor", "weather"])
            ),
            vol.Optional(
                CONF_CLOUD_SENSOR,
                default=defaults.get(CONF_CLOUD_SENSOR),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS)
            ),
            vol.Optional(
                CONF_SUNSHINE_SENSOR,
                default=defaults.get(CONF_SUNSHINE_SENSOR),
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
        }
    )
