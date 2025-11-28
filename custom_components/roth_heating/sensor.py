"""Sensor platform for Roth Heating System."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Roth sensor entities from config entry."""
    # Temporarily disabled - no sensors to avoid import issues
    async_add_entities([])

_LOGGER = logging.getLogger(__name__)

SENSOR_DESCRIPTIONS = [
    SensorEntityDescription(
        key="current_temperature",
        name="Current Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
    ),
    SensorEntityDescription(
        key="target_temperature",
        name="Target Temperature", 
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-chevron-up",
    ),
    SensorEntityDescription(
        key="operation_mode",
        name="Operation Mode",
        icon="mdi:thermostat",
    ),
    SensorEntityDescription(
        key="week_program",
        name="Week Program",
        icon="mdi:calendar-week",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Roth sensor entities from config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    
    entities = []
    
    # System status sensor
    entities.append(
        RothSystemSensor(
            coordinator=coordinator,
            name="System Status",
            unique_id="roth_system_status",
            icon="mdi:check-circle",
        )
    )
    
    # Create sensors for each device
    for device_id, device_data in coordinator.data["devices"].items():
        device_name = device_data.get("Name", f"Zone {device_id + 1}")
        
        for description in SENSOR_DESCRIPTIONS:
            entities.append(
                RothDeviceSensor(
                    coordinator=coordinator,
                    device_id=device_id,
                    device_name=device_name,
                    description=description,
                )
            )
    
    async_add_entities(entities)


class RothSystemSensor(CoordinatorEntity[RothDataUpdateCoordinator], SensorEntity):
    """Sensor for system-wide information."""
    
    def __init__(
        self,
        coordinator: RothDataUpdateCoordinator,
        name: str,
        unique_id: str,
        icon: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = f"Roth {name}"
        self._attr_unique_id = unique_id
        self._attr_icon = icon
    
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
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        system_status = self.coordinator.data.get("system_status")
        if system_status == "0":
            return "OK"
        elif system_status == "1":
            return "Warning"
        elif system_status == "2":
            return "Error"
        return system_status


class RothDeviceSensor(CoordinatorEntity[RothDataUpdateCoordinator], SensorEntity):
    """Sensor for device-specific information."""
    
    def __init__(
        self,
        coordinator: RothDataUpdateCoordinator,
        device_id: int,
        device_name: str,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._device_id = device_id
        self._device_name = device_name
        self._attr_unique_id = f"roth_{device_id}_{description.key}"
        self._attr_name = f"Roth {device_name} {description.name}"
    
    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, f"{DEVICE_INFO_IDENTIFIER}_zone_{self._device_id}")},
            "name": f"Roth {self._device_name}",
            "manufacturer": MANUFACTURER,
            "model": f"Zone {self._device_id + 1}",
            "via_device": (DOMAIN, DEVICE_INFO_IDENTIFIER),
        }
    
    @property
    def device_data(self) -> dict[str, Any]:
        """Get current device data."""
        return self.coordinator.data["devices"].get(self._device_id, {})
    
    @property
    def native_value(self) -> float | str | None:
        """Return the state of the sensor."""
        if self.entity_description.key == "current_temperature":
            return self.device_data.get("Temperature")
        elif self.entity_description.key == "target_temperature":
            return self.device_data.get("Setpoint")
        elif self.entity_description.key == "operation_mode":
            mode = self.device_data.get("Operation mode")
            if mode is not None:
                return OPERATION_MODES.get(mode, f"Mode {mode}")
            return None
        elif self.entity_description.key == "week_program":
            program = self.device_data.get("Week program")
            if program is not None:
                return WEEK_PROGRAMS.get(program, f"Program {program}")
            return None
        return None