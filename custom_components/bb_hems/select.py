"""Select settings for BB HEMS."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import MODES, OPT_MODE
from .coordinator import HemsCoordinator
from .entity import HemsEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: HemsCoordinator = entry.runtime_data
    async_add_entities([HemsModeSelect(coordinator)])


class HemsModeSelect(HemsEntity, SelectEntity):
    _attr_translation_key = "mode"
    _attr_icon = "mdi:tune-variant"
    _attr_options = MODES

    def __init__(self, coordinator: HemsCoordinator) -> None:
        super().__init__(coordinator, "mode")

    @property
    def current_option(self) -> str:
        return str(self.coordinator.opts[OPT_MODE])

    async def async_select_option(self, option: str) -> None:
        if option in MODES:
            await self.coordinator.async_set_option(OPT_MODE, option)
