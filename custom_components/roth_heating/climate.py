"""Climate platform for Roth Heating System."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import RothDataUpdateCoordinator
from .const import (
    DOMAIN,
    OPERATION_MODES,
    HVAC_MODES,
    MIN_TEMP,
    MAX_TEMP,
    TEMP_PRECISION,
    DEVICE_INFO_IDENTIFIER,
    DEVICE_INFO_NAME,
    DEVICE_INFO_MODEL,
    MANUFACTURER,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Roth climate entities from config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][config_entry.entry_id]["api"]
    
    entities = []
    
    # Create climate entity for each device
    for device_id, device_data in coordinator.data["devices"].items():
        entities.append(
            RothClimate(
                coordinator=coordinator,
                api=api,
                device_id=device_id,
                device_name=device_data.get("Name", f"Zone {device_id + 1}"),
            )
        )
    
    async_add_entities(entities)


class RothClimate(CoordinatorEntity[RothDataUpdateCoordinator], ClimateEntity):
    """Representation of a Roth heating zone."""
    
    def __init__(
        self,
        coordinator: RothDataUpdateCoordinator,
        api,
        device_id: int,
        device_name: str,
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self.api = api
        self._device_id = device_id
        self._device_name = device_name
        self._attr_unique_id = f"roth_climate_{device_id}"
        self._attr_name = f"Roth {device_name}"
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_target_temperature_step = TEMP_PRECISION
        self._attr_min_temp = MIN_TEMP
        self._attr_max_temp = MAX_TEMP
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
        )
        self._attr_hvac_modes = [
            HVACMode.AUTO,
            HVACMode.HEAT,
            HVACMode.OFF,
        ]
    
    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, DEVICE_INFO_IDENTIFIER)},
            "name": DEVICE_INFO_NAME,
            "manufacturer": MANUFACTURER,
            "model": DEVICE_INFO_MODEL,
        }
    
    @property
    def device_data(self) -> dict[str, Any]:
        """Get current device data."""
        return self.coordinator.data["devices"].get(self._device_id, {})
    
    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self.device_data.get("Temperature")
    
    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        return self.device_data.get("Setpoint")
    
    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return hvac operation ie. heat, cool mode."""
        operation_mode = self.device_data.get("Operation mode")
        if operation_mode is not None:
            return OPERATION_MODES.get(operation_mode, HVACMode.AUTO)
        return None
    
    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        
        success = await self.api.set_target_temperature(self._device_id, temperature)
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set temperature for device %s", self._device_id)
    
    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        operation_mode = HVAC_MODES.get(hvac_mode)
        if operation_mode is None:
            _LOGGER.error("Unsupported HVAC mode: %s", hvac_mode)
            return
        
        success = await self.api.set_operation_mode(self._device_id, operation_mode)
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set HVAC mode for device %s", self._device_id)