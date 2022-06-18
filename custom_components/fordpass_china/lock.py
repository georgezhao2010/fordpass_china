from homeassistant.components.lock import LockEntity
from .baseentity import FordpassSwitchEntity
from .baseentity import VEHICLE_LOCKS
from homeassistant.const import (
    STATE_LOCKED,
    STATE_UNLOCKED,
)
from typing import Any
from .const import (
    FORD_VEHICLES
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    locks = []
    for vehicle in hass.data[config_entry.entry_id][FORD_VEHICLES]:
        for key in VEHICLE_LOCKS:
            lock = FordVehilleLock(vehicle, key)
            locks.append(lock)
    async_add_entities(locks)


class FordVehilleLock(FordpassSwitchEntity, LockEntity):
    @property
    def state(self):
        value = self.get_value()
        if value == "LOCKED":
            result = STATE_LOCKED
        else:
            result = STATE_UNLOCKED
        return result

    @property
    def is_locked(self):
        return self.state == STATE_LOCKED

    async def async_lock(self, **kwargs: Any) -> None:
        await self.switch_on()

    async def async_unlock(self, **kwargs: Any) -> None:
        await self.switch_off()

    async def async_open(self, **kwargs: Any) -> None:
        await self.async_unlock()
