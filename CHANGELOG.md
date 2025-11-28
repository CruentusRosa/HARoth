# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2024-12-19

### Fixed
- Fixed AttributeError in sensor platform: `last_update_success_time` does not exist on coordinator
- Replaced timestamp attribute with proper connection status boolean mapping
- Resolved sensor initialization error that prevented integration from loading properly

## [1.2.0] - 2024-12-19

### Added
- Enhanced sensor architecture with multiple sensor types per zone
- New RothDataUpdateCoordinator for better data management
- Comprehensive system status monitoring
- Connection status sensor for controller connectivity
- Heating status sensor with intelligent demand detection
- Operation mode sensor with proper mode mapping
- Better device organization with per-zone device info
- Improved error handling and logging throughout
- Temperature difference calculations in heating status
- Week program information in sensor attributes

### Changed
- Restructured data coordinator for better separation of concerns
- Improved config flow with better connection validation
- Enhanced sensor naming and unique ID generation
- Better error messages in strings.json
- Optimized API communication with proper timeout handling
- Updated manifest.json to reflect new capabilities

### Fixed
- Proper coordinator usage in climate and sensor platforms
- Correct import statements and dependencies
- Better handling of device data retrieval
- Improved sensor state calculations and mapping

### Technical Improvements
- Separated coordinator logic into dedicated coordinator.py
- Enhanced sensor.py with base sensor class and proper inheritance
- Better type hints and documentation
- Improved async/await patterns throughout codebase
- More robust error handling in API communication

## [1.1.0] - 2024-12-18

### Added
- Sensor platform implementation with temperature and mode sensors
- Enhanced config flow with IP address validation
- Better error handling in config flow
- Improved strings.json for better user experience
- System status sensor for overall health monitoring

### Changed
- Updated manifest.json version
- Improved config flow validation and error messages
- Better sensor organization and naming

### Fixed
- Config flow handler registration issues
- Python import problems with HVACMode constants
- HACS caching issues through version management

## [1.0.0] - 2024-12-17

### Added
- Initial release of Roth Heating System integration
- Basic climate entity support with temperature control
- HVAC mode support (Auto, Heat, Off)  
- Config flow for easy setup via Home Assistant UI
- IP address input and configuration
- HACS compatibility with proper manifest.json
- Basic API communication with Roth TouchLine controllers
- Minimum viable product functionality

### Features
- Climate control for heating zones
- Temperature setting and reading
- Operation mode switching
- Basic error handling
- Home Assistant integration standards compliance