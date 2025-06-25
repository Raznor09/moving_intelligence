"""The Moving Intelligence component - Final Multi-Vehicle All-in-one version."""
from datetime import timedelta
import logging
import hashlib
import random
import string
import time
import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["device_tracker"]
API_HOST = "https://api-app.movingintelligence.com"
TIMEOUT = 10

class MiApiClient:
    """A minimal, self-contained API client for Moving Intelligence."""

    def __init__(self, username, apikey):
        """Initialize the API client."""
        self.username = username
        self.apikey = apikey

    async def request(self, method, path, data=None):
        """Send a signed request to the API."""
        nonce = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        timestamp = str(int(time.time()))
        signature_base = (path + self.username + nonce + timestamp + self.apikey).encode()
        signature = hashlib.sha512(signature_base).hexdigest()

        headers = {
            "X-Mi-User": self.username,
            "X-Mi-Nonce": nonce,
            "X-Mi-Timestamp": timestamp,
            "X-Signature": f"sha512 {signature}",
        }
        url = f"{API_HOST}{path}"

        async with aiohttp.ClientSession() as session:
            try:
                resp = await session.get(url, headers=headers, timeout=TIMEOUT) if method == "get" else await session.post(url, headers=headers, json=data, timeout=TIMEOUT)
                if resp.status == 401:
                    raise ConfigEntryAuthFailed("Invalid credentials provided")
                
                resp.raise_for_status()
                return await resp.json()
            except aiohttp.ClientError as err:
                _LOGGER.error("Error communicating with Moving Intelligence API: %s", err)
                return None


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Moving Intelligence from a config entry."""
    hass.data.setdefault(DOMAIN, {}).setdefault(entry.entry_id, {})
    api_client = MiApiClient(username=entry.data["username"], apikey=entry.data["apikey"])
    initial_vehicles = await api_client.request("get", "/v1/objects")
    if initial_vehicles is None:
        raise ConfigEntryNotReady("Could not connect to Moving Intelligence API during setup.")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=lambda: update_vehicles_status(hass, api_client),
        update_interval=timedelta(minutes=1),
    )
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator}
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def update_vehicles_status(hass: HomeAssistant, api_client: MiApiClient):
    """Update status for all active vehicles."""
    try:
        _LOGGER.debug("Updating status for all vehicles")
        all_vehicles_data = await api_client.request("get", "/v1/objects")
        if not all_vehicles_data:
            raise UpdateFailed("Failed to fetch vehicle list from API.")

        processed_vehicles = []

        for vehicle_data in all_vehicles_data:
            vehicle_id = vehicle_data.get('id')
            if not vehicle_id or not vehicle_data.get('licence'):
                continue

            _LOGGER.debug(f"Processing vehicle {vehicle_id}")

            odo_url = f"/v1/object/{vehicle_id}/odometer"
            odo_data = await api_client.request("get", odo_url)
            if odo_data and odo_data.get("odoInMeters"):
                km_stand = round(odo_data["odoInMeters"] / 1000)
                vehicle_data['odometer'] = km_stand
            else:
                vehicle_data['odometer'] = 0
            _LOGGER.debug(f"Odometer for {vehicle_id}: {vehicle_data.get('odometer')}")

            last_location = None
            vehicle_data['end_trip_address'] = None 
            
            periods_to_check = ['TODAY', 'YESTERDAY', 'CURRENT_WEEK']
            classifications_str = "&classifications=UNKNOWN&classifications=PRIVATE&classifications=COMMUTE&classifications=BUSINESS&classifications=CORRECTION"

            for period in periods_to_check:
                url = f"/v1/object/{vehicle_id}/detailedtrips?period={period}{classifications_str}"
                trips = await api_client.request("get", url)
                
                if trips and isinstance(trips, list):
                    last_trip = trips[-1]
                    if last_trip:
                        end_road = last_trip.get('endRoad', '')
                        end_city = last_trip.get('endCity', '')
                        full_address = f"{end_road}, {end_city}" if end_road and end_city else end_road or end_city or None
                        vehicle_data['end_trip_address'] = full_address

                        if last_trip.get('locationAndSpeed'):
                            last_location = last_trip['locationAndSpeed'][-1]
                            _LOGGER.debug(f"Found last location for vehicle {vehicle_id}")
                            break
            
            if last_location and 'lat' in last_location and 'lon' in last_location:
                vehicle_data['latitude'] = last_location['lat'] / 1000000.0
                vehicle_data['longitude'] = last_location['lon'] / 1000000.0
                vehicle_data['speed'] = last_location.get('speed', 0)
            else:
                vehicle_data['latitude'] = 0
                vehicle_data['longitude'] = 0
                vehicle_data['speed'] = 0

            class VehicleObject:
                pass
            
            vehicle = VehicleObject()
            vehicle.data = vehicle_data
            processed_vehicles.append(vehicle)
            
        return processed_vehicles

    except Exception as e:
        _LOGGER.exception("Error fetching data in update_vehicles_status")
        raise UpdateFailed(e) from e


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
