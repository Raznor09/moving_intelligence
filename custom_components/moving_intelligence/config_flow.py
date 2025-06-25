"""Config flow for Moving Intelligence."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant

# Importeer onze EIGEN ApiClient, niet de oude bibliotheek
from . import MiApiClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict) -> None:
    """Validate the user input allows us to connect."""
    # Gebruik onze eigen API client om de credentials te testen
    client = MiApiClient(username=data["username"], apikey=data["apikey"])
    # Doe een test-request, bv. de voertuiglijst ophalen
    if not await client.request("get", "/v1/objects"):
        # Als we None terugkrijgen, is er een fout
        raise ValueError("Cannot connect")


class MovingIntelligenceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Moving Intelligence."""

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
        errors = {}
        if user_input is not None:
            try:
                await validate_input(self.hass, user_input)
                # Check of er al een entry met deze username is
                await self.async_set_unique_id(user_input["username"])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(title=user_input["username"], data=user_input)

            except ValueError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required("username"): str, vol.Required("apikey"): str}
            ),
            errors=errors,
        )