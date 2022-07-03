import logging
import homeassistant.util.dt as dt_util
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.core import HomeAssistant
from .const import (
    DOMAIN,
    FORD_VEHICLES,
    DEFAULT_SCAN_INTERVAL,
    CONF_VEHICLE_TYPE,
    CONF_REFRESH_TOKEN
)
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_SCAN_INTERVAL
)
from .ford.fordpass import FordPass
from .vehicle import FordVehicle

_LOGGER = logging.getLogger(__name__)


async def update_listener(hass, config_entry):
    update_interval = config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    for coordinator in hass.data[config_entry.entry_id][FORD_VEHICLES]:
        coordinator.set_update_interval(update_interval)


async def async_setup(hass: HomeAssistant, hass_config: dict):
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry):
    config = config_entry.data
    vehicle_type = config.get(CONF_VEHICLE_TYPE)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    refresh_token = config.get(CONF_REFRESH_TOKEN)
    session = async_create_clientsession(hass)
    scan_interval = config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    fordpass = FordPass(session=session, username=username, password=password,
                        vehicle_type=vehicle_type, refresh_token=refresh_token)

    async def async_setup_entities(now):
        try:
            if fordpass.refresh_token():
                vehicles = await fordpass.get_vehicles()
                if config_entry.entry_id not in hass.data:
                    hass.data[config_entry.entry_id] = {}
                if vehicles is not None:
                    for s_vehicle in vehicles:
                        _LOGGER.debug(f"Got vehicle: {s_vehicle}")
                        if s_vehicle["vehicleAuthorizationIndicator"] == 1 and s_vehicle["tcuEnabled"]:
                            ford_vehicle = FordVehicle(hass, fordpass, s_vehicle, scan_interval)
                            hass.data[config_entry.entry_id][FORD_VEHICLES] = []
                            hass.data[config_entry.entry_id][FORD_VEHICLES].append(ford_vehicle)
                            await ford_vehicle.async_refresh()
                    for platform in {"device_tracker", "switch", "lock", "sensor", "binary_sensor"}:
                        hass.async_create_task(hass.config_entries.async_forward_entry_setup(
                            config_entry, platform))
                    config_entry.add_update_listener(update_listener)
            else:
                _LOGGER.error("Failed to refresh token, the refresh_token is invalid")
            return
        except Exception:
            pass
        async_track_point_in_utc_time(hass, async_setup_entities, dt_util.utcnow() + 30)

    async_track_point_in_utc_time(hass, async_setup_entities, dt_util.utcnow())
    return True


async def async_unload_entry(hass: HomeAssistant, config_entry):
    del hass.data[config_entry.entry_id]
    for platform in {"device_tracker", "sensor", "switch", "lock", "binary_sensor"}:
        await hass.config_entries.async_forward_entry_unload(config_entry, platform)
    return True
