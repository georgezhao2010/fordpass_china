import logging
from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL, ACCOUNTS
from .fordpass import FordPass

from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_SCAN_INTERVAL
)

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None, error=None):
        if user_input is not None:
            if DOMAIN in self.hass.data and ACCOUNTS in self.hass.data[DOMAIN] \
                    and user_input[CONF_USERNAME] in self.hass.data[DOMAIN][ACCOUNTS]:
                return await self.async_step_user(error="account_exist")
            fordpass = FordPass(user_input[CONF_USERNAME], user_input[CONF_PASSWORD])
            if await self.hass.async_add_executor_job(fordpass.auth):
                return self.async_create_entry(title=user_input[CONF_USERNAME], data=user_input)
            else:
                return await self.async_step_user(error="cant_login")
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str
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
