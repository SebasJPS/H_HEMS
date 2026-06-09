"""Coordinator and decision model for BB HEMS."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta
import json
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_OFF, STATE_ON, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    BAD_WEATHER,
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
    GOOD_WEATHER,
    MODE_AUTO,
    MODE_COMFORT,
    MODE_ECO,
    MODE_FORCE_SURPLUS,
    MODE_OFF,
    OPT_AUTO_ENABLED,
    OPT_BATTERY_CHARGE_RESERVE_CLOUDY,
    OPT_BATTERY_CHARGE_RESERVE_GOOD,
    OPT_BATTERY_CHARGE_SHARE_SOC,
    OPT_BATTERY_DISCHARGE_LIMIT,
    OPT_BATTERY_PROTECTION_ENABLED,
    OPT_DASHBOARD_ENABLED,
    OPT_FLEXIBLE_LOAD_POWER,
    OPT_GRID_EXPORT_PRICE,
    OPT_GRID_HARD_IMPORT_LIMIT,
    OPT_GRID_IMPORT_LIMIT,
    OPT_GRID_IMPORT_PRICE,
    OPT_HEATING_ROD_POWER,
    OPT_HEATING_ROD_TEMPERATURE_HYSTERESIS,
    OPT_MIN_BATTERY_SOC,
    OPT_MODE,
    OPT_PROTECT_BATTERY_SOC,
    OPT_PV_AVG_THRESHOLD,
    OPT_PV_THRESHOLD,
    OPT_RESPONSE_PROFILE,
    OPT_START_ONLY_APPLIANCE_POWER,
    OPT_USE_VIRTUAL_BATTERY,
    OPT_VIRTUAL_BATTERY_CAPACITY,
    OPT_VIRTUAL_BATTERY_CHARGE_EFFICIENCY,
    OPT_VIRTUAL_BATTERY_DISCHARGE_EFFICIENCY,
    OPT_VIRTUAL_BATTERY_ENABLED,
    OPT_VIRTUAL_BATTERY_MANUAL_SOC,
    OPT_VIRTUAL_BATTERY_MAX_SOC,
    OPT_VIRTUAL_BATTERY_MIN_SOC,
    RESPONSE_AUTO,
    RESPONSE_MINUTES,
    RESPONSE_REALTIME,
    RESPONSE_SECONDS,
    SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)
LEARNING_STORE_VERSION = 1
LEARNING_SAVE_INTERVAL = timedelta(minutes=5)
LEARNING_MIN_SAMPLES = 12
LEARNING_DECISION_MIN_SAMPLES = 72
DAILY_HISTORY_DAYS = 90


@dataclass(frozen=True)
class LoadProfile:
    """A controllable surplus load with a simple smart scheduling profile."""

    entity_id: str
    name: str
    category: str
    estimated_power: float
    actual_power: float | None
    power_sensor: str | None
    priority: int
    min_runtime: timedelta
    cooldown: timedelta
    allow_battery: bool
    control_mode: str
    start_power_threshold: float
    start_timeout: timedelta
    is_on: bool
    blocked: bool = False
    blocked_reason: str | None = None
    temperature: float | None = None
    target_temperature: float | None = None

    @property
    def scheduling_power(self) -> float:
        """Return the best available power value for scheduling."""
        if self.is_on and self.actual_power is not None and self.actual_power > 0:
            return self.actual_power
        return self.estimated_power


@dataclass(frozen=True)
class PvArrayProfile:
    """A PV surface with its own orientation and installed module size."""

    azimuth: float
    tilt: float
    peak_power: float
    module_count: float | None = None
    module_power: float | None = None
    name: str | None = None


@dataclass(frozen=True)
class HemsData:
    """Computed HEMS state."""

    grid_power: float
    grid_average: float
    grid_import: float
    grid_export: float
    grid_import_price: float
    grid_export_price: float
    savings_price: float
    price_reason: str
    pv_power: float
    pv_average: float
    pv_forecast_today: float | None
    pv_forecast_next_hour: float | None
    pv_forecast_next_3h: float | None
    sun_elevation: float | None
    sun_azimuth: float | None
    pv_array_count: int
    pv_best_array: str | None
    pv_orientation_score: float | None
    pv_window: str
    pv_window_reason: str
    battery_soc_min: float | None
    battery_discharge: float
    battery_charge: float
    house_load: float
    usable_battery_charge: float
    virtual_battery_enabled: bool
    virtual_battery_used: bool
    virtual_battery_soc: float | None
    virtual_battery_energy: float | None
    virtual_battery_usable_energy: float | None
    virtual_battery_confidence: float
    virtual_battery_reason: str
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
    configured_start_only_appliances: int
    configured_wallboxes: int
    configured_heat_pumps: int
    configured_heating_rods: int
    configured_profile_loads: int
    blocked_heating_rods: int
    response_profile: str
    switch_on_delay_seconds: int
    switch_off_delay_seconds: int
    available_surplus_budget: float
    scheduled_surplus_loads: tuple[str, ...]
    scheduled_surplus_power: float
    temperature_blocked_loads: tuple[str, ...]
    shifted_energy_today: float
    estimated_savings_today: float
    shifted_energy_total: float
    daily_history: list[dict[str, Any]]
    learning_bucket: str
    learning_samples: int
    seasonal_success_rate: float | None
    seasonal_average_shifted_energy: float | None
    seasonal_average_budget: float | None
    seasonal_grid_adjustment: float
    seasonal_recommendation: str
    scheduler_reason: str
    weather_reason: str
    surplus_reason: str
    battery_reason: str
    load_reason: str
    action_history: list[dict[str, str]]


class HemsCoordinator(DataUpdateCoordinator[HemsData]):
    """Calculate reusable HEMS decisions from configured Home Assistant entities."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.config_entry = entry
        self._action_history: list[dict[str, str]] = []
        self._last_decision_snapshot: dict[str, Any] | None = None
        self._flexible_loads_allowed_since: datetime | None = None
        self._flexible_loads_blocked_since: datetime | None = None
        self._energy_estimate_day: str | None = None
        self._energy_estimate_last_update: datetime | None = None
        self._energy_estimate_last_power: float = 0.0
        self._shifted_energy_today: float = 0.0
        self._shifted_energy_total: float = 0.0
        self._daily_history: dict[str, dict[str, Any]] = {}
        self._virtual_battery_energy: float | None = None
        self._virtual_battery_last_update: datetime | None = None
        self._virtual_battery_manual_reference: float | None = None
        self._virtual_battery_corrections: int = 0
        self._device_runtime_state: dict[str, dict[str, str]] = {}
        self._learning_store = Store(
            hass, LEARNING_STORE_VERSION, f"{DOMAIN}_{entry.entry_id}_learning"
        )
        self._learning_buckets: dict[str, dict[str, Any]] = {}
        self._learning_last_save: datetime | None = None

    async def async_load_learning(self) -> None:
        """Load persisted HEMS learning data."""
        stored = await self._learning_store.async_load()
        if not isinstance(stored, dict):
            return

        self._action_history = self._safe_action_history(
            stored.get("action_history")
        )
        self._energy_estimate_day = (
            str(stored["energy_estimate_day"])
            if stored.get("energy_estimate_day")
            else None
        )
        self._shifted_energy_today = self._safe_float(
            stored.get("shifted_energy_today"), 0.0
        )
        self._shifted_energy_total = self._safe_float(
            stored.get("shifted_energy_total"), 0.0
        )
        self._daily_history = self._safe_daily_history(stored.get("daily_history"))
        self._virtual_battery_energy = (
            self._safe_float(stored.get("virtual_battery_energy"), 0.0)
            if stored.get("virtual_battery_energy") is not None
            else None
        )
        self._virtual_battery_manual_reference = (
            self._safe_float(stored.get("virtual_battery_manual_reference"), 0.0)
            if stored.get("virtual_battery_manual_reference") is not None
            else None
        )
        self._virtual_battery_corrections = int(
            self._safe_float(stored.get("virtual_battery_corrections"), 0.0)
        )
        self._device_runtime_state = self._safe_device_runtime_state(
            stored.get("device_runtime_state")
        )
        self._learning_buckets = self._safe_learning_buckets(
            stored.get("learning_buckets")
        )

    async def async_save_learning(self, *, force: bool = False) -> None:
        """Persist learned HEMS data with a small write throttle."""
        now = datetime.now()
        if (
            not force
            and self._learning_last_save is not None
            and now - self._learning_last_save < LEARNING_SAVE_INTERVAL
        ):
            return

        self._learning_last_save = now
        await self._learning_store.async_save(
            {
                "energy_estimate_day": self._energy_estimate_day,
                "shifted_energy_today": self._shifted_energy_today,
                "shifted_energy_total": self._shifted_energy_total,
                "daily_history": self._daily_history,
                "virtual_battery_energy": self._virtual_battery_energy,
                "virtual_battery_manual_reference": (
                    self._virtual_battery_manual_reference
                ),
                "virtual_battery_corrections": self._virtual_battery_corrections,
                "device_runtime_state": self._device_runtime_state,
                "learning_buckets": self._learning_buckets,
                "action_history": self._action_history,
            }
        )

    async def _async_update_data(self) -> HemsData:
        data = self._calculate()
        action_added = await self._async_apply_flexible_load_control(data)
        await self.async_save_learning(force=action_added)
        if action_added:
            return replace(data, action_history=list(self._action_history))
        return data

    @property
    def opts(self) -> dict[str, Any]:
        """Return options with defaults."""
        return {**DEFAULTS, **dict(self.config_entry.options)}

    @property
    def _language_is_german(self) -> bool:
        language = getattr(self.hass.config, "language", None)
        return bool(language and str(language).lower().startswith("de"))

    def _txt(self, de: str, en: str) -> str:
        return de if self._language_is_german else en

    async def async_set_option(self, key: str, value: Any) -> None:
        """Persist an option and refresh entities."""
        options = dict(self.config_entry.options)
        previous = options.get(key, DEFAULTS.get(key))
        options[key] = value
        self._add_action(
            self._txt("Einstellung geändert", "Setting changed"),
            f"{self._option_label(key)}: {previous} -> {value}",
            "manual",
        )
        self.hass.config_entries.async_update_entry(self.config_entry, options=options)
        await self.async_request_refresh()

    def _calculate(self) -> HemsData:
        data = self.config_entry.data
        opts = self.opts

        legacy_grid_power = self._float_state(data.get(CONF_GRID_POWER_SENSOR), 0.0)
        grid_import, grid_export = self._grid_flow(data, legacy_grid_power)
        grid_power = grid_import - grid_export
        grid_average = self._float_state(
            data.get(CONF_GRID_AVERAGE_SENSOR), grid_power
        )
        grid_import_price = self._price_value(
            CONF_GRID_IMPORT_PRICE_SENSOR, OPT_GRID_IMPORT_PRICE
        )
        grid_export_price = self._price_value(
            CONF_GRID_EXPORT_PRICE_SENSOR, OPT_GRID_EXPORT_PRICE
        )
        savings_price = max(0.0, grid_import_price - grid_export_price)
        price_reason = (
            self._txt(
                f"Ersparnis je verschobener kWh: Netzbezug {grid_import_price:.3f} EUR/kWh "
                f"minus Einspeisevergütung {grid_export_price:.3f} EUR/kWh.",
                f"Savings per shifted kWh: grid import {grid_import_price:.3f} EUR/kWh "
                f"minus export compensation {grid_export_price:.3f} EUR/kWh.",
            )
        )
        pv_sources = data.get(CONF_PV_POWER_SENSORS, [])
        battery_soc_sources = data.get(CONF_BATTERY_SOC_SENSORS, [])
        flexible_loads = data.get(CONF_FLEXIBLE_LOAD_SWITCHES, [])
        wallboxes = data.get(CONF_WALLBOX_SWITCHES, [])
        heat_pumps = data.get(CONF_HEAT_PUMP_SWITCHES, [])
        heating_rods = data.get(CONF_HEATING_ROD_SWITCHES, [])
        controlled_loads = self._controlled_surplus_load_profiles()

        pv_power = sum(self._float_state(entity_id, 0.0) for entity_id in pv_sources)
        pv_average = self._float_state(data.get(CONF_PV_AVERAGE_SENSOR), pv_power)
        pv_forecast_today = self._float_state(
            data.get(CONF_PV_FORECAST_TODAY_SENSOR), None
        )
        pv_forecast_next_hour = self._float_state(
            data.get(CONF_PV_FORECAST_NEXT_HOUR_SENSOR), None
        )
        pv_forecast_next_3h = self._float_state(
            data.get(CONF_PV_FORECAST_NEXT_3H_SENSOR), None
        )
        pv_arrays = self._pv_arrays(data.get(CONF_PV_ARRAY_SPECS))
        sun_entity = data.get(CONF_SUN_ENTITY) or "sun.sun"
        sun_elevation = self._float_attr(sun_entity, "elevation", None)
        sun_azimuth = self._float_attr(sun_entity, "azimuth", None)
        pv_orientation = self._pv_orientation(pv_arrays, sun_elevation, sun_azimuth)
        pv_window, pv_window_reason = self._pv_window(
            pv_power,
            pv_average,
            pv_forecast_today,
            pv_forecast_next_hour,
            pv_forecast_next_3h,
            sun_elevation,
            sun_azimuth,
            pv_arrays,
            pv_orientation,
        )
        battery_socs = [
            self._float_state(entity_id, None) for entity_id in battery_soc_sources
        ]
        battery_socs = [value for value in battery_socs if value is not None]
        battery_soc_min = min(battery_socs) if battery_socs else None
        battery_charge, battery_discharge = self._battery_flow(data)
        house_load = self._positive_sum(data.get(CONF_HOUSE_LOAD_SENSORS, []))
        virtual_battery = self._update_virtual_battery()
        if virtual_battery["used"]:
            if virtual_battery["soc"] is not None:
                battery_socs.append(virtual_battery["soc"])
                battery_soc_min = min(battery_socs)
            battery_discharge += virtual_battery["discharge_power"]
            battery_charge += virtual_battery["charge_power"]

        weather_state = self._state(data.get(CONF_WEATHER_STATE_SENSOR))
        weather_normalized = weather_state.lower() if weather_state else None
        cloud_coverage = self._float_state(data.get(CONF_CLOUD_SENSOR), None)
        sunshine_minutes = self._float_state(data.get(CONF_SUNSHINE_SENSOR), None)

        good_weather = self._good_weather(
            battery_soc_min, weather_normalized, cloud_coverage, sunshine_minutes
        )
        weather_reason = self._weather_reason(
            battery_soc_min, weather_normalized, cloud_coverage, sunshine_minutes
        )
        bad_weather = self._bad_weather(weather_normalized, cloud_coverage)
        mode = opts[OPT_MODE]
        grid_tolerance = self._grid_tolerance(battery_soc_min, good_weather)
        seasonal_grid_adjustment = self._learning_grid_tolerance_adjustment(mode)
        grid_tolerance += seasonal_grid_adjustment
        min_battery_soc = float(opts[OPT_MIN_BATTERY_SOC])
        usable_battery_charge = self._usable_battery_charge(
            battery_soc_min, battery_charge, min_battery_soc, good_weather, bad_weather
        )
        battery_charge_release = usable_battery_charge > 0
        weather_release = good_weather or battery_charge_release

        auto_enabled = bool(opts[OPT_AUTO_ENABLED])
        battery_protect = self._battery_protect(
            battery_soc_min, battery_discharge, bad_weather
        )

        if mode == MODE_OFF or not auto_enabled:
            surplus_available = False
            flexible_loads_allowed = False
            energy_mode = "off"
            surplus_reason = self._txt(
                "Automatik oder HEMS-Modus ist ausgeschaltet.",
                "Automation or HEMS mode is switched off.",
            )
            load_reason = self._txt(
                "Flexible Verbraucher sind gesperrt, weil HEMS ausgeschaltet ist.",
                "Flexible loads are blocked because HEMS is switched off.",
            )
        elif mode == MODE_FORCE_SURPLUS:
            surplus_available = True
            flexible_loads_allowed = not battery_protect
            energy_mode = "force_surplus" if flexible_loads_allowed else "battery_protect"
            surplus_reason = self._txt(
                "Modus force_surplus erzwingt die Überschussfreigabe.",
                "Mode force_surplus forces surplus release.",
            )
            load_reason = (
                self._txt(
                    "Flexible Verbraucher sind erlaubt, weil force_surplus aktiv ist.",
                    "Flexible loads are allowed because force_surplus is active.",
                )
                if flexible_loads_allowed
                else self._txt(
                    "Flexible Verbraucher bleiben trotz force_surplus gesperrt, weil Batterieschutz aktiv ist.",
                    "Flexible loads remain blocked despite force_surplus because battery protection is active.",
                )
            )
        else:
            pv_threshold = float(opts[OPT_PV_THRESHOLD])
            pv_avg_threshold = float(opts[OPT_PV_AVG_THRESHOLD])
            grid_limit = self._mode_grid_limit(mode, grid_tolerance)
            surplus_available = (
                (
                    pv_power >= pv_threshold
                    and pv_average >= pv_avg_threshold
                    and (
                        grid_power <= grid_limit
                        or (grid_average < 50 and weather_release)
                    )
                )
                or (
                    usable_battery_charge >= float(opts[OPT_FLEXIBLE_LOAD_POWER])
                    and grid_power <= max(grid_limit, float(opts[OPT_GRID_IMPORT_LIMIT]))
                )
            )
            surplus_reason = self._surplus_reason(
                pv_power,
                pv_average,
                grid_power,
                grid_average,
                grid_limit,
                pv_threshold,
                pv_avg_threshold,
                usable_battery_charge,
                weather_release,
                surplus_available,
            )
            flexible_loads_allowed = (
                surplus_available
                and weather_release
                and not battery_protect
                and self._battery_soc_ok(battery_soc_min)
            )
            load_reason = self._load_reason(
                surplus_available,
                weather_release,
                battery_protect,
                battery_soc_min,
                flexible_loads_allowed,
                battery_charge_release,
            )
            energy_mode = self._energy_mode(
                mode,
                grid_power,
                pv_power,
                surplus_available,
                battery_protect,
                weather_release,
            )

        active_flexible_loads = sum(
            1
            for load in controlled_loads
            if load.is_on
        )
        active_flexible_entities = [
            load.entity_id
            for load in controlled_loads
            if load.is_on
        ]
        scheduled_loads, scheduled_power, available_budget, scheduler_reason = (
            self._schedule_surplus_loads(
                controlled_loads,
                flexible_loads_allowed,
                grid_power,
                battery_discharge,
                battery_charge,
                usable_battery_charge,
                battery_soc_min,
                min_battery_soc,
                good_weather,
                bad_weather,
            )
        )
        switch_on_delay, switch_off_delay = self._response_delays(
            battery_protect=battery_protect,
            grid_power=grid_power,
        )
        shifted_energy_today = self._update_shifted_energy_estimate(
            scheduled_power if flexible_loads_allowed else 0.0
        )
        estimated_savings_today = shifted_energy_today * savings_price
        self._update_daily_history_metrics(
            shifted_energy_today,
            estimated_savings_today,
            scheduled_power if flexible_loads_allowed else 0.0,
            available_budget,
            flexible_loads_allowed,
        )
        learning = self._update_learning_bucket(
            flexible_loads_allowed=flexible_loads_allowed,
            scheduled_power=scheduled_power,
            available_budget=available_budget,
            shifted_energy_today=shifted_energy_today,
            pv_power=pv_power,
            grid_power=grid_power,
        )
        self._update_action_history(
            energy_mode,
            surplus_available,
            flexible_loads_allowed,
            battery_protect,
            active_flexible_loads,
            active_flexible_entities,
            load_reason,
        )

        return HemsData(
            grid_power=grid_power,
            grid_average=grid_average,
            grid_import=grid_import,
            grid_export=grid_export,
            grid_import_price=grid_import_price,
            grid_export_price=grid_export_price,
            savings_price=savings_price,
            price_reason=price_reason,
            pv_power=pv_power,
            pv_average=pv_average,
            pv_forecast_today=pv_forecast_today,
            pv_forecast_next_hour=pv_forecast_next_hour,
            pv_forecast_next_3h=pv_forecast_next_3h,
            sun_elevation=sun_elevation,
            sun_azimuth=sun_azimuth,
            pv_array_count=len(pv_arrays),
            pv_best_array=pv_orientation["best_array"],
            pv_orientation_score=pv_orientation["score"],
            pv_window=pv_window,
            pv_window_reason=pv_window_reason,
            battery_soc_min=battery_soc_min,
            battery_discharge=battery_discharge,
            battery_charge=battery_charge,
            house_load=house_load,
            usable_battery_charge=usable_battery_charge,
            virtual_battery_enabled=virtual_battery["enabled"],
            virtual_battery_used=virtual_battery["used"],
            virtual_battery_soc=virtual_battery["soc"],
            virtual_battery_energy=virtual_battery["energy"],
            virtual_battery_usable_energy=virtual_battery["usable_energy"],
            virtual_battery_confidence=virtual_battery["confidence"],
            virtual_battery_reason=virtual_battery["reason"],
            cloud_coverage=cloud_coverage,
            sunshine_minutes=sunshine_minutes,
            weather_state=weather_state,
            good_weather=good_weather,
            bad_weather=bad_weather,
            battery_protect=battery_protect,
            surplus_available=surplus_available,
            flexible_loads_allowed=flexible_loads_allowed,
            energy_mode=energy_mode,
            grid_tolerance=grid_tolerance,
            active_flexible_loads=active_flexible_loads,
            configured_pv_sources=len(pv_sources),
            configured_batteries=max(
                len(battery_soc_sources),
                len(data.get(CONF_BATTERY_DISCHARGE_SENSORS, [])),
                len(data.get(CONF_BATTERY_CHARGE_SENSORS, [])),
                len(data.get(CONF_BATTERY_SIGNED_DISCHARGE_POSITIVE_SENSORS, [])),
                len(data.get(CONF_BATTERY_SIGNED_CHARGE_POSITIVE_SENSORS, [])),
            ),
            configured_flexible_loads=len(flexible_loads),
            configured_start_only_appliances=len(
                data.get(CONF_START_ONLY_APPLIANCE_SWITCHES, [])
            ),
            configured_wallboxes=len(wallboxes),
            configured_heat_pumps=len(heat_pumps),
            configured_heating_rods=len(heating_rods),
            configured_profile_loads=len(
                self._device_profile_items(data.get(CONF_DEVICE_PROFILES))
            ),
            blocked_heating_rods=sum(1 for load in controlled_loads if load.blocked),
            response_profile=str(opts[OPT_RESPONSE_PROFILE]),
            switch_on_delay_seconds=int(switch_on_delay.total_seconds()),
            switch_off_delay_seconds=int(switch_off_delay.total_seconds()),
            available_surplus_budget=available_budget,
            scheduled_surplus_loads=scheduled_loads,
            scheduled_surplus_power=scheduled_power,
            temperature_blocked_loads=tuple(
                load.entity_id for load in controlled_loads if load.blocked
            ),
            shifted_energy_today=shifted_energy_today,
            estimated_savings_today=estimated_savings_today,
            shifted_energy_total=self._shifted_energy_total,
            daily_history=self._daily_history_rows(),
            learning_bucket=learning["label"],
            learning_samples=learning["samples"],
            seasonal_success_rate=learning["success_rate"],
            seasonal_average_shifted_energy=learning["average_shifted_energy"],
            seasonal_average_budget=learning["average_budget"],
            seasonal_grid_adjustment=seasonal_grid_adjustment,
            seasonal_recommendation=learning["recommendation"],
            scheduler_reason=scheduler_reason,
            weather_reason=weather_reason,
            surplus_reason=surplus_reason,
            battery_reason=self._battery_reason(
                battery_soc_min, battery_discharge, bad_weather, battery_protect
            ),
            load_reason=load_reason,
            action_history=list(self._action_history),
        )

    def _update_shifted_energy_estimate(self, current_power: float) -> float:
        """Estimate kWh shifted into surplus periods by integrating planned HEMS load."""
        now = datetime.now()
        today = now.date().isoformat()
        if self._energy_estimate_day != today:
            if self._energy_estimate_day:
                previous = self._daily_row(self._energy_estimate_day)
                previous["shifted_energy"] = round(self._shifted_energy_today, 4)
            self._energy_estimate_day = today
            self._shifted_energy_today = 0.0
            self._energy_estimate_last_update = now
            self._energy_estimate_last_power = max(0.0, current_power)
            return self._shifted_energy_today

        if self._energy_estimate_last_update is not None:
            elapsed_hours = max(
                0.0, (now - self._energy_estimate_last_update).total_seconds() / 3600
            )
            added_kwh = max(0.0, self._energy_estimate_last_power) * elapsed_hours / 1000
            self._shifted_energy_today += added_kwh
            self._shifted_energy_total += added_kwh

        self._energy_estimate_last_update = now
        self._energy_estimate_last_power = max(0.0, current_power)
        return self._shifted_energy_today

    def _update_virtual_battery(self) -> dict[str, Any]:
        """Estimate a virtual battery SoC from charge/discharge power."""
        opts = self.opts
        enabled = bool(opts[OPT_VIRTUAL_BATTERY_ENABLED])
        use_for_hems = bool(opts[OPT_USE_VIRTUAL_BATTERY])
        capacity = max(0.1, float(opts[OPT_VIRTUAL_BATTERY_CAPACITY]))
        manual_soc = max(
            0.0, min(100.0, float(opts[OPT_VIRTUAL_BATTERY_MANUAL_SOC]))
        )
        min_soc = max(0.0, min(100.0, float(opts[OPT_VIRTUAL_BATTERY_MIN_SOC])))
        max_soc = max(min_soc, min(100.0, float(opts[OPT_VIRTUAL_BATTERY_MAX_SOC])))
        charge_power = self._positive_float_state(
            self.config_entry.data.get(CONF_VIRTUAL_BATTERY_CHARGE_SENSOR)
        ) or 0.0
        discharge_power = self._positive_float_state(
            self.config_entry.data.get(CONF_VIRTUAL_BATTERY_DISCHARGE_SENSOR)
        ) or 0.0

        if not enabled:
            self._virtual_battery_last_update = datetime.now()
            return {
                "enabled": False,
                "used": False,
                "soc": None,
                "energy": None,
                "usable_energy": None,
                "confidence": 0.0,
                "reason": self._txt(
                    "Virtuelle Batterie ist deaktiviert.",
                    "Virtual battery is disabled.",
                ),
                "charge_power": 0.0,
                "discharge_power": 0.0,
            }

        now = datetime.now()
        if self._virtual_battery_energy is None:
            self._virtual_battery_energy = capacity * manual_soc / 100
            self._virtual_battery_manual_reference = manual_soc
        elif (
            self._virtual_battery_manual_reference is None
            or abs(manual_soc - self._virtual_battery_manual_reference) >= 0.5
        ):
            current_soc = self._virtual_battery_energy / capacity * 100
            if abs(manual_soc - current_soc) >= 1.0:
                self._virtual_battery_corrections += 1
            self._virtual_battery_energy = capacity * manual_soc / 100
            self._virtual_battery_manual_reference = manual_soc

        if self._virtual_battery_last_update is not None:
            elapsed_hours = max(
                0.0, (now - self._virtual_battery_last_update).total_seconds() / 3600
            )
            charge_eff = max(
                0.0, min(1.0, float(opts[OPT_VIRTUAL_BATTERY_CHARGE_EFFICIENCY]) / 100)
            )
            discharge_eff = max(
                0.01,
                min(1.0, float(opts[OPT_VIRTUAL_BATTERY_DISCHARGE_EFFICIENCY]) / 100),
            )
            delta = (
                charge_power * charge_eff
                - discharge_power / discharge_eff
            ) * elapsed_hours / 1000
            self._virtual_battery_energy = max(
                0.0, min(capacity, self._virtual_battery_energy + delta)
            )

        self._virtual_battery_last_update = now
        soc = max(0.0, min(100.0, self._virtual_battery_energy / capacity * 100))
        usable_energy = max(
            0.0, min(capacity * max_soc / 100, self._virtual_battery_energy)
            - capacity * min_soc / 100
        )
        confidence = min(100.0, 30.0 + self._virtual_battery_corrections * 12.0)
        reason = (
            self._txt(
                f"Virtuelle Batterie berechnet aus Ladung {charge_power:.0f} W, "
                f"Entladung {discharge_power:.0f} W und manueller Kalibrierung "
                f"{manual_soc:.1f}%.",
                f"Virtual battery calculated from charge {charge_power:.0f} W, "
                f"discharge {discharge_power:.0f} W and manual calibration "
                f"{manual_soc:.1f}%.",
            )
        )
        return {
            "enabled": True,
            "used": use_for_hems,
            "soc": soc,
            "energy": self._virtual_battery_energy,
            "usable_energy": usable_energy,
            "confidence": confidence,
            "reason": reason,
            "charge_power": charge_power,
            "discharge_power": discharge_power,
        }

    def _update_learning_bucket(
        self,
        *,
        flexible_loads_allowed: bool,
        scheduled_power: float,
        available_budget: float,
        shifted_energy_today: float,
        pv_power: float,
        grid_power: float,
    ) -> dict[str, Any]:
        """Update seasonal/time-of-day experience and return current summary."""
        now = datetime.now()
        key, label = self._learning_bucket(now)
        bucket = self._learning_buckets.setdefault(
            key,
            {
                "label": label,
                "samples": 0,
                "allowed_samples": 0,
                "scheduled_power_total": 0.0,
                "budget_total": 0.0,
                "pv_power_total": 0.0,
                "grid_power_total": 0.0,
                "shifted_energy_total": 0.0,
                "last_shifted_energy_today": shifted_energy_today,
                "last_seen": now.isoformat(timespec="seconds"),
            },
        )

        previous_shifted = self._safe_float(
            bucket.get("last_shifted_energy_today"), shifted_energy_today
        )
        shifted_delta = max(0.0, shifted_energy_today - previous_shifted)
        if shifted_energy_today < previous_shifted:
            shifted_delta = shifted_energy_today

        bucket["label"] = label
        bucket["samples"] = int(bucket.get("samples", 0)) + 1
        bucket["allowed_samples"] = int(bucket.get("allowed_samples", 0)) + (
            1 if flexible_loads_allowed else 0
        )
        bucket["scheduled_power_total"] = self._safe_float(
            bucket.get("scheduled_power_total"), 0.0
        ) + max(0.0, scheduled_power)
        bucket["budget_total"] = self._safe_float(
            bucket.get("budget_total"), 0.0
        ) + max(0.0, available_budget)
        bucket["pv_power_total"] = self._safe_float(
            bucket.get("pv_power_total"), 0.0
        ) + max(0.0, pv_power)
        bucket["grid_power_total"] = self._safe_float(
            bucket.get("grid_power_total"), 0.0
        ) + grid_power
        bucket["shifted_energy_total"] = self._safe_float(
            bucket.get("shifted_energy_total"), 0.0
        ) + shifted_delta
        bucket["last_shifted_energy_today"] = shifted_energy_today
        bucket["last_seen"] = now.isoformat(timespec="seconds")

        return self._learning_summary(key)

    def _learning_summary(self, key: str) -> dict[str, Any]:
        bucket = self._learning_buckets.get(key, {})
        samples = int(bucket.get("samples", 0))
        allowed = int(bucket.get("allowed_samples", 0))
        success_rate = round(allowed / samples * 100, 1) if samples else None
        average_shifted = (
            self._safe_float(bucket.get("shifted_energy_total"), 0.0) / samples
            if samples
            else None
        )
        average_budget = (
            self._safe_float(bucket.get("budget_total"), 0.0) / samples
            if samples
            else None
        )
        return {
            "label": bucket.get("label", key),
            "samples": samples,
            "success_rate": success_rate,
            "average_shifted_energy": round(average_shifted, 4)
            if average_shifted is not None
            else None,
            "average_budget": round(average_budget, 1)
            if average_budget is not None
            else None,
            "recommendation": self._learning_recommendation(
                str(bucket.get("label", key)), samples, success_rate, average_budget
            ),
        }

    def _learning_recommendation(
        self,
        label: str,
        samples: int,
        success_rate: float | None,
        average_budget: float | None,
    ) -> str:
        if samples < LEARNING_MIN_SAMPLES:
            return self._txt(
                f"HEMS lernt {label} noch. Nach mehr Messpunkten wird diese Jahreszeit/Tageszeit besser bewertet.",
                f"HEMS is still learning {label}. This season/time window will be rated better after more samples.",
            )
        if success_rate is not None and success_rate >= 60:
            return self._txt(
                f"{label} war bisher oft geeignet: {success_rate:.0f}% Freigaben, durchschnittlich {average_budget or 0:.0f} W Budget.",
                f"{label} has often been suitable so far: {success_rate:.0f}% releases, average budget {average_budget or 0:.0f} W.",
            )
        if success_rate is not None and success_rate >= 30:
            return self._txt(
                f"{label} ist wechselhaft: {success_rate:.0f}% Freigaben. HEMS bleibt vorsichtig und wartet auf klares Budget.",
                f"{label} is mixed: {success_rate:.0f}% releases. HEMS stays cautious and waits for a clear budget.",
            )
        return self._txt(
            f"{label} war bisher selten geeignet. HEMS bewertet diese Phase konservativer und wartet eher auf echte Überschüsse.",
            f"{label} has rarely been suitable so far. HEMS rates this phase more conservatively and waits for real surplus.",
        )

    def _learning_grid_tolerance_adjustment(self, mode: str) -> float:
        """Return a conservative learned grid-tolerance adjustment."""
        if mode in {MODE_ECO, MODE_FORCE_SURPLUS, MODE_OFF}:
            return 0.0

        key, _label = self._learning_bucket(datetime.now())
        summary = self._learning_summary(key)
        samples = int(summary["samples"])
        success_rate = summary["success_rate"]
        average_budget = summary["average_budget"]
        if samples < LEARNING_DECISION_MIN_SAMPLES or success_rate is None:
            return 0.0

        flexible_power = float(self.opts[OPT_FLEXIBLE_LOAD_POWER])
        if success_rate >= 70 and (average_budget or 0.0) >= flexible_power:
            return 100.0 if mode == MODE_COMFORT else 50.0
        if success_rate <= 15:
            return -50.0
        return 0.0

    def _learning_bucket(self, now: datetime) -> tuple[str, str]:
        season = self._season(now.month)
        day_part = self._day_part(now.hour)
        return f"{season}:{day_part}", f"{self._season_label(season)}, {self._day_part_label(day_part)}"

    def _season(self, month: int) -> str:
        if month in {12, 1, 2}:
            return "winter"
        if month in {3, 4, 5}:
            return "spring"
        if month in {6, 7, 8}:
            return "summer"
        return "autumn"

    def _season_label(self, season: str) -> str:
        labels = (
            {"winter": "Winter", "spring": "Frühjahr", "summer": "Sommer", "autumn": "Herbst"}
            if self._language_is_german
            else {"winter": "winter", "spring": "spring", "summer": "summer", "autumn": "autumn"}
        )
        return labels.get(season, season)

    def _day_part(self, hour: int) -> str:
        if hour < 6:
            return "night"
        if hour < 10:
            return "morning"
        if hour < 14:
            return "midday"
        if hour < 18:
            return "afternoon"
        return "evening"

    def _day_part_label(self, day_part: str) -> str:
        labels = (
            {"night": "Nacht", "morning": "Morgen", "midday": "Mittag", "afternoon": "Nachmittag", "evening": "Abend"}
            if self._language_is_german
            else {"night": "night", "morning": "morning", "midday": "midday", "afternoon": "afternoon", "evening": "evening"}
        )
        return labels.get(day_part, day_part)

    def _safe_learning_buckets(self, value: Any) -> dict[str, dict[str, Any]]:
        if not isinstance(value, dict):
            return {}
        buckets: dict[str, dict[str, Any]] = {}
        for key, bucket in value.items():
            if isinstance(key, str) and isinstance(bucket, dict):
                buckets[key] = dict(bucket)
        return buckets

    def _safe_action_history(self, value: Any) -> list[dict[str, str]]:
        if not isinstance(value, list):
            return []
        rows: list[dict[str, str]] = []
        for item in value[:10]:
            if not isinstance(item, dict):
                continue
            rows.append(
                {
                    "time": str(item.get("time", "")),
                    "title": str(item.get("title", "")),
                    "reason": str(item.get("reason", "")),
                    "kind": str(item.get("kind", "")),
                }
            )
        return rows

    def _safe_daily_history(self, value: Any) -> dict[str, dict[str, Any]]:
        if not isinstance(value, dict):
            return {}
        rows: dict[str, dict[str, Any]] = {}
        for date_key, raw in value.items():
            if not isinstance(date_key, str) or not isinstance(raw, dict):
                continue
            rows[date_key] = {
                "date": date_key,
                "shifted_energy": round(self._safe_float(raw.get("shifted_energy"), 0.0), 4),
                "estimated_savings": round(self._safe_float(raw.get("estimated_savings"), 0.0), 4),
                "max_scheduled_power": round(self._safe_float(raw.get("max_scheduled_power"), 0.0), 1),
                "max_available_budget": round(self._safe_float(raw.get("max_available_budget"), 0.0), 1),
                "release_updates": int(self._safe_float(raw.get("release_updates"), 0.0)),
                "events": int(self._safe_float(raw.get("events"), 0.0)),
                "switches": int(self._safe_float(raw.get("switches"), 0.0)),
                "blocks": int(self._safe_float(raw.get("blocks"), 0.0)),
            }
        return dict(sorted(rows.items())[-DAILY_HISTORY_DAYS:])

    def _daily_row(self, date_key: str | None = None) -> dict[str, Any]:
        key = date_key or datetime.now().date().isoformat()
        row = self._daily_history.setdefault(
            key,
            {
                "date": key,
                "shifted_energy": 0.0,
                "estimated_savings": 0.0,
                "max_scheduled_power": 0.0,
                "max_available_budget": 0.0,
                "release_updates": 0,
                "events": 0,
                "switches": 0,
                "blocks": 0,
            },
        )
        return row

    def _daily_history_rows(self) -> list[dict[str, Any]]:
        return [
            dict(row)
            for _key, row in sorted(self._daily_history.items(), reverse=True)[
                :DAILY_HISTORY_DAYS
            ]
        ]

    def _update_daily_history_metrics(
        self,
        shifted_energy: float,
        estimated_savings: float,
        scheduled_power: float,
        available_budget: float,
        flexible_loads_allowed: bool,
    ) -> None:
        row = self._daily_row()
        row["shifted_energy"] = round(max(0.0, shifted_energy), 4)
        row["estimated_savings"] = round(max(0.0, estimated_savings), 4)
        row["max_scheduled_power"] = round(
            max(self._safe_float(row.get("max_scheduled_power"), 0.0), scheduled_power),
            1,
        )
        row["max_available_budget"] = round(
            max(self._safe_float(row.get("max_available_budget"), 0.0), available_budget),
            1,
        )
        if flexible_loads_allowed:
            row["release_updates"] = int(row.get("release_updates", 0)) + 1
        self._daily_history = dict(
            sorted(self._daily_history.items())[-DAILY_HISTORY_DAYS:]
        )

    def _safe_device_runtime_state(self, value: Any) -> dict[str, dict[str, str]]:
        if not isinstance(value, dict):
            return {}
        result: dict[str, dict[str, str]] = {}
        for entity_id, state in value.items():
            if not isinstance(entity_id, str) or not isinstance(state, dict):
                continue
            result[entity_id] = {
                key: str(raw)
                for key, raw in state.items()
                if key in {"last_on", "last_off", "start_pending_at", "started_at"} and raw
            }
        return result

    def _safe_float(self, value: Any, default: float) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _safe_bool(self, value: Any, default: bool) -> bool:
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() not in {"0", "false", "no", "off", "nein"}
        return bool(value)

    def _positive_sum(self, entity_ids: list[str]) -> float:
        """Sum positive power values from a list of sensors."""
        return sum(max(0.0, self._float_state(entity_id, 0.0)) for entity_id in entity_ids)

    def _signed_split(
        self, entity_ids: list[str], *, positive_is_first: bool
    ) -> tuple[float, float]:
        """Split signed sensors into two positive buckets."""
        first = 0.0
        second = 0.0
        for entity_id in entity_ids:
            value = self._float_state(entity_id, 0.0)
            if positive_is_first:
                first += max(0.0, value)
                second += max(0.0, -value)
            else:
                first += max(0.0, -value)
                second += max(0.0, value)
        return first, second

    def _grid_flow(self, data: dict[str, Any], legacy_grid_power: float) -> tuple[float, float]:
        """Normalize grid sensors into import and export power."""
        grid_import = max(0.0, legacy_grid_power)
        grid_export = max(0.0, -legacy_grid_power)
        grid_import += self._positive_sum(data.get(CONF_GRID_IMPORT_POWER_SENSORS, []))
        grid_export += self._positive_sum(data.get(CONF_GRID_EXPORT_POWER_SENSORS, []))
        signed_import, signed_export = self._signed_split(
            data.get(CONF_GRID_SIGNED_IMPORT_POSITIVE_SENSORS, []),
            positive_is_first=True,
        )
        grid_import += signed_import
        grid_export += signed_export
        signed_import, signed_export = self._signed_split(
            data.get(CONF_GRID_SIGNED_EXPORT_POSITIVE_SENSORS, []),
            positive_is_first=False,
        )
        grid_import += signed_import
        grid_export += signed_export
        return grid_import, grid_export

    def _battery_flow(self, data: dict[str, Any]) -> tuple[float, float]:
        """Normalize battery sensors into charge and discharge power."""
        battery_charge = self._positive_sum(data.get(CONF_BATTERY_CHARGE_SENSORS, []))
        battery_discharge = self._positive_sum(
            data.get(CONF_BATTERY_DISCHARGE_SENSORS, [])
        )
        signed_discharge, signed_charge = self._signed_split(
            data.get(CONF_BATTERY_SIGNED_DISCHARGE_POSITIVE_SENSORS, []),
            positive_is_first=True,
        )
        battery_discharge += signed_discharge
        battery_charge += signed_charge
        signed_charge, signed_discharge = self._signed_split(
            data.get(CONF_BATTERY_SIGNED_CHARGE_POSITIVE_SENSORS, []),
            positive_is_first=True,
        )
        battery_charge += signed_charge
        battery_discharge += signed_discharge
        return battery_charge, battery_discharge

    async def _async_apply_flexible_load_control(self, data: HemsData) -> bool:
        """Switch configured flexible loads according to the current HEMS decision."""
        opts = self.opts
        if not bool(opts[OPT_AUTO_ENABLED]):
            return False

        action_added = await self._async_turn_off_temperature_blocked_loads(data)
        target_on = data.flexible_loads_allowed and bool(data.scheduled_surplus_loads)
        if not self._flexible_load_decision_is_stable(target_on, data):
            return action_added

        desired_on = set(data.scheduled_surplus_loads) if target_on else set()
        flexible_loads = self._controlled_surplus_load_profiles()

        for load in flexible_loads:
            entity_id = load.entity_id
            should_be_on = entity_id in desired_on
            if load.control_mode == "start_only" and not should_be_on:
                if await self._async_apply_start_only_timeout(load):
                    action_added = True
                continue
            blocked_reason = self._device_switch_block_reason(load, should_be_on)
            if blocked_reason is not None:
                self._add_action(
                    self._txt("Geräteprofil wartet", "Device profile waits"),
                    blocked_reason,
                    "device",
                )
                action_added = True
                continue
            service = "turn_on" if should_be_on else "turn_off"
            desired_state = STATE_ON if should_be_on else STATE_OFF
            state = self.hass.states.get(load.entity_id)
            domain = entity_id.split(".", 1)[0]
            is_start_button = load.control_mode == "start_only" and domain == "button"
            if state is None or state.state in {STATE_UNAVAILABLE, STATE_UNKNOWN}:
                continue
            if not is_start_button and state.state == desired_state:
                continue
            if is_start_button:
                service = "press"
            elif domain not in {"switch", "input_boolean"}:
                continue

            await self.hass.services.async_call(
                domain,
                service,
                {"entity_id": entity_id},
                blocking=False,
            )
            self._add_action(
                self._txt("Verbraucher geschaltet", "Load switched"),
                self._txt(
                    f"{load.name} wurde {'eingeschaltet' if should_be_on else 'ausgeschaltet'}. {data.scheduler_reason}",
                    f"{load.name} was {'switched on' if should_be_on else 'switched off'}. {data.scheduler_reason}",
                ),
                "device",
            )
            self._record_device_switch(load, should_be_on)
            action_added = True

        return action_added

    async def _async_apply_start_only_timeout(self, load: LoadProfile) -> bool:
        """Turn a start-only release off only when no program started in time."""
        state = self.hass.states.get(load.entity_id)
        if state is None or state.state != STATE_ON:
            return False
        runtime_state = self._device_runtime_state.get(load.entity_id, {})
        pending_at = self._parse_datetime(runtime_state.get("start_pending_at"))
        if (
            pending_at is None
            or load.power_sensor is None
            or load.start_timeout <= timedelta(seconds=0)
            or datetime.now() - pending_at < load.start_timeout
            or self._start_only_is_running(load)
        ):
            return False

        domain = load.entity_id.split(".", 1)[0]
        if domain not in {"switch", "input_boolean"}:
            return False
        await self.hass.services.async_call(
            domain,
            "turn_off",
            {"entity_id": load.entity_id},
            blocking=False,
        )
        self._add_action(
            self._txt("Startfreigabe beendet", "Start release ended"),
            self._txt(
                f"{load.name} wurde nach {self._duration_text(load.start_timeout)} ohne Lauf-Erkennung wieder freigegeben.",
                f"{load.name} was released again after {self._duration_text(load.start_timeout)} without run detection.",
            ),
            "device",
        )
        self._record_device_switch(load, False)
        runtime_state.pop("start_pending_at", None)
        return True

    def _device_switch_block_reason(
        self, load: LoadProfile, should_be_on: bool
    ) -> str | None:
        now = datetime.now()
        state = self._device_runtime_state.setdefault(load.entity_id, {})
        if load.control_mode == "start_only":
            if should_be_on:
                if self._start_only_is_running(load):
                    state["started_at"] = state.get(
                        "started_at"
                    ) or now.isoformat(timespec="seconds")
                    state.pop("start_pending_at", None)
                    return self._txt(
                        f"{load.name} läuft bereits und wird nicht erneut gestartet.",
                        f"{load.name} is already running and will not be started again.",
                    )
                pending_at = self._parse_datetime(state.get("start_pending_at"))
                if pending_at is not None and now - pending_at < load.start_timeout:
                    remaining = load.start_timeout - (now - pending_at)
                    return self._txt(
                        f"{load.name} wartet noch {self._duration_text(remaining)} auf Lauf-Erkennung.",
                        f"{load.name} waits another {self._duration_text(remaining)} for run detection.",
                    )
            else:
                return self._txt(
                    f"{load.name} ist Start-only und wird nach dem Start nicht ausgeschaltet.",
                    f"{load.name} is start-only and will not be switched off after start.",
                )

        if should_be_on:
            last_off = self._parse_datetime(state.get("last_off"))
            if last_off is not None and now - last_off < load.cooldown:
                remaining = load.cooldown - (now - last_off)
                return self._txt(
                    f"{load.name} bleibt wegen Cooldown noch {self._duration_text(remaining)} aus.",
                    f"{load.name} remains off for cooldown for another {self._duration_text(remaining)}.",
                )
            return None

        last_on = self._parse_datetime(state.get("last_on"))
        if load.is_on and last_on is not None and now - last_on < load.min_runtime:
            remaining = load.min_runtime - (now - last_on)
            return self._txt(
                f"{load.name} bleibt wegen Mindestlaufzeit noch {self._duration_text(remaining)} an.",
                f"{load.name} remains on for minimum runtime for another {self._duration_text(remaining)}.",
            )
        return None

    def _record_device_switch(self, load: LoadProfile, switched_on: bool) -> None:
        state = self._device_runtime_state.setdefault(load.entity_id, {})
        key = "last_on" if switched_on else "last_off"
        state[key] = datetime.now().isoformat(timespec="seconds")
        if load.control_mode == "start_only":
            if switched_on:
                state["start_pending_at"] = state[key]
                state.pop("started_at", None)
            else:
                state.pop("start_pending_at", None)

    def _start_only_is_running(self, load: LoadProfile) -> bool:
        return (
            load.control_mode == "start_only"
            and load.actual_power is not None
            and load.actual_power >= load.start_power_threshold
        )

    def _parse_datetime(self, value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    def _duration_text(self, value: timedelta) -> str:
        seconds = max(0, int(value.total_seconds()))
        minutes = seconds // 60
        if minutes:
            return f"{minutes} min"
        return f"{seconds} s"

    async def _async_turn_off_temperature_blocked_loads(self, data: HemsData) -> bool:
        """Immediately stop heating rods that reached their target temperature."""
        action_added = False
        for entity_id in data.temperature_blocked_loads:
            state = self.hass.states.get(entity_id)
            if state is None or state.state in {
                STATE_OFF,
                STATE_UNAVAILABLE,
                STATE_UNKNOWN,
            }:
                continue
            domain = entity_id.split(".", 1)[0]
            if domain not in {"switch", "input_boolean"}:
                continue
            await self.hass.services.async_call(
                domain,
                "turn_off",
                {"entity_id": entity_id},
                blocking=False,
            )
            self._add_action(
                self._txt("Heizstab Temperatur erreicht", "Heating rod target reached"),
                self._txt(
                    f"{entity_id} wurde ausgeschaltet, weil die Zieltemperatur erreicht ist.",
                    f"{entity_id} was switched off because the target temperature was reached.",
                ),
                "protect",
            )
            action_added = True
        return action_added

    def _controlled_surplus_load_profiles(self) -> list[LoadProfile]:
        """Return all loads controlled by the smart surplus scheduler."""
        data = self.config_entry.data
        opts = self.opts
        flexible_power = float(opts[OPT_FLEXIBLE_LOAD_POWER])
        start_only_power = float(opts[OPT_START_ONLY_APPLIANCE_POWER])
        heating_rod_power = float(opts[OPT_HEATING_ROD_POWER])
        flexible_power_sensors = data.get(CONF_FLEXIBLE_LOAD_POWER_SENSORS, [])
        start_only_power_sensors = data.get(
            CONF_START_ONLY_APPLIANCE_POWER_SENSORS, []
        )
        heating_rod_power_sensors = data.get(CONF_HEATING_ROD_POWER_SENSORS, [])
        heating_rod_temperature_sensors = data.get(
            CONF_HEATING_ROD_TEMPERATURE_SENSORS, []
        )
        heating_rod_targets = self._float_list(
            data.get(CONF_HEATING_ROD_TARGET_TEMPERATURES)
        )
        hysteresis = float(opts[OPT_HEATING_ROD_TEMPERATURE_HYSTERESIS])

        profiles: list[LoadProfile] = []
        for index, entity_id in enumerate(data.get(CONF_FLEXIBLE_LOAD_SWITCHES, [])):
            power_sensor = self._matching_entity(flexible_power_sensors, index)
            profiles.append(
                LoadProfile(
                    entity_id=entity_id,
                    name=entity_id,
                    category="flexible_load",
                    estimated_power=flexible_power,
                    actual_power=self._positive_float_state(power_sensor),
                    power_sensor=power_sensor,
                    priority=10,
                    min_runtime=timedelta(seconds=0),
                    cooldown=timedelta(seconds=0),
                    allow_battery=True,
                    control_mode="managed",
                    start_power_threshold=20.0,
                    start_timeout=timedelta(seconds=0),
                    is_on=self.hass.states.is_state(entity_id, STATE_ON),
                )
            )
        for index, entity_id in enumerate(
            data.get(CONF_START_ONLY_APPLIANCE_SWITCHES, [])
        ):
            power_sensor = self._matching_entity(start_only_power_sensors, index)
            profile = LoadProfile(
                entity_id=entity_id,
                name=entity_id,
                category="appliance",
                estimated_power=start_only_power,
                actual_power=self._positive_float_state(power_sensor),
                power_sensor=power_sensor,
                priority=40,
                min_runtime=timedelta(seconds=0),
                cooldown=timedelta(hours=12),
                allow_battery=False,
                control_mode="start_only",
                start_power_threshold=20.0,
                start_timeout=timedelta(minutes=30),
                is_on=self.hass.states.is_state(entity_id, STATE_ON),
            )
            profiles.append(self._with_start_only_block(profile))
        for index, entity_id in enumerate(data.get(CONF_HEATING_ROD_SWITCHES, [])):
            power_sensor = self._matching_entity(heating_rod_power_sensors, index)
            temperature_sensor = self._matching_entity(
                heating_rod_temperature_sensors, index
            )
            temperature = self._float_state(temperature_sensor, None)
            target_temperature = self._matching_number(heating_rod_targets, index)
            is_on = self.hass.states.is_state(entity_id, STATE_ON)
            blocked, blocked_reason = self._heating_rod_temperature_block(
                temperature, target_temperature, hysteresis, is_on
            )
            profiles.append(
                LoadProfile(
                    entity_id=entity_id,
                    name=entity_id,
                    category="heating_rod",
                    estimated_power=heating_rod_power,
                    actual_power=self._positive_float_state(power_sensor),
                    power_sensor=power_sensor,
                    priority=30,
                    min_runtime=timedelta(seconds=0),
                    cooldown=timedelta(seconds=0),
                    allow_battery=True,
                    control_mode="managed",
                    start_power_threshold=20.0,
                    start_timeout=timedelta(seconds=0),
                    is_on=is_on,
                    blocked=blocked,
                    blocked_reason=blocked_reason,
                    temperature=temperature,
                    target_temperature=target_temperature,
                )
            )
        profiles.extend(self._configured_device_profiles())
        deduplicated: dict[str, LoadProfile] = {}
        for profile in profiles:
            deduplicated[profile.entity_id] = profile
        return list(deduplicated.values())

    def _configured_device_profiles(self) -> list[LoadProfile]:
        """Return advanced per-device profiles from JSON configuration."""
        raw_profiles = self._device_profile_items(
            self.config_entry.data.get(CONF_DEVICE_PROFILES)
        )
        profiles: list[LoadProfile] = []
        for index, item in enumerate(raw_profiles):
            entity_id = str(item.get("switch") or item.get("entity_id") or "").strip()
            if not entity_id:
                continue
            category = str(item.get("category") or "flexible_load")
            estimated_power = self._safe_float(
                item.get("power") or item.get("estimated_power"),
                float(self.opts[OPT_FLEXIBLE_LOAD_POWER]),
            )
            power_sensor = item.get("power_sensor")
            temperature_sensor = item.get("temperature_sensor")
            temperature = self._float_state(str(temperature_sensor), None) if temperature_sensor else None
            target_temperature = (
                self._safe_float(item.get("target_temperature"), 0.0)
                if item.get("target_temperature") is not None
                else None
            )
            is_on = self.hass.states.is_state(entity_id, STATE_ON)
            blocked, blocked_reason = self._heating_rod_temperature_block(
                temperature,
                target_temperature,
                float(self.opts[OPT_HEATING_ROD_TEMPERATURE_HYSTERESIS]),
                is_on,
            )
            control_mode = str(item.get("control_mode") or "managed").strip().lower()
            if control_mode not in {"managed", "start_only"}:
                control_mode = "managed"
            actual_power = (
                self._positive_float_state(str(power_sensor)) if power_sensor else None
            )
            profile = LoadProfile(
                entity_id=entity_id,
                name=str(item.get("name") or entity_id),
                category=category,
                estimated_power=max(0.0, estimated_power),
                actual_power=actual_power,
                power_sensor=str(power_sensor) if power_sensor else None,
                priority=int(self._safe_float(item.get("priority"), 50 + index)),
                min_runtime=timedelta(
                    minutes=max(0.0, self._safe_float(item.get("min_runtime"), 0.0))
                ),
                cooldown=timedelta(
                    minutes=max(0.0, self._safe_float(item.get("cooldown"), 0.0))
                ),
                allow_battery=self._safe_bool(item.get("allow_battery"), True),
                control_mode=control_mode,
                start_power_threshold=max(
                    0.0, self._safe_float(item.get("start_power_threshold"), 20.0)
                ),
                start_timeout=timedelta(
                    minutes=max(0.0, self._safe_float(item.get("start_timeout"), 30.0))
                ),
                is_on=is_on,
                blocked=blocked,
                blocked_reason=blocked_reason,
                temperature=temperature,
                target_temperature=target_temperature,
            )
            profiles.append(self._with_start_only_block(profile))
        return profiles

    def _with_start_only_block(self, load: LoadProfile) -> LoadProfile:
        if load.control_mode != "start_only":
            return load
        now = datetime.now()
        state = self._device_runtime_state.get(load.entity_id, {})
        if self._start_only_is_running(load):
            runtime_state = self._device_runtime_state.setdefault(load.entity_id, {})
            runtime_state["started_at"] = runtime_state.get(
                "started_at"
            ) or now.isoformat(timespec="seconds")
            runtime_state.pop("start_pending_at", None)
            return replace(
                load,
                blocked=True,
                blocked_reason=self._txt(
                    f"{load.name} läuft bereits.",
                    f"{load.name} is already running.",
                ),
            )
        pending_at = self._parse_datetime(state.get("start_pending_at"))
        if pending_at is not None and now - pending_at < load.start_timeout:
            remaining = load.start_timeout - (now - pending_at)
            return replace(
                load,
                blocked=True,
                blocked_reason=self._txt(
                    f"{load.name} wartet noch {self._duration_text(remaining)} auf Lauf-Erkennung.",
                    f"{load.name} waits another {self._duration_text(remaining)} for run detection.",
                ),
            )
        if pending_at is not None and load.is_on:
            if load.power_sensor is None:
                return replace(
                    load,
                    blocked=True,
                    blocked_reason=self._txt(
                        f"{load.name} wurde gestartet und hat keinen Leistungssensor für Lauf-Erkennung.",
                        f"{load.name} was started and has no power sensor for run detection.",
                    ),
                )
            return replace(
                load,
                blocked=True,
                blocked_reason=self._txt(
                    f"{load.name} hat innerhalb des Start-Timeouts keinen Lauf erkannt.",
                    f"{load.name} did not detect a run within the start timeout.",
                ),
            )
        last_on = self._parse_datetime(state.get("last_on"))
        if last_on is not None and now - last_on < load.cooldown:
            remaining = load.cooldown - (now - last_on)
            return replace(
                load,
                blocked=True,
                blocked_reason=self._txt(
                    f"{load.name} bleibt wegen Cooldown noch {self._duration_text(remaining)} gesperrt.",
                    f"{load.name} remains blocked for cooldown for another {self._duration_text(remaining)}.",
                ),
            )
        return load

    def _device_profile_items(self, value: Any) -> list[dict[str, Any]]:
        if not value:
            return []
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        try:
            parsed = json.loads(str(value))
        except (TypeError, ValueError, json.JSONDecodeError):
            return []
        if isinstance(parsed, list):
            return [item for item in parsed if isinstance(item, dict)]
        if isinstance(parsed, dict):
            return [parsed]
        return []

    def _matching_entity(self, entity_ids: list[str], index: int) -> str | None:
        """Return the same-position entity from a parallel entity list."""
        if index >= len(entity_ids):
            return None
        return entity_ids[index]

    def _matching_number(self, values: list[float | None], index: int) -> float | None:
        if index >= len(values):
            return None
        return values[index]

    def _float_list(self, value: Any) -> list[float | None]:
        if not value:
            return []
        raw_items = value if isinstance(value, list) else str(value).split(",")
        numbers: list[float | None] = []
        for raw in raw_items:
            try:
                numbers.append(float(str(raw).strip().replace(",", ".")))
            except (TypeError, ValueError):
                numbers.append(None)
        return numbers

    def _heating_rod_temperature_block(
        self,
        temperature: float | None,
        target: float | None,
        hysteresis: float,
        is_on: bool,
    ) -> tuple[bool, str | None]:
        if temperature is None or target is None:
            return False, None
        if temperature >= target:
            return (
                True,
                self._txt(
                    f"Temperatur {temperature:.1f}°C hat Ziel {target:.1f}°C erreicht.",
                    f"Temperature {temperature:.1f}°C reached target {target:.1f}°C.",
                ),
            )
        if not is_on and temperature >= target - max(0.0, hysteresis):
            return (
                True,
                self._txt(
                    f"Temperatur {temperature:.1f}°C liegt innerhalb der Hysterese unter Ziel {target:.1f}°C.",
                    f"Temperature {temperature:.1f}°C is within hysteresis below target {target:.1f}°C.",
                ),
            )
        return False, None

    def _schedule_surplus_loads(
        self,
        loads: list[LoadProfile],
        allowed: bool,
        grid_power: float,
        battery_discharge: float,
        battery_charge: float,
        usable_battery_charge: float,
        battery_soc: float | None,
        min_battery_soc: float,
        good_weather: bool,
        bad_weather: bool,
    ) -> tuple[tuple[str, ...], float, float, str]:
        """Select the loads that fit into the current surplus budget."""
        active_power = sum(load.scheduling_power for load in loads if load.is_on)
        current_export = max(0.0, -grid_power)
        budget_with_battery = max(
            0.0,
            current_export
            + active_power
            + usable_battery_charge
            - max(0.0, battery_discharge),
        )
        budget_without_battery = max(
            0.0,
            current_export + active_power - max(0.0, battery_discharge),
        )
        if not allowed:
            return (), 0.0, budget_with_battery, self._txt(
                "Smart Scheduler blockiert alle Überschussverbraucher, weil die zentrale HEMS-Freigabe fehlt.",
                "Smart scheduler blocks all surplus loads because the central HEMS release is missing.",
            )
        available_loads = [load for load in loads if not load.blocked]
        blocked_loads = [load for load in loads if load.blocked]
        if not loads:
            return (), 0.0, budget_with_battery, self._txt(
                "Smart Scheduler hat keine schaltbaren Überschussverbraucher konfiguriert.",
                "Smart scheduler has no switchable surplus loads configured.",
            )
        if not available_loads:
            reason = self._txt(
                "Alle HEMS-Verbraucher sind blockiert.",
                "All HEMS loads are blocked.",
            )
            if blocked_loads:
                reason = self._txt(
                    "Alle HEMS-Verbraucher sind blockiert: ",
                    "All HEMS loads are blocked: ",
                ) + "; ".join(load.blocked_reason or load.entity_id for load in blocked_loads
                )
            return (), 0.0, budget_with_battery, reason

        selected: list[LoadProfile] = []
        used_power = 0.0
        for load in sorted(available_loads, key=lambda item: (item.priority, not item.is_on, item.estimated_power)):
            load_power = load.scheduling_power
            budget = budget_with_battery if load.allow_battery else budget_without_battery
            if load_power <= 0 or used_power + load_power <= budget:
                selected.append(load)
                used_power += load_power

        if not selected:
            battery_note = self._usable_battery_charge_note(
                battery_soc,
                battery_charge,
                usable_battery_charge,
                min_battery_soc,
                good_weather,
                bad_weather,
            )
            return (), 0.0, budget_with_battery, self._txt(
                f"Smart Scheduler wartet: echtes Überschussbudget {budget_with_battery:.0f} W reicht für keinen konfigurierten Verbraucher. Export {current_export:.0f} W, laufende Lasten {active_power:.0f} W, {battery_note}, Batterieentladung {battery_discharge:.0f} W.",
                f"Smart scheduler waits: real surplus budget {budget_with_battery:.0f} W is not enough for any configured load. Export {current_export:.0f} W, running loads {active_power:.0f} W, {battery_note}, battery discharge {battery_discharge:.0f} W.",
            )

        names = ", ".join(load.name for load in selected)
        return (
            tuple(load.entity_id for load in selected),
            used_power,
            budget_with_battery,
            self._txt(
                f"Smart Scheduler plant {len(selected)} Verbraucher mit ca. {used_power:.0f} W: {names}. Echtes Überschussbudget: {budget_with_battery:.0f} W (Export {current_export:.0f} W + laufende Lasten {active_power:.0f} W + nutzbare Batterieladung {usable_battery_charge:.0f} W - Batterieentladung {battery_discharge:.0f} W).",
                f"Smart scheduler plans {len(selected)} load(s) with about {used_power:.0f} W: {names}. Real surplus budget: {budget_with_battery:.0f} W (export {current_export:.0f} W + running loads {active_power:.0f} W + usable battery charge {usable_battery_charge:.0f} W - battery discharge {battery_discharge:.0f} W).",
            ),
        )

    def _usable_battery_charge_note(
        self,
        battery_soc: float | None,
        battery_charge: float,
        usable_battery_charge: float,
        min_battery_soc: float,
        good_weather: bool,
        bad_weather: bool,
    ) -> str:
        """Explain why measured battery charge is or is not usable."""
        if battery_charge <= 0:
            return self._txt("Batterie lädt nicht", "battery is not charging")
        if battery_soc is None:
            return self._txt(
                f"Batterie lädt {battery_charge:.0f} W, davon nutzbar 0 W, weil kein SoC bekannt ist",
                f"battery charges {battery_charge:.0f} W, usable 0 W because no SoC is known",
            )
        if battery_soc < min_battery_soc:
            return self._txt(
                f"Batterie lädt {battery_charge:.0f} W, davon nutzbar 0 W, weil SoC {battery_soc:.1f}% unter Mindest-SoC {min_battery_soc:.1f}% liegt",
                f"battery charges {battery_charge:.0f} W, usable 0 W because SoC {battery_soc:.1f}% is below minimum SoC {min_battery_soc:.1f}%",
            )
        share_soc = max(
            min_battery_soc,
            float(self.opts[OPT_BATTERY_CHARGE_SHARE_SOC]),
        )
        if battery_soc < share_soc:
            return self._txt(
                f"Batterie lädt {battery_charge:.0f} W, davon nutzbar 0 W, weil SoC {battery_soc:.1f}% unter Freigabe-SoC {share_soc:.1f}% liegt",
                f"battery charges {battery_charge:.0f} W, usable 0 W because SoC {battery_soc:.1f}% is below charge-share SoC {share_soc:.1f}%",
            )
        if bad_weather:
            return self._txt(
                f"Batterie lädt {battery_charge:.0f} W, davon nutzbar 0 W, weil schlechte Wetterlage erkannt wurde",
                f"battery charges {battery_charge:.0f} W, usable 0 W because bad weather was detected",
            )
        reserve_percent = (
            float(self.opts[OPT_BATTERY_CHARGE_RESERVE_GOOD])
            if good_weather
            else float(self.opts[OPT_BATTERY_CHARGE_RESERVE_CLOUDY])
        )
        if usable_battery_charge <= 0:
            return self._txt(
                f"Batterie lädt {battery_charge:.0f} W, davon nutzbar 0 W nach {reserve_percent:.0f}% Batteriereserve",
                f"battery charges {battery_charge:.0f} W, usable 0 W after {reserve_percent:.0f}% battery reserve",
            )
        return self._txt(
            f"Batterie lädt {battery_charge:.0f} W, davon nutzbar {usable_battery_charge:.0f} W; {reserve_percent:.0f}% bleiben für die Batterie reserviert",
            f"battery charges {battery_charge:.0f} W, usable {usable_battery_charge:.0f} W; {reserve_percent:.0f}% remains reserved for the battery",
        )

    def _flexible_load_decision_is_stable(
        self, target_on: bool, data: HemsData
    ) -> bool:
        """Require a stable decision before switching flexible loads."""
        now = datetime.now()
        switch_on_delay, switch_off_delay = self._response_delays(data)
        if target_on:
            self._flexible_loads_blocked_since = None
            if self._flexible_loads_allowed_since is None:
                self._flexible_loads_allowed_since = now
            return now - self._flexible_loads_allowed_since >= switch_on_delay

        self._flexible_loads_allowed_since = None
        if self._flexible_loads_blocked_since is None:
            self._flexible_loads_blocked_since = now
        return now - self._flexible_loads_blocked_since >= switch_off_delay

    def _response_delays(
        self,
        data: HemsData | None = None,
        *,
        battery_protect: bool | None = None,
        grid_power: float | None = None,
    ) -> tuple[timedelta, timedelta]:
        """Return on/off stability delays for the selected response profile."""
        profile = str(self.opts[OPT_RESPONSE_PROFILE])
        if profile == RESPONSE_REALTIME:
            return timedelta(seconds=0), timedelta(seconds=0)
        if profile == RESPONSE_SECONDS:
            return timedelta(seconds=60), timedelta(seconds=30)
        if profile == RESPONSE_MINUTES:
            return timedelta(minutes=10), timedelta(minutes=5)

        if profile == RESPONSE_AUTO:
            protect = data.battery_protect if data is not None else battery_protect
            grid = data.grid_power if data is not None else grid_power
            hard_import = grid is not None and grid > float(
                self.opts[OPT_GRID_HARD_IMPORT_LIMIT]
            )
            if protect or hard_import:
                return timedelta(seconds=60), timedelta(seconds=0)
            return timedelta(seconds=60), timedelta(seconds=30)

        return timedelta(seconds=60), timedelta(seconds=30)

    def _add_action(self, title: str, reason: str, kind: str) -> None:
        """Add one dashboard action entry."""
        now = datetime.now()
        self._action_history.insert(
            0,
            {
                "time": now.isoformat(timespec="seconds"),
                "title": title,
                "reason": reason,
                "kind": kind,
            },
        )
        del self._action_history[10:]
        row = self._daily_row(now.date().isoformat())
        row["events"] = int(row.get("events", 0)) + 1
        if kind == "device":
            row["switches"] = int(row.get("switches", 0)) + 1
        if kind in {"block", "protect"} or "block" in kind:
            row["blocks"] = int(row.get("blocks", 0)) + 1

    def _update_action_history(
        self,
        energy_mode: str,
        surplus_available: bool,
        flexible_loads_allowed: bool,
        battery_protect: bool,
        active_flexible_loads: int,
        active_flexible_entities: list[str],
        load_reason: str,
    ) -> None:
        """Track meaningful decision changes for the dashboard."""
        snapshot = {
            "energy_mode": energy_mode,
            "surplus_available": surplus_available,
            "flexible_loads_allowed": flexible_loads_allowed,
            "battery_protect": battery_protect,
            "active_flexible_loads": active_flexible_loads,
            "active_flexible_entities": tuple(active_flexible_entities),
        }
        previous = self._last_decision_snapshot
        self._last_decision_snapshot = snapshot

        if previous is None:
            self._add_action(self._txt("HEMS bewertet", "HEMS evaluated"), load_reason, energy_mode)
            return

        if previous["energy_mode"] != energy_mode:
            self._add_action(
                self._txt("Modus geändert", "Mode changed"),
                f"{previous['energy_mode']} -> {energy_mode}. {load_reason}",
                energy_mode,
            )
        if previous["flexible_loads_allowed"] != flexible_loads_allowed:
            self._add_action(
                self._txt("Flexible Verbraucher freigegeben", "Flexible loads released")
                if flexible_loads_allowed
                else self._txt("Flexible Verbraucher gesperrt", "Flexible loads blocked"),
                load_reason,
                "allow" if flexible_loads_allowed else "block",
            )
        if previous["battery_protect"] != battery_protect:
            self._add_action(
                self._txt("Batterieschutz aktiv", "Battery protection active")
                if battery_protect
                else self._txt("Batterieschutz beendet", "Battery protection ended"),
                load_reason,
                "protect" if battery_protect else "allow",
            )
        if (
            previous["active_flexible_loads"] != active_flexible_loads
            or previous["active_flexible_entities"] != tuple(active_flexible_entities)
        ):
            active = ", ".join(active_flexible_entities) or self._txt("keiner", "none")
            self._add_action(
                self._txt("Verbraucherstatus geändert", "Load status changed"),
                self._txt(
                    f"{active_flexible_loads} aktive flexible Verbraucher: {active}.",
                    f"{active_flexible_loads} active flexible loads: {active}.",
                ),
                "device",
            )

    def _option_label(self, key: str) -> str:
        """Return a readable option label for the dashboard history."""
        labels_de = {
            OPT_AUTO_ENABLED: "Automatik",
            OPT_BATTERY_CHARGE_RESERVE_CLOUDY: "Batteriereserve bei Bewölkung",
            OPT_BATTERY_CHARGE_RESERVE_GOOD: "Batteriereserve bei Wetterfreigabe",
            OPT_BATTERY_CHARGE_SHARE_SOC: "Batterieladung teilen ab SoC",
            OPT_BATTERY_DISCHARGE_LIMIT: "Entladegrenze Batterie",
            OPT_BATTERY_PROTECTION_ENABLED: "Batterieschutz",
            OPT_DASHBOARD_ENABLED: "Dashboard",
            OPT_HEATING_ROD_TEMPERATURE_HYSTERESIS: "Heizstab Temperatur-Hysterese",
            OPT_GRID_HARD_IMPORT_LIMIT: "Netzbezug hart",
            OPT_GRID_IMPORT_LIMIT: "Netzbezug-Toleranz",
            OPT_FLEXIBLE_LOAD_POWER: "Fallback-Leistung flexible Verbraucher",
            OPT_HEATING_ROD_POWER: "Fallback-Leistung Heizstab",
            OPT_MIN_BATTERY_SOC: "Mindest-SoC",
            OPT_MODE: "Betriebsart",
            OPT_RESPONSE_PROFILE: "Reaktionsmodus",
            OPT_PROTECT_BATTERY_SOC: "Batterieschutz-SoC",
            OPT_PV_AVG_THRESHOLD: "PV-Schwellwert 15 min",
            OPT_PV_THRESHOLD: "PV-Schwellwert aktuell",
            OPT_START_ONLY_APPLIANCE_POWER: "Fallback-Leistung Nur-starten-Geräte",
            OPT_USE_VIRTUAL_BATTERY: "Virtuelle Batterie im HEMS nutzen",
            OPT_VIRTUAL_BATTERY_ENABLED: "Virtuelle Batterie",
            OPT_VIRTUAL_BATTERY_CAPACITY: "Virtuelle Batterie Kapazität",
            OPT_VIRTUAL_BATTERY_MIN_SOC: "Virtuelle Batterie min SoC",
            OPT_VIRTUAL_BATTERY_MAX_SOC: "Virtuelle Batterie max SoC",
            OPT_VIRTUAL_BATTERY_MANUAL_SOC: "Virtuelle Batterie manueller SoC",
            OPT_VIRTUAL_BATTERY_CHARGE_EFFICIENCY: "Virtuelle Batterie Lade-Wirkungsgrad",
            OPT_VIRTUAL_BATTERY_DISCHARGE_EFFICIENCY: "Virtuelle Batterie Entlade-Wirkungsgrad",
        }
        labels_en = {
            OPT_AUTO_ENABLED: "Automation",
            OPT_BATTERY_CHARGE_RESERVE_CLOUDY: "Battery reserve when cloudy",
            OPT_BATTERY_CHARGE_RESERVE_GOOD: "Battery reserve with weather release",
            OPT_BATTERY_CHARGE_SHARE_SOC: "Share battery charging from SoC",
            OPT_BATTERY_DISCHARGE_LIMIT: "Battery discharge limit",
            OPT_BATTERY_PROTECTION_ENABLED: "Battery protection",
            OPT_DASHBOARD_ENABLED: "Dashboard",
            OPT_HEATING_ROD_TEMPERATURE_HYSTERESIS: "Heating rod temperature hysteresis",
            OPT_GRID_HARD_IMPORT_LIMIT: "Hard grid import",
            OPT_GRID_IMPORT_LIMIT: "Grid import tolerance",
            OPT_FLEXIBLE_LOAD_POWER: "Fallback flexible load power",
            OPT_HEATING_ROD_POWER: "Fallback heating rod power",
            OPT_MIN_BATTERY_SOC: "Minimum SoC",
            OPT_MODE: "Operating mode",
            OPT_RESPONSE_PROFILE: "Response mode",
            OPT_PROTECT_BATTERY_SOC: "Battery protection SoC",
            OPT_PV_AVG_THRESHOLD: "PV threshold 15 min",
            OPT_PV_THRESHOLD: "Current PV threshold",
            OPT_START_ONLY_APPLIANCE_POWER: "Fallback start-only appliance power",
            OPT_USE_VIRTUAL_BATTERY: "Use virtual battery in HEMS",
            OPT_VIRTUAL_BATTERY_ENABLED: "Virtual battery",
            OPT_VIRTUAL_BATTERY_CAPACITY: "Virtual battery capacity",
            OPT_VIRTUAL_BATTERY_MIN_SOC: "Virtual battery min SoC",
            OPT_VIRTUAL_BATTERY_MAX_SOC: "Virtual battery max SoC",
            OPT_VIRTUAL_BATTERY_MANUAL_SOC: "Virtual battery manual SoC",
            OPT_VIRTUAL_BATTERY_CHARGE_EFFICIENCY: "Virtual battery charge efficiency",
            OPT_VIRTUAL_BATTERY_DISCHARGE_EFFICIENCY: "Virtual battery discharge efficiency",
        }
        return (labels_de if self._language_is_german else labels_en).get(key, key)

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

    def _float_attr(
        self, entity_id: str | None, attribute: str, default: float | None
    ) -> float | None:
        if not entity_id:
            return default
        state = self.hass.states.get(entity_id)
        if state is None:
            return default
        value = state.attributes.get(attribute)
        if value is None:
            return default
        try:
            return float(str(value).replace(",", "."))
        except (TypeError, ValueError):
            return default

    def _positive_float_state(self, entity_id: str | None) -> float | None:
        value = self._float_state(entity_id, None)
        if value is None:
            return None
        return max(0.0, value)

    def _price_value(self, sensor_key: str, option_key: str) -> float:
        configured = self.config_entry.data.get(sensor_key)
        value = self._float_state(configured, None)
        if value is None:
            value = float(self.opts[option_key])
        if value > 10:
            value = value / 100
        return max(0.0, value)

    def _pv_arrays(self, specs: str | None) -> list[PvArrayProfile]:
        """Parse PV surfaces from azimuth:tilt[:Wp|modules x Wp] items."""
        arrays: list[PvArrayProfile] = []
        if specs:
            normalized = specs.replace(";", ",").replace("\n", ",")
            for raw_item in normalized.split(","):
                item = raw_item.strip()
                if not item:
                    continue
                name = None
                if "=" in item:
                    name, item = [part.strip() for part in item.split("=", 1)]
                    name = name or None
                parts = [
                    part.strip()
                    for part in item.replace("/", ":").split(":")
                    if part.strip()
                ]
                if len(parts) < 2:
                    continue
                try:
                    azimuth = float(parts[0].replace(",", "."))
                    tilt = float(parts[1].replace(",", "."))
                    peak_power, module_count, module_power = self._pv_array_size(parts)
                except (TypeError, ValueError):
                    continue
                arrays.append(
                    PvArrayProfile(
                        azimuth=azimuth % 360,
                        tilt=max(0.0, min(90.0, tilt)),
                        peak_power=max(0.1, peak_power),
                        module_count=module_count,
                        module_power=module_power,
                        name=name,
                    )
                )

        if arrays:
            return arrays
        return [
            PvArrayProfile(
                azimuth=180.0,
                tilt=30.0,
                peak_power=1.0,
            )
        ]

    def _pv_array_size(self, parts: list[str]) -> tuple[float, float | None, float | None]:
        """Return peak power, module count and module power from a PV spec."""
        if len(parts) >= 4:
            module_count = float(parts[2].replace(",", "."))
            module_power = float(parts[3].replace(",", "."))
            return module_count * module_power, module_count, module_power
        if len(parts) >= 3:
            raw_size = parts[2].lower().replace(" ", "").replace(",", ".")
            for separator in ("x", "*"):
                if separator in raw_size:
                    module_count_raw, module_power_raw = raw_size.split(separator, 1)
                    module_count = float(module_count_raw)
                    module_power = float(module_power_raw)
                    return module_count * module_power, module_count, module_power
            peak_power = float(raw_size)
            return peak_power, None, None
        return 1.0, None, None

    def _pv_orientation(
        self,
        arrays: list[PvArrayProfile],
        sun_elevation: float | None,
        sun_azimuth: float | None,
    ) -> dict[str, Any]:
        """Return the best matching PV surface for current sun position."""
        if sun_elevation is None or sun_azimuth is None or sun_elevation <= 0:
            return {"score": None, "best_array": None, "best_delta": None}

        best_score = -1.0
        best_array: PvArrayProfile | None = None
        best_delta: float | None = None
        total_peak_power = sum(array.peak_power for array in arrays) or 1.0

        for array in arrays:
            azimuth_delta = self._angle_delta(sun_azimuth, array.azimuth)
            azimuth_score = max(0.0, 1.0 - azimuth_delta / 90.0)
            ideal_elevation = max(10.0, 90.0 - array.tilt)
            elevation_delta = abs(sun_elevation - ideal_elevation)
            elevation_score = max(0.0, 1.0 - elevation_delta / 75.0)
            size_score = array.peak_power / total_peak_power
            score = (azimuth_score * 0.7 + elevation_score * 0.3) * (
                0.7 + size_score * 0.3
            )
            if score > best_score:
                best_score = score
                best_array = array
                best_delta = azimuth_delta

        if best_array is None:
            return {"score": None, "best_array": None, "best_delta": None}
        best_label = (
            f"{best_array.name} " if best_array.name else ""
        ) + f"{best_array.azimuth:.0f}°/{best_array.tilt:.0f}°"
        if best_array.module_count is not None and best_array.module_power is not None:
            best_label += (
                f"/{best_array.module_count:g}x{best_array.module_power:g} Wp"
            )
        elif best_array.peak_power > 1.0:
            best_label += f"/{best_array.peak_power:.0f} Wp"
        return {
            "score": round(max(0.0, min(1.0, best_score)), 3),
            "best_array": best_label,
            "best_delta": best_delta,
        }

    def _pv_window(
        self,
        pv_power: float,
        pv_average: float,
        forecast_today: float | None,
        forecast_next_hour: float | None,
        forecast_next_3h: float | None,
        sun_elevation: float | None,
        sun_azimuth: float | None,
        pv_arrays: list[PvArrayProfile],
        pv_orientation: dict[str, Any],
    ) -> tuple[str, str]:
        """Classify the current PV production window."""
        pv_threshold = float(self.opts[OPT_PV_THRESHOLD])
        next_hour = forecast_next_hour
        next_3h = forecast_next_3h

        if sun_elevation is not None and sun_elevation <= 0:
            return "night", self._txt(
                "Sonne ist unter dem Horizont; PV-Fenster ist nachts geschlossen.",
                "Sun is below the horizon; PV window is closed at night.",
            )

        if (
            next_3h is not None
            and next_3h < pv_threshold
            and pv_power < pv_threshold
        ):
            today_text = (
                f", heute {forecast_today:.1f}" if forecast_today is not None else ""
            )
            today_text_en = f", today {forecast_today:.1f}" if forecast_today is not None else ""
            return "low_today", self._txt(
                f"PV-Forecast bleibt niedrig: nächste 3 h {next_3h:.1f}{today_text}; aktuelles PV {pv_power:.1f} W.",
                f"PV forecast remains low: next 3 h {next_3h:.1f}{today_text_en}; current PV {pv_power:.1f} W.",
            )

        if next_3h is not None and next_3h >= max(pv_power * 1.5, pv_threshold * 2):
            return "good_later", self._txt(
                f"PV-Forecast erwartet später deutlich mehr: nächste 3 h {next_3h:.1f} gegenüber aktuell {pv_power:.1f} W.",
                f"PV forecast expects much more later: next 3 h {next_3h:.1f} compared with current {pv_power:.1f} W.",
            )

        if next_hour is not None and next_hour >= max(pv_power * 1.25, pv_threshold * 1.5):
            return "rising", self._txt(
                f"PV steigt voraussichtlich: nächste Stunde {next_hour:.1f}, aktuell {pv_power:.1f} W.",
                f"PV is expected to rise: next hour {next_hour:.1f}, current {pv_power:.1f} W.",
            )

        if sun_azimuth is not None and sun_elevation is not None:
            score = pv_orientation["score"]
            best_array = pv_orientation["best_array"]
            best_delta = pv_orientation["best_delta"]
            if score is not None and score >= 0.62:
                return "peak_now", self._txt(
                    f"Sonne steht günstig zu einer PV-Fläche: beste Fläche {best_array}, Azimut-Differenz {best_delta:.1f}°, Score {score:.2f}, Elevation {sun_elevation:.1f}°.",
                    f"Sun is well aligned with a PV surface: best surface {best_array}, azimuth delta {best_delta:.1f}°, score {score:.2f}, elevation {sun_elevation:.1f}°.",
                )
            if score is not None and (score <= 0.22 or sun_elevation < 12):
                return "falling", self._txt(
                    f"PV-Fenster wird schwach: {len(pv_arrays)} PV-Flächen, beste Fläche {best_array}, Score {score:.2f}, Elevation {sun_elevation:.1f}°.",
                    f"PV window is getting weak: {len(pv_arrays)} PV surfaces, best surface {best_array}, score {score:.2f}, elevation {sun_elevation:.1f}°.",
                )

        if pv_power > pv_average * 1.1 and pv_power >= pv_threshold:
            return "rising", self._txt(
                f"PV-Leistung liegt über dem 15-Minuten-Mittel: aktuell {pv_power:.1f} W, Mittel {pv_average:.1f} W.",
                f"PV power is above the 15-minute average: current {pv_power:.1f} W, average {pv_average:.1f} W.",
            )
        if pv_power < pv_average * 0.8 and pv_average >= pv_threshold:
            return "falling", self._txt(
                f"PV-Leistung fällt unter das 15-Minuten-Mittel: aktuell {pv_power:.1f} W, Mittel {pv_average:.1f} W.",
                f"PV power falls below the 15-minute average: current {pv_power:.1f} W, average {pv_average:.1f} W.",
            )

        if pv_power >= pv_threshold:
            return "usable_now", self._txt(
                f"PV-Fenster ist nutzbar: aktuell {pv_power:.1f} W über Schwellwert {pv_threshold:.1f} W.",
                f"PV window is usable: current {pv_power:.1f} W above threshold {pv_threshold:.1f} W.",
            )
        return "weak_now", self._txt(
            f"PV-Fenster ist schwach: aktuell {pv_power:.1f} W unter Schwellwert {pv_threshold:.1f} W.",
            f"PV window is weak: current {pv_power:.1f} W below threshold {pv_threshold:.1f} W.",
        )

    def _angle_delta(self, first: float, second: float) -> float:
        """Return smallest difference between two compass angles."""
        delta = abs((first - second + 180) % 360 - 180)
        return float(delta)

    def _good_weather(
        self,
        battery_soc: float | None,
        weather: str | None,
        clouds: float | None,
        sunshine: float | None,
    ) -> bool:
        if battery_soc is not None and battery_soc >= 90:
            return True
        if weather is None:
            return True
        weather_ok = weather in GOOD_WEATHER
        cloud_value = clouds if clouds is not None else 0
        sunshine_value = sunshine if sunshine is not None else 999
        if battery_soc is not None and battery_soc >= 75:
            return weather_ok and cloud_value < 85
        return weather_ok and cloud_value < 70 and sunshine_value > 20

    def _weather_reason(
        self,
        battery_soc: float | None,
        weather: str | None,
        clouds: float | None,
        sunshine: float | None,
    ) -> str:
        if battery_soc is not None and battery_soc >= 90:
            return self._txt(
                f"Batterie-SoC {battery_soc:.1f}% ist mindestens 90%, Wetter wird großzügig freigegeben.",
                f"Battery SoC {battery_soc:.1f}% is at least 90%; weather is released generously.",
            )
        if weather is None:
            return self._txt(
                "Kein Wetterzustand konfiguriert oder verfügbar; Wetter blockiert deshalb nicht.",
                "No weather state configured or available; weather does not block.",
            )

        weather_ok = weather in GOOD_WEATHER
        cloud_value = clouds if clouds is not None else 0
        sunshine_value = sunshine if sunshine is not None else 999

        if battery_soc is not None and battery_soc >= 75:
            if weather_ok and cloud_value < 85:
                return self._txt(
                    f"Wetter '{weather}' ist freigegeben und Bewölkung {cloud_value:.1f}% liegt unter 85%.",
                    f"Weather '{weather}' is released and cloud coverage {cloud_value:.1f}% is below 85%.",
                )
            return self._txt(
                f"Wetter hält zurück: Zustand '{weather}', Bewölkung {cloud_value:.1f}% bei SoC {battery_soc:.1f}%. Erlaubt wären freigegebenes Wetter und unter 85% Bewölkung.",
                f"Weather holds back: state '{weather}', cloud coverage {cloud_value:.1f}% at SoC {battery_soc:.1f}%. Released weather and below 85% cloud coverage would be required.",
            )

        if weather_ok and cloud_value < 70 and sunshine_value > 20:
            return self._txt(
                f"Wetter '{weather}', Bewölkung {cloud_value:.1f}% unter 70% und Sonne {sunshine_value:.1f} min über 20 min.",
                f"Weather '{weather}', cloud coverage {cloud_value:.1f}% below 70% and sun {sunshine_value:.1f} min above 20 min.",
            )
        return self._txt(
            f"Wetter hält zurück: Zustand '{weather}', Bewölkung {cloud_value:.1f}% und Sonne {sunshine_value:.1f} min. Bei SoC unter 75% braucht BB HEMS gutes Wetter, unter 70% Bewölkung und über 20 min Sonne.",
            f"Weather holds back: state '{weather}', cloud coverage {cloud_value:.1f}% and sun {sunshine_value:.1f} min. Below 75% SoC, BB HEMS requires good weather, below 70% cloud coverage and more than 20 min sun.",
        )

    def _bad_weather(self, weather: str | None, clouds: float | None) -> bool:
        cloud_value = clouds if clouds is not None else 0
        return (weather in BAD_WEATHER if weather else False) or cloud_value > 90

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

    def _battery_protect(
        self, battery_soc: float | None, battery_discharge: float, bad_weather: bool
    ) -> bool:
        opts = self.opts
        if not bool(opts[OPT_BATTERY_PROTECTION_ENABLED]):
            return False
        if battery_soc is not None and battery_soc < float(opts[OPT_PROTECT_BATTERY_SOC]):
            return True
        discharge_limit = float(opts[OPT_BATTERY_DISCHARGE_LIMIT])
        if discharge_limit <= 0 and battery_discharge > 0:
            return True
        if discharge_limit > 0 and battery_discharge >= discharge_limit:
            return True
        return bool(bad_weather and battery_soc is not None and battery_soc < 70)

    def _usable_battery_charge(
        self,
        battery_soc: float | None,
        battery_charge: float,
        min_battery_soc: float,
        good_weather: bool,
        bad_weather: bool,
    ) -> float:
        """Return battery charge power that may be shifted to flexible loads."""
        share_soc = max(
            min_battery_soc,
            float(self.opts[OPT_BATTERY_CHARGE_SHARE_SOC]),
        )
        if (
            battery_soc is None
            or battery_soc < min_battery_soc
            or battery_soc < share_soc
            or bad_weather
        ):
            return 0.0
        reserve_percent = (
            float(self.opts[OPT_BATTERY_CHARGE_RESERVE_GOOD])
            if good_weather
            else float(self.opts[OPT_BATTERY_CHARGE_RESERVE_CLOUDY])
        )
        usable_percent = max(0.0, min(100.0, 100.0 - reserve_percent))
        return max(0.0, battery_charge * usable_percent / 100.0)

    def _battery_reason(
        self,
        battery_soc: float | None,
        battery_discharge: float,
        bad_weather: bool,
        battery_protect: bool,
    ) -> str:
        opts = self.opts
        if not bool(opts[OPT_BATTERY_PROTECTION_ENABLED]):
            return self._txt(
                "Batterieschutz ist deaktiviert; SoC- und Batterieentladegrenzen blockieren HEMS nicht.",
                "Battery protection is disabled; SoC and battery discharge limits do not block HEMS.",
            )
        protect_soc = float(opts[OPT_PROTECT_BATTERY_SOC])
        discharge_limit = float(opts[OPT_BATTERY_DISCHARGE_LIMIT])
        if battery_soc is not None and battery_soc < protect_soc:
            return self._txt(
                f"Batterieschutz aktiv: SoC {battery_soc:.1f}% liegt unter Schutzgrenze {protect_soc:.1f}%.",
                f"Battery protection active: SoC {battery_soc:.1f}% is below protection limit {protect_soc:.1f}%.",
            )
        if discharge_limit <= 0 and battery_discharge > 0:
            return self._txt(
                f"Batterieschutz aktiv: Batterie entlädt mit {battery_discharge:.1f} W; die Entladegrenze ist auf 0 W gesetzt.",
                f"Battery protection active: battery discharges with {battery_discharge:.1f} W; discharge limit is set to 0 W.",
            )
        if discharge_limit > 0 and battery_discharge >= discharge_limit:
            return self._txt(
                f"Batterieschutz aktiv: Batterie entlädt mit {battery_discharge:.1f} W und erreicht die Grenze {discharge_limit:.1f} W.",
                f"Battery protection active: battery discharges with {battery_discharge:.1f} W and reaches the limit {discharge_limit:.1f} W.",
            )
        if bad_weather and battery_soc is not None and battery_soc < 70:
            return self._txt(
                f"Batterieschutz aktiv: schlechtes Wetter und SoC {battery_soc:.1f}% unter 70%.",
                f"Battery protection active: bad weather and SoC {battery_soc:.1f}% below 70%.",
            )
        if battery_protect:
            return self._txt("Batterieschutz ist aktiv.", "Battery protection is active.")
        return self._txt(
            f"Kein Batterieschutz: SoC {battery_soc if battery_soc is not None else 'n/a'}%, Entladung {battery_discharge:.1f} W.",
            f"No battery protection: SoC {battery_soc if battery_soc is not None else 'n/a'}%, discharge {battery_discharge:.1f} W.",
        )

    def _battery_soc_ok(self, battery_soc: float | None) -> bool:
        if not bool(self.opts[OPT_BATTERY_PROTECTION_ENABLED]):
            return True
        if battery_soc is None:
            return True
        return battery_soc >= float(self.opts[OPT_MIN_BATTERY_SOC])

    def _surplus_reason(
        self,
        pv_power: float,
        pv_average: float,
        grid_power: float,
        grid_average: float,
        grid_limit: float,
        pv_threshold: float,
        pv_avg_threshold: float,
        usable_battery_charge: float,
        good_weather: bool,
        surplus_available: bool,
    ) -> str:
        if surplus_available:
            if usable_battery_charge > 0:
                charge_grid_limit = max(
                    grid_limit, float(self.opts[OPT_GRID_IMPORT_LIMIT])
                )
                return self._txt(
                    f"Überschuss erfüllt: zusätzlich zur PV ist nutzbare Batterieladung {usable_battery_charge:.1f} W verfügbar; Netz {grid_power:.1f} W <= {charge_grid_limit:.1f} W.",
                    f"Surplus fulfilled: in addition to PV, usable battery charge {usable_battery_charge:.1f} W is available; grid {grid_power:.1f} W <= {charge_grid_limit:.1f} W.",
                )
            return self._txt(
                f"Überschuss erfüllt: PV {pv_power:.1f} W >= {pv_threshold:.1f} W, PV 15 min {pv_average:.1f} W >= {pv_avg_threshold:.1f} W und Netz {grid_power:.1f} W <= {grid_limit:.1f} W oder Netzmittel {grid_average:.1f} W < 50 W bei Wetterfreigabe.",
                f"Surplus fulfilled: PV {pv_power:.1f} W >= {pv_threshold:.1f} W, PV 15 min {pv_average:.1f} W >= {pv_avg_threshold:.1f} W and grid {grid_power:.1f} W <= {grid_limit:.1f} W or grid average {grid_average:.1f} W < 50 W with weather release.",
            )
        missing: list[str] = []
        if pv_power < pv_threshold:
            missing.append(self._txt(
                f"PV aktuell {pv_power:.1f} W unter {pv_threshold:.1f} W",
                f"current PV {pv_power:.1f} W below {pv_threshold:.1f} W",
            ))
        if pv_average < pv_avg_threshold:
            missing.append(self._txt(
                f"PV 15 min {pv_average:.1f} W unter {pv_avg_threshold:.1f} W",
                f"PV 15 min {pv_average:.1f} W below {pv_avg_threshold:.1f} W",
            ))
        if not (grid_power <= grid_limit or (grid_average < 50 and good_weather)):
            missing.append(self._txt(
                f"Netz {grid_power:.1f} W über Limit {grid_limit:.1f} W und Netzmittel {grid_average:.1f} W nicht als Ausgleich nutzbar",
                f"grid {grid_power:.1f} W above limit {grid_limit:.1f} W and grid average {grid_average:.1f} W not usable as compensation",
            ))
        if usable_battery_charge <= 0:
            missing.append(self._txt("keine nutzbare Batterieladung", "no usable battery charge"))
        return self._txt("Überschuss fehlt: ", "Surplus missing: ") + "; ".join(missing)

    def _load_reason(
        self,
        surplus_available: bool,
        weather_release: bool,
        battery_protect: bool,
        battery_soc: float | None,
        flexible_loads_allowed: bool,
        battery_charge_release: bool = False,
    ) -> str:
        if flexible_loads_allowed:
            if battery_charge_release:
                return self._txt(
                    "Flexible Verbraucher sind erlaubt, weil die Batterie sicher geladen ist und ein Teil der aktiven Batterieladung für HEMS freigegeben wird.",
                    "Flexible loads are allowed because the battery is safely charged and part of the active battery charging power is released for HEMS.",
                )
            if not bool(self.opts[OPT_BATTERY_PROTECTION_ENABLED]):
                return self._txt(
                    "Flexible Verbraucher sind erlaubt, weil Überschuss und Wetterfreigabe passen; Batterieschutz ist deaktiviert.",
                    "Flexible loads are allowed because surplus and weather release match; battery protection is disabled.",
                )
            return self._txt(
                "Flexible Verbraucher sind erlaubt, weil Überschuss, Wetterfreigabe, SoC und Batterieschutz passen.",
                "Flexible loads are allowed because surplus, weather release, SoC and battery protection match.",
            )
        blockers: list[str] = []
        if not surplus_available:
            blockers.append(self._txt("kein Überschuss", "no surplus"))
        if not weather_release:
            blockers.append(self._txt("keine Wetterfreigabe", "no weather release"))
        if battery_protect:
            blockers.append(self._txt("Batterieschutz aktiv", "battery protection active"))
        if not self._battery_soc_ok(battery_soc):
            blockers.append(self._txt(
                f"SoC {battery_soc:.1f}% unter Mindest-SoC {float(self.opts[OPT_MIN_BATTERY_SOC]):.1f}%",
                f"SoC {battery_soc:.1f}% below minimum SoC {float(self.opts[OPT_MIN_BATTERY_SOC]):.1f}%",
            ))
        return self._txt("Flexible Verbraucher gesperrt: ", "Flexible loads blocked: ") + ", ".join(blockers)

    def _mode_grid_limit(self, mode: str, grid_tolerance: float) -> float:
        if mode == MODE_COMFORT:
            return max(grid_tolerance, float(self.opts[OPT_GRID_IMPORT_LIMIT]) + 100)
        if mode == MODE_ECO:
            return min(grid_tolerance, 0.0)
        return grid_tolerance

    def _energy_mode(
        self,
        mode: str,
        grid_power: float,
        pv_power: float,
        surplus_available: bool,
        battery_protect: bool,
        good_weather: bool,
    ) -> str:
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
