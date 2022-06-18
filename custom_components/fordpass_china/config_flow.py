import logging
from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    CONF_VEHICLE_TYPE,
    CONF_REFRESH_TOKEN
)

from .ford.fordpass import FordPass
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_SCAN_INTERVAL
)

_LOGGER = logging.getLogger(__name__)

VEHICLE_TYPES = {
    "ford": "福特派",
    "lincoln": "林肯之道"
}

AUTHENTICATION = {
    "account": "使用福特派或者林肯之道账户验证",
    "refresh_token": "使用refresh_token验证"
}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    def _already_configured(self, title):
        for entry in self._async_current_entries():
            _LOGGER.debug(entry)
            if title == entry.title:
                return True
        return False

    async def async_step_user(self, user_input=None, error=None):
        if user_input is not None:
            if user_input["auth_type"] == "account":
                return await self.async_step_account()
            else:
                return await self.async_step_token()
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("auth_type", default="refresh_token"): vol.In(AUTHENTICATION)
            }),
            errors={"base": error} if error else None
        )

    async def async_step_account(self, user_input=None, error=None):
        if user_input is not None:
            config_name = user_input[CONF_USERNAME] + "@" + VEHICLE_TYPES[user_input[CONF_VEHICLE_TYPE]]
            if self._already_configured(config_name):
                return await self.async_step_user(error="account_exist")
            session = async_create_clientsession(self.hass)
            fordpass = FordPass(
                session=session,
                username=user_input[CONF_USERNAME],
                password=user_input[CONF_PASSWORD],
                vehicle_type=user_input[CONF_VEHICLE_TYPE])
            if await fordpass.auth():
                return self.async_create_entry(
                    title=config_name,
                    data=user_input)
            else:
                return await self.async_step_account(error="cant_login")
        return self.async_show_form(
            step_id="account",
            data_schema=vol.Schema({
                vol.Required(CONF_VEHICLE_TYPE, default="ford"): vol.In(VEHICLE_TYPES),
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str
            }),
            errors={"base": error} if error else None
        )

    async def async_step_token(self, user_input=None, error=None):
        if user_input is not None:
            session = async_create_clientsession(self.hass)
            fordpass = FordPass(
                session=session,
                refresh_token=user_input[CONF_REFRESH_TOKEN],
                vehicle_type=user_input[CONF_VEHICLE_TYPE])
            if await fordpass.refresh_token():
                user_info = await fordpass.get_user_info()
                config_name = user_info["userId"] + "@" + VEHICLE_TYPES[user_input[CONF_VEHICLE_TYPE]]
                if self._already_configured(config_name):
                    return await self.async_step_token(error="account_exist")
                return self.async_create_entry(
                    title=config_name,
                    data=user_input)
            else:
                return await self.async_step_token(error="cant_auth")
        return self.async_show_form(
            step_id="token",
            data_schema=vol.Schema({
                vol.Required(CONF_VEHICLE_TYPE, default="ford"): vol.In(VEHICLE_TYPES),
                vol.Required(CONF_REFRESH_TOKEN): str
            }),
            errors={"base": error} if error else None
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):

    def __init__(self, config_entry: config_entries.ConfigEntry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        scan_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=scan_interval,
                ): vol.All(vol.Coerce(int)),
            })
        )
