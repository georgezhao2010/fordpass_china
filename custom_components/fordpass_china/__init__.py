import logging

from homeassistant.core import HomeAssistant
from .const import (
    DOMAIN,
    FORD_VEHICLES,
    STATES_MANAGER,
    DEFAULT_SCAN_INTERVAL
)

from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_SCAN_INTERVAL
)

from .fordpass import FordPass
from .vehicle import FordVehicle
from .state_manager import StateManager

_LOGGER = logging.getLogger(__name__)


async def update_listener(hass, config_entry):
    hub = hass.data[config_entry.entry_id][STATES_MANAGER]
    scan_interval = config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    if hub is not None:
        hub.set_interval(scan_interval * 60)


async def async_setup(hass: HomeAssistant, hass_config: dict):
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry):
    config = config_entry.data
    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]
    scan_interval = config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    fpass = FordPass(username, password)
    vehicles = await hass.async_add_executor_job(fpass.get_vehicles)
    if len(vehicles) > 0:
        hass.data[config_entry.entry_id] = {}
        hass.data[config_entry.entry_id][FORD_VEHICLES] = []

        for single in vehicles:
            single_vehicle = FordVehicle(fpass, single)
            await hass.async_add_executor_job(single_vehicle.refresh_status)
            if single_vehicle.is_valid:
                hass.data[config_entry.entry_id][FORD_VEHICLES].append(single_vehicle)

        s_manager = StateManager(fpass, scan_interval * 60, hass.data[config_entry.entry_id][FORD_VEHICLES])
        hass.data[config_entry.entry_id][STATES_MANAGER] = s_manager

        for platform in {"device_tracker", "sensor", "switch", "lock"}:
            hass.async_create_task(hass.config_entries.async_forward_entry_setup(
                config_entry, platform))

        s_manager.start_keep_alive()
        config_entry.add_update_listener(update_listener)
        return True
    return False