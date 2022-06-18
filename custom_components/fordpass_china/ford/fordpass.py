from typing import Any
from aiohttp import ClientSession, ClientError
import json
import time
import logging
from enum import Enum

SSO_URL = "https://sso.ci.ford.com.cn/"
CV_URL = "https://cnapi.cv.ford.com.cn/"
API_URL = "https://cn.api.mps.ford.com.cn/"

DEFAULT_HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "en-us",
    "User-Agent": "fordpass-cn/320 CFNetwork/1331.0.7 Darwin/21.4.0",
    "Accept-Encoding": "gzip, deflate, br",
    "authorization": "Basic ZWFpLWNsaWVudDo=",
}

'''
The old application IDs

APPLICATION_ID = {
    "Ford": "46409D04-BD1B-40C6-9D51-13A52666E9F9",
    "Lincoln": "D14B573E-4C11-404B-89AD-DC1EF8C34C28"
}
'''


APPLICATION_ID = {
    "ford": "35F9024B-010E-4FE7-B202-62D941F8681C",
    "lincoln": "5EE5E683-1B71-4D6B-BAA8-F344D6672796"
}

CLIENT_ID = "6487f540-5f6b-4c04-8384-23827b00b4ba"

_LOGGER = logging.getLogger(__name__)


class CommandResult(str, Enum):
    SUCCESS = "success"
    PENDING = "pending"
    FAILED = "failed"

class FordPass(object):
    def __init__(self, session: ClientSession, username: str = None, password: str = None,
                 vehicle_type: str = "ford", refresh_token: str = None):
        vehicle_type = vehicle_type if vehicle_type in APPLICATION_ID else "ford"
        self._session = session
        self._AppID = APPLICATION_ID[vehicle_type]
        self._username = username
        self._password = password
        self._token = None
        self._refresh_token = refresh_token
        if refresh_token:
            self._expires = time.time() - 100
        else:
            self._expires = None

    def make_api_header(self, use_token=True):
        header = {
            **DEFAULT_HEADERS,
            "Content-Type": "application/json",
            "Application-Id": self._AppID
        }
        if use_token:
            header["auth-token"] = self._token
        return header

    async def access_api(self, url, method, **kwargs: Any):
        code = -1
        response = None
        r = await self._session.request(method=method, url=url, timeout=10, **kwargs)
        try:
            code = r.status
            if code == 200:
                raw = await r.read()
                response = json.loads(raw)
            else:
                _LOGGER.error(f"The URL {url} result code: {code}, reason: {r.reason}")
        except ClientError as e:
            _LOGGER.error(f"API={url}, method={method}, params={kwargs}, error={e}")
        except Exception as e:
            _LOGGER.error(f"API={url}, method={method}, params={kwargs}, error={e}")
        return code, response

    def clear_token(self):
        self._token = None
        self._refresh_token = None
        self._expires = None

    async def auth(self):
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
        code, response = await self.access_api(
            url=f"{SSO_URL}oidc/endpoint/default/token",
            method="post",
            data=data,
            headers=headers)
        if code == 200:
            data = {"ciToken": response["access_token"]}
            code, response = await self.access_api(
                url=f"{API_URL}api/token/v2/cat-with-ci-access-token",
                method="post",
                data=json.dumps(data),
                headers=self.make_api_header(use_token=False))
            if response:
                self._token = response["access_token"]
                self._refresh_token = response["refresh_token"]
                self._expires = time.time() + response["expires_in"] - 100
                return True
        return False

    async def refresh_token(self):
        if self._refresh_token:
            self._token = None
            self._expires = None
            data = {"refresh_token": self._refresh_token}
            code, response = await self.access_api(
                url=f"{API_URL}api/token/v2/cat-with-refresh-token",
                method="post",
                data=json.dumps(data),
                headers=self.make_api_header(use_token=False))
            if code == 200:
                self._token = response["access_token"]
                self._refresh_token = response["refresh_token"]
                self._expires = time.time() + response["expires_in"]
                return True
            else:
                self.clear_token()
                if code == 401:
                    return await self.auth()
                else:
                    _LOGGER.error(f"Got unexpected status code {code} when refresh token")
        else:
            _LOGGER.error(f"There is not refresh_token")
        return False

    async def check_token(self):
        if self._expires:
            if time.time() > self._expires:
                _LOGGER.debug("Token is expired， refreshing...")
                await self.refresh_token()
        else:
            await self.auth()
        return self._token is not None

    async def get_user_info(self):
        if await self.check_token():
            code, response = await self.access_api(
                url=f"{CV_URL}api/users",
                method="get",
                headers=self.make_api_header())
            if code == 200:
                return response["profile"]
        return None

    async def get_vehicles(self):
        response = None
        if await self.check_token():
            code, response = await self.access_api(
                url=f"{CV_URL}api/users/vehicles",
                method="get",
                headers=self.make_api_header())
            if code == 200:
                response = response["vehicles"]["$values"]
        return response

    async def get_vehicle_info(self, vin):
        response = None
        if await self.check_token():
            code, response = await self.access_api(
                url=f"{CV_URL}api/users/vehicles/{vin}/detail",
                method="get",
                headers=self.make_api_header())
            if code == 200:
                response = response["vehicle"]
        return response

    async def get_vehicle_status(self, vin):
        response = None
        if await self.check_token():
            code, response = await self.access_api(
                url=f"{CV_URL}api/vehicles/v5/{vin}/status",
                method="get",
                headers=self.make_api_header())
            if code == 200:
                response = response["vehiclestatus"]
        return response

    async def get_vehicle_auth_status(self, vin):
        response = None
        if await self.check_token():
            code, response = await self.access_api(
                url=f"{CV_URL}api/vehicles/{vin}/authstatus",
                method="get",
                headers=self.make_api_header())
        return response

    async def vehicle_is_authorized(self, vin):
        response = await self.get_vehicle_auth_status(vin)
        if response and "vehicleAuthorizationStatus" in response and \
                "authorization" in response["vehicleAuthorizationStatus"] and \
                response["vehicleAuthorizationStatus"]["authorization"] == "AUTHORIZED":
            return True
        return False

    async def _send_command(self, method, url):
        _LOGGER.debug(f"Send command URL:{url}, method:{method}")
        if self.check_token():
            code, response = await self.access_api(
                url=url,
                method=method,
                headers=self.make_api_header())
            if code == 200:
                return response["commandId"]
        return None

    async def _check_command(self, url):
        if self.check_token():
            code, response = await self.access_api(
                url=url,
                method="get",
                headers=self.make_api_header())
            if code == 200:
                if response["status"] == 200:
                    _LOGGER.debug(f"Command {url} is completed")
                    return CommandResult.SUCCESS
                elif response["status"] == 552:  # pending
                    _LOGGER.debug(f"Command {url} is pending")
                    return CommandResult.SUCCESS
                else:
                    _LOGGER.error(f"Got unexpected status code when get {url} - {response}")
        return CommandResult.FAILED

    async def async_set_switch(self, vin, end_point, turn_on):
        if turn_on:
            method = "put"
        else:
            method = "delete"
        return await self._send_command(
            method=method,
            url=f"{CV_URL}api/vehicles/v2/{vin}/{end_point}")

    async def async_get_switch_completed(self, vin, end_point, command_id):
        return await self._check_command(
            f"{CV_URL}api/vehicles/v2/{vin}/{end_point}/{command_id}")
