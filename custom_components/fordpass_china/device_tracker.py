from homeassistant.components.device_tracker import SOURCE_TYPE_GPS
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from .baseentity import FordpassEntity
from .const import FORD_VEHICLES


async def async_setup_entry(hass, config_entry, async_add_entities):
    vehicles = []
    for vehicle in hass.data[config_entry.entry_id][FORD_VEHICLES]:
        dev = FordVehicleTracker(vehicle)
        vehicles.append(dev)
    async_add_entities(vehicles)


class FordVehicleTracker(FordpassEntity, TrackerEntity):
    @property
    def source_type(self) -> str:
        return SOURCE_TYPE_GPS

    @property
    def latitude(self):
        return self.coordinator.data["gps"]["latitude"]

    @property
    def longitude(self):
        return self.coordinator.data["gps"]["longitude"]

    @property
    def name(self):
        return self.coordinator.vehicle_name

    @property
    def icon(self):
        return "mdi:car-sports"
