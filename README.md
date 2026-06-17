# BB HEMS

BB HEMS is a slim Home Assistant energy manager for one job:

**release flexible loads only when there is real surplus at the smart meter.**

This v1 line intentionally removes the old broad model with virtual batteries,
weather decisions, learning values, PV forecasts, advanced JSON device profiles,
wallbox control and heat-pump control. PV inverter and PV battery remain in
their own native control loops. BB HEMS observes them and only decides whether
selected loads may run.

## What v1 controls

- Pool pump / pool heating
- Dehumidifier
- Start-only releases for appliances such as dishwasher or washing machine
- AC battery charge/discharge setpoints

## Core rules

- Default grid tolerance: `50 W`
- Pool has first surplus priority
- Dehumidifier runs only on free surplus, not from grid and not from battery
- Start-only appliances are released/started, then not switched off by HEMS
- Manual stop pauses that load for the configured pause duration
- AC battery charges only from BKW/PV export surplus
- AC battery charges only after PV battery SoC reaches the configured threshold
- AC battery uses a fixed night discharge value for base load coverage

## Required inputs

- Smart meter power, either signed or separate import/export sensors
- PV/BKW power sensors
- PV battery SoC
- PV battery discharge power
- Pool/dehumidifier/start-release entities
- Optional power sensors for controlled loads
- Optional AC battery profile

## AC battery profile example

```json
[
  {
    "name": "EcoFlow",
    "soc_sensor": "sensor.ecoflow_soc",
    "charge_power_sensor": "sensor.ecoflow_charge_power",
    "discharge_power_sensor": "sensor.ecoflow_discharge_power",
    "charge_power_number": "number.ecoflow_charge_w",
    "discharge_power_number": "number.ecoflow_discharge_w",
    "min_soc": 15,
    "max_soc": 90,
    "max_charge_power": 800,
    "max_discharge_power": 800,
    "step_power": 10,
    "control_interval_seconds": 30,
    "direction_switch_delay_seconds": 1
  }
]
```

## Main entities

Sensors:

- `sensor.bb_hems_energy_mode`
- `sensor.bb_hems_grid_power`
- `sensor.bb_hems_grid_import_power`
- `sensor.bb_hems_grid_export_power`
- `sensor.bb_hems_pv_power_total`
- `sensor.bb_hems_battery_soc_min`
- `sensor.bb_hems_battery_discharge_total`
- `sensor.bb_hems_available_surplus_budget`
- `sensor.bb_hems_scheduled_surplus_power`

Controls:

- `switch.bb_hems_auto_enabled`
- `switch.bb_hems_dashboard_enabled`
- `select.bb_hems_mode`
- `number.bb_hems_grid_tolerance_w`
- `number.bb_hems_pv_battery_ac_charge_threshold_soc`
- `number.bb_hems_manual_pause_hours`
- `number.bb_hems_ac_battery_night_discharge_w`
- `number.bb_hems_pool_power`
- `number.bb_hems_dehumidifier_power`
- `number.bb_hems_start_only_appliance_power`

Binary sensors:

- `binary_sensor.bb_hems_surplus_available`
- `binary_sensor.bb_hems_flexible_loads_allowed`

## Removed from v1

- Virtual battery
- Weather approval
- PV forecast logic
- PV array/orientation model
- Seasonal learning
- Advanced device profile JSON
- Heating-rod target temperature logic
- Wallbox control
- Heat-pump control
- Comfort/Eco/force-surplus modes

These can return later as separate, explicit modules once the strict surplus
core is stable.
