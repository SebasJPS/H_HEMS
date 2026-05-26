"""Coordinator and decision model for BB HEMS."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_OFF, STATE_ON, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    BAD_WEATHER,
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
    CONF_PV_AVERAGE_SENSOR,
    CONF_PV_POWER_SENSORS,
    CONF_SUNSHINE_SENSOR,
    CONF_WALLBOX_SWITCHES,
    CONF_WEATHER_STATE_SENSOR,
    DEFAULTS,
    DOMAIN,
    GOOD_WEATHER,
    MODE_AUTO,
    MODE_COMFORT,
    MODE_ECO,
    MODE_FORCE_SURPLUS,
    MODE_OFF,
    OPT_AUTO_ENABLED,
    OPT_BATTERY_DISCHARGE_LIMIT,
    OPT_DASHBOARD_ENABLED,
    OPT_FLEXIBLE_LOAD_POWER,
    OPT_GRID_HARD_IMPORT_LIMIT,
    OPT_GRID_IMPORT_LIMIT,
    OPT_HEATING_ROD_POWER,
    OPT_MIN_BATTERY_SOC,
    OPT_MODE,
    OPT_PROTECT_BATTERY_SOC,
    OPT_PV_AVG_THRESHOLD,
    OPT_PV_THRESHOLD,
    OPT_RESPONSE_PROFILE,
    RESPONSE_AUTO,
    RESPONSE_MINUTES,
    RESPONSE_REALTIME,
    RESPONSE_SECONDS,
    SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class LoadProfile:
    """A controllable surplus load with a simple smart scheduling profile."""

    entity_id: str
    category: str
    estimated_power: float
    actual_power: float | None
    power_sensor: str | None
    priority: int
    is_on: bool

    @property
    def scheduling_power(self) -> float:
        """Return the best available power value for scheduling."""
        if self.is_on and self.actual_power is not None and self.actual_power > 0:
            return self.actual_power
        return self.estimated_power


@dataclass(frozen=True)
class HemsData:
    """Computed HEMS state."""

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
    configured_heating_rods: int
    response_profile: str
    switch_on_delay_seconds: int
    switch_off_delay_seconds: int
    available_surplus_budget: float
    scheduled_surplus_loads: tuple[str, ...]
    scheduled_surplus_power: float
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

    async def _async_update_data(self) -> HemsData:
        data = self._calculate()
        action_added = await self._async_apply_flexible_load_control(data)
        if action_added:
            return replace(data, action_history=list(self._action_history))
        return data

    @property
    def opts(self) -> dict[str, Any]:
        """Return options with defaults."""
        return {**DEFAULTS, **dict(self.config_entry.options)}

    async def async_set_option(self, key: str, value: Any) -> None:
        """Persist an option and refresh entities."""
        options = dict(self.config_entry.options)
        previous = options.get(key, DEFAULTS.get(key))
        options[key] = value
        self._add_action(
            "Einstellung geändert",
            f"{self._option_label(key)}: {previous} -> {value}",
            "manual",
        )
        self.hass.config_entries.async_update_entry(self.config_entry, options=options)
        await self.async_request_refresh()

    def _calculate(self) -> HemsData:
        data = self.config_entry.data
        opts = self.opts

        grid_power = self._float_state(data.get(CONF_GRID_POWER_SENSOR), 0.0)
        grid_average = self._float_state(
            data.get(CONF_GRID_AVERAGE_SENSOR), grid_power
        )
        pv_sources = data.get(CONF_PV_POWER_SENSORS, [])
        battery_soc_sources = data.get(CONF_BATTERY_SOC_SENSORS, [])
        battery_discharge_sources = data.get(CONF_BATTERY_DISCHARGE_SENSORS, [])
        flexible_loads = data.get(CONF_FLEXIBLE_LOAD_SWITCHES, [])
        wallboxes = data.get(CONF_WALLBOX_SWITCHES, [])
        heat_pumps = data.get(CONF_HEAT_PUMP_SWITCHES, [])
        heating_rods = data.get(CONF_HEATING_ROD_SWITCHES, [])
        controlled_loads = self._controlled_surplus_load_profiles()

        pv_power = sum(self._float_state(entity_id, 0.0) for entity_id in pv_sources)
        pv_average = self._float_state(data.get(CONF_PV_AVERAGE_SENSOR), pv_power)
        battery_socs = [
            self._float_state(entity_id, None) for entity_id in battery_soc_sources
        ]
        battery_socs = [value for value in battery_socs if value is not None]
        battery_soc_min = min(battery_socs) if battery_socs else None
        battery_discharge = sum(
            self._float_state(entity_id, 0.0)
            for entity_id in battery_discharge_sources
        )

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
        grid_tolerance = self._grid_tolerance(battery_soc_min, good_weather)

        auto_enabled = bool(opts[OPT_AUTO_ENABLED])
        mode = opts[OPT_MODE]
        battery_protect = self._battery_protect(
            battery_soc_min, battery_discharge, bad_weather
        )

        if mode == MODE_OFF or not auto_enabled:
            surplus_available = False
            flexible_loads_allowed = False
            energy_mode = "off"
            surplus_reason = "Automatik oder HEMS-Modus ist ausgeschaltet."
            load_reason = "Flexible Verbraucher sind gesperrt, weil HEMS ausgeschaltet ist."
        elif mode == MODE_FORCE_SURPLUS:
            surplus_available = True
            flexible_loads_allowed = not battery_protect
            energy_mode = "force_surplus" if flexible_loads_allowed else "battery_protect"
            surplus_reason = "Modus force_surplus erzwingt die Überschussfreigabe."
            load_reason = (
                "Flexible Verbraucher sind erlaubt, weil force_surplus aktiv ist."
                if flexible_loads_allowed
                else "Flexible Verbraucher bleiben trotz force_surplus gesperrt, weil Batterieschutz aktiv ist."
            )
        else:
            pv_threshold = float(opts[OPT_PV_THRESHOLD])
            pv_avg_threshold = float(opts[OPT_PV_AVG_THRESHOLD])
            grid_limit = self._mode_grid_limit(mode, grid_tolerance)
            surplus_available = (
                pv_power >= pv_threshold
                and pv_average >= pv_avg_threshold
                and (grid_power <= grid_limit or (grid_average < 50 and good_weather))
            )
            surplus_reason = self._surplus_reason(
                pv_power,
                pv_average,
                grid_power,
                grid_average,
                grid_limit,
                pv_threshold,
                pv_avg_threshold,
                good_weather,
                surplus_available,
            )
            flexible_loads_allowed = (
                surplus_available
                and good_weather
                and not battery_protect
                and self._battery_soc_ok(battery_soc_min)
            )
            load_reason = self._load_reason(
                surplus_available,
                good_weather,
                battery_protect,
                battery_soc_min,
                flexible_loads_allowed,
            )
            energy_mode = self._energy_mode(
                mode,
                grid_power,
                pv_power,
                surplus_available,
                battery_protect,
                good_weather,
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
            )
        )
        switch_on_delay, switch_off_delay = self._response_delays(
            battery_protect=battery_protect,
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
            pv_power=pv_power,
            pv_average=pv_average,
            battery_soc_min=battery_soc_min,
            battery_discharge=battery_discharge,
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
            configured_batteries=len(battery_soc_sources),
            configured_flexible_loads=len(flexible_loads),
            configured_wallboxes=len(wallboxes),
            configured_heat_pumps=len(heat_pumps),
            configured_heating_rods=len(heating_rods),
            response_profile=str(opts[OPT_RESPONSE_PROFILE]),
            switch_on_delay_seconds=int(switch_on_delay.total_seconds()),
            switch_off_delay_seconds=int(switch_off_delay.total_seconds()),
            available_surplus_budget=available_budget,
            scheduled_surplus_loads=scheduled_loads,
            scheduled_surplus_power=scheduled_power,
            scheduler_reason=scheduler_reason,
            weather_reason=weather_reason,
            surplus_reason=surplus_reason,
            battery_reason=self._battery_reason(
                battery_soc_min, battery_discharge, bad_weather, battery_protect
            ),
            load_reason=load_reason,
            action_history=list(self._action_history),
        )

    async def _async_apply_flexible_load_control(self, data: HemsData) -> bool:
        """Switch configured flexible loads according to the current HEMS decision."""
        opts = self.opts
        if not bool(opts[OPT_AUTO_ENABLED]):
            return False

        target_on = data.flexible_loads_allowed and bool(data.scheduled_surplus_loads)
        if not self._flexible_load_decision_is_stable(target_on, data):
            return False

        desired_on = set(data.scheduled_surplus_loads) if target_on else set()
        flexible_loads = self._controlled_surplus_load_profiles()
        action_added = False

        for load in flexible_loads:
            entity_id = load.entity_id
            should_be_on = entity_id in desired_on
            service = "turn_on" if should_be_on else "turn_off"
            desired_state = STATE_ON if should_be_on else STATE_OFF
            state = self.hass.states.get(load.entity_id)
            if state is None or state.state in {
                desired_state,
                STATE_UNAVAILABLE,
                STATE_UNKNOWN,
            }:
                continue

            domain = entity_id.split(".", 1)[0]
            if domain not in {"switch", "input_boolean"}:
                continue

            await self.hass.services.async_call(
                domain,
                service,
                {"entity_id": entity_id},
                blocking=False,
            )
            self._add_action(
                "Verbraucher geschaltet",
                f"{entity_id} wurde {'eingeschaltet' if should_be_on else 'ausgeschaltet'}. {data.scheduler_reason}",
                "device",
            )
            action_added = True

        return action_added

    def _controlled_surplus_load_profiles(self) -> list[LoadProfile]:
        """Return all loads controlled by the smart surplus scheduler."""
        data = self.config_entry.data
        opts = self.opts
        flexible_power = float(opts[OPT_FLEXIBLE_LOAD_POWER])
        heating_rod_power = float(opts[OPT_HEATING_ROD_POWER])
        flexible_power_sensors = data.get(CONF_FLEXIBLE_LOAD_POWER_SENSORS, [])
        heating_rod_power_sensors = data.get(CONF_HEATING_ROD_POWER_SENSORS, [])

        profiles: list[LoadProfile] = []
        for index, entity_id in enumerate(data.get(CONF_FLEXIBLE_LOAD_SWITCHES, [])):
            power_sensor = self._matching_entity(flexible_power_sensors, index)
            profiles.append(
                LoadProfile(
                    entity_id=entity_id,
                    category="flexible_load",
                    estimated_power=flexible_power,
                    actual_power=self._positive_float_state(power_sensor),
                    power_sensor=power_sensor,
                    priority=10,
                    is_on=self.hass.states.is_state(entity_id, STATE_ON),
                )
            )
        for index, entity_id in enumerate(data.get(CONF_HEATING_ROD_SWITCHES, [])):
            power_sensor = self._matching_entity(heating_rod_power_sensors, index)
            profiles.append(
                LoadProfile(
                    entity_id=entity_id,
                    category="heating_rod",
                    estimated_power=heating_rod_power,
                    actual_power=self._positive_float_state(power_sensor),
                    power_sensor=power_sensor,
                    priority=30,
                    is_on=self.hass.states.is_state(entity_id, STATE_ON),
                )
            )
        return profiles

    def _matching_entity(self, entity_ids: list[str], index: int) -> str | None:
        """Return the same-position entity from a parallel entity list."""
        if index >= len(entity_ids):
            return None
        return entity_ids[index]

    def _schedule_surplus_loads(
        self,
        loads: list[LoadProfile],
        allowed: bool,
        grid_power: float,
        battery_discharge: float,
    ) -> tuple[tuple[str, ...], float, float, str]:
        """Select the loads that fit into the current surplus budget."""
        active_power = sum(load.scheduling_power for load in loads if load.is_on)
        current_export = max(0.0, -grid_power)
        budget = max(0.0, current_export + active_power - max(0.0, battery_discharge))
        if not allowed:
            return (), 0.0, budget, "Smart Scheduler blockiert alle Überschussverbraucher, weil die zentrale HEMS-Freigabe fehlt."
        if not loads:
            return (), 0.0, budget, "Smart Scheduler hat keine schaltbaren Überschussverbraucher konfiguriert."

        selected: list[LoadProfile] = []
        used_power = 0.0
        for load in sorted(loads, key=lambda item: (item.priority, not item.is_on, item.estimated_power)):
            load_power = load.scheduling_power
            if load_power <= 0 or used_power + load_power <= budget:
                selected.append(load)
                used_power += load_power

        if not selected:
            return (), 0.0, budget, f"Smart Scheduler wartet: echtes Überschussbudget {budget:.0f} W reicht für keinen konfigurierten Verbraucher. Export {current_export:.0f} W, laufende Lasten {active_power:.0f} W, Batterieentladung {battery_discharge:.0f} W."

        names = ", ".join(load.entity_id for load in selected)
        return (
            tuple(load.entity_id for load in selected),
            used_power,
            budget,
            f"Smart Scheduler plant {len(selected)} Verbraucher mit ca. {used_power:.0f} W: {names}. Echtes Überschussbudget: {budget:.0f} W (Export {current_export:.0f} W + laufende Lasten {active_power:.0f} W - Batterieentladung {battery_discharge:.0f} W).",
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
        self._action_history.insert(
            0,
            {
                "time": datetime.now().isoformat(timespec="seconds"),
                "title": title,
                "reason": reason,
                "kind": kind,
            },
        )
        del self._action_history[10:]

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
            self._add_action("HEMS bewertet", load_reason, energy_mode)
            return

        if previous["energy_mode"] != energy_mode:
            self._add_action(
                "Modus geändert",
                f"{previous['energy_mode']} -> {energy_mode}. {load_reason}",
                energy_mode,
            )
        if previous["flexible_loads_allowed"] != flexible_loads_allowed:
            self._add_action(
                "Flexible Verbraucher freigegeben"
                if flexible_loads_allowed
                else "Flexible Verbraucher gesperrt",
                load_reason,
                "allow" if flexible_loads_allowed else "block",
            )
        if previous["battery_protect"] != battery_protect:
            self._add_action(
                "Batterieschutz aktiv" if battery_protect else "Batterieschutz beendet",
                load_reason,
                "protect" if battery_protect else "allow",
            )
        if (
            previous["active_flexible_loads"] != active_flexible_loads
            or previous["active_flexible_entities"] != tuple(active_flexible_entities)
        ):
            active = ", ".join(active_flexible_entities) or "keiner"
            self._add_action(
                "Verbraucherstatus geändert",
                f"{active_flexible_loads} aktive flexible Verbraucher: {active}.",
                "device",
            )

    def _option_label(self, key: str) -> str:
        """Return a readable option label for the dashboard history."""
        return {
            OPT_AUTO_ENABLED: "Automatik",
            OPT_BATTERY_DISCHARGE_LIMIT: "Entladegrenze Batterie",
            OPT_DASHBOARD_ENABLED: "Dashboard",
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
        }.get(key, key)

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

    def _positive_float_state(self, entity_id: str | None) -> float | None:
        value = self._float_state(entity_id, None)
        if value is None:
            return None
        return max(0.0, value)

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
            return f"Batterie-SoC {battery_soc:.1f}% ist mindestens 90%, Wetter wird großzügig freigegeben."
        if weather is None:
            return "Kein Wetterzustand konfiguriert oder verfügbar; Wetter blockiert deshalb nicht."

        weather_ok = weather in GOOD_WEATHER
        cloud_value = clouds if clouds is not None else 0
        sunshine_value = sunshine if sunshine is not None else 999

        if battery_soc is not None and battery_soc >= 75:
            if weather_ok and cloud_value < 85:
                return f"Wetter '{weather}' ist freigegeben und Bewölkung {cloud_value:.1f}% liegt unter 85%."
            return f"Wetter hält zurück: Zustand '{weather}', Bewölkung {cloud_value:.1f}% bei SoC {battery_soc:.1f}%. Erlaubt wären freigegebenes Wetter und unter 85% Bewölkung."

        if weather_ok and cloud_value < 70 and sunshine_value > 20:
            return f"Wetter '{weather}', Bewölkung {cloud_value:.1f}% unter 70% und Sonne {sunshine_value:.1f} min über 20 min."
        return f"Wetter hält zurück: Zustand '{weather}', Bewölkung {cloud_value:.1f}% und Sonne {sunshine_value:.1f} min. Bei SoC unter 75% braucht BB HEMS gutes Wetter, unter 70% Bewölkung und über 20 min Sonne."

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
        if battery_soc is not None and battery_soc < float(opts[OPT_PROTECT_BATTERY_SOC]):
            return True
        discharge_limit = float(opts[OPT_BATTERY_DISCHARGE_LIMIT])
        if discharge_limit <= 0 and battery_discharge > 0:
            return True
        if discharge_limit > 0 and battery_discharge >= discharge_limit:
            return True
        return bool(bad_weather and battery_soc is not None and battery_soc < 70)

    def _battery_reason(
        self,
        battery_soc: float | None,
        battery_discharge: float,
        bad_weather: bool,
        battery_protect: bool,
    ) -> str:
        opts = self.opts
        protect_soc = float(opts[OPT_PROTECT_BATTERY_SOC])
        discharge_limit = float(opts[OPT_BATTERY_DISCHARGE_LIMIT])
        if battery_soc is not None and battery_soc < protect_soc:
            return f"Batterieschutz aktiv: SoC {battery_soc:.1f}% liegt unter Schutzgrenze {protect_soc:.1f}%."
        if discharge_limit <= 0 and battery_discharge > 0:
            return f"Batterieschutz aktiv: Batterie entlädt mit {battery_discharge:.1f} W; die Entladegrenze ist auf 0 W gesetzt."
        if discharge_limit > 0 and battery_discharge >= discharge_limit:
            return f"Batterieschutz aktiv: Batterie entlädt mit {battery_discharge:.1f} W und erreicht die Grenze {discharge_limit:.1f} W."
        if bad_weather and battery_soc is not None and battery_soc < 70:
            return f"Batterieschutz aktiv: schlechtes Wetter und SoC {battery_soc:.1f}% unter 70%."
        if battery_protect:
            return "Batterieschutz ist aktiv."
        return f"Kein Batterieschutz: SoC {battery_soc if battery_soc is not None else 'n/a'}%, Entladung {battery_discharge:.1f} W."

    def _battery_soc_ok(self, battery_soc: float | None) -> bool:
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
        good_weather: bool,
        surplus_available: bool,
    ) -> str:
        if surplus_available:
            return f"Überschuss erfüllt: PV {pv_power:.1f} W >= {pv_threshold:.1f} W, PV 15 min {pv_average:.1f} W >= {pv_avg_threshold:.1f} W und Netz {grid_power:.1f} W <= {grid_limit:.1f} W oder Netzmittel {grid_average:.1f} W < 50 W bei Wetterfreigabe."
        missing: list[str] = []
        if pv_power < pv_threshold:
            missing.append(f"PV aktuell {pv_power:.1f} W unter {pv_threshold:.1f} W")
        if pv_average < pv_avg_threshold:
            missing.append(f"PV 15 min {pv_average:.1f} W unter {pv_avg_threshold:.1f} W")
        if not (grid_power <= grid_limit or (grid_average < 50 and good_weather)):
            missing.append(f"Netz {grid_power:.1f} W über Limit {grid_limit:.1f} W und Netzmittel {grid_average:.1f} W nicht als Ausgleich nutzbar")
        return "Überschuss fehlt: " + "; ".join(missing)

    def _load_reason(
        self,
        surplus_available: bool,
        good_weather: bool,
        battery_protect: bool,
        battery_soc: float | None,
        flexible_loads_allowed: bool,
    ) -> str:
        if flexible_loads_allowed:
            return "Flexible Verbraucher sind erlaubt, weil Überschuss, Wetterfreigabe, SoC und Batterieschutz passen."
        blockers: list[str] = []
        if not surplus_available:
            blockers.append("kein Überschuss")
        if not good_weather:
            blockers.append("keine Wetterfreigabe")
        if battery_protect:
            blockers.append("Batterieschutz aktiv")
        if not self._battery_soc_ok(battery_soc):
            blockers.append(f"SoC {battery_soc:.1f}% unter Mindest-SoC {float(self.opts[OPT_MIN_BATTERY_SOC]):.1f}%")
        return "Flexible Verbraucher gesperrt: " + ", ".join(blockers)

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
