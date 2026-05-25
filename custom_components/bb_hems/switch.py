"""Switch settings for BB HEMS."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import OPT_AUTO_ENABLED
from .coordinator import HemsCoordinator
from .entity import HemsEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: HemsCoordinator = entry.runtime_data
    async_add_entities([HemsAutoSwitch(coordinator)])


class HemsAutoSwitch(HemsEntity, SwitchEntity):
    _attr_translation_key = "auto_enabled"
    _attr_icon = "mdi:autorenew"

    def __init__(self, coordinator: HemsCoordinator) -> None:
        super().__init__(coordinator, "auto_enabled")

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.opts[OPT_AUTO_ENABLED])

    async def async_turn_on(self, **kwargs: object) -> None:
        await self.coordinator.async_set_option(OPT_AUTO_ENABLED, True)

    async def async_turn_off(self, **kwargs: object) -> None:
        await self.coordinator.async_set_option(OPT_AUTO_ENABLED, False)
