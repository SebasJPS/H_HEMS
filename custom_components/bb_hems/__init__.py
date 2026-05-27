"""BB Home Energy Management System integration."""

from __future__ import annotations

import json
from pathlib import Path

from homeassistant.components import frontend
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DEFAULTS, NAME, OPT_DASHBOARD_ENABLED, PANEL_URL, PLATFORMS
from .coordinator import HemsCoordinator

PANEL_COMPONENT_NAME = "bb-hems-panel"
STATIC_URL = "/api/bb_hems/static"
MANIFEST_PATH = Path(__file__).parent / "manifest.json"


def _frontend_version() -> str:
    """Return the integration version for frontend cache busting."""
    try:
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8")).get(
            "version", "dev"
        )
    except (OSError, json.JSONDecodeError):
        return "dev"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up BB HEMS from a config entry."""
    coordinator = HemsCoordinator(hass, entry)
    await coordinator.async_load_learning()
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    if {**DEFAULTS, **dict(entry.options)}[OPT_DASHBOARD_ENABLED]:
        await _async_register_dashboard(hass)
    else:
        frontend.async_remove_panel(hass, PANEL_URL)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    coordinator: HemsCoordinator = entry.runtime_data
    await coordinator.async_save_learning(force=True)
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        frontend.async_remove_panel(hass, PANEL_URL)
    return unload_ok


async def _async_register_dashboard(hass: HomeAssistant) -> None:
    """Expose the bundled dashboard and add a sidebar panel."""
    static_path = Path(__file__).parent / "static"
    frontend_version = _frontend_version()

    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                STATIC_URL,
                str(static_path),
                cache_headers=False,
            )
        ]
    )

    frontend.async_register_built_in_panel(
        hass,
        component_name="custom",
        sidebar_title=NAME,
        sidebar_icon="mdi:home-lightning-bolt",
        frontend_url_path=PANEL_URL,
        config={
            "_panel_custom": {
                "name": PANEL_COMPONENT_NAME,
                "module_url": f"{STATIC_URL}/panel.js?v={frontend_version}",
                "embed_iframe": False,
                "trust_external": False,
            }
        },
        require_admin=False,
    )
