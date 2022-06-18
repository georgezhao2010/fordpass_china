from homeassistant.helpers.entity import ToggleEntity
from .baseentity import FordpassSwitchEntity
from .baseentity import VEHICLE_SWITCHES
from homeassistant.const import (
    STATE_ON,
    STATE_OFF
)

from typing import Any

from .const import (
    FORD_VEHICLES
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    switches = []
    for vehicle in hass.data[config_entry.entry_id][FORD_VEHICLES]:
        for key in VEHICLE_SWITCHES:
            r_switch = FordVehicleSwitch(vehicle, key)
            switches.append(r_switch)
    async_add_entities(switches)


class FordVehicleSwitch(FordpassSwitchEntity, ToggleEntity):
    @property
    def state(self):
        value = self.get_value()
        if value == 0:
            result = STATE_OFF
        else:
            result = STATE_ON
        return result

    @property
    def is_on(self) -> bool:
        return self._state == STATE_ON

    async def async_turn_on(self, **kwargs: Any):
        await self.async_switch_on()

    async def async_turn_off(self, **kwargs: Any):
        await self.async_switch_off()
