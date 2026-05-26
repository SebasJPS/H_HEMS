"""Shared entity helpers for BB HEMS."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NAME
from .coordinator import HemsCoordinator


class HemsEntity(CoordinatorEntity[HemsCoordinator]):
    """Base entity for all HEMS entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: HemsCoordinator, key: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{key}"
        self._attr_suggested_object_id = f"{DOMAIN}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=NAME,
            manufacturer="BB",
            model="Home Energy Management System",
        )
