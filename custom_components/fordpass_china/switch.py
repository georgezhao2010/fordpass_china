from homeassistant.helpers.entity import ToggleEntity
from .baseentity import FordpassEntity
from .baseentity import VEHICLE_SWITCHES
from homeassistant.const import (
    STATE_ON,
    STATE_OFF
)

from typing import Any

from .const import (
    FORD_VEHICLES,
    STATES_MANAGER
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    switches = []
    states_manager = hass.data[config_entry.entry_id][STATES_MANAGER]
    for single_vehicle in hass.data[config_entry.entry_id][FORD_VEHICLES]:
        for key in VEHICLE_SWITCHES:
            r_switch = FordVehicleSwitch(states_manager, single_vehicle, key)
            switches.append(r_switch)
    async_add_entities(switches)

class FordVehicleSwitch(FordpassEntity, ToggleEntity):
    @property
    def state(self):
        value = self._vehicle.status
        for key in self._state_key["key_path"]:
            value = value[key]
        if value == 0:
            result = STATE_OFF
        else:
            result = STATE_ON
        return result

    @property
    def name(self):
        return f"{self._vehicle.name} {self._state_key['name']}"

    @property
    def icon(self):
        return self._state_key["icon"] if "icon" in self._state_key else None;

    @property
    def is_on(self) -> bool:
        return self._state == STATE_ON

    def turn_on(self, **kwargs: Any):
        command_id = self._vehicle.start_engine()
        if command_id is not None:
            self._state_manager.add_subscription(self._vehicle.vin, self._state_key["key"], command_id)

    def turn_off(self, **kwargs: Any):
        command_id = self._vehicle.stop_engine()
        if command_id is not None:
            self._state_manager.add_subscription(self._vehicle.vin, self._state_key["key"], command_id)