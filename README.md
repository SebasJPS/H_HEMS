# BB HEMS

Modular Home Energy Management System for Home Assistant.

BB HEMS turns existing Home Assistant sensors and switches into one central energy decision layer. It is designed for homes with balcony power plants, PV inverters, batteries, wallboxes, heat pumps and flexible consumers such as dehumidifiers, boilers or appliances.

![BB HEMS dashboard screenshot](docs/screenshots/dashboard-overview.svg)

## Goals

- Use the sensors you already have in Home Assistant.
- Aggregate multiple PV or balcony power plant sources.
- Support several batteries and use the lowest SoC for conservative protection.
- Provide one central HEMS state instead of repeating the same YAML logic per device.
- Expose settings directly as Home Assistant entities.
- Add a sidebar dashboard that explains what the HEMS is doing and why.
- Prepare the model for many controllable consumers with priorities and categories.

## Current Status

This repository contains an initial custom integration scaffold:

- Config flow for selecting Home Assistant entities.
- Sensors for grid power, PV total, battery minimum SoC, battery discharge, grid tolerance and energy mode.
- Binary sensors for surplus availability, battery protection, weather approval and flexible-load approval.
- Number entities for editable thresholds.
- Select entity for HEMS operating mode.
- Switch entity for enabling or disabling automatic HEMS decisions.
- Direct control of configured flexible loads when the HEMS decision allows or blocks them.
- Sidebar dashboard served by the integration.

The current version calculates central decisions and directly switches configured flexible loads. It does not yet schedule every individual device by priority; that is the next layer.

## System Model

![BB HEMS system model](docs/mockups/system-model.svg)

BB HEMS is split into three layers:

1. **Sources**  
   Grid meter, PV power, balcony power plants, battery SoC, battery discharge, weather and device states.

2. **Controller**  
   Central HEMS logic calculates energy mode, surplus availability, grid tolerance, weather approval and battery protection.

3. **Consumers**  
   Flexible loads, wallboxes, heat pumps and future device categories consume the central HEMS decisions.

## Configuration Preview

![BB HEMS configuration preview](docs/mockups/config-flow.svg)

The integration setup asks for entity IDs. Multiple entities can be entered comma-separated where useful.

Suggested mapping from the original automation:

| HEMS Field | Home Assistant Entity |
|---|---|
| Grid power | `sensor.power_shelly_gesamt` |
| Grid average | `sensor.grid_average_15m` |
| PV power sources | `sensor.shellyplusplugs_b0b21c105338_switch_0_power` |
| PV average | `sensor.pv_average_15m` |
| Battery SoC | `sensor.batterie_geschatzt_soc` |
| Battery discharge | `sensor.batterie_discharge` |
| Weather state | `sensor.berlin_tempelhof_wetterzustand` |
| Cloud coverage | `sensor.berlin_tempelhof_bewolkungsgrad` |
| Sunshine duration | `sensor.berlin_tempelhof_sonnenscheindauer` |
| Flexible loads | `switch.a8m` |

## Entities

### Sensors

- `sensor.bb_hems_energy_mode`
- `sensor.bb_hems_grid_power`
- `sensor.bb_hems_grid_average`
- `sensor.bb_hems_pv_power_total`
- `sensor.bb_hems_pv_average`
- `sensor.bb_hems_battery_soc_min`
- `sensor.bb_hems_battery_discharge_total`
- `sensor.bb_hems_grid_tolerance`
- `sensor.bb_hems_cloud_coverage`
- `sensor.bb_hems_sunshine_minutes`
- `sensor.bb_hems_active_flexible_loads`
- `sensor.bb_hems_configured_assets`

### Binary Sensors

- `binary_sensor.bb_hems_surplus_available`
- `binary_sensor.bb_hems_battery_protect`
- `binary_sensor.bb_hems_good_weather`
- `binary_sensor.bb_hems_flexible_loads_allowed`

### Settings

- `select.bb_hems_mode`
- `switch.bb_hems_auto_enabled`
- `number.bb_hems_min_battery_soc`
- `number.bb_hems_protect_battery_soc`
- `number.bb_hems_pv_threshold`
- `number.bb_hems_pv_avg_threshold`
- `number.bb_hems_grid_import_limit`
- `number.bb_hems_grid_hard_import_limit`
- `number.bb_hems_battery_discharge_limit`

## Operating Modes

| Mode | Behavior |
|---|---|
| `auto` | Balanced default mode. Uses PV, grid, battery and weather logic. |
| `eco` | More conservative. Avoids tolerated grid import where possible. |
| `comfort` | Allows more grid tolerance when the house should favor comfort. |
| `force_surplus` | Treats surplus as available unless battery protection blocks it. |
| `off` | Disables HEMS decisions. |

## Decision Logic

The first controller version evaluates:

- Current grid import/export.
- Optional 15-minute grid average.
- Total PV power from all configured PV sources.
- Optional 15-minute PV average.
- Minimum battery SoC across all configured batteries.
- Total battery discharge.
- Weather state, cloud coverage and sunshine.
- Configured thresholds and operating mode.

The main output is still exposed for dashboards and optional automations:

```yaml
binary_sensor.bb_hems_flexible_loads_allowed
```

Configured flexible loads are switched by the integration itself:

- When `binary_sensor.bb_hems_flexible_loads_allowed` stays on for 10 minutes, configured flexible-load switches are turned on.
- When it stays off for 5 minutes, configured flexible-load switches are turned off.
- When `switch.bb_hems_auto_enabled` is off, BB HEMS does not switch devices automatically.

## Installation

Copy this folder into Home Assistant:

```text
custom_components/bb_hems
```

Restart Home Assistant, then add the integration:

```text
Settings -> Devices & services -> Add integration -> BB HEMS
```

After setup, a `BB HEMS` entry appears in the Home Assistant sidebar.

## Support

Home Health Overview ist kostenlos und bleibt kostenlos.

Home Health Overview is free and will remain free.

[Buy me a coffee](https://buymeacoffee.com/sebasbe)

## Roadmap

- Per-device registry with name, category, switch entity, power estimate, priority, minimum runtime and cooldown.
- Priority scheduler for many flexible loads.
- Dedicated wallbox strategy with charge-current control.
- Heat-pump strategy with comfort bands and thermal buffer support.
- Device-level history: why a device was allowed, blocked, started or stopped.
- Forecast-aware planning for PV windows.
- Import/export cost awareness.
- Native Lovelace cards or a richer frontend panel.

## Development

Basic local checks:

```bash
PYTHONPYCACHEPREFIX=/tmp/bb_hems_pycache python3 -m py_compile custom_components/bb_hems/*.py
python3 -m json.tool custom_components/bb_hems/manifest.json >/dev/null
python3 -m json.tool custom_components/bb_hems/translations/de.json >/dev/null
python3 -m json.tool custom_components/bb_hems/translations/en.json >/dev/null
```
