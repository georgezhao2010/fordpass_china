import math
import logging
import asyncio
from .ford.fordpass import FordPass, CommandResult
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta
import async_timeout


_LOGGER = logging.getLogger(__name__)

PI = 3.1415926536


def transformlat(x, y):
    ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * PI) + 20.0 * math.sin(2.0 * x * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(y * PI) + 40.0 * math.sin(y / 3.0 * PI)) * 2.0 / 3.0
    ret += (160.0 * math.sin(y / 12.0 * PI) + 320 * math.sin(y * PI / 30.0)) * 2.0 / 3.0
    return ret


def transformlon(x, y):
    ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * PI) + 20.0 * math.sin(2.0 * x * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(x * PI) + 40.0 * math.sin(x / 3.0 * PI)) * 2.0 / 3.0
    ret += (150.0 * math.sin(x / 12.0 * PI) + 300.0 * math.sin(x / 30.0 * PI)) * 2.0 / 3.0
    return ret


def gps_unshift(wglat, wglon):
    a = 6378245.0
    ee = 0.00669342162296594323
    dlat = transformlat(wglon - 105.0, wglat - 35.0)
    dlon = transformlon(wglon - 105.0, wglat - 35.0)
    radlat = wglat / 180.0 * PI
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * PI)
    dlon = (dlon * 180.0) / (a / sqrtmagic * math.cos(radlat) * PI)
    mglat = wglat - dlat
    mglon = wglon - dlon

    return mglat, mglon


class FordVehicle(DataUpdateCoordinator):
    def __init__(self, hass, fordpass: FordPass, vehicle_info, update_interval):
        super().__init__(
            hass,
            _LOGGER,
            name=vehicle_info["vin"],
            update_interval=timedelta(minutes=update_interval)
        )
        self._fordpass = fordpass
        self._vin = vehicle_info["vin"]
        self._model = vehicle_info["modelName"]
        self._year = vehicle_info["modelYear"]
        self._vehicle_name = vehicle_info["nickName"]

    async def _async_update_data(self):
        _LOGGER.debug("Data updating...")
        data = None
        try:
            async with async_timeout.timeout(20):
                data = await self._fordpass.get_vehicle_status(self._vin)
                if data is not None:
                    if "gps" in data and "latitude" in data["gps"] and "longitude" in data["gps"]:
                        wglat = float(data["gps"]["latitude"])
                        wglon = float(data["gps"]["longitude"])
                        data["gps"]["latitude"], data["gps"]["longitude"] = gps_unshift(wglat, wglon)
                else:
                    raise UpdateFailed("Failed to data update")
        except asyncio.TimeoutError:
            _LOGGER.warning("Data update timed out")
        return data

    def set_update_interval(self, update_interval):
        _LOGGER.debug(f"Data update interval set to {update_interval} minutes")
        self.update_interval = timedelta(minutes=update_interval)

    @property
    def vin(self) -> str:
        return self._vin

    @property
    def model(self) -> str:
        return self._model

    @property
    def year(self) -> str:
        return self._year

    @property
    def vehicle_name(self) -> str:
        return self._vehicle_name

    async def _check_command(self, commandid, end_point):
        while True:
            result = await self._fordpass.async_get_switch_completed(self.vin, end_point, commandid)
            if result == CommandResult.PENDING:
                await asyncio.sleep(1)
                continue
            else:
                if result == CommandResult.SUCCESS:
                    await self.async_refresh()
                return

    async def async_set_switch(self, end_point, turn_on):
        commandid = await self._fordpass.async_set_switch(self.vin, end_point, turn_on)
        if commandid:
            self.hass.loop.create_task(self._check_command(commandid, end_point))
