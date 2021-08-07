import logging
from homeassistant.const import (
    LENGTH_KILOMETERS,
    POWER_VOLT_AMPERE,
    PERCENTAGE
)
from homeassistant.helpers.entity import Entity
from .const import DOMAIN
from .vehicle import FordVehicle

_LOGGER = logging.getLogger(__name__)

VEHICLE_STATUS = [
    {
        "key": "alarm",
        "name": "Alarm",
        "key_path": ["alarm", "value"],
        "icon": "mdi:bell"
    },{
        "key": "odometer",
        "name": "Odometer",
        "key_path": ["odometer", "value"],
        "icon": "mdi:car-cruise-control",
        "unit": LENGTH_KILOMETERS
    },{
        "key": "fuel",
        "name": "Fuel",
        "key_path": ["fuel", "fuelLevel"],
        "icon": "mdi:fuel",
        "unit": PERCENTAGE
    },{
        "key": "range",
        "name": "Range",
        "key_path": ["fuel", "distanceToEmpty"],
        "icon": "mdi:map-marker-distance",
        "unit": LENGTH_KILOMETERS
    },{
        "key": "battery_health",
        "name": "Battery Health",
        "key_path": ["battery", "batteryHealth", "value"],
        "icon": "mdi:car-battery"
    },{
        "key": "battery_voltage",
        "name": "Battery Voltage",
        "key_path": ["battery", "batteryStatusActual", "value"],
        "icon": "mdi:car-battery",
        "unit": POWER_VOLT_AMPERE
    },{
        "key": "oil_life",
        "name": "Oil Life",
        "key_path": ["oil", "oilLifeActual"],
        "icon": "mdi:oil",
        "unit": PERCENTAGE
    },{
        "key": "left_front_tire_pressure",
        "name": "Left Front Tire Pressure",
        "key_path": ["TPMS", "leftFrontTirePressure", "value"],
        "icon": "mdi:gauge",
        "unit": "KPa"
    },{
        "key": "right_front_tire_pressure",
        "name": "Right Front Tire Pressure",
        "key_path": ["TPMS", "rightFrontTirePressure", "value"],
        "icon": "mdi:gauge",
        "unit": "KPa"
    },{
        "key": "Left_rear_tire_pressure",
        "name": "Left Rear Tire Pressure",
        "key_path": ["TPMS", "outerLeftRearTirePressure", "value"],
        "icon": "mdi:gauge",
        "unit": "KPa"
    },{
        "key": "right_rear_tire_pressure",
        "name": "Right Rear Tire Pressure",
        "key_path": ["TPMS", "outerRightRearTirePressure", "value"],
        "icon": "mdi:gauge",
        "unit": "KPa"
    },{
        "key": "driver_window_position",
        "name": "Driver Window Position",
        "key_path": ["windowPosition", "driverWindowPosition", "value"],
        "icon": "mdi:dock-window"
    },{
        "key": "pass_window_position",
        "name": "Passenger Window Position",
        "key_path": ["windowPosition", "passWindowPosition", "value"],
        "icon": "mdi:dock-window"
    },{
        "key": "rear_driver_window_pos",
        "name": "Rear Driver Window Position",
        "key_path": ["windowPosition", "rearDriverWindowPos", "value"],
        "icon": "mdi:dock-window"
    },{
        "key": "rear_pass_window_pos",
        "name": "Rear Passenger Window Position",
        "key_path": ["windowPosition", "rearPassWindowPos", "value"],
        "icon": "mdi:dock-window"
    },{
        "key": "right_rear_door",
        "name": "Right Rear Door",
        "key_path": ["doorStatus", "rightRearDoor", "value"],
        "icon": "mdi:car-door"
    },{
        "key": "left_rear_door",
        "name": "Left Rear Door",
        "key_path": ["doorStatus", "leftRearDoor", "value"],
        "icon": "mdi:car-door"
    },{
        "key": "driver_door",
        "name": "Driver Door",
        "key_path": ["doorStatus", "driverDoor", "value"],
        "icon": "mdi:car-door"
    },{
        "key": "passenger_door",
        "name": "Passenger Door",
        "key_path": ["doorStatus", "passengerDoor", "value"],
        "icon": "mdi:car-door"
    },{
        "key": "hood_door",
        "name": "Hood",
        "key_path": ["doorStatus", "hoodDoor", "value"],
        "icon": "mdi:car-door"
    },{
        "key": "tail_gate_door",
        "name": "Tail Gate Door",
        "key_path": ["doorStatus", "tailgateDoor", "value"],
        "icon": "mdi:car-door"
    },{
        "key": "inner_tail_gate_oor",
        "name": "Inner Tail Gate Door",
        "key_path": ["doorStatus", "innerTailgateDoor", "value"],
        "icon": "mdi:car-door"
    },{
        "key": "ignition_status",
        "name": "Ignition Status",
        "key_path": ["ignitionStatus", "value"],
        "icon": "mdi:engine"
    }
]

VEHICLE_SWITCHES = [
    {
        "key": "remote_start",
        "name": "Remote Start",
        "key_path": ["remoteStartStatus", "value"],
        "icon": "mdi:engine"
    }
]

VEHICLE_LOCKS = [
    {
        "key": "lock",
        "name": "Lock",
        "key_path": ["lockStatus", "value"],
        "icon": "mdi:lock"
    }
]

class FordpassEntity(Entity):
    def __init__(self, state_manager, vehicle: FordVehicle, state_key=None):
        self._state_manager = state_manager
        self._vehicle = vehicle
        self._state_key = state_key
        self._state_manager.add_update(self._vehicle.vin, self._update_state)
        if state_key is None:
            self._unique_id = f"{DOMAIN}.{self._vehicle.vin.lower()}"
        else:
            self._unique_id = f"{DOMAIN}.{self._vehicle.vin.lower()}_{self._state_key['key']}"
        self.entity_id = self._unique_id
        self._device_info = {
            "manufacturer": "Ford Motor Company",
            "model": self._vehicle.model,
            "identifiers": {(DOMAIN, self._vehicle.vin.lower())},
            "name": self._vehicle.name,
            "sw_version": self._vehicle.year,
        }

    def _update_state(self):
        self.schedule_update_ha_state()
        #self.async_schedule_update_ha_state()

    @property
    def device_info(self):
        return self._device_info

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def should_poll(self):
        return False
