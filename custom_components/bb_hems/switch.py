"""Switch settings for BB HEMS."""

from __future__ import annotations

from homeassistant.components import frontend
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import OPT_AUTO_ENABLED, OPT_DASHBOARD_ENABLED, PANEL_URL
from .coordinator import HemsCoordinator
from .entity import HemsEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HEMS switches."""
    coordinator: HemsCoordinator = entry.runtime_data
    async_add_entities([HemsAutoSwitch(coordinator), HemsDashboardSwitch(coordinator)])


class HemsAutoSwitch(HemsEntity, SwitchEntity):
    """Enable or disable automatic HEMS decisions."""

    _attr_translation_key = "auto_enabled"
    _attr_icon = "mdi:autorenew"

    def __init__(self, coordinator: HemsCoordinator) -> None:
        super().__init__(coordinator, "auto_enabled")

    @property
    def is_on(self) -> bool:
        """Return if automation decisions are enabled."""
        return bool(self.coordinator.opts[OPT_AUTO_ENABLED])

    async def async_turn_on(self, **kwargs: object) -> None:
        """Enable HEMS decisions."""
        await self.coordinator.async_set_option(OPT_AUTO_ENABLED, True)

    async def async_turn_off(self, **kwargs: object) -> None:
        """Disable HEMS decisions."""
        await self.coordinator.async_set_option(OPT_AUTO_ENABLED, False)


class HemsDashboardSwitch(HemsEntity, SwitchEntity):
    """Show or hide the bundled sidebar dashboard."""

    _attr_translation_key = "dashboard_enabled"
    _attr_icon = "mdi:view-dashboard"

    def __init__(self, coordinator: HemsCoordinator) -> None:
        super().__init__(coordinator, "dashboard_enabled")

    @property
    def is_on(self) -> bool:
        """Return if the sidebar dashboard is enabled."""
        return bool(self.coordinator.opts[OPT_DASHBOARD_ENABLED])

    async def async_turn_on(self, **kwargs: object) -> None:
        """Enable the bundled dashboard."""
        await self.coordinator.async_set_option(OPT_DASHBOARD_ENABLED, True)
        from . import _async_register_dashboard

        await _async_register_dashboard(self.coordinator.hass)

    async def async_turn_off(self, **kwargs: object) -> None:
        """Disable the bundled dashboard."""
        await self.coordinator.async_set_option(OPT_DASHBOARD_ENABLED, False)
        frontend.async_remove_panel(self.coordinator.hass, PANEL_URL)
