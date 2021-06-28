from .baseentity import FordpassEntity
from .baseentity import VEHICLE_STATUS

from .const import (
    DOMAIN,
    FORD_VEHICLES,
    STATES_MANAGER
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    sensors = []
    states_manager = hass.data[config_entry.entry_id][STATES_MANAGER]
    for single_vehicle in hass.data[config_entry.entry_id][FORD_VEHICLES]:
        for key in VEHICLE_STATUS:
            r_sensor = FordVehiCleSensor(states_manager, single_vehicle, key)
            sensors.append(r_sensor)
    async_add_entities(sensors)


class FordVehiCleSensor(FordpassEntity):
    @property
    def state(self):
        """Return the state of the entity."""
        value = self._vehicle.status
        for key in self._state_key["key_path"]:
            value = value[key]
        if type(value).__name__ == "float":
            return round(value, 2)
        return value

    @property
    def name(self):
        return f"{self._vehicle.name} {self._state_key['name']}"

    @property
    def unit_of_measurement(self):
        return self._state_key["unit"] if "unit" in self._state_key else None;

    @property
    def icon(self):
        return self._state_key["icon"] if "icon" in self._state_key else None;
