"""Select settings for BB HEMS."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import MODES, OPT_MODE, OPT_RESPONSE_PROFILE, RESPONSE_PROFILES
from .coordinator import HemsCoordinator
from .entity import HemsEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HEMS select settings."""
    coordinator: HemsCoordinator = entry.runtime_data
    async_add_entities(
        [
            HemsModeSelect(coordinator),
            HemsResponseProfileSelect(coordinator),
        ]
    )


class HemsModeSelect(HemsEntity, SelectEntity):
    """HEMS operating mode."""

    _attr_translation_key = "mode"
    _attr_icon = "mdi:tune-variant"
    _attr_options = MODES

    def __init__(self, coordinator: HemsCoordinator) -> None:
        super().__init__(coordinator, "mode")

    @property
    def current_option(self) -> str:
        """Return selected mode."""
        return str(self.coordinator.opts[OPT_MODE])

    async def async_select_option(self, option: str) -> None:
        """Change mode."""
        if option not in MODES:
            return
        await self.coordinator.async_set_option(OPT_MODE, option)


class HemsResponseProfileSelect(HemsEntity, SelectEntity):
    """HEMS switching response profile."""

    _attr_translation_key = "response_profile"
    _attr_icon = "mdi:speedometer"
    _attr_options = RESPONSE_PROFILES

    def __init__(self, coordinator: HemsCoordinator) -> None:
        super().__init__(coordinator, "response_profile")

    @property
    def current_option(self) -> str:
        """Return selected response profile."""
        return str(self.coordinator.opts[OPT_RESPONSE_PROFILE])

    async def async_select_option(self, option: str) -> None:
        """Change response profile."""
        if option not in RESPONSE_PROFILES:
            return
        await self.coordinator.async_set_option(OPT_RESPONSE_PROFILE, option)
