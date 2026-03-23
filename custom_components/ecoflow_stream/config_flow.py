"""Config Flow für EcoFlow Stream."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .api import EcoFlowApiClient
from .const import DOMAIN, CONF_ACCESS_KEY, CONF_SECRET_KEY, CONF_MAIN_SN, CONF_SECONDARY_SN

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ACCESS_KEY): str,
        vol.Required(CONF_SECRET_KEY): str,
        vol.Required(CONF_MAIN_SN): str,
        vol.Optional(CONF_SECONDARY_SN, default=""): str,
    }
)


class EcoFlowStreamConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow Handler."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_MAIN_SN])
            self._abort_if_unique_id_configured()

            api = EcoFlowApiClient(
                user_input[CONF_ACCESS_KEY],
                user_input[CONF_SECRET_KEY],
            )
            try:
                valid = await api.validate_credentials()
                if not valid:
                    errors["base"] = "invalid_credentials"
                else:
                    await api.close()
                    return self.async_create_entry(
                        title=f"EcoFlow Stream ({user_input[CONF_MAIN_SN][-4:]})",
                        data=user_input,
                    )
            except Exception:
                errors["base"] = "cannot_connect"
            finally:
                await api.close()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
