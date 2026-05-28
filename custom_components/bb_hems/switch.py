"""Switch settings for BB HEMS."""

from __future__ import annotations

from homeassistant.components import frontend
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    OPT_AUTO_ENABLED,
    OPT_BATTERY_PROTECTION_ENABLED,
    OPT_DASHBOARD_ENABLED,
    OPT_USE_VIRTUAL_BATTERY,
    OPT_VIRTUAL_BATTERY_ENABLED,
    PANEL_URL,
)
from .coordinator import HemsCoordinator
from .entity import HemsEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HEMS switches."""
    coordinator: HemsCoordinator = entry.runtime_data
    async_add_entities(
        [
            HemsAutoSwitch(coordinator),
            HemsBatteryProtectionSwitch(coordinator),
            HemsDashboardSwitch(coordinator),
            HemsVirtualBatterySwitch(coordinator),
            HemsUseVirtualBatterySwitch(coordinator),
        ]
    )


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


class HemsBatteryProtectionSwitch(HemsEntity, SwitchEntity):
    """Enable or disable battery protection rules."""

    _attr_translation_key = "battery_protection_enabled"
    _attr_icon = "mdi:battery-heart"

    def __init__(self, coordinator: HemsCoordinator) -> None:
        super().__init__(coordinator, "battery_protection_enabled")

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.opts[OPT_BATTERY_PROTECTION_ENABLED])

    async def async_turn_on(self, **kwargs: object) -> None:
        await self.coordinator.async_set_option(OPT_BATTERY_PROTECTION_ENABLED, True)

    async def async_turn_off(self, **kwargs: object) -> None:
        await self.coordinator.async_set_option(OPT_BATTERY_PROTECTION_ENABLED, False)


class HemsVirtualBatterySwitch(HemsEntity, SwitchEntity):
    """Enable virtual battery calculation."""

    _attr_translation_key = "virtual_battery_enabled"
    _attr_icon = "mdi:battery-sync"

    def __init__(self, coordinator: HemsCoordinator) -> None:
        super().__init__(coordinator, "virtual_battery_enabled")

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.opts[OPT_VIRTUAL_BATTERY_ENABLED])

    async def async_turn_on(self, **kwargs: object) -> None:
        await self.coordinator.async_set_option(OPT_VIRTUAL_BATTERY_ENABLED, True)

    async def async_turn_off(self, **kwargs: object) -> None:
        await self.coordinator.async_set_option(OPT_VIRTUAL_BATTERY_ENABLED, False)


class HemsUseVirtualBatterySwitch(HemsEntity, SwitchEntity):
    """Allow the virtual battery to participate in HEMS decisions."""

    _attr_translation_key = "use_virtual_battery"
    _attr_icon = "mdi:battery-check"

    def __init__(self, coordinator: HemsCoordinator) -> None:
        super().__init__(coordinator, "use_virtual_battery")

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.opts[OPT_USE_VIRTUAL_BATTERY])

    async def async_turn_on(self, **kwargs: object) -> None:
        await self.coordinator.async_set_option(OPT_USE_VIRTUAL_BATTERY, True)

    async def async_turn_off(self, **kwargs: object) -> None:
        await self.coordinator.async_set_option(OPT_USE_VIRTUAL_BATTERY, False)
