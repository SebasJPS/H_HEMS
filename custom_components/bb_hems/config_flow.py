"""Config flow for BB HEMS slim v1."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import selector

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
    DEFAULTS,
    DOMAIN,
    NAME,
)

NUMERIC_DOMAINS = ["sensor", "number", "input_number"]
SWITCHABLE_DOMAINS = ["switch", "input_boolean"]
STARTABLE_DOMAINS = ["switch", "input_boolean", "button"]


def _entity_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return [item for item in value if item]


def _optional_entity(defaults: dict[str, Any], key: str) -> vol.Optional:
    value = defaults.get(key)
    return vol.Optional(key, default=value) if value else vol.Optional(key)


def _optional_text(defaults: dict[str, Any], key: str) -> vol.Optional:
    value = defaults.get(key)
    return vol.Optional(key, default=value) if value else vol.Optional(key)


def _menu_labels(language: str | None) -> dict[str, str]:
    if language and language.lower().startswith("de"):
        return {
            "energy": "Energiequellen",
            "loads": "Verbraucher",
            "ac_battery": "AC-Akku",
        }
    return {
        "energy": "Energy sources",
        "loads": "Loads",
        "ac_battery": "AC battery",
    }


class BbHemsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Create a BB HEMS config entry."""

    VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input.get(CONF_NAME, NAME),
                data=_entry_data(user_input),
                options=DEFAULTS,
            )
        return self.async_show_form(step_id="user", data_schema=_schema({}))

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return BbHemsOptionsFlow(config_entry)


class BbHemsOptionsFlow(config_entries.OptionsFlow):
    """Edit BB HEMS sources."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        return self.async_show_menu(
            step_id="init",
            menu_options=_menu_labels(self.hass.config.language),
        )

    async def async_step_energy(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            self._update_data(_energy_data(user_input))
            return self.async_create_entry(title="", data=dict(self._entry.options))
        return self.async_show_form(
            step_id="energy", data_schema=_energy_schema(self._defaults())
        )

    async def async_step_loads(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            self._update_data(_load_data(user_input))
            return self.async_create_entry(title="", data=dict(self._entry.options))
        return self.async_show_form(
            step_id="loads", data_schema=_load_schema(self._defaults())
        )

    async def async_step_ac_battery(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            self._update_data(
                {CONF_AC_BATTERY_PROFILES: user_input.get(CONF_AC_BATTERY_PROFILES)}
            )
            return self.async_create_entry(title="", data=dict(self._entry.options))
        return self.async_show_form(
            step_id="ac_battery", data_schema=_ac_battery_schema(self._defaults())
        )

    def _update_data(self, updates: dict[str, Any]) -> None:
        data = dict(self._entry.data)
        data.update(updates)
        self.hass.config_entries.async_update_entry(self._entry, data=data)

    def _defaults(self) -> dict[str, Any]:
        data = self._entry.data
        return {
            **{key: data.get(key) for key in _SINGLE_ENTITY_KEYS},
            **{key: _entity_list(data.get(key)) for key in _MULTI_ENTITY_KEYS},
            CONF_AC_BATTERY_PROFILES: data.get(CONF_AC_BATTERY_PROFILES),
        }


_SINGLE_ENTITY_KEYS = [CONF_GRID_POWER_SENSOR]
_MULTI_ENTITY_KEYS = [
    CONF_GRID_IMPORT_POWER_SENSORS,
    CONF_GRID_EXPORT_POWER_SENSORS,
    CONF_GRID_SIGNED_IMPORT_POSITIVE_SENSORS,
    CONF_GRID_SIGNED_EXPORT_POSITIVE_SENSORS,
    CONF_PV_POWER_SENSORS,
    CONF_BATTERY_SOC_SENSORS,
    CONF_BATTERY_DISCHARGE_SENSORS,
    CONF_HOUSE_LOAD_SENSORS,
    CONF_POOL_SWITCHES,
    CONF_POOL_POWER_SENSORS,
    CONF_DEHUMIDIFIER_SWITCHES,
    CONF_DEHUMIDIFIER_POWER_SENSORS,
    CONF_START_ONLY_APPLIANCE_SWITCHES,
    CONF_START_ONLY_APPLIANCE_POWER_SENSORS,
]


def _entry_data(user_input: dict[str, Any]) -> dict[str, Any]:
    return {
        CONF_NAME: user_input.get(CONF_NAME, NAME),
        **_energy_data(user_input),
        **_load_data(user_input),
        CONF_AC_BATTERY_PROFILES: user_input.get(CONF_AC_BATTERY_PROFILES),
    }


def _energy_data(user_input: dict[str, Any]) -> dict[str, Any]:
    return {
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
        CONF_PV_POWER_SENSORS: _entity_list(user_input.get(CONF_PV_POWER_SENSORS)),
        CONF_BATTERY_SOC_SENSORS: _entity_list(
            user_input.get(CONF_BATTERY_SOC_SENSORS)
        ),
        CONF_BATTERY_DISCHARGE_SENSORS: _entity_list(
            user_input.get(CONF_BATTERY_DISCHARGE_SENSORS)
        ),
        CONF_HOUSE_LOAD_SENSORS: _entity_list(user_input.get(CONF_HOUSE_LOAD_SENSORS)),
    }


def _load_data(user_input: dict[str, Any]) -> dict[str, Any]:
    return {
        CONF_POOL_SWITCHES: _entity_list(user_input.get(CONF_POOL_SWITCHES)),
        CONF_POOL_POWER_SENSORS: _entity_list(
            user_input.get(CONF_POOL_POWER_SENSORS)
        ),
        CONF_DEHUMIDIFIER_SWITCHES: _entity_list(
            user_input.get(CONF_DEHUMIDIFIER_SWITCHES)
        ),
        CONF_DEHUMIDIFIER_POWER_SENSORS: _entity_list(
            user_input.get(CONF_DEHUMIDIFIER_POWER_SENSORS)
        ),
        CONF_START_ONLY_APPLIANCE_SWITCHES: _entity_list(
            user_input.get(CONF_START_ONLY_APPLIANCE_SWITCHES)
        ),
        CONF_START_ONLY_APPLIANCE_POWER_SENSORS: _entity_list(
            user_input.get(CONF_START_ONLY_APPLIANCE_POWER_SENSORS)
        ),
    }


def _schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional(CONF_NAME, default=defaults.get(CONF_NAME, NAME)): str,
            **_energy_fields(defaults),
            **_load_fields(defaults),
            **_ac_battery_fields(defaults),
        }
    )


def _energy_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(_energy_fields(defaults))


def _load_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(_load_fields(defaults))


def _ac_battery_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(_ac_battery_fields(defaults))


def _energy_fields(defaults: dict[str, Any]) -> dict[Any, Any]:
    return {
        _optional_entity(defaults, CONF_GRID_POWER_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS)
        ),
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
            CONF_HOUSE_LOAD_SENSORS,
            default=defaults.get(CONF_HOUSE_LOAD_SENSORS, []),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS, multiple=True)
        ),
    }


def _load_fields(defaults: dict[str, Any]) -> dict[Any, Any]:
    return {
        vol.Optional(
            CONF_POOL_SWITCHES, default=defaults.get(CONF_POOL_SWITCHES, [])
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=SWITCHABLE_DOMAINS, multiple=True)
        ),
        vol.Optional(
            CONF_POOL_POWER_SENSORS,
            default=defaults.get(CONF_POOL_POWER_SENSORS, []),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=NUMERIC_DOMAINS, multiple=True)
        ),
        vol.Optional(
            CONF_DEHUMIDIFIER_SWITCHES,
            default=defaults.get(CONF_DEHUMIDIFIER_SWITCHES, []),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=SWITCHABLE_DOMAINS, multiple=True)
        ),
        vol.Optional(
            CONF_DEHUMIDIFIER_POWER_SENSORS,
            default=defaults.get(CONF_DEHUMIDIFIER_POWER_SENSORS, []),
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
    }


def _ac_battery_fields(defaults: dict[str, Any]) -> dict[Any, Any]:
    return {
        _optional_text(defaults, CONF_AC_BATTERY_PROFILES): selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
        ),
    }
