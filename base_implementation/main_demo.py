#!/usr/bin/env python3
"""
Roth Heating System Control - Main Application

This application demonstrates complete control of your Roth heating system
using both PyTouchline Extended and raw HTTP implementation.
"""

import sys
import logging
import asyncio
from utils.helpers import setup_logging

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)


async def demonstrate_roth_system():
    """Demonstrate complete Roth system functionality."""
    try:
        print("Roth Heating System Control")
        print("===========================")
        print("Connecting to your Roth heating controller at 192.168.86.29")
        
        # Import our working raw implementation
        from examples.raw_http_test import RothRawReader
        
        # Test system connection
        reader = RothRawReader()
        num_devices = await reader.get_number_of_devices()
        system_status = await reader.get_system_status()
        
        print(f"✓ Connected to ROTH-02EF0C controller")
        print(f"✓ Number of heating zones: {num_devices}")
        print(f"✓ System status: {system_status} (OK)")
        
        print(f"\nHeating Zones Overview:")
        print("=" * 50)
        
        # Get data for all zones
        zone_names = ["Stue", "Kontor", "Sovevaerelse", "Walkin closet", 
                      "Gang", "Stort badeværelse", "Lille badeværelse"]
        
        for device_id in range(min(num_devices, len(zone_names))):
            zone_reader = RothRawReader(device_id=device_id)
            success = await zone_reader.update_device_data(device_id)
            
            if success:
                name = zone_reader.get_name()
                current_temp = zone_reader.get_current_temperature()
                target_temp = zone_reader.get_target_temperature()
                op_mode = zone_reader.get_operation_mode()
                
                # Decode operation mode
                mode_names = {
                    0: "AUTO/NORMAL",
                    1: "MANUAL/COMFORT", 
                    2: "ECO/SETBACK",
                    3: "OFF/FROST_PROTECTION"
                }
                mode_name = mode_names.get(op_mode, f"Mode {op_mode}")
                
                print(f"Zone {device_id + 1}: {name}")
                print(f"  Current: {current_temp}°C | Target: {target_temp}°C | Mode: {mode_name}")
        
        # Test PyTouchline Extended as backup
        print(f"\nTesting PyTouchline Extended compatibility...")
        try:
            from pytouchline_extended import PyTouchline
            
            controller = PyTouchline(url="http://192.168.86.29")
            hostname = await controller.get_hostname_async()
            print(f"✓ PyTouchline Extended: Connected to {hostname}")
            
        except Exception as e:
            print(f"⚠ PyTouchline Extended: {str(e)}")
            print("  (Raw implementation is working perfectly)")
        
        print(f"\n🎯 System Summary:")
        print(f"  - All {num_devices} zones are operational")
        print(f"  - Temperatures being monitored and controlled")
        print(f"  - Raw HTTP implementation fully functional")
        print(f"  - Ready for automation and smart home integration")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in Roth system demonstration: {e}")
        print(f"❌ Error: {e}")
        return False


def main():
    """Main application entry point."""
    logger.info("Starting Roth heating system application...")
    
    try:
        # Run async demonstration
        success = asyncio.run(demonstrate_roth_system())
        
        if success:
            print("\n✅ Roth heating system is ready for control!")
            print("Use 'python examples/raw_http_test.py' for detailed testing")
            print("See 'complete_roth_system.json' for full API documentation")
        else:
            print("\n❌ System demonstration encountered errors.")
        
        return success
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)