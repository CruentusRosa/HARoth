"""Constants for the Roth Heating System integration."""

DOMAIN = "roth_heating"
MANUFACTURER = "Roth"
MODEL = "TouchLine"

# Configuration
CONF_HOST = "host"
CONF_SCAN_INTERVAL = "scan_interval"

# Default values
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_NAME = "Roth Heating"

# API endpoints
API_READ_ENDPOINT = "/cgi-bin/ILRReadValues.cgi"
API_WRITE_ENDPOINT = "/cgi-bin/writeVal.cgi"

# XML client information
XML_CLIENT = "IMaster6_02_00"
XML_CLIENT_VERSION = "6.02.0006"

# Operation modes mapping (fixed import issue)
from homeassistant.components.climate import HVACMode

OPERATION_MODES = {
    0: HVACMode.AUTO,
    1: HVACMode.HEAT, 
    2: HVACMode.ECO,
    3: HVACMode.OFF
}

# Operation modes reverse mapping
HVAC_MODES = {
    HVACMode.AUTO: 0,
    HVACMode.HEAT: 1,
    HVACMode.ECO: 2, 
    HVACMode.OFF: 3
}

# Week programs
WEEK_PROGRAMS = {
    0: "default",
    1: "program_1",
    2: "program_2", 
    3: "program_3",
    4: "program_4"
}

# Temperature limits
MIN_TEMP = 5.0
MAX_TEMP = 30.0
TEMP_PRECISION = 0.5

# Device info
DEVICE_INFO_IDENTIFIER = "roth_controller"
DEVICE_INFO_NAME = "Roth TouchLine Controller"
DEVICE_INFO_MODEL = "ROTH-02EF0C"