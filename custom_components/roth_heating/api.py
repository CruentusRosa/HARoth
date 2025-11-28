"""
Roth Heating System API Client

Based on the raw HTTP implementation from the original project.
This module handles all communication with the Roth TouchLine controller.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
import httpx
import xml.etree.ElementTree as ET

_LOGGER = logging.getLogger(__name__)


class RothHeatingAPI:
    """API client for Roth TouchLine heating system."""
    
    def __init__(self, host: str, timeout: int = 10):
        """Initialize the API client."""
        self.host = host
        self.base_url = f"http://{host}"
        self.timeout = timeout
        self._header = {"Content-Type": "text/xml"}
        self._read_path = "/cgi-bin/ILRReadValues.cgi"
        self._write_path = "/cgi-bin/writeVal.cgi"
        
        # XML parameter definitions
        self._xml_element_list = [
            {"type": "G", "name": "name", "desc": "Name"},
            {"type": "G", "name": "SollTempMaxVal", "desc": "Setpoint max"},
            {"type": "G", "name": "SollTempMinVal", "desc": "Setpoint min"},
            {"type": "G", "name": "WeekProg", "desc": "Week program"},
            {"type": "G", "name": "OPMode", "desc": "Operation mode"},
            {"type": "G", "name": "SollTemp", "desc": "Setpoint"},
            {"type": "G", "name": "RaumTemp", "desc": "Temperature"},
            {"type": "G", "name": "kurzID", "desc": "Device ID"},
            {"type": "G", "name": "ownerKurzID", "desc": "Controller ID"}
        ]

    def get_touchline_request(self, items: List[str]) -> str:
        """Build the XML request body."""
        request = "<body>"
        request += "<version>1.0</version>"
        request += "<client>IMaster6_02_00</client>"
        request += "<client_ver>6.02.0006</client_ver>"
        request += "<file_name>room</file_name>"
        request += "<item_list_size>0</item_list_size>"
        request += "<item_list>"
        for item in items:
            request += item
        request += "</item_list>"
        request += "</body>"
        return request

    async def request_and_receive_xml(self, req_body: str) -> ET.Element:
        """Send HTTP request and parse XML response."""
        try:
            # Create client without context manager to avoid SSL blocking issues
            client = httpx.AsyncClient(timeout=self.timeout, verify=False)
            try:
                response = await client.post(
                    url=self.base_url + self._read_path,
                    content=req_body,
                    headers=self._header
                )
                
                if response.status_code != 200:
                    raise Exception(f"HTTP error: {response.status_code}")
                
                return ET.fromstring(response.content)
            finally:
                await client.aclose()
                
        except Exception as e:
            _LOGGER.error(f"Network request failed: {e}")
            raise

    async def get_number_of_devices(self) -> int:
        """Get total number of devices."""
        try:
            items = ["<i><n>totalNumberOfDevices</n></i>"]
            request = self.get_touchline_request(items)
            response = await self.request_and_receive_xml(request)
            
            item_list = response.find('item_list')
            item = item_list.find('i')
            return int(item.find('v').text)
            
        except Exception as e:
            _LOGGER.error(f"Failed to get number of devices: {e}")
            raise

    async def get_system_status(self) -> str:
        """Get system status."""
        try:
            items = ["<i><n>R0.SystemStatus</n></i>"]
            request = self.get_touchline_request(items)
            response = await self.request_and_receive_xml(request)
            
            item_list = response.find('item_list')
            item = item_list.find('i')
            return item.find('v').text
            
        except Exception as e:
            _LOGGER.error(f"Failed to get system status: {e}")
            raise

    async def get_device_data(self, device_id: int) -> Dict[str, Any]:
        """Get all data for a specific device."""
        try:
            # Build parameter request
            parameters = ""
            for parameter in self._xml_element_list:
                parameters += f"<n>G{device_id}.{parameter['name']}</n>"
            
            items = ["<i>" + parameters + "</i>"]
            request = self.get_touchline_request(items)
            response = await self.request_and_receive_xml(request)
            
            # Parse response
            data = {}
            item_list = response.find('item_list')
            if item_list is not None:
                item = item_list.find('i')
                if item is not None:
                    device_list = list(item)
                    
                    for i, parameter in enumerate(self._xml_element_list):
                        list_iterator = i * 2
                        if list_iterator + 1 < len(device_list):
                            value = device_list[list_iterator + 1].text
                            if value and value != "NA":
                                if parameter["desc"] in ["Temperature", "Setpoint", "Setpoint max", "Setpoint min"]:
                                    # Convert raw temperature values (divide by 100)
                                    data[parameter["desc"]] = float(value) / 100.0
                                elif parameter["desc"] in ["Operation mode", "Week program", "Device ID", "Controller ID"]:
                                    data[parameter["desc"]] = int(value)
                                else:
                                    data[parameter["desc"]] = value
            
            return data
            
        except Exception as e:
            _LOGGER.error(f"Failed to get device {device_id} data: {e}")
            raise

    async def set_target_temperature(self, device_id: int, temperature: float) -> bool:
        """Set target temperature for a device."""
        try:
            # Convert temperature to raw value (multiply by 100)
            raw_temp = int(temperature * 100)
            
            # Build form data for write request
            form_data = f"G{device_id}.SollTemp={raw_temp}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url=self.base_url + self._write_path,
                    content=form_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                return response.status_code == 200
                
        except Exception as e:
            _LOGGER.error(f"Failed to set temperature for device {device_id}: {e}")
            return False

    async def set_operation_mode(self, device_id: int, mode: int) -> bool:
        """Set operation mode for a device."""
        try:
            form_data = f"G{device_id}.OPMode={mode}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url=self.base_url + self._write_path,
                    content=form_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                return response.status_code == 200
                
        except Exception as e:
            _LOGGER.error(f"Failed to set operation mode for device {device_id}: {e}")
            return False

    async def get_all_devices_data(self) -> Dict[int, Dict[str, Any]]:
        """Get data for all devices."""
        try:
            num_devices = await self.get_number_of_devices()
            devices_data = {}
            
            for device_id in range(num_devices):
                try:
                    data = await self.get_device_data(device_id)
                    if data:
                        devices_data[device_id] = data
                except Exception as e:
                    _LOGGER.warning(f"Failed to get data for device {device_id}: {e}")
            
            return devices_data
            
        except Exception as e:
            _LOGGER.error(f"Failed to get all devices data: {e}")
            raise

    async def set_temperature(self, device_id: int, temperature: float) -> bool:
        """Set target temperature for a device."""
        try:
            return await self.set_target_temperature(device_id, temperature)
        except Exception as e:
            _LOGGER.error(f"Failed to set temperature: {e}")
            return False

    async def set_operation_mode(self, device_id: int, mode: int) -> bool:
        """Set operation mode for a device."""
        try:
            return await self.set_mode(device_id, mode)
        except Exception as e:
            _LOGGER.error(f"Failed to set operation mode: {e}")
            return False

    async def set_target_temperature(self, device_id: int, temperature: float) -> bool:
        """Set target temperature for specific device."""
        try:
            # Create POST request for setting temperature
            client = httpx.AsyncClient(timeout=self.timeout, verify=False)
            try:
                url = f"{self.base_url}{self._write_path}"
                data = {
                    'ID': device_id,
                    'OBJ': 'TempSetpoint',
                    'VAL': temperature
                }
                
                response = await client.post(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
                
                if response.status_code == 200:
                    _LOGGER.debug(f"Successfully set temperature {temperature}°C for device {device_id}")
                    return True
                else:
                    _LOGGER.error(f"Failed to set temperature: HTTP {response.status_code}")
                    return False
                    
            finally:
                await client.aclose()
                
        except Exception as e:
            _LOGGER.error(f"Exception setting temperature: {e}")
            return False

    async def set_mode(self, device_id: int, mode: int) -> bool:
        """Set operation mode for specific device."""
        try:
            # Create POST request for setting mode
            client = httpx.AsyncClient(timeout=self.timeout, verify=False)
            try:
                url = f"{self.base_url}{self._write_path}"
                data = {
                    'ID': device_id,
                    'OBJ': 'OperationMode',
                    'VAL': mode
                }
                
                response = await client.post(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
                
                if response.status_code == 200:
                    _LOGGER.debug(f"Successfully set mode {mode} for device {device_id}")
                    return True
                else:
                    _LOGGER.error(f"Failed to set mode: HTTP {response.status_code}")
                    return False
                    
            finally:
                await client.aclose()
                
        except Exception as e:
            _LOGGER.error(f"Exception setting mode: {e}")
            return False