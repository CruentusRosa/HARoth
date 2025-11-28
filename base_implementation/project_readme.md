# Roth Heating System Control

Complete Python implementation for controlling Roth TouchLine heating systems.

## System Information
- **Controller**: ROTH-02EF0C at http://192.168.86.29
- **SCADA System**: SpiderControl
- **Zones**: 7 heating zones with real-time temperature control
- **Authentication**: Open access (no credentials required)

## Quick Start

```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run main application
python main.py

# Test raw HTTP implementation
python examples\raw_http_test.py
```

## Core Files
- `main.py` - Main application using PyTouchline Extended
- `examples/raw_http_test.py` - Raw HTTP implementation with magic numbers decoding
- `complete_roth_system.json` - Complete system data and API documentation
- `utils/helpers.py` - Utility functions

## Heating Zones
1. **Stue** (Living Room) - Device ID 1
2. **Kontor** (Office) - Device ID 2  
3. **Sovevaerelse** (Bedroom) - Device ID 3
4. **Walkin closet** - Device ID 4
5. **Gang** (Hallway) - Device ID 5
6. **Stort badeværelse** (Large Bathroom) - Device ID 6
7. **Lille badeværelse** (Small Bathroom) - Device ID 7

## API Operations

### Read Temperature
```python
from examples.raw_http_test import RothRawReader

reader = RothRawReader(device_id=1)
await reader.update_device_data()
temp = reader.get_current_temperature()  # Returns float in °C
```

### Operation Modes
- `0` - AUTO/NORMAL: Standard automatic operation
- `1` - MANUAL/COMFORT: Manual override to comfort temperature
- `2` - ECO/SETBACK: Energy saving reduced temperature
- `3` - OFF/FROST_PROTECTION: Minimal heating protection

### Write Operations
System supports writing to `/cgi-bin/writeVal.cgi` endpoint without authentication.

## System Data
Complete system information available in `complete_roth_system.json` including:
- All zone temperatures and settings
- Operation modes and week programs
- API endpoints and request formats
- Magic numbers decoding