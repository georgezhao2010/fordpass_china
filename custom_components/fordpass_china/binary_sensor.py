from .baseentity import FordpassEntity
from .baseentity import VEHICLE_BINARY_SENSORS
from .const import (
    FORD_VEHICLES
)
from homeassistant.components.binary_sensor import BinarySensorEntity


async def async_setup_entry(hass, config_entry, async_add_entities):
    sensors = []
    for vehicle in hass.data[config_entry.entry_id][FORD_VEHICLES]:
        for key in VEHICLE_BINARY_SENSORS:
            r_sensor = FordVehiCleBinarySensor(vehicle, key)
            sensors.append(r_sensor)
    async_add_entities(sensors)


class FordVehiCleBinarySensor(FordpassEntity, BinarySensorEntity):
    def __init__(self, coordinator, state_key=None):
        super().__init__(coordinator, state_key)

    @property
    def device_class(self):
        return self._state_key["device_class"]

    @property
    def is_on(self):
        return False if self.get_value() == self._state_key["off_state"] else True
