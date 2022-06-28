from homeassistant.components.lock import LockEntity
from .baseentity import FordpassSwitchEntity
from .baseentity import VEHICLE_LOCKS
from homeassistant.const import (
    STATE_LOCKED,
    STATE_UNLOCKED,
    STATE_LOCKING,
    STATE_UNLOCKING
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
        if self.coordinator.check_command_pending(
                self._state_key["op_endpoint"], turn_on=True):
            result = STATE_LOCKING
        elif self.coordinator.check_command_pending(
                self._state_key["op_endpoint"], turn_on=False):
            result = STATE_UNLOCKING
        else:
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
        await self.async_switch_on()
        self.schedule_update_ha_state()

    async def async_unlock(self, **kwargs: Any) -> None:
        await self.async_switch_off()
        self.schedule_update_ha_state()

    async def async_open(self, **kwargs: Any) -> None:
        await self.async_unlock()
