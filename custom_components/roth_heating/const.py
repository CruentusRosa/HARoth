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

# Operation modes mapping
OPERATION_MODES = {
    0: "auto",
    1: "heat", 
    2: "auto",  # ECO mode maps to auto
    3: "off"
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