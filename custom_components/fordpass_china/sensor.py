from .baseentity import FordpassEntity
from .baseentity import VEHICLE_SENSORS
from .const import (
    FORD_VEHICLES
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    sensors = []
    for vehicle in hass.data[config_entry.entry_id][FORD_VEHICLES]:
        for key in VEHICLE_SENSORS:
            r_sensor = FordVehiCleSensor(vehicle, key)
            sensors.append(r_sensor)
    async_add_entities(sensors)


class FordVehiCleSensor(FordpassEntity):
    @property
    def state(self):
        return self.get_value()

    @property
    def unit_of_measurement(self):
        return self._state_key["unit"] if "unit" in self._state_key else None;
