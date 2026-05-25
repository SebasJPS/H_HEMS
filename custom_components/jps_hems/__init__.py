"""JPS Home Energy Management System integration."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components import frontend
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import NAME, PANEL_URL, PLATFORMS
from .coordinator import HemsCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up JPS HEMS from a config entry."""
    coordinator = HemsCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await _async_register_dashboard(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        frontend.async_remove_panel(hass, PANEL_URL)
    return unload_ok


async def _async_register_dashboard(hass: HomeAssistant) -> None:
    """Expose the bundled dashboard and add a sidebar panel."""
    static_path = Path(__file__).parent / "static"
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                "/api/jps_hems/static",
                str(static_path),
                cache_headers=False,
            )
        ]
    )

    frontend.async_register_built_in_panel(
        hass,
        component_name="iframe",
        sidebar_title=NAME,
        sidebar_icon="mdi:home-lightning-bolt",
        frontend_url_path=PANEL_URL,
        config={"url": "/api/jps_hems/static/dashboard.html"},
        require_admin=False,
    )
