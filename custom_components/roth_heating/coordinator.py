"""Data update coordinator for Roth Heating integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import RothHeatingAPI
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class RothDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Roth data."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        self.config_entry = config_entry
        self.api = RothHeatingAPI(
            host=config_entry.data[CONF_HOST],
        )
        
        update_interval = timedelta(
            seconds=config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Roth controller."""
        try:
            _LOGGER.debug("Fetching data from Roth controller at %s", self.api.host)
            
            # Fetch data with timeout
            async with asyncio.timeout(30):
                devices_data = await self.api.get_all_devices_data()
                system_status = await self.api.get_system_status()
                
                data = {
                    "devices": devices_data,
                    "system_status": system_status,
                }
                
            if not data.get("devices"):
                _LOGGER.warning("No device data received from Roth controller")
                
            _LOGGER.debug("Successfully fetched data: %s devices found", 
                         len(data.get("devices", {})))
            return data
            
        except asyncio.TimeoutError as err:
            raise UpdateFailed("Timeout communicating with Roth controller") from err
        except Exception as err:
            _LOGGER.error("Error communicating with Roth controller: %s", err)
            raise UpdateFailed(f"Error communicating with controller: {err}") from err

    async def async_set_temperature(self, device_id: int, temperature: float) -> bool:
        """Set temperature for a device."""
        try:
            return await self.api.set_temperature(device_id, temperature)
        except Exception as err:
            _LOGGER.error("Error setting temperature: %s", err)
            return False

    async def async_set_mode(self, device_id: int, mode: int) -> bool:
        """Set operation mode for a device."""
        try:
            return await self.api.set_operation_mode(device_id, mode)
        except Exception as err:
            _LOGGER.error("Error setting mode: %s", err)
            return False