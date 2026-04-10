"""The Pylontech Force H3X integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_HOST, CONF_PORT
from .coordinator import PylontechCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.NUMBER, Platform.SELECT, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Pylontech Force H3X from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Get IP and PORT from config-flow
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]

    # Initialize coordinator
    coordinator = PylontechCoordinator(hass, host, port)

    
    await coordinator.async_config_entry_first_refresh()

    
    hass.data[DOMAIN][entry.entry_id] = coordinator

    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        
        coordinator = hass.data[DOMAIN][entry.entry_id]
        if coordinator.client.connected:
            coordinator.client.close()
            
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok