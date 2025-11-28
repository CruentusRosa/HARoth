# Roth Heating System - Home Assistant Custom Component

Complete Home Assistant integration for Roth TouchLine heating systems with advanced sensors and robust climate control.

## 🌟 Features

- **Full Climate Control**: Complete temperature and mode control for all zones
- **Comprehensive Sensors**: Temperature, heating status, operation modes, and system monitoring  
- **HACS Compatible**: Easy installation and updates via Home Assistant Community Store
- **Smart Data Coordination**: Intelligent updates with configurable intervals
- **Robust Error Handling**: Extensive logging and error recovery
- **Device Organization**: Proper device identification and organization in Home Assistant

## 📋 Supported Entities

### Climate Entities
- Temperature control (5°C - 30°C) with 0.5°C precision
- HVAC modes: Auto, Heat, Off
- Current and target temperature display
- Zone-specific device information

### Sensor Entities
**Per Zone:**
- Current Temperature - Real-time temperature readings
- Target Temperature - Set point temperature  
- Heating Status - Active heating state (Heating/Demand/Satisfied/Off)
- Operation Mode - Current mode (auto/heat/eco/off)

**System Level:**
- System Status - Overall system health (OK/Warning/Error/Active)
- Connection Status - Controller connectivity monitoring
- Zone count and activity statistics

## 🚀 Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner and select "Custom repositories"
4. Add this repository URL: `https://github.com/CruentusRosa/HARoth`
5. Category: "Integration"
6. Click "Add"
7. Search for "Roth Heating System" and install it
8. Restart Home Assistant
9. Go to Configuration → Integrations
10. Click "Add Integration" and search for "Roth Heating System"
11. **Enter your Roth controller IP address** (e.g., 192.168.86.29)

### Manuel Installation (Alternativ)

Hvis du ikke kan bruge HACS, kan du installere integrationen manuelt:

1. Download eller klon dette repository.
2. Kopiér `roth_heating` mappen ind i din `custom_components` mappe i din Home Assistant konfigurationsmappe.
   - Strukturen skal være: `custom_components/roth_heating/` med alle filer inde i `roth_heating` mappen.
   - Sørg for at alle filer er kopieret korrekt (inkl. `config_flow.py`, `manifest.json`, etc.)
3. Genstart Home Assistant (Settings → ⋮ → Restart Home Assistant → Restart).
4. [Konfigurer](#konfiguration) Roth Heating gennem Settings → Devices & Services → Add Integration.
   * **Config Flow Link** (virker kun hvis du har Home Assistant Companion app installeret):  
   [![Open your Home Assistant instance and start setting up Roth Heating System](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=roth_heating)
   * **Manuel metode**: Gå til Settings → Devices & Services → Add Integration → Søg efter "Roth Heating System"
5. **Indtast din Roth controller IP-adresse** (f.eks. 192.168.86.29)

> **Bemærk**: HACS er stærkt anbefalet, da det gør opdateringer meget nemmere.

## Features

- **Climate Entities**: Full climate control for each heating zone
- **Temperature Sensors**: Current and target temperature monitoring  
- **Operation Mode Control**: AUTO, HEAT, ECO, OFF modes
- **System Status**: Overall system health monitoring
- **Real-time Updates**: Configurable polling interval (default 30s)

## Konfiguration

Integrationen understøtter konfiguration gennem brugergrænsefladen. Du skal kun angive:

- **Host**: IP-adressen på din Roth controller (f.eks. 192.168.86.29)
- **Opdateringsinterval**: Hvor ofte der skal hentes opdateringer (valgfrit, standard 30 sekunder)

## Entities Created

### Climate Entities
For each heating zone:
- `climate.roth_[zone_name]` - Full climate control

### Sensor Entities  
For each zone:
- `sensor.roth_[zone_name]_current_temperature`
- `sensor.roth_[zone_name]_target_temperature` 
- `sensor.roth_[zone_name]_operation_mode`
- `sensor.roth_[zone_name]_week_program`

System sensors:
- `sensor.roth_system_status`

## Services

The integration provides standard Home Assistant climate services:
- `climate.set_temperature`
- `climate.set_hvac_mode`

## Automation Example

```yaml
automation:
  - alias: "Lower heating at night"
    trigger:
      platform: time
      at: "22:00:00"
    action:
      service: climate.set_hvac_mode
      target:
        entity_id: climate.roth_stue
      data:
        hvac_mode: eco
```

## Based on Original Implementation

This custom component is built on the proven base implementation that includes:
- Raw HTTP communication with Roth TouchLine controllers
- Complete API coverage for read/write operations
- Magic numbers decoding for operation modes
- Real-time temperature monitoring
- No authentication required (open access model)

## Supported Models

- Roth TouchLine controllers with SpiderControl SCADA
- ROTH-02EF0C and similar models
- Any Roth controller supporting the standard XML API

## Troubleshooting

- Ensure your Roth controller is accessible on your network
- Check that the IP address is correct
- Verify your controller supports the TouchLine API
- Check Home Assistant logs for detailed error messages