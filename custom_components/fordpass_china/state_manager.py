import threading
import time
import logging

_LOGGER = logging.getLogger(__name__)


class StateManager(threading.Thread):
    def __init__(self, fordpass, scan_interval, vehicles):
        super().__init__()
        self._fordpass = fordpass
        self._interval = scan_interval
        self._vehicles = vehicles
        self._updates = {}
        self._subscription = {}
        self._run = False
        self._interval = scan_interval
        for vehicle in self._vehicles:
            self._updates[vehicle.vin] = []
            self._subscription[vehicle.vin] = None

    def update_vehicle_status(self, vehicle):
        vehicle.refresh_status()
        for update_state in self._updates[vehicle.vin]:
            update_state()

    def run(self):
        counters = {}

        for vehicle in self._vehicles:
            counters[vehicle.vin] = 0
        while self._run:
            for vehicle in self._vehicles:
                time_remaining = self._interval - counters[vehicle.vin]
                if time_remaining <= 0:
                    self.update_vehicle_status(vehicle)
                    counters[vehicle.vin] = 0
                elif self._subscription[vehicle.vin] is not None:
                    subscription = self._subscription[vehicle.vin]
                    if subscription["opt"] == "lock":
                        result = vehicle.check_lock(subscription["command_id"])
                    else:
                        result = vehicle.check_engine(subscription["command_id"])
                    if result:
                        self._subscription[vehicle.vin] = None
                        self.update_vehicle_status(vehicle)
                        counters[vehicle.vin] = 0
                else:
                    counters[vehicle.vin] = counters[vehicle.vin] + 1
            time.sleep(1)

    def start_keep_alive(self):
        self._run = True
        threading.Thread.start(self)

    def stop_gather(self):
        self._run = False
        threading.Thread.join(self)

    def set_interval(self, interval):
        self._interval = interval

    def add_update(self, vin, handler):
        self._updates[vin].append(handler)

    def add_subscription(self, vin, opt, command_id):
        self._subscription[vin] = {"opt": opt, "command_id": command_id}
