import time
import json
import logging
import requests
from .const import (
                    SSO_URL,
                    CV_URL,
                    API_URL,
                    CLIENT_ID,
                    DEFAULT_HEADERS,
                    API_HEADERS
                   )

_LOGGER = logging.getLogger(__name__)


class FordPass(object):
    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._token = None
        self._refresh_token = None
        self._expires = None

    def auth(self):
        self._token = None
        self._refresh_token = None
        self._expires = None
        data = {
            "client_id": CLIENT_ID,
            "grant_type": "password",
            "username": self._username,
            "password": self._password,
        }
        headers = {
            **DEFAULT_HEADERS,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        r = requests.post(
            f"{SSO_URL}/oidc/endpoint/default/token",
            data=data,
            headers=headers,
        )
        if r.status_code == 200:
            result = r.json()
            data = {"code": result["access_token"]}
            r = requests.put(
                f"{API_URL}api/oauth2/v1/token",
                data=json.dumps(data),
                headers=API_HEADERS,
            )
            if r.status_code == 200:
                result = r.json()
                self._token = result["access_token"]
                self._refresh_token = result["refresh_token"]
                self._expires = time.time() + result["expires_in"] - 100
        return self._token is not None

    def refresh_token(self):
        data = {"refresh_token": self._refresh_token}
        r = requests.put(
            f"{API_URL}api/oauth2/v1/refresh",
            data=json.dumps(data),
            headers=API_HEADERS
        )
        if r.status_code == 200:
            result = r.json()
            self._token = result["access_token"]
            self._refresh_token = result["refresh_token"]
            self._expires = time.time() + result["expires_in"] - 100
        elif r.status_code == 401:
            self.auth()

    def check_token(self):
        if self._expires:
            if time.time() > self._expires:
                self.refresh_token()
        else:
            self.auth()
        return self._token is not None

    def get_user_info(self):
        result = None
        if self.check_token():
            params = {"lrdt": "01-01-1970 00:00:00"}
            headers = {
                **API_HEADERS,
                "auth-token": self._token
            }
            r = requests.get(
                f"{CV_URL}api/users", params=params, headers=headers
            )
            if r.status_code == 200:
                result = r.json()
            elif r.status_code == 401:
                if self.auth():
                    headers = {
                        **API_HEADERS,
                        "auth-token": self._token
                    }
                    r = requests.get(
                        f"{CV_URL}api/users", params=params, headers=headers
                    )
                    if r.status_code == 200:
                        result = r.json()
        return result

    def get_vehicles(self):
        result = None
        if self.check_token():
            params = {
                "language": "ZH",
                "region": "CN",
                "country": "CHN",
            }
            headers = {
                **API_HEADERS,
                "auth-token": self._token
            }
            r = requests.get(
                f"{API_URL}api/dashboard/v1/users/vehicles",
                params=params,
                headers=headers
            )
            if r.status_code == 200:
                result = r.json()
            elif r.status_code == 401:
                if self.auth():
                    headers = {
                        **API_HEADERS,
                        "auth-token": self._token
                    }
                    r = requests.get(
                        f"{API_URL}api/dashboard/v1/users/vehicles", params=params, headers=headers
                    )
                    if r.status_code == 200:
                        result = r.json()
        return result

    def get_vehicle_status(self, vin):
        result = None
        if self.check_token():
            params = {"lrdt": "01-01-1970 00:00:00"}
            headers = {
                **API_HEADERS,
                "auth-token": self._token
            }
            r = requests.get(
                f"{CV_URL}api/vehicles/v4/{vin}/status", params=params, headers=headers
            )
            if r.status_code == 200:
                result = r.json()
            elif r.status_code == 401:
                if self.auth():
                    headers = {
                        **API_HEADERS,
                        "auth-token": self._token
                    }
                    r = requests.get(
                        f"{CV_URL}vehicles/v4/{vin}/status", params=params, headers=headers
                    )
                    if r.status_code == 200:
                        result = r.json()
        _LOGGER.debug(f"New vehicle status received {result}")
        return result

    def _send_command(self, opt, url):
        if self.check_token():
            headers = {
                **API_HEADERS,
                "auth-token": self._token
            }
            r = getattr(requests, opt)(url, headers = headers)
            if r.status_code == 200:
                rjson = r.json()
                if rjson["status"] == 200:
                    return rjson["commandId"]
                else:
                    _LOGGER.debug(f"Got unexpected status code on {opt} {url} - {rjson}")
        return None

    def _send_check_command(self, url):
        if self.check_token():
            headers = {
                **API_HEADERS,
                "auth-token": self._token
            }
            r = requests.get(url, headers = headers)
            if r.status_code == 200:
                rjson = r.json()
                if rjson["status"] == 200:
                    return True
                elif rjson["status"] != 552:      # pending
                    pass
                else:
                    _LOGGER.debug(f"Got unexpected status code on get {url} - {rjson}")
        return False

    def lock_doors(self, vin):
        return self._send_command("put", f"{CV_URL}api/vehicles/v2/{vin}/doors/lock")

    def unlock_doors(self, vin):
        return self._send_command("delete", f"{CV_URL}api/vehicles/v2/{vin}/doors/lock")

    def start_engine(self, vin):
        return self._send_command("put", f"{CV_URL}api/vehicles/v2/{vin}/engine/start")

    def stop_engine(self, vin):
        return self._send_command("delete", f"{CV_URL}api/vehicles/v2/{vin}/engine/start")

    def check_lock(self, vin, command_id):
        return self._send_check_command(f"{CV_URL}api/vehicles/v2/{vin}/doors/lock/{command_id}")

    def check_engine(self, vin, command_id):
        return self._send_check_command(f"{CV_URL}api/vehicles/v2/{vin}/engine/start/{command_id}")