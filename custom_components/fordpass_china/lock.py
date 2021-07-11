from homeassistant.components.lock import LockEntity
from .baseentity import FordpassEntity
from .baseentity import VEHICLE_LOCKS
from homeassistant.const import (
    STATE_LOCKED,
    STATE_UNLOCKED,
)

from typing import Any

from .const import (
    FORD_VEHICLES,
    STATES_MANAGER
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    locks = []
    states_manager = hass.data[config_entry.entry_id][STATES_MANAGER]
    for single_vehicle in hass.data[config_entry.entry_id][FORD_VEHICLES]:
        for key in VEHICLE_LOCKS:
            r_lock = FordVehilleLock(states_manager, single_vehicle, key)
            locks.append(r_lock)
    async_add_entities(locks)


class FordVehilleLock(FordpassEntity, LockEntity):
    @property
    def state(self):
        value = self._vehicle.status
        for key in self._state_key["key_path"]:
            value = value[key]
        if value == "LOCKED":
            result = STATE_LOCKED
        else:
            result = STATE_UNLOCKED
        return result

    @property
    def name(self):
        return f"{self._vehicle.name} {self._state_key['name']}"

    @property
    def is_locked(self):
        return self.state == STATE_LOCKED

    def lock(self, **kwargs: Any) -> None:
        command_id = self._vehicle.lock_doors()
        if command_id is not None:
            self._state_manager.add_subscription(self._vehicle.vin, self._state_key["key"], command_id)

    def unlock(self, **kwargs: Any) -> None:
        command_id = self._vehicle.unlock_doors()
        if command_id is not None:
            self._state_manager.add_subscription(self._vehicle.vin, self._state_key["key"], command_id)

    def open(self, **kwargs: Any) -> None:
        self.unlock()