"""Support for Roth Heating sensors."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Roth Heating sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    
    entities: list[SensorEntity] = []
    
    # Add system status sensor
    entities.append(RothSystemStatusSensor(coordinator, config_entry))
    
    # Add sensors for each device/zone
    if coordinator.data and "devices" in coordinator.data:
        for device_id, device_data in coordinator.data["devices"].items():
            device_name = device_data.get("Name", f"Zone {device_id + 1}")
            
            # Current temperature sensor
            entities.append(RothCurrentTemperatureSensor(coordinator, config_entry, device_id, device_name))
            
            # Target temperature sensor
            entities.append(RothTargetTemperatureSensor(coordinator, config_entry, device_id, device_name))
            
            # Heating status sensor
            entities.append(RothHeatingStatusSensor(coordinator, config_entry, device_id, device_name))
            
            # Operation mode sensor
            entities.append(RothOperationModeSensor(coordinator, config_entry, device_id, device_name))
    
    _LOGGER.info(f"Setting up {len(entities)} Roth sensors")
    async_add_entities(entities)


class RothBaseSensor(CoordinatorEntity, SensorEntity):
    """Base sensor for Roth Heating sensors."""

    def __init__(
        self,
        coordinator,
        config_entry: ConfigEntry,
        sensor_type: str,
        device_id: int | None = None,
        device_name: str | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._sensor_type = sensor_type
        self._device_id = device_id
        self._device_name = device_name
        
        if device_id is not None:
            self._attr_name = f"Roth {device_name} {sensor_type}"
            self._attr_unique_id = f"{config_entry.entry_id}_device_{device_id}_{sensor_type.lower().replace(' ', '_')}"
        else:
            self._attr_name = f"Roth {sensor_type}"
            self._attr_unique_id = f"{config_entry.entry_id}_{sensor_type.lower().replace(' ', '_')}"

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        if self._device_id is not None:
            return {
                "identifiers": {(DOMAIN, f"{self._config_entry.entry_id}_device_{self._device_id}")},
                "name": f"Roth {self._device_name}",
                "manufacturer": "Roth",
                "model": "TouchLine Zone",
                "sw_version": "1.1.0",
                "via_device": (DOMAIN, self._config_entry.entry_id),
            }
        else:
            return {
                "identifiers": {(DOMAIN, self._config_entry.entry_id)},
                "name": "Roth Heating System",
                "manufacturer": "Roth",
                "model": "TouchLine",
                "sw_version": "1.1.0",
            }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def device_data(self) -> dict[str, Any]:
        """Get current device data."""
        if self._device_id is not None and self.coordinator.data and "devices" in self.coordinator.data:
            return self.coordinator.data["devices"].get(self._device_id, {})
        return {}


class RothSystemStatusSensor(RothBaseSensor):
    """Sensor for overall system status."""
    
    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the system status sensor."""
        super().__init__(coordinator, config_entry, "System Status")
        self._attr_icon = "mdi:home-thermometer-outline"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return "Unavailable"
        
        # Check system status from API
        system_status = self.coordinator.data.get("system_status")
        if system_status == "0" or system_status == 0:
            return "OK"
        elif system_status == "1" or system_status == 1:
            return "Warning"
        elif system_status == "2" or system_status == 2:
            return "Error"
        
        # Check if any devices are active
        devices = self.coordinator.data.get("devices", {})
        if devices:
            return "Active"
        
        return "Unknown"

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return None
        
        devices = self.coordinator.data.get("devices", {})
        return {
            "total_zones": len(devices),
            "connection_status": "connected" if self.coordinator.last_update_success else "disconnected",
            "controller_host": self._config_entry.data.get("host"),
        }


class RothCurrentTemperatureSensor(RothBaseSensor):
    """Current temperature sensor for Roth zones."""
    
    def __init__(self, coordinator, config_entry: ConfigEntry, device_id: int, device_name: str) -> None:
        """Initialize the current temperature sensor."""
        super().__init__(coordinator, config_entry, "Temperature", device_id, device_name)
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_icon = "mdi:thermometer"

    @property
    def native_value(self) -> float | None:
        """Return the current temperature."""
        temp = self.device_data.get("Temperature")
        if temp is not None:
            return round(float(temp), 1)
        return None


class RothTargetTemperatureSensor(RothBaseSensor):
    """Target temperature sensor for Roth zones."""
    
    def __init__(self, coordinator, config_entry: ConfigEntry, device_id: int, device_name: str) -> None:
        """Initialize the target temperature sensor."""
        super().__init__(coordinator, config_entry, "Target Temperature", device_id, device_name)
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_icon = "mdi:thermometer-chevron-up"

    @property
    def native_value(self) -> float | None:
        """Return the target temperature."""
        temp = self.device_data.get("Setpoint")
        if temp is not None:
            return round(float(temp), 1)
        return None


class RothHeatingStatusSensor(RothBaseSensor):
    """Heating status sensor for Roth zones."""
    
    def __init__(self, coordinator, config_entry: ConfigEntry, device_id: int, device_name: str) -> None:
        """Initialize the heating status sensor."""
        super().__init__(coordinator, config_entry, "Heating Status", device_id, device_name)
        self._attr_icon = "mdi:radiator"

    @property
    def native_value(self) -> StateType:
        """Return the heating status."""
        device_data = self.device_data
        if not device_data:
            return "Unknown"
        
        current_temp = device_data.get("Temperature")
        target_temp = device_data.get("Setpoint")
        operation_mode = device_data.get("Operation mode")
        
        if current_temp is not None and target_temp is not None:
            temp_diff = target_temp - current_temp
            
            # Check if heating is likely active
            if operation_mode in [1, "1"]:  # Heat mode
                if temp_diff > 0.5:
                    return "Heating"
                else:
                    return "Satisfied"
            elif operation_mode in [0, "0"]:  # Auto mode
                if temp_diff > 0.5:
                    return "Demand"
                else:
                    return "Satisfied"
            elif operation_mode in [3, "3"]:  # Off mode
                return "Off"
            else:
                return "Idle"
        
        return "Unknown"

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        device_data = self.device_data
        if not device_data:
            return None
        
        current_temp = device_data.get("Temperature")
        target_temp = device_data.get("Setpoint")
        temp_diff = None
        if current_temp is not None and target_temp is not None:
            temp_diff = round(target_temp - current_temp, 1)
        
        return {
            "temperature_difference": temp_diff,
            "operation_mode": device_data.get("Operation mode"),
            "week_program": device_data.get("Week program"),
        }


class RothOperationModeSensor(RothBaseSensor):
    """Operation mode sensor for Roth zones."""
    
    def __init__(self, coordinator, config_entry: ConfigEntry, device_id: int, device_name: str) -> None:
        """Initialize the operation mode sensor."""
        super().__init__(coordinator, config_entry, "Operation Mode", device_id, device_name)
        self._attr_icon = "mdi:thermostat"

    @property
    def native_value(self) -> StateType:
        """Return the operation mode."""
        device_data = self.device_data
        operation_mode = device_data.get("Operation mode")
        
        if operation_mode is not None:
            mode_mapping = {
                0: "auto",
                1: "heat", 
                2: "eco",
                3: "off",
                "0": "auto",
                "1": "heat",
                "2": "eco", 
                "3": "off"
            }
            return mode_mapping.get(operation_mode, f"mode_{operation_mode}")
        
        return "unknown"

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        device_data = self.device_data
        if not device_data:
            return None
        
        week_program = device_data.get("Week program")
        week_program_name = "Unknown"
        if week_program is not None:
            program_mapping = {
                0: "Program 1",
                1: "Program 2", 
                2: "Program 3",
                3: "Program 4",
                "0": "Program 1",
                "1": "Program 2",
                "2": "Program 3", 
                "3": "Program 4"
            }
            week_program_name = program_mapping.get(week_program, f"Program {week_program}")
        
        return {
            "week_program": week_program_name,
            "week_program_id": week_program,
        }