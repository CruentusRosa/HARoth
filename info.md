# Roth Heating System

Integration for Roth TouchLine heating controllers in Home Assistant.

## Key Features

- **Complete Climate Control**: Full HVAC management for each heating zone
- **Real-time Monitoring**: Temperature and system status sensors
- **Easy Setup**: Simple IP address configuration
- **Multiple Operation Modes**: AUTO, HEAT, ECO, OFF
- **Local Communication**: Direct connection to your Roth controller

## Installation

This integration can be installed through HACS (Home Assistant Community Store).

1. In HACS, search for "Roth Heating System"
2. Install the integration
3. Restart Home Assistant
4. Add the integration through Settings → Devices & Services
5. Enter your Roth controller's IP address when prompted

## Configuration

- **IP Address**: Your Roth TouchLine controller IP (e.g., 192.168.1.100)
- **Scan Interval**: Update frequency in seconds (default: 30)

## Supported Hardware

- Roth TouchLine controllers
- ROTH-02EF0C models
- Controllers with SpiderControl SCADA system

## Created Entities

### Climate
- `climate.roth_[zone_name]` for each heating zone

### Sensors
- Current temperature sensors
- Target temperature sensors  
- Operation mode sensors
- Week program sensors
- System status sensor

Perfect for automating your Roth heating system with Home Assistant!