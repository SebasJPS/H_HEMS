"""Slim coordinator and control model for BB HEMS v1."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, replace
from datetime import datetime, time, timedelta
import json
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_OFF, STATE_ON, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

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
    MODE_AUTO,
    MODE_OFF,
    OPT_AC_BATTERY_NIGHT_DISCHARGE_W,
    OPT_AC_BATTERY_NIGHT_END,
    OPT_AC_BATTERY_NIGHT_START,
    OPT_AUTO_ENABLED,
    OPT_DEHUMIDIFIER_POWER,
    OPT_GRID_TOLERANCE_W,
    OPT_MANUAL_PAUSE_HOURS,
    OPT_MODE,
    OPT_POOL_POWER,
    OPT_PV_BATTERY_AC_CHARGE_THRESHOLD_SOC,
    OPT_START_ONLY_APPLIANCE_POWER,
    SCAN_INTERVAL,
)
from .surplus_policy import (
    StrictSurplusOptions,
    SurplusLoad,
    ac_battery_target,
    schedule_strict_surplus_loads,
)

_LOGGER = logging.getLogger(__name__)
STORE_VERSION = 1
STORE_SAVE_INTERVAL = timedelta(minutes=2)
ACTION_HISTORY_LIMIT = 12


@dataclass(frozen=True)
class LoadProfile:
    """A controllable load in the slim HEMS model."""

    entity_id: str
    name: str
    category: str
    estimated_power: float
    actual_power: float | None
    priority: int
    control_mode: str
    is_on: bool

    @property
    def scheduling_power(self) -> float:
        if self.is_on and self.actual_power is not None and self.actual_power > 0:
            return self.actual_power
        return self.estimated_power


@dataclass(frozen=True)
class AcBatteryProfile:
    """A controllable AC battery such as EcoFlow Stream."""

    name: str
    soc_sensor: str
    charge_power_sensor: str | None
    discharge_power_sensor: str | None
    charge_power_number: str
    discharge_power_number: str
    min_soc: float
    max_soc: float
    max_charge_power: float
    max_discharge_power: float
    step_power: float
    control_interval: float
    direction_switch_delay: float
    priority: int
    soc: float | None = None
    charge_power: float = 0.0
    discharge_power: float = 0.0


@dataclass(frozen=True)
class HemsData:
    """Computed slim HEMS state."""

    grid_power: float
    grid_import: float
    grid_export: float
    pv_power: float
    battery_soc_min: float | None
    battery_discharge: float
    house_load: float
    surplus_available: bool
    flexible_loads_allowed: bool
    energy_mode: str
    grid_tolerance: float
    available_surplus_budget: float
    scheduled_surplus_loads: tuple[str, ...]
    scheduled_surplus_power: float
    manually_paused_loads: tuple[str, ...]
    pool_loads: tuple[str, ...]
    dehumidifier_loads: tuple[str, ...]
    start_only_loads: tuple[str, ...]
    active_loads: tuple[str, ...]
    ac_battery_details: list[dict[str, Any]]
    ac_battery_reason: str
    surplus_reason: str
    scheduler_reason: str
    load_reason: str
    action_history: list[dict[str, str]]


class HemsCoordinator(DataUpdateCoordinator[HemsData]):
    """Calculate and apply slim surplus decisions."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.config_entry = entry
        self._action_history: list[dict[str, str]] = []
        self._manual_pauses: dict[str, str] = {}
        self._device_runtime_state: dict[str, dict[str, str]] = {}
        self._ac_battery_runtime_state: dict[str, dict[str, Any]] = {}
        self._store = Store(hass, STORE_VERSION, f"{DOMAIN}_{entry.entry_id}_slim")
        self._last_save: datetime | None = None
        self._ac_battery_task: asyncio.Task | None = self.hass.async_create_task(
            self._async_ac_battery_loop()
        )

    async def async_load_storage(self) -> None:
        """Load persisted runtime state."""
        stored = await self._store.async_load()
        if not isinstance(stored, dict):
            return
        self._action_history = self._safe_action_history(
            stored.get("action_history")
        )
        self._manual_pauses = self._safe_manual_pauses(stored.get("manual_pauses"))
        self._device_runtime_state = self._safe_device_runtime_state(
            stored.get("device_runtime_state")
        )

    async def async_save_storage(self, *, force: bool = False) -> None:
        """Persist runtime state."""
        now = datetime.now()
        if (
            not force
            and self._last_save is not None
            and now - self._last_save < STORE_SAVE_INTERVAL
        ):
            return
        self._last_save = now
        await self._store.async_save(
            {
                "action_history": self._action_history,
                "manual_pauses": self._manual_pauses,
                "device_runtime_state": self._device_runtime_state,
            }
        )

    async def _async_update_data(self) -> HemsData:
        data = self._calculate()
        changed = await self._async_apply_load_control(data)
        await self.async_save_storage(force=changed)
        if changed:
            return replace(data, action_history=list(self._action_history))
        return data

    async def async_shutdown(self) -> None:
        if self._ac_battery_task is not None:
            self._ac_battery_task.cancel()
            try:
                await self._ac_battery_task
            except asyncio.CancelledError:
                pass
            self._ac_battery_task = None

    @property
    def opts(self) -> dict[str, Any]:
        return {**DEFAULTS, **dict(self.config_entry.options)}

    @property
    def _language_is_german(self) -> bool:
        language = getattr(self.hass.config, "language", None)
        return bool(language and str(language).lower().startswith("de"))

    def _txt(self, de: str, en: str) -> str:
        return de if self._language_is_german else en

    async def async_set_option(self, key: str, value: Any) -> None:
        options = dict(self.config_entry.options)
        previous = options.get(key, DEFAULTS.get(key))
        options[key] = value
        self._add_action(
            self._txt("Einstellung geändert", "Setting changed"),
            f"{key}: {previous} -> {value}",
            "manual",
        )
        self.hass.config_entries.async_update_entry(self.config_entry, options=options)
        await self.async_request_refresh()

    def _calculate(self) -> HemsData:
        config = self.config_entry.data
        legacy_grid_power = self._float_state(config.get(CONF_GRID_POWER_SENSOR), 0.0)
        grid_import, grid_export = self._grid_flow(config, legacy_grid_power)
        grid_power = grid_import - grid_export
        pv_power = self._positive_sum(config.get(CONF_PV_POWER_SENSORS, []))
        battery_soc_min = self._battery_soc_min()
        battery_discharge = self._positive_sum(
            config.get(CONF_BATTERY_DISCHARGE_SENSORS, [])
        )
        house_load = self._positive_sum(config.get(CONF_HOUSE_LOAD_SENSORS, []))
        options = self._strict_options()
        loads = self._load_profiles()

        auto_enabled = bool(self.opts[OPT_AUTO_ENABLED])
        mode = str(self.opts[OPT_MODE])
        central_allowed = (
            auto_enabled and mode != MODE_OFF and grid_import <= options.grid_tolerance_w
        )
        schedule = schedule_strict_surplus_loads(
            loads=[
                SurplusLoad(
                    entity_id=load.entity_id,
                    name=load.name,
                    category=load.category,
                    power_w=load.scheduling_power,
                    priority=load.priority,
                    is_on=load.is_on,
                    start_only=load.control_mode == "start_only",
                    manually_paused=load.entity_id in self._active_manual_pauses(),
                    pause_reason=self._manual_pause_reason(load.entity_id),
                )
                for load in loads
            ],
            allowed=central_allowed,
            grid_import_w=grid_import,
            grid_export_w=grid_export,
            battery_discharge_w=battery_discharge,
            options=options,
        )
        energy_mode = self._energy_mode(mode, auto_enabled, schedule, grid_import)
        active_loads = tuple(load.entity_id for load in loads if load.is_on)
        ac_batteries = self._ac_battery_profiles()
        ac_details = self._ac_battery_details(ac_batteries)
        return HemsData(
            grid_power=grid_power,
            grid_import=grid_import,
            grid_export=grid_export,
            pv_power=pv_power,
            battery_soc_min=battery_soc_min,
            battery_discharge=battery_discharge,
            house_load=house_load,
            surplus_available=schedule.available_budget_w > 0 and central_allowed,
            flexible_loads_allowed=central_allowed,
            energy_mode=energy_mode,
            grid_tolerance=options.grid_tolerance_w,
            available_surplus_budget=schedule.available_budget_w,
            scheduled_surplus_loads=schedule.scheduled_loads,
            scheduled_surplus_power=schedule.scheduled_power_w,
            manually_paused_loads=tuple(self._active_manual_pauses().keys()),
            pool_loads=tuple(config.get(CONF_POOL_SWITCHES, [])),
            dehumidifier_loads=tuple(config.get(CONF_DEHUMIDIFIER_SWITCHES, [])),
            start_only_loads=tuple(config.get(CONF_START_ONLY_APPLIANCE_SWITCHES, [])),
            active_loads=active_loads,
            ac_battery_details=ac_details,
            ac_battery_reason=self._ac_battery_summary(ac_details),
            surplus_reason=self._surplus_reason(grid_import, grid_export, battery_discharge),
            scheduler_reason=self._localized_policy_reason(schedule.reason),
            load_reason=self._load_reason(mode, auto_enabled, grid_import, schedule),
            action_history=list(self._action_history),
        )

    def _energy_mode(
        self,
        mode: str,
        auto_enabled: bool,
        schedule: Any,
        grid_import: float,
    ) -> str:
        if not auto_enabled or mode == MODE_OFF:
            return "off"
        if grid_import > float(self.opts[OPT_GRID_TOLERANCE_W]):
            return "grid_hold"
        if schedule.scheduled_loads:
            return "surplus_active"
        if schedule.available_budget_w > 0:
            return "surplus_waiting"
        return MODE_AUTO

    def _surplus_reason(
        self, grid_import: float, grid_export: float, battery_discharge: float
    ) -> str:
        tolerance = float(self.opts[OPT_GRID_TOLERANCE_W])
        if grid_import > tolerance:
            return self._txt(
                f"Netzbezug {grid_import:.0f} W liegt über der Toleranz {tolerance:.0f} W.",
                f"Grid import {grid_import:.0f} W exceeds tolerance {tolerance:.0f} W.",
            )
        if battery_discharge > 0:
            return self._txt(
                f"Einspeisung {grid_export:.0f} W, Batterieentladung {battery_discharge:.0f} W wird abgezogen.",
                f"Export {grid_export:.0f} W, battery discharge {battery_discharge:.0f} W is subtracted.",
            )
        return self._txt(
            f"Echter Überschuss aus Smartmeter: {grid_export:.0f} W Einspeisung.",
            f"Real smart-meter surplus: {grid_export:.0f} W export.",
        )

    def _load_reason(
        self, mode: str, auto_enabled: bool, grid_import: float, schedule: Any
    ) -> str:
        if not auto_enabled or mode == MODE_OFF:
            return self._txt("HEMS ist ausgeschaltet.", "HEMS is switched off.")
        if grid_import > float(self.opts[OPT_GRID_TOLERANCE_W]):
            return self._txt(
                "Verbraucher warten, weil Netzbezug anliegt.",
                "Loads wait because grid import is present.",
            )
        return self._localized_policy_reason(schedule.reason)

    async def _async_apply_load_control(self, data: HemsData) -> bool:
        changed = False
        desired = set(data.scheduled_surplus_loads)
        for load in self._load_profiles():
            if self._manual_pause_needed(load, load.entity_id in desired):
                changed = True
                continue
            if load.control_mode == "start_only":
                if load.entity_id in desired:
                    if self._start_only_recently_released(load):
                        continue
                    changed |= await self._async_turn_on_load(load, data.scheduler_reason)
                continue
            if load.entity_id in desired:
                changed |= await self._async_turn_on_load(load, data.scheduler_reason)
            else:
                changed |= await self._async_turn_off_load(load, data.scheduler_reason)
        return changed

    def _start_only_recently_released(self, load: LoadProfile) -> bool:
        runtime = self._device_runtime_state.get(load.entity_id, {})
        last_on = self._parse_datetime(runtime.get("last_on"))
        return last_on is not None and datetime.now() - last_on < timedelta(hours=12)

    def _manual_pause_needed(self, load: LoadProfile, should_be_on: bool) -> bool:
        if not should_be_on or load.control_mode == "start_only":
            return False
        if load.entity_id in self._active_manual_pauses():
            return True
        runtime = self._device_runtime_state.setdefault(load.entity_id, {})
        last_on = self._parse_datetime(runtime.get("last_on"))
        if (
            runtime.get("hems_on") != "true"
            or load.is_on
            or last_on is None
            or datetime.now() - last_on < timedelta(minutes=2)
        ):
            return False
        paused_until = datetime.now() + timedelta(
            hours=float(self.opts[OPT_MANUAL_PAUSE_HOURS])
        )
        self._manual_pauses[load.entity_id] = paused_until.isoformat(timespec="seconds")
        runtime["hems_on"] = "false"
        self._add_action(
            self._txt("Manuelle Pause erkannt", "Manual pause detected"),
            self._txt(
                f"{load.name} bleibt bis {paused_until.strftime('%H:%M')} pausiert.",
                f"{load.name} remains paused until {paused_until.strftime('%H:%M')}.",
            ),
            "manual",
        )
        return True

    async def _async_turn_on_load(self, load: LoadProfile, reason: str) -> bool:
        state = self.hass.states.get(load.entity_id)
        if state is None or state.state in {STATE_UNAVAILABLE, STATE_UNKNOWN}:
            return False
        domain = load.entity_id.split(".", 1)[0]
        service = "press" if domain == "button" else "turn_on"
        if domain not in {"switch", "input_boolean", "button"}:
            return False
        if domain != "button" and state.state == STATE_ON:
            return False
        await self.hass.services.async_call(
            domain, service, {"entity_id": load.entity_id}, blocking=False
        )
        self._record_switch(load, True)
        self._add_action(
            self._txt("Verbraucher freigegeben", "Load released"),
            f"{load.name}: {reason}",
            "device",
        )
        return True

    async def _async_turn_off_load(self, load: LoadProfile, reason: str) -> bool:
        state = self.hass.states.get(load.entity_id)
        if state is None or state.state in {STATE_OFF, STATE_UNAVAILABLE, STATE_UNKNOWN}:
            return False
        domain = load.entity_id.split(".", 1)[0]
        if domain not in {"switch", "input_boolean"}:
            return False
        await self.hass.services.async_call(
            domain, "turn_off", {"entity_id": load.entity_id}, blocking=False
        )
        self._record_switch(load, False)
        self._add_action(
            self._txt("Verbraucher gestoppt", "Load stopped"),
            f"{load.name}: {reason}",
            "device",
        )
        return True

    def _record_switch(self, load: LoadProfile, switched_on: bool) -> None:
        state = self._device_runtime_state.setdefault(load.entity_id, {})
        state["last_on" if switched_on else "last_off"] = datetime.now().isoformat(
            timespec="seconds"
        )
        state["hems_on"] = "true" if switched_on else "false"

    async def _async_ac_battery_loop(self) -> None:
        while True:
            try:
                profiles = self._ac_battery_profiles()
                interval = min(
                    (profile.control_interval for profile in profiles),
                    default=30.0,
                )
                await asyncio.sleep(max(5.0, interval))
                profiles = self._ac_battery_profiles()
                if profiles:
                    await self._async_apply_ac_battery_control(profiles)
            except asyncio.CancelledError:
                raise
            except Exception:
                _LOGGER.exception("Failed to control AC battery")
                await asyncio.sleep(30)

    async def _async_apply_ac_battery_control(
        self, profiles: list[AcBatteryProfile]
    ) -> bool:
        if not bool(self.opts[OPT_AUTO_ENABLED]) or self.opts[OPT_MODE] == MODE_OFF:
            return await self._async_stop_ac_batteries(profiles)
        grid_import, grid_export = self._grid_flow(
            self.config_entry.data,
            self._float_state(self.config_entry.data.get(CONF_GRID_POWER_SENSOR), 0.0),
        )
        battery_discharge = self._positive_sum(
            self.config_entry.data.get(CONF_BATTERY_DISCHARGE_SENSORS, [])
        )
        budget = max(0.0, grid_export - battery_discharge)
        changed = False
        for profile in sorted(profiles, key=lambda item: item.priority):
            charge, discharge, reason = self._ac_battery_target(profile, budget, grid_import)
            runtime = self._ac_battery_runtime_state.setdefault(profile.name, {})
            runtime.update(
                {
                    "target_charge": charge,
                    "target_discharge": discharge,
                    "reason": reason,
                    "soc": profile.soc,
                    "charge_power": profile.charge_power,
                    "discharge_power": profile.discharge_power,
                }
            )
            if charge > 0:
                budget = max(0.0, budget - charge)
            changed |= await self._async_set_ac_battery_numbers(
                profile, charge, discharge, reason
            )
        return changed

    async def _async_stop_ac_batteries(
        self, profiles: list[AcBatteryProfile]
    ) -> bool:
        changed = False
        for profile in profiles:
            reason = self._txt("HEMS ist ausgeschaltet.", "HEMS is switched off.")
            self._ac_battery_runtime_state.setdefault(profile.name, {}).update(
                {"target_charge": 0.0, "target_discharge": 0.0, "reason": reason}
            )
            changed |= await self._async_set_ac_battery_numbers(
                profile, 0.0, 0.0, reason
            )
        return changed

    def _ac_battery_target(
        self, profile: AcBatteryProfile, surplus_budget: float, grid_import: float
    ) -> tuple[float, float, str]:
        decision = ac_battery_target(
            soc=profile.soc,
            min_soc=profile.min_soc,
            max_soc=profile.max_soc,
            max_charge_power_w=profile.max_charge_power,
            max_discharge_power_w=profile.max_discharge_power,
            step_power_w=profile.step_power,
            surplus_budget_w=surplus_budget,
            grid_import_w=grid_import,
            pv_battery_soc=self._battery_soc_min(),
            now=datetime.now().time(),
            options=self._strict_options(),
        )
        return decision.charge_w, decision.discharge_w, self._localized_ac_reason(
            profile.name, decision.reason
        )

    async def _async_set_ac_battery_numbers(
        self,
        profile: AcBatteryProfile,
        charge_target: float,
        discharge_target: float,
        reason: str,
    ) -> bool:
        current_charge = self._positive_float_state(profile.charge_power_number) or 0.0
        current_discharge = self._positive_float_state(profile.discharge_power_number) or 0.0
        changed = False
        if charge_target > 0 and current_discharge > 0:
            changed |= await self._async_set_number(profile.discharge_power_number, 0.0)
            await asyncio.sleep(profile.direction_switch_delay)
            current_discharge = 0.0
        if discharge_target > 0 and current_charge > 0:
            changed |= await self._async_set_number(profile.charge_power_number, 0.0)
            await asyncio.sleep(profile.direction_switch_delay)
            current_charge = 0.0
        if self._number_changed(current_charge, charge_target):
            changed |= await self._async_set_number(profile.charge_power_number, charge_target)
        if self._number_changed(current_discharge, discharge_target):
            changed |= await self._async_set_number(profile.discharge_power_number, discharge_target)
        if changed:
            self._add_action(
                self._txt("AC-Akku geregelt", "AC battery controlled"),
                self._txt(
                    f"{profile.name}: Laden {charge_target:.0f} W, Entladen {discharge_target:.0f} W. {reason}",
                    f"{profile.name}: charge {charge_target:.0f} W, discharge {discharge_target:.0f} W. {reason}",
                ),
                "battery",
            )
        return changed

    async def _async_set_number(self, entity_id: str, value: float) -> bool:
        state = self.hass.states.get(entity_id)
        if state is None or state.state in {STATE_UNAVAILABLE, STATE_UNKNOWN}:
            return False
        await self.hass.services.async_call(
            "number",
            "set_value",
            {"entity_id": entity_id, "value": round(max(0.0, value), 1)},
            blocking=False,
        )
        return True

    def _number_changed(self, current: float, target: float) -> bool:
        return abs(current - target) >= 1.0

    def _load_profiles(self) -> list[LoadProfile]:
        data = self.config_entry.data
        profiles: list[LoadProfile] = []
        profiles.extend(
            self._profiles_from_entities(
                data.get(CONF_POOL_SWITCHES, []),
                data.get(CONF_POOL_POWER_SENSORS, []),
                "pool",
                float(self.opts[OPT_POOL_POWER]),
                5,
                "managed",
            )
        )
        profiles.extend(
            self._profiles_from_entities(
                data.get(CONF_DEHUMIDIFIER_SWITCHES, []),
                data.get(CONF_DEHUMIDIFIER_POWER_SENSORS, []),
                "dehumidifier",
                float(self.opts[OPT_DEHUMIDIFIER_POWER]),
                20,
                "managed",
            )
        )
        profiles.extend(
            self._profiles_from_entities(
                data.get(CONF_START_ONLY_APPLIANCE_SWITCHES, []),
                data.get(CONF_START_ONLY_APPLIANCE_POWER_SENSORS, []),
                "appliance",
                float(self.opts[OPT_START_ONLY_APPLIANCE_POWER]),
                60,
                "start_only",
            )
        )
        deduped: dict[str, LoadProfile] = {}
        for profile in profiles:
            deduped[profile.entity_id] = profile
        return list(deduped.values())

    def _profiles_from_entities(
        self,
        entity_ids: list[str],
        power_sensors: list[str],
        category: str,
        fallback_power: float,
        priority: int,
        control_mode: str,
    ) -> list[LoadProfile]:
        profiles: list[LoadProfile] = []
        for index, entity_id in enumerate(entity_ids):
            power_sensor = power_sensors[index] if index < len(power_sensors) else None
            profiles.append(
                LoadProfile(
                    entity_id=entity_id,
                    name=entity_id,
                    category=category,
                    estimated_power=fallback_power,
                    actual_power=self._positive_float_state(power_sensor),
                    priority=priority,
                    control_mode=control_mode,
                    is_on=self.hass.states.is_state(entity_id, STATE_ON),
                )
            )
        return profiles

    def _ac_battery_profiles(self) -> list[AcBatteryProfile]:
        profiles: list[AcBatteryProfile] = []
        for index, item in enumerate(self._json_items(self.config_entry.data.get(CONF_AC_BATTERY_PROFILES))):
            name = str(item.get("name") or f"AC Akku {index + 1}")
            soc_sensor = str(item.get("soc_sensor") or "").strip()
            charge_number = str(item.get("charge_power_number") or "").strip()
            discharge_number = str(item.get("discharge_power_number") or "").strip()
            if not soc_sensor or not charge_number or not discharge_number:
                continue
            profiles.append(
                AcBatteryProfile(
                    name=name,
                    soc_sensor=soc_sensor,
                    charge_power_sensor=item.get("charge_power_sensor"),
                    discharge_power_sensor=item.get("discharge_power_sensor"),
                    charge_power_number=charge_number,
                    discharge_power_number=discharge_number,
                    min_soc=max(0.0, self._safe_float(item.get("min_soc"), 15.0)),
                    max_soc=max(0.0, self._safe_float(item.get("max_soc"), 90.0)),
                    max_charge_power=max(0.0, self._safe_float(item.get("max_charge_power"), 800.0)),
                    max_discharge_power=max(0.0, self._safe_float(item.get("max_discharge_power"), 800.0)),
                    step_power=max(1.0, self._safe_float(item.get("step_power"), 10.0)),
                    control_interval=max(5.0, self._safe_float(item.get("control_interval_seconds"), 30.0)),
                    direction_switch_delay=max(0.0, self._safe_float(item.get("direction_switch_delay_seconds"), 1.0)),
                    priority=int(self._safe_float(item.get("priority"), 50 + index)),
                    soc=self._float_state(soc_sensor, None),
                    charge_power=self._positive_float_state(item.get("charge_power_sensor")) or 0.0,
                    discharge_power=self._positive_float_state(item.get("discharge_power_sensor")) or 0.0,
                )
            )
        return profiles

    def _ac_battery_details(self, profiles: list[AcBatteryProfile]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for profile in profiles:
            runtime = self._ac_battery_runtime_state.get(profile.name, {})
            rows.append(
                {
                    "name": profile.name,
                    "soc": profile.soc,
                    "charge_power": profile.charge_power,
                    "discharge_power": profile.discharge_power,
                    "target_charge": runtime.get("target_charge", 0.0),
                    "target_discharge": runtime.get("target_discharge", 0.0),
                    "reason": runtime.get("reason")
                    or self._txt("Wartet auf Regelung.", "Waiting for control."),
                }
            )
        return rows

    def _ac_battery_summary(self, rows: list[dict[str, Any]]) -> str:
        if not rows:
            return self._txt(
                "Kein steuerbarer AC-Akku konfiguriert.",
                "No controllable AC battery configured.",
            )
        return self._txt(
            f"{len(rows)} AC-Akku(s) konfiguriert.",
            f"{len(rows)} AC battery/batteries configured.",
        )

    def _localized_ac_reason(self, name: str, reason: str) -> str:
        mapping = {
            "AC battery has no SoC": self._txt(
                f"{name}: kein SoC verfügbar.", f"{name}: no SoC available."
            ),
            "night discharge blocked by minimum SoC": self._txt(
                f"{name}: Nachtentladung durch Mindest-SoC blockiert.",
                f"{name}: night discharge blocked by minimum SoC.",
            ),
            "fixed night discharge": self._txt(
                f"{name}: feste Nachtentladung für die Grundlast.",
                f"{name}: fixed night discharge for base load.",
            ),
            "AC battery will not charge while grid import is present": self._txt(
                f"{name}: lädt nicht bei Netzbezug.",
                f"{name}: does not charge during grid import.",
            ),
            "PV battery has priority before AC battery charging": self._txt(
                f"{name}: PV-Batterie hat Vorrang.",
                f"{name}: PV battery has priority.",
            ),
            "AC battery max SoC reached": self._txt(
                f"{name}: max. SoC erreicht.", f"{name}: max SoC reached."
            ),
            "no usable surplus for AC battery charging": self._txt(
                f"{name}: kein nutzbarer Überschuss.",
                f"{name}: no usable surplus.",
            ),
            "charging from BKW/PV export surplus": self._txt(
                f"{name}: lädt aus BKW-/PV-Exportüberschuss.",
                f"{name}: charging from BKW/PV export surplus.",
            ),
        }
        return mapping.get(reason, f"{name}: {reason}")

    def _strict_options(self) -> StrictSurplusOptions:
        opts = self.opts
        return StrictSurplusOptions(
            grid_tolerance_w=float(opts[OPT_GRID_TOLERANCE_W]),
            pv_battery_ac_charge_threshold_soc=float(
                opts[OPT_PV_BATTERY_AC_CHARGE_THRESHOLD_SOC]
            ),
            manual_pause_hours=float(opts[OPT_MANUAL_PAUSE_HOURS]),
            ac_battery_night_discharge_w=float(opts[OPT_AC_BATTERY_NIGHT_DISCHARGE_W]),
            ac_battery_night_start=self._time_option(
                str(opts[OPT_AC_BATTERY_NIGHT_START]), time(22, 0)
            ),
            ac_battery_night_end=self._time_option(
                str(opts[OPT_AC_BATTERY_NIGHT_END]), time(6, 0)
            ),
        )

    def _grid_flow(self, data: dict[str, Any], legacy_grid_power: float) -> tuple[float, float]:
        import_power = self._positive_sum(data.get(CONF_GRID_IMPORT_POWER_SENSORS, []))
        export_power = self._positive_sum(data.get(CONF_GRID_EXPORT_POWER_SENSORS, []))
        for entity_id in data.get(CONF_GRID_SIGNED_IMPORT_POSITIVE_SENSORS, []):
            value = self._float_state(entity_id, 0.0)
            import_power += max(0.0, value)
            export_power += max(0.0, -value)
        for entity_id in data.get(CONF_GRID_SIGNED_EXPORT_POSITIVE_SENSORS, []):
            value = self._float_state(entity_id, 0.0)
            export_power += max(0.0, value)
            import_power += max(0.0, -value)
        if import_power > 0 or export_power > 0:
            return import_power, export_power
        return max(0.0, legacy_grid_power), max(0.0, -legacy_grid_power)

    def _battery_soc_min(self) -> float | None:
        values = [
            self._float_state(entity_id, None)
            for entity_id in self.config_entry.data.get(CONF_BATTERY_SOC_SENSORS, [])
        ]
        values = [value for value in values if value is not None]
        return min(values) if values else None

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
            return float(str(state).replace(",", "."))
        except (TypeError, ValueError):
            return default

    def _positive_float_state(self, entity_id: str | None) -> float | None:
        value = self._float_state(entity_id, None)
        return None if value is None else max(0.0, value)

    def _positive_sum(self, entity_ids: list[str]) -> float:
        return sum(self._positive_float_state(entity_id) or 0.0 for entity_id in entity_ids)

    def _json_items(self, value: Any) -> list[dict[str, Any]]:
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

    def _safe_float(self, value: Any, default: float) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _time_option(self, value: str, default: time) -> time:
        try:
            hour, minute = value.split(":", 1)
            return time(max(0, min(23, int(hour))), max(0, min(59, int(minute))))
        except (TypeError, ValueError):
            return default

    def _parse_datetime(self, value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    def _active_manual_pauses(self) -> dict[str, str]:
        now = datetime.now()
        active: dict[str, str] = {}
        for entity_id, raw_until in list(self._manual_pauses.items()):
            paused_until = self._parse_datetime(raw_until)
            if paused_until is None or paused_until <= now:
                self._manual_pauses.pop(entity_id, None)
                continue
            active[entity_id] = raw_until
        return active

    def _manual_pause_reason(self, entity_id: str) -> str | None:
        paused_until = self._parse_datetime(self._active_manual_pauses().get(entity_id))
        if paused_until is None:
            return None
        return self._txt(
            f"{entity_id} ist bis {paused_until.strftime('%H:%M')} pausiert.",
            f"{entity_id} is paused until {paused_until.strftime('%H:%M')}.",
        )

    def _localized_policy_reason(self, reason: str) -> str:
        if reason == "central release missing":
            return self._txt("Zentrale Freigabe fehlt.", "Central release is missing.")
        if reason == "no controllable surplus loads":
            return self._txt(
                "Keine steuerbaren Verbraucher konfiguriert.",
                "No controllable loads configured.",
            )
        if reason == "all loads blocked by strict guardrails":
            return self._txt(
                "Alle Verbraucher sind blockiert.",
                "All loads are blocked.",
            )
        return reason

    def _add_action(self, title: str, reason: str, kind: str) -> None:
        self._action_history.insert(
            0,
            {
                "time": datetime.now().isoformat(timespec="seconds"),
                "title": title,
                "reason": reason,
                "kind": kind,
            },
        )
        del self._action_history[ACTION_HISTORY_LIMIT:]

    def _safe_action_history(self, value: Any) -> list[dict[str, str]]:
        if not isinstance(value, list):
            return []
        rows: list[dict[str, str]] = []
        for item in value[:ACTION_HISTORY_LIMIT]:
            if isinstance(item, dict):
                rows.append(
                    {
                        "time": str(item.get("time", "")),
                        "title": str(item.get("title", "")),
                        "reason": str(item.get("reason", "")),
                        "kind": str(item.get("kind", "")),
                    }
                )
        return rows

    def _safe_manual_pauses(self, value: Any) -> dict[str, str]:
        if not isinstance(value, dict):
            return {}
        result: dict[str, str] = {}
        now = datetime.now()
        for entity_id, raw_until in value.items():
            paused_until = self._parse_datetime(str(raw_until))
            if isinstance(entity_id, str) and paused_until is not None and paused_until > now:
                result[entity_id] = paused_until.isoformat(timespec="seconds")
        return result

    def _safe_device_runtime_state(self, value: Any) -> dict[str, dict[str, str]]:
        if not isinstance(value, dict):
            return {}
        result: dict[str, dict[str, str]] = {}
        for entity_id, state in value.items():
            if isinstance(entity_id, str) and isinstance(state, dict):
                result[entity_id] = {
                    key: str(raw)
                    for key, raw in state.items()
                    if key in {"last_on", "last_off", "hems_on"} and raw
                }
        return result
