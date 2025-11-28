"""Climate platform for Roth Heating System."""
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

from .const import DOMAIN, MIN_TEMP, MAX_TEMP, TEMP_PRECISION

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Roth climate entities from config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    
    entities = []
    
    # Create climate entity for each device
    if coordinator.data and "devices" in coordinator.data:
        for device_id, device_data in coordinator.data["devices"].items():
            entities.append(
                RothClimate(
                    coordinator=coordinator,
                    config_entry=config_entry,
                    device_id=device_id,
                    device_name=device_data.get("Name", f"Zone {device_id + 1}"),
                )
            )
    
    async_add_entities(entities)

class RothClimate(CoordinatorEntity, ClimateEntity):
    """Representation of a Roth heating zone."""
    
    def __init__(self, coordinator, config_entry, device_id: int, device_name: str) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._device_id = device_id
        self._device_name = device_name
        self._attr_unique_id = f"roth_climate_{device_id}"
        self._attr_name = f"Roth {device_name}"
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_target_temperature_step = TEMP_PRECISION
        self._attr_min_temp = MIN_TEMP
        self._attr_max_temp = MAX_TEMP
        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
        self._attr_hvac_modes = [HVACMode.AUTO, HVACMode.HEAT, HVACMode.OFF]
    
    @property
    def device_data(self):
        """Get current device data."""
        if self.coordinator.data and "devices" in self.coordinator.data:
            return self.coordinator.data["devices"].get(self._device_id, {})
        return {}
    
    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self.device_data.get("Temperature")
    
    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self.device_data.get("Setpoint")
    
    @property
    def hvac_mode(self):
        """Return hvac operation ie. heat, cool mode."""
        operation_mode = self.device_data.get("Operation mode")
        if operation_mode == 0:
            return HVACMode.AUTO
        elif operation_mode == 1:
            return HVACMode.HEAT
        elif operation_mode == 3:
            return HVACMode.OFF
        return HVACMode.AUTO
    
    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is not None:
            success = await self.coordinator.async_set_temperature(self._device_id, temperature)
            if success:
                await self.coordinator.async_request_refresh()
    
    async def async_set_hvac_mode(self, hvac_mode: HVACMode):
        """Set new target hvac mode."""
        mode_map = {
            HVACMode.AUTO: 0,
            HVACMode.HEAT: 1,
            HVACMode.OFF: 3
        }
        operation_mode = mode_map.get(hvac_mode)
        if operation_mode is not None:
            success = await self.coordinator.async_set_mode(self._device_id, operation_mode)
            if success:
                await self.coordinator.async_request_refresh()