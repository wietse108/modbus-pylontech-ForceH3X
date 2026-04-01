"""Select platform for Pylontech Force H3X."""
from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL

# Dit vertaalt het Modbus cijfer naar leesbare tekst in Home Assistant
EMS_MODE_OPTIONS = {
    "0": "Self-Consumption",
    "1": "Back up mode",
    "2": "Off-Grid mode",
    "3": "Feed in priority mode",
    "4": "User mode",
    "5": "PN-Customer mode",
}

# Dit vertaalt de tekst weer terug naar een cijfer voor de omvormer
EMS_MODE_OPTIONS_REVERSE = {v: int(k) for k, v in EMS_MODE_OPTIONS.items()}

@dataclass
class PylontechSelectEntityDescription(SelectEntityDescription):
    """Beschrijving van een Pylontech Select entiteit."""
    register_address: int = 0
    slave_id: int = 2


SELECT_TYPES: tuple[PylontechSelectEntityDescription, ...] = (
    PylontechSelectEntityDescription(
        key="ems_mode",
        name="EMS Mode",
        icon="mdi:state-machine",
        register_address=40907,
        slave_id=2,
        options=list(EMS_MODE_OPTIONS.values()),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Pylontech select based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        PylontechSelect(coordinator, description, entry)
        for description in SELECT_TYPES
    ]

    async_add_entities(entities)


class PylontechSelect(CoordinatorEntity, SelectEntity):
    """Representation of a Pylontech select dropdown."""

    _attr_has_entity_name = True
    entity_description: PylontechSelectEntityDescription

    def __init__(
        self,
        coordinator,
        description: PylontechSelectEntityDescription,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self.entity_description = description
        
        self._attr_unique_id = f"{DOMAIN}_{entry.data['host']}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }

    @property
    def current_option(self) -> str | None:
        """Geef de huidige ingestelde optie terug."""
        raw_value = self.coordinator.data.get(self.entity_description.key)
        if raw_value is not None and str(raw_value) in EMS_MODE_OPTIONS:
            return EMS_MODE_OPTIONS[str(raw_value)]
        return None

    async def async_select_option(self, option: str) -> None:
        """Dit wordt aangeroepen als je in Home Assistant een nieuwe optie kiest."""
        int_value = EMS_MODE_OPTIONS_REVERSE.get(option)
        
        if int_value is not None:
            success = await self.coordinator.async_write_register(
                address=self.entity_description.register_address,
                value=int_value,
                slave=self.entity_description.slave_id
            )
            
            if success:
                # Update lokaal zodat de UI direct correct staat
                self.coordinator.data[self.entity_description.key] = str(int_value)
                self.async_write_ha_state()