"""Constants for the Pylontech Force H3X integration."""
from datetime import timedelta

DOMAIN = "pylon_fh3x"
MANUFACTURER = "Pylontech"
MODEL = "Force H3X"

DEFAULT_NAME = "Pylontech Force H3X"
DEFAULT_PORT = 502
DEFAULT_SCAN_INTERVAL = 10

# polling interval for DataUpdateCoordinator
SCAN_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL)


CONF_HOST = "host"
CONF_PORT = "port"