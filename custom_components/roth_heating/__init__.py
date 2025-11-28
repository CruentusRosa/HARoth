"""The Roth Heating System integration."""
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import RothHeatingAPI
from .const import DOMAIN, CONF_HOST, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.CLIMATE, Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Roth Heating from a config entry."""
    host = entry.data[CONF_HOST]
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    
    api = RothHeatingAPI(host)
    
    coordinator = RothDataUpdateCoordinator(
        hass,
        _LOGGER,
        name="roth_heating",
        api=api,
        update_interval=timedelta(seconds=scan_interval),
    )
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
    }
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok

class RothDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Roth API."""
    
    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        *,
        name: str,
        api: RothHeatingAPI,
        update_interval: timedelta,
    ) -> None:
        """Initialize."""
        self.api = api
        super().__init__(hass, logger, name=name, update_interval=update_interval)
    
    async def _async_update_data(self):
        """Update data via library."""
        try:
            # Get data for all devices
            devices_data = await self.api.get_all_devices_data()
            system_status = await self.api.get_system_status()
            
            return {
                "devices": devices_data,
                "system_status": system_status,
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err