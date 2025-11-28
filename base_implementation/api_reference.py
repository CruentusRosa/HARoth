#!/usr/bin/env python3
"""
Roth Heating System - Raw HTTP Implementation Test

This script uses raw HTTP requests to directly communicate with your Roth heating system
without using the write functionality, based on the original PyTouchline implementation.
"""

import json
import logging
from datetime import datetime
import httpx
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

# Your Roth controller configuration
ROTH_IP = "192.168.86.29"
ROTH_URL = f"http://{ROTH_IP}"


class RothRawReader:
    """Raw HTTP reader for Roth heating system based on original PyTouchline."""
    
    def __init__(self, device_id=0):
        self._id = device_id
        self._temp_scale = 100
        self._header = {"Content-Type": "text/xml"}
        self._read_path = "/cgi-bin/ILRReadValues.cgi"
        self._parameter = {}
        self._xml_element_list = []
        
        # Define all the parameters we want to read (excluding write-only ones)
        self._xml_element_list.append(
            {"name": "name", "desc": "Name", "type": "G"})
        self._xml_element_list.append(
            {"name": "SollTempMaxVal", "desc": "Setpoint max", "type": "G"})
        self._xml_element_list.append(
            {"name": "SollTempMinVal", "desc": "Setpoint min", "type": "G"})
        self._xml_element_list.append(
            {"name": "WeekProg", "desc": "Week program", "type": "G"})
        self._xml_element_list.append(
            {"name": "OPMode", "desc": "Operation mode", "type": "G"})
        self._xml_element_list.append(
            {"name": "SollTemp", "desc": "Setpoint", "type": "G"})
        self._xml_element_list.append(
            {"name": "RaumTemp", "desc": "Temperature", "type": "G"})
        self._xml_element_list.append(
            {"name": "kurzID", "desc": "Device ID", "type": "G"})
        self._xml_element_list.append(
            {"name": "ownerKurzID", "desc": "Controller ID", "type": "G"})
    
    def get_touchline_request(self, items):
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
    
    async def request_and_receive_xml(self, req_body):
        """Send HTTP request and parse XML response."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url=ROTH_URL + self._read_path,
                    content=req_body,
                    headers=self._header
                )
                
                if response.status_code != 200:
                    raise Exception(f"HTTP error: {response.status_code}")
                
                # Parse XML response
                return ET.fromstring(response.content)
                
        except Exception as e:
            logger.error(f"Network request failed: {e}")
            raise
    
    def get_touchline_device_item(self, device_id):
        """Get device-specific parameter request items."""
        items = []
        parameters = ""
        
        for parameter in self._xml_element_list:
            if parameter["type"] == "G":
                parameters += f"<n>G{device_id}.{parameter['name']}</n>"
            else:
                parameters += f"<n>CD.{parameter['name']}</n>"
        
        items.append("<i>" + parameters + "</i>")
        return items
    
    async def get_number_of_devices(self):
        """Get total number of devices."""
        try:
            items = ["<i><n>totalNumberOfDevices</n></i>"]
            request = self.get_touchline_request(items)
            response = await self.request_and_receive_xml(request)
            
            item_list = response.find('item_list')
            item = item_list.find('i')
            return int(item.find('v').text)
            
        except Exception as e:
            logger.error(f"Failed to get number of devices: {e}")
            return None
    
    async def get_system_status(self):
        """Get system status."""
        try:
            items = ["<i><n>R0.SystemStatus</n></i>"]
            request = self.get_touchline_request(items)
            response = await self.request_and_receive_xml(request)
            
            item_list = response.find('item_list')
            item = item_list.find('i')
            return item.find('v').text
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return None
    
    def parse_device_response(self, response):
        """Parse device-specific response and extract parameters."""
        self._parameter = {}
        
        try:
            item_list = response.find('item_list')
            for item in item_list.iterfind("i"):
                list_iterator = 0
                device_list = list(item)
                
                for parameter in self._xml_element_list:
                    if list_iterator >= len(device_list):
                        break
                        
                    if device_list[list_iterator].tag != "n":
                        list_iterator -= 1
                        self._parameter[parameter["desc"]] = "NA"
                    else:
                        if list_iterator + 1 < len(device_list):
                            value = device_list[list_iterator + 1].text
                            self._parameter[parameter["desc"]] = str(value) if value else "NA"
                            
                            # Extract unique ID from first parameter
                            if list_iterator == 0 and value:
                                try:
                                    unique_id = device_list[list_iterator].text.split(".")[0].split("G")[1]
                                    self._parameter["Unique ID"] = unique_id
                                except:
                                    pass
                    
                    list_iterator += 2
                    
        except Exception as e:
            logger.error(f"Failed to parse device response: {e}")
    
    async def update_device_data(self, device_id=None):
        """Update device data for specified device ID."""
        if device_id is None:
            device_id = self._id
            
        try:
            device_items = self.get_touchline_device_item(device_id)
            request = self.get_touchline_request(device_items)
            response = await self.request_and_receive_xml(request)
            self.parse_device_response(response)
            return True
            
        except Exception as e:
            logger.error(f"Failed to update device data for device {device_id}: {e}")
            return False
    
    def get_name(self):
        """Get device name."""
        return self._parameter.get("Name")
    
    def get_current_temperature(self):
        """Get current temperature."""
        temp_str = self._parameter.get("Temperature")
        if temp_str and temp_str != "NA":
            try:
                return int(temp_str) / self._temp_scale
            except ValueError:
                return None
        return None
    
    def get_target_temperature(self):
        """Get target temperature."""
        temp_str = self._parameter.get("Setpoint")
        if temp_str and temp_str != "NA":
            try:
                return int(temp_str) / self._temp_scale
            except ValueError:
                return None
        return None
    
    def get_target_temperature_high(self):
        """Get high temperature limit."""
        temp_str = self._parameter.get("Setpoint max")
        if temp_str and temp_str != "NA":
            try:
                return int(temp_str) / self._temp_scale
            except ValueError:
                return None
        return None
    
    def get_target_temperature_low(self):
        """Get low temperature limit."""
        temp_str = self._parameter.get("Setpoint min")
        if temp_str and temp_str != "NA":
            try:
                return int(temp_str) / self._temp_scale
            except ValueError:
                return None
        return None
    
    def get_week_program(self):
        """Get week program setting."""
        prog_str = self._parameter.get("Week program")
        if prog_str and prog_str != "NA":
            try:
                return int(prog_str)
            except ValueError:
                return None
        return None
    
    def get_operation_mode(self):
        """Get operation mode."""
        mode_str = self._parameter.get("Operation mode")
        if mode_str and mode_str != "NA":
            try:
                return int(mode_str)
            except ValueError:
                return None
        return None
    
    def get_device_id(self):
        """Get device ID."""
        id_str = self._parameter.get("Device ID")
        if id_str and id_str != "NA":
            try:
                return int(id_str)
            except ValueError:
                return None
        return None
    
    def get_controller_id(self):
        """Get controller ID."""
        id_str = self._parameter.get("Controller ID")
        if id_str and id_str != "NA":
            try:
                return int(id_str)
            except ValueError:
                return None
        return None
    
    def get_all_parameters(self):
        """Get all parsed parameters."""
        return self._parameter.copy()


async def test_raw_implementation():
    """Test the raw HTTP implementation."""
    print("Roth Heating System - Raw HTTP Implementation Test")
    print("=" * 55)
    
    # Initialize the reader
    reader = RothRawReader(device_id=1)  # Start with device 1 as it had data before
    
    # Collect all data
    data = {
        "test_timestamp": datetime.now().isoformat(),
        "system_data": {},
        "device_data": {},
        "raw_parameters": {},
        "all_devices": {},
        "errors": []
    }
    
    try:
        # Get system-level data
        print("Getting system information...")
        
        num_devices = await reader.get_number_of_devices()
        system_status = await reader.get_system_status()
        
        data["system_data"] = {
            "number_of_devices": num_devices,
            "system_status": system_status,
            "controller_url": ROTH_URL
        }
        
        print(f"✓ Number of devices: {num_devices}")
        print(f"✓ System status: {system_status}")
        
        # Test device data collection
        print(f"\nTesting device data collection...")
        
        # Try device 1 (which had data in previous tests)
        success = await reader.update_device_data(device_id=1)
        if success:
            print("✓ Device 1 data updated successfully")
            
            # Get all the parsed parameters
            all_params = reader.get_all_parameters()
            data["raw_parameters"] = all_params
            
            # Get individual values
            device_info = {
                "name": reader.get_name(),
                "current_temperature": reader.get_current_temperature(),
                "target_temperature": reader.get_target_temperature(),
                "target_temperature_high": reader.get_target_temperature_high(),
                "target_temperature_low": reader.get_target_temperature_low(),
                "operation_mode": reader.get_operation_mode(),
                "week_program": reader.get_week_program(),
                "device_id": reader.get_device_id(),
                "controller_id": reader.get_controller_id()
            }
            
            data["device_data"] = device_info
            
            print(f"✓ Device name: {device_info['name']}")
            print(f"✓ Current temperature: {device_info['current_temperature']}°C")
            print(f"✓ Target temperature: {device_info['target_temperature']}°C")
            print(f"✓ Operation mode: {device_info['operation_mode']}")
        else:
            print("❌ Failed to update device 1 data")
        
        # Test all devices
        print(f"\nTesting all devices (0-{num_devices-1})...")
        
        for device_id in range(num_devices):
            print(f"  Testing device {device_id}...")
            device_reader = RothRawReader(device_id=device_id)
            
            success = await device_reader.update_device_data(device_id)
            if success:
                device_params = device_reader.get_all_parameters()
                if device_params:
                    data["all_devices"][f"device_{device_id}"] = {
                        "raw_parameters": device_params,
                        "parsed_data": {
                            "name": device_reader.get_name(),
                            "current_temperature": device_reader.get_current_temperature(),
                            "target_temperature": device_reader.get_target_temperature(),
                            "operation_mode": device_reader.get_operation_mode(),
                            "device_id": device_reader.get_device_id(),
                            "controller_id": device_reader.get_controller_id()
                        }
                    }
                    
                    # Show non-null values
                    non_null_data = {k: v for k, v in data["all_devices"][f"device_{device_id}"]["parsed_data"].items() 
                                   if v is not None}
                    if non_null_data:
                        print(f"    ✓ Device {device_id} has data: {list(non_null_data.keys())}")
            else:
                data["all_devices"][f"device_{device_id}"] = {"error": "Failed to update"}
        
    except Exception as e:
        data["errors"].append(str(e))
        print(f"❌ Error during testing: {e}")
    
    # Save results
    output_file = f"roth_raw_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Raw test results saved to: {output_file}")
    
    # Summary
    working_devices = len([d for d in data.get("all_devices", {}).values() 
                          if "error" not in d and any(v is not None for v in d.get("parsed_data", {}).values())])
    
    print(f"📊 Test Summary:")
    print(f"   System devices found: {data['system_data'].get('number_of_devices', 0)}")
    print(f"   Devices with data: {working_devices}")
    print(f"   Errors: {len(data.get('errors', []))}")
    
    # Add magic numbers decoding to the results
    if data.get("all_devices"):
        print(f"\n🔍 Decoding magic numbers...")
        decoded_data = decode_magic_numbers(data["all_devices"])
        data["decoded_devices"] = decoded_data
        print(f"✓ Magic numbers decoded for {len(decoded_data)} devices")
    
    return data


def decode_magic_numbers(device_data):
    """Decode magic numbers with enhanced meanings based on exploration."""
    decoded = {}
    
    for device_key, device_info in device_data.items():
        if isinstance(device_info, dict) and "parsed_data" in device_info:
            parsed = device_info["parsed_data"]
            decoded_device = device_info.copy()
            
            # Enhanced operation mode decoding (from magic numbers exploration)
            if parsed.get('operation_mode'):
                op_mode = str(parsed['operation_mode'])
                decoded_device['operation_mode_decoded'] = {
                    '0': 'AUTO/NORMAL - Standard automatic operation based on schedule',
                    '1': 'MANUAL/COMFORT - Manual override to comfort temperature', 
                    '2': 'ECO/SETBACK - Energy saving reduced temperature mode',
                    '3': 'OFF/FROST_PROTECTION - Minimal heating for frost protection'
                }.get(op_mode, f'Unknown Mode ({op_mode})')
            
            # Enhanced week program decoding
            if 'week_program' in device_info.get("raw_parameters", {}):
                week_prog = str(device_info["raw_parameters"]["week_program"])
                decoded_device['week_program_decoded'] = {
                    '0': 'Default Program - No custom schedule active',
                    '1': 'Weekly Program 1 - Custom heating schedule 1',
                    '2': 'Weekly Program 2 - Custom heating schedule 2', 
                    '3': 'Weekly Program 3 - Custom heating schedule 3',
                    '4': 'Weekly Program 4 - Custom heating schedule 4'
                }.get(week_prog, f'Custom Program {week_prog}')
            
            # Add comprehensive temperature information
            if parsed.get('current_temperature') is not None or parsed.get('target_temperature') is not None:
                decoded_device['temperature_info'] = {
                    'scale': 'Celsius (°C)',
                    'conversion_note': 'Raw XML values are in centi-degrees (divide by 100)',
                    'example': 'Raw 2300 = 23.00°C',
                    'current_formatted': f"{parsed.get('current_temperature', 'N/A')}°C",
                    'target_formatted': f"{parsed.get('target_temperature', 'N/A')}°C"
                }
            
            # Add device info summary
            decoded_device['device_summary'] = {
                'device_key': device_key,
                'zone_name': parsed.get('name', 'Unknown Zone'),
                'device_id': parsed.get('device_id'),
                'controller_type': 'Roth TouchLine System',
                'status': 'Active' if parsed.get('current_temperature') is not None else 'Inactive'
            }
            
            decoded[device_key] = decoded_device
        else:
            decoded[device_key] = device_info
    
    return decoded


if __name__ == "__main__":
    import asyncio
    
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    try:
        asyncio.run(test_raw_implementation())
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()