"""Tests for the strict BB HEMS surplus policy."""

from __future__ import annotations

from datetime import time
import importlib.util
from pathlib import Path
import sys
import unittest

POLICY_PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "bb_hems"
    / "surplus_policy.py"
)
SPEC = importlib.util.spec_from_file_location("bb_hems_surplus_policy", POLICY_PATH)
surplus_policy = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = surplus_policy
SPEC.loader.exec_module(surplus_policy)

StrictSurplusOptions = surplus_policy.StrictSurplusOptions
SurplusLoad = surplus_policy.SurplusLoad
ac_battery_target = surplus_policy.ac_battery_target
schedule_strict_surplus_loads = surplus_policy.schedule_strict_surplus_loads


class StrictSurplusPolicyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.options = StrictSurplusOptions()

    def test_pool_runs_when_export_exceeds_power_plus_tolerance(self) -> None:
        result = schedule_strict_surplus_loads(
            loads=[
                SurplusLoad(
                    "switch.pool",
                    "Pool",
                    "pool",
                    1000,
                    5,
                    allow_battery=False,
                )
            ],
            allowed=True,
            grid_import_w=0,
            grid_export_w=1060,
            battery_discharge_w=0,
            options=self.options,
        )

        self.assertEqual(result.scheduled_loads, ("switch.pool",))
        self.assertEqual(result.scheduled_power_w, 1000)

    def test_pool_stops_when_grid_import_exceeds_tolerance(self) -> None:
        result = schedule_strict_surplus_loads(
            loads=[SurplusLoad("switch.pool", "Pool", "pool", 1000, 5)],
            allowed=True,
            grid_import_w=80,
            grid_export_w=0,
            battery_discharge_w=0,
            options=self.options,
        )

        self.assertEqual(result.scheduled_loads, ())
        self.assertIn("exceeds tolerance", result.reason)

    def test_pool_waits_without_startup_tolerance_margin(self) -> None:
        result = schedule_strict_surplus_loads(
            loads=[SurplusLoad("switch.pool", "Pool", "pool", 1000, 5)],
            allowed=True,
            grid_import_w=0,
            grid_export_w=1040,
            battery_discharge_w=0,
            options=self.options,
        )

        self.assertEqual(result.scheduled_loads, ())

    def test_dehumidifier_does_not_use_battery_or_grid(self) -> None:
        result = schedule_strict_surplus_loads(
            loads=[
                SurplusLoad(
                    "switch.dehumidifier",
                    "Lufttrockner",
                    "dehumidifier",
                    300,
                    20,
                    allow_battery=False,
                )
            ],
            allowed=True,
            grid_import_w=0,
            grid_export_w=500,
            battery_discharge_w=250,
            options=self.options,
        )

        self.assertEqual(result.scheduled_loads, ())
        self.assertLess(result.available_budget_w, 300)

    def test_ac_battery_does_not_charge_below_pv_battery_threshold(self) -> None:
        decision = ac_battery_target(
            soc=40,
            min_soc=15,
            max_soc=90,
            max_charge_power_w=800,
            max_discharge_power_w=800,
            step_power_w=10,
            surplus_budget_w=500,
            grid_import_w=0,
            pv_battery_soc=79,
            now=time(12, 0),
            options=self.options,
        )

        self.assertEqual(decision.charge_w, 0)
        self.assertEqual(decision.discharge_w, 0)

    def test_ac_battery_never_charges_while_importing_grid(self) -> None:
        decision = ac_battery_target(
            soc=40,
            min_soc=15,
            max_soc=90,
            max_charge_power_w=800,
            max_discharge_power_w=800,
            step_power_w=10,
            surplus_budget_w=500,
            grid_import_w=80,
            pv_battery_soc=90,
            now=time(12, 0),
            options=self.options,
        )

        self.assertEqual(decision.charge_w, 0)
        self.assertIn("grid import", decision.reason)

    def test_ac_battery_uses_fixed_night_discharge(self) -> None:
        decision = ac_battery_target(
            soc=60,
            min_soc=15,
            max_soc=90,
            max_charge_power_w=800,
            max_discharge_power_w=800,
            step_power_w=10,
            surplus_budget_w=0,
            grid_import_w=0,
            pv_battery_soc=90,
            now=time(23, 0),
            options=self.options,
        )

        self.assertEqual(decision.charge_w, 0)
        self.assertEqual(decision.discharge_w, 120)

    def test_start_only_appliance_gets_release_but_is_not_specially_stopped(self) -> None:
        result = schedule_strict_surplus_loads(
            loads=[
                SurplusLoad(
                    "button.dishwasher",
                    "Geschirrspueler",
                    "appliance",
                    1200,
                    60,
                    start_only=True,
                )
            ],
            allowed=True,
            grid_import_w=0,
            grid_export_w=1300,
            battery_discharge_w=0,
            options=self.options,
        )

        self.assertEqual(result.scheduled_loads, ("button.dishwasher",))

    def test_manual_pause_blocks_load_for_policy_pass(self) -> None:
        result = schedule_strict_surplus_loads(
            loads=[
                SurplusLoad(
                    "switch.pool",
                    "Pool",
                    "pool",
                    1000,
                    5,
                    manually_paused=True,
                    pause_reason="paused for 4 h",
                )
            ],
            allowed=True,
            grid_import_w=0,
            grid_export_w=1500,
            battery_discharge_w=0,
            options=self.options,
        )

        self.assertEqual(result.scheduled_loads, ())
        self.assertIn("paused", result.reason)


if __name__ == "__main__":
    unittest.main()
