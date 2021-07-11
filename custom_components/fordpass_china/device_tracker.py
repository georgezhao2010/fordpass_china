from homeassistant.components.device_tracker import SOURCE_TYPE_GPS
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from .baseentity import FordpassEntity
from .const import STATES_MANAGER,FORD_VEHICLES


async def async_setup_entry(hass, config_entry, async_add_entities):
    vehicles = []
    states_manager = hass.data[config_entry.entry_id][STATES_MANAGER]
    for single_vehicle in hass.data[config_entry.entry_id][FORD_VEHICLES]:
        dev = FordVehicleTracker(states_manager, single_vehicle)
        vehicles.append(dev)
    async_add_entities(vehicles)


class FordVehicleTracker(FordpassEntity, TrackerEntity):
    @property
    def source_type(self) -> str:
        return SOURCE_TYPE_GPS

    @property
    def latitude(self):
        return self._vehicle.latitude

    @property
    def longitude(self):
        return self._vehicle.longitude

    @property
    def name(self):
        return self._vehicle.name

    @property
    def icon(self):
        return "mdi:car-sports"
