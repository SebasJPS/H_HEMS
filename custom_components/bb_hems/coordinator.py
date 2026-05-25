"""Coordinator and decision model for BB HEMS."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import *

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class HemsData:
    grid_power: float
    grid_average: float
    pv_power: float
    pv_average: float
    battery_soc_min: float | None
    battery_discharge: float
    cloud_coverage: float | None
    sunshine_minutes: float | None
    weather_state: str | None
    good_weather: bool
    bad_weather: bool
    battery_protect: bool
    surplus_available: bool
    flexible_loads_allowed: bool
    energy_mode: str
    grid_tolerance: float
    active_flexible_loads: int
    configured_pv_sources: int
    configured_batteries: int
    configured_flexible_loads: int
    configured_wallboxes: int
    configured_heat_pumps: int


class HemsCoordinator(DataUpdateCoordinator[HemsData]):
    """Calculate reusable HEMS decisions from configured Home Assistant entities."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, logger=_LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)
        self.config_entry = entry

    async def _async_update_data(self) -> HemsData:
        return self._calculate()

    @property
    def opts(self) -> dict[str, Any]:
        return {**DEFAULTS, **dict(self.config_entry.options)}

    async def async_set_option(self, key: str, value: Any) -> None:
        options = dict(self.config_entry.options)
        options[key] = value
        self.hass.config_entries.async_update_entry(self.config_entry, options=options)
        await self.async_request_refresh()

    def _calculate(self) -> HemsData:
        data = self.config_entry.data
        opts = self.opts
        grid_power = self._float_state(data.get(CONF_GRID_POWER_SENSOR), 0.0)
        grid_average = self._float_state(data.get(CONF_GRID_AVERAGE_SENSOR), grid_power)
        pv_sources = data.get(CONF_PV_POWER_SENSORS, [])
        soc_sources = data.get(CONF_BATTERY_SOC_SENSORS, [])
        discharge_sources = data.get(CONF_BATTERY_DISCHARGE_SENSORS, [])
        flexible_loads = data.get(CONF_FLEXIBLE_LOAD_SWITCHES, [])
        wallboxes = data.get(CONF_WALLBOX_SWITCHES, [])
        heat_pumps = data.get(CONF_HEAT_PUMP_SWITCHES, [])
        pv_power = sum(self._float_state(entity_id, 0.0) for entity_id in pv_sources)
        pv_average = self._float_state(data.get(CONF_PV_AVERAGE_SENSOR), pv_power)
        soc_values = [self._float_state(entity_id, None) for entity_id in soc_sources]
        soc_values = [value for value in soc_values if value is not None]
        battery_soc_min = min(soc_values) if soc_values else None
        battery_discharge = sum(self._float_state(entity_id, 0.0) for entity_id in discharge_sources)
        weather_state = self._state(data.get(CONF_WEATHER_STATE_SENSOR))
        weather = weather_state.lower() if weather_state else None
        clouds = self._float_state(data.get(CONF_CLOUD_SENSOR), None)
        sunshine = self._float_state(data.get(CONF_SUNSHINE_SENSOR), None)
        good_weather = self._good_weather(battery_soc_min, weather, clouds, sunshine)
        bad_weather = self._bad_weather(weather, clouds)
        grid_tolerance = self._grid_tolerance(battery_soc_min, good_weather)
        battery_protect = self._battery_protect(battery_soc_min, battery_discharge, bad_weather)
        mode = opts[OPT_MODE]
        if mode == MODE_OFF or not opts[OPT_AUTO_ENABLED]:
            surplus_available = False
            flexible_loads_allowed = False
            energy_mode = "off"
        elif mode == MODE_FORCE_SURPLUS:
            surplus_available = True
            flexible_loads_allowed = not battery_protect
            energy_mode = "force_surplus" if flexible_loads_allowed else "battery_protect"
        else:
            grid_limit = self._mode_grid_limit(mode, grid_tolerance)
            surplus_available = (
                pv_power >= float(opts[OPT_PV_THRESHOLD])
                and pv_average >= float(opts[OPT_PV_AVG_THRESHOLD])
                and (grid_power <= grid_limit or (grid_average < 50 and good_weather))
            )
            flexible_loads_allowed = surplus_available and good_weather and not battery_protect and self._battery_soc_ok(battery_soc_min)
            energy_mode = self._energy_mode(mode, grid_power, pv_power, surplus_available, battery_protect, good_weather)
        active_flexible_loads = sum(1 for entity_id in flexible_loads if self.hass.states.is_state(entity_id, STATE_ON))
        return HemsData(grid_power, grid_average, pv_power, pv_average, battery_soc_min, battery_discharge, clouds, sunshine, weather_state, good_weather, bad_weather, battery_protect, surplus_available, flexible_loads_allowed, energy_mode, grid_tolerance, active_flexible_loads, len(pv_sources), len(soc_sources), len(flexible_loads), len(wallboxes), len(heat_pumps))

    def _state(self, entity_id: str | None) -> str | None:
        if not entity_id:
            return None
        state = self.hass.states.get(entity_id)
        if state is None or state.state in {STATE_UNKNOWN, STATE_UNAVAILABLE}:
            return None
        return state.state

    def _float_state(self, entity_id: str | None, default: float | None) -> float | None:
        state = self._state(entity_id)
        if state is None:
            return default
        try:
            return float(state.replace(",", "."))
        except (TypeError, ValueError):
            return default

    def _good_weather(self, battery_soc: float | None, weather: str | None, clouds: float | None, sunshine: float | None) -> bool:
        if battery_soc is not None and battery_soc >= 90:
            return True
        if weather is None:
            return True
        cloud_value = clouds if clouds is not None else 0
        sunshine_value = sunshine if sunshine is not None else 999
        if battery_soc is not None and battery_soc >= 75:
            return weather in GOOD_WEATHER and cloud_value < 85
        return weather in GOOD_WEATHER and cloud_value < 70 and sunshine_value > 20

    def _bad_weather(self, weather: str | None, clouds: float | None) -> bool:
        return (weather in BAD_WEATHER if weather else False) or (clouds if clouds is not None else 0) > 90

    def _grid_tolerance(self, battery_soc: float | None, good_weather: bool) -> float:
        if not good_weather:
            return -25.0
        if battery_soc is not None and battery_soc >= 90:
            return 300.0
        if battery_soc is not None and battery_soc >= 75:
            return 175.0
        if battery_soc is not None and battery_soc >= 50:
            return float(self.opts[OPT_GRID_IMPORT_LIMIT])
        return -25.0

    def _battery_protect(self, battery_soc: float | None, battery_discharge: float, bad_weather: bool) -> bool:
        if battery_soc is not None and battery_soc < float(self.opts[OPT_PROTECT_BATTERY_SOC]):
            return True
        if battery_discharge > float(self.opts[OPT_BATTERY_DISCHARGE_LIMIT]):
            return True
        return bool(bad_weather and battery_soc is not None and battery_soc < 70)

    def _battery_soc_ok(self, battery_soc: float | None) -> bool:
        return True if battery_soc is None else battery_soc >= float(self.opts[OPT_MIN_BATTERY_SOC])

    def _mode_grid_limit(self, mode: str, grid_tolerance: float) -> float:
        if mode == MODE_COMFORT:
            return max(grid_tolerance, float(self.opts[OPT_GRID_IMPORT_LIMIT]) + 100)
        if mode == MODE_ECO:
            return min(grid_tolerance, 0.0)
        return grid_tolerance

    def _energy_mode(self, mode: str, grid_power: float, pv_power: float, surplus_available: bool, battery_protect: bool, good_weather: bool) -> str:
        if battery_protect:
            return "battery_protect"
        if not good_weather:
            return "weather_hold"
        if surplus_available and pv_power >= float(self.opts[OPT_PV_THRESHOLD]) * 2:
            return "surplus_high"
        if surplus_available:
            return "surplus_medium" if mode != MODE_ECO else "surplus_low"
        if grid_power > float(self.opts[OPT_GRID_HARD_IMPORT_LIMIT]):
            return "importing_high"
        if grid_power > 0:
            return "importing"
        return MODE_AUTO
