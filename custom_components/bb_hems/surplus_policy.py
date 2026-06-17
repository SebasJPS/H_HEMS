"""Strict surplus policy for BB HEMS.

This module intentionally has no Home Assistant imports so the core decisions
can be tested without a running HA instance.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import time


@dataclass(frozen=True)
class StrictSurplusOptions:
    """User-facing guardrails for surplus decisions."""

    grid_tolerance_w: float = 50.0
    pv_battery_ac_charge_threshold_soc: float = 80.0
    manual_pause_hours: float = 4.0
    ac_battery_night_discharge_w: float = 120.0
    ac_battery_night_start: time = time(22, 0)
    ac_battery_night_end: time = time(6, 0)


@dataclass(frozen=True)
class SurplusLoad:
    """A load candidate for the strict surplus scheduler."""

    entity_id: str
    name: str
    category: str
    power_w: float
    priority: int
    is_on: bool = False
    is_blocked: bool = False
    block_reason: str | None = None
    allow_battery: bool = False
    allow_grid: bool = False
    start_only: bool = False
    manually_paused: bool = False
    pause_reason: str | None = None


@dataclass(frozen=True)
class ScheduleResult:
    """Result of a strict surplus scheduling pass."""

    scheduled_loads: tuple[str, ...]
    scheduled_power_w: float
    available_budget_w: float
    reason: str


@dataclass(frozen=True)
class AcBatteryDecision:
    """Charge/discharge target for one AC battery."""

    charge_w: float
    discharge_w: float
    reason: str


def strict_surplus_budget(
    *,
    grid_import_w: float,
    grid_export_w: float,
    running_load_power_w: float,
    battery_discharge_w: float,
    options: StrictSurplusOptions,
) -> float:
    """Return load budget that does not rely on battery or meaningful grid import."""
    if grid_import_w > options.grid_tolerance_w:
        return 0.0
    return max(0.0, grid_export_w + running_load_power_w - max(0.0, battery_discharge_w))


def schedule_strict_surplus_loads(
    *,
    loads: list[SurplusLoad],
    allowed: bool,
    grid_import_w: float,
    grid_export_w: float,
    battery_discharge_w: float,
    options: StrictSurplusOptions,
) -> ScheduleResult:
    """Choose loads that fit the strict no-grid/no-battery surplus budget."""
    running_power = sum(load.power_w for load in loads if load.is_on)
    budget = strict_surplus_budget(
        grid_import_w=grid_import_w,
        grid_export_w=grid_export_w,
        running_load_power_w=running_power,
        battery_discharge_w=battery_discharge_w,
        options=options,
    )
    if not allowed:
        return ScheduleResult((), 0.0, budget, "central release missing")
    if grid_import_w > options.grid_tolerance_w:
        return ScheduleResult(
            (),
            0.0,
            budget,
            f"grid import {grid_import_w:.0f} W exceeds tolerance {options.grid_tolerance_w:.0f} W",
        )

    candidates = [
        load
        for load in loads
        if not load.is_blocked
        and not load.manually_paused
        and not load.allow_battery
        and not load.allow_grid
    ]
    if not loads:
        return ScheduleResult((), 0.0, budget, "no controllable surplus loads")
    if not candidates:
        paused = [load.pause_reason for load in loads if load.manually_paused and load.pause_reason]
        blocked = [load.block_reason for load in loads if load.is_blocked and load.block_reason]
        reason = "; ".join(paused + blocked) or "all loads blocked by strict guardrails"
        return ScheduleResult((), 0.0, budget, reason)

    selected: list[SurplusLoad] = []
    used_power = 0.0
    for load in sorted(candidates, key=lambda item: (item.priority, not item.is_on, item.power_w)):
        power = max(0.0, load.power_w)
        startup_margin = 0.0 if load.is_on else options.grid_tolerance_w
        if power <= 0 or used_power + power + startup_margin <= budget:
            selected.append(load)
            used_power += power

    if not selected:
        return ScheduleResult(
            (),
            0.0,
            budget,
            f"surplus budget {budget:.0f} W is not enough for any configured strict load",
        )

    names = ", ".join(load.name for load in selected)
    return ScheduleResult(
        tuple(load.entity_id for load in selected),
        used_power,
        budget,
        f"strict surplus schedules {len(selected)} load(s) with {used_power:.0f} W: {names}",
    )


def ac_battery_target(
    *,
    soc: float | None,
    min_soc: float,
    max_soc: float,
    max_charge_power_w: float,
    max_discharge_power_w: float,
    step_power_w: float,
    surplus_budget_w: float,
    grid_import_w: float,
    pv_battery_soc: float | None,
    now: time,
    options: StrictSurplusOptions,
) -> AcBatteryDecision:
    """Return AC battery targets for BKW/PV buffering and fixed night discharge."""
    if soc is None:
        return AcBatteryDecision(0.0, 0.0, "AC battery has no SoC")
    if _in_time_window(now, options.ac_battery_night_start, options.ac_battery_night_end):
        if soc <= min_soc:
            return AcBatteryDecision(0.0, 0.0, "night discharge blocked by minimum SoC")
        target = _round_power(
            min(options.ac_battery_night_discharge_w, max_discharge_power_w),
            step_power_w,
        )
        return AcBatteryDecision(0.0, target, "fixed night discharge")
    if grid_import_w > options.grid_tolerance_w:
        return AcBatteryDecision(0.0, 0.0, "AC battery will not charge while grid import is present")
    if pv_battery_soc is None or pv_battery_soc < options.pv_battery_ac_charge_threshold_soc:
        return AcBatteryDecision(
            0.0,
            0.0,
            "PV battery has priority before AC battery charging",
        )
    if soc >= max_soc:
        return AcBatteryDecision(0.0, 0.0, "AC battery max SoC reached")
    if surplus_budget_w <= options.grid_tolerance_w:
        return AcBatteryDecision(0.0, 0.0, "no usable surplus for AC battery charging")
    target = _round_power(min(surplus_budget_w, max_charge_power_w), step_power_w)
    return AcBatteryDecision(target, 0.0, "charging from BKW/PV export surplus")


def _round_power(value: float, step: float) -> float:
    if step <= 0:
        return max(0.0, value)
    return max(0.0, round(value / step) * step)


def _in_time_window(value: time, start: time, end: time) -> bool:
    if start <= end:
        return start <= value < end
    return value >= start or value < end
