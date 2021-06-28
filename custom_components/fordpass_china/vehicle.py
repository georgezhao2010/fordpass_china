from .fordpass import FordPass
import math

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


class FordVehicle():
    def __init__(self, fordpass: FordPass, vehicle_info):
        self._fordpass = fordpass
        self._vin = vehicle_info["vin"]
        self._model = vehicle_info["modelName"]
        self._year = vehicle_info["modelYear"]
        self._name = vehicle_info["nickName"]
        self._status = []
        self._latitude = 0
        self._longitude = 0

    def refresh_status(self):
        self._status = self._fordpass.get_vehicle_status(self._vin)
        if ("vehiclestatus" in self._status
                and "gps" in self._status["vehiclestatus"]
                and "latitude" in self._status["vehiclestatus"]["gps"]
                and "longitude" in self._status["vehiclestatus"]["gps"]):
            wglat = float(self._status["vehiclestatus"]["gps"]["latitude"])
            wglon = float(self._status["vehiclestatus"]["gps"]["longitude"])
            self._latitude, self._longitude = gps_unshift(wglat, wglon)

    @property
    def is_valid(self):
        return "status" in self._status and self._status["status"] == 200

    @property
    def status(self):
        if self.is_valid and "vehiclestatus" in self._status:
            return self._status["vehiclestatus"]
        else:
            return None

    @property
    def latitude(self):
        return self._latitude

    @property
    def longitude(self):
        return self._longitude

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
    def name(self) -> str:
        return self._name

    def lock_doors(self):
        return self._fordpass.lock_doors(self._vin)

    def unlock_doors(self):
        return self._fordpass.unlock_doors(self._vin)

    def start_engine(self):
        return self._fordpass.start_engine(self._vin)

    def stop_engine(self):
        return self._fordpass.stop_engine(self._vin)

    def check_lock(self, command_id):
        return self._fordpass.check_lock(self._vin, command_id)

    def check_engine(self, command_id):
        return self._fordpass.check_engine(self._vin, command_id)
