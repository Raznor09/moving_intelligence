"""Device tracker for the Moving Intelligence."""
import logging

from homeassistant.components.device_tracker import SourceType
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Set up the Moving Intelligence tracker from config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]

    trackers = []
    # Loop door alle voertuigen die de coordinator heeft gevonden
    for vehicle_obj in coordinator.data:
        # Sla voertuigen zonder data over
        if not vehicle_obj.data:
            continue
        tracker = MovingIntelligenceLocationTracker(coordinator, vehicle_obj.data)
        trackers.append(tracker)

    async_add_devices(trackers, True)


class MovingIntelligenceBaseEntity(CoordinatorEntity):
    """Base entity for Moving Intelligence tracker."""

    def __init__(self, coordinator, vehicle_data) -> None:
        super().__init__(coordinator)
        self._vehicle_data = vehicle_data
        
        self._vin = self._vehicle_data.get("chassisNumber")
        self._plate = self._vehicle_data.get("licence")
        self._make = self._vehicle_data.get("brand")
        self._model = self._vehicle_data.get("model")

        self._attr_name = f"{self._plate or 'Onbekend'} {self._make or ''} {self._model or ''}".strip()
        self._attr_unique_id = f"mi_tracker_{self._vin or self._plate}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._vin or self._plate)},
            "name": self._plate,
            "model": self._model,
            "manufacturer": self._make
        }

    @property
    def vehicle(self):
        # Vind de specifieke data voor dit voertuig in de laatste update
        for vehicle_obj in self.coordinator.data:
            if (vehicle_obj.data.get("chassisNumber") == self._vin) or (vehicle_obj.data.get("licence") == self._plate):
                return vehicle_obj.data
        return self._vehicle_data


class MovingIntelligenceLocationTracker(MovingIntelligenceBaseEntity, TrackerEntity):
    """The Moving Intelligence tracker."""

    def __init__(self, coordinator, vehicle_data) -> None:
        """Initialize the Tracker."""
        super().__init__(coordinator, vehicle_data)
        self._attr_icon = "mdi:car-estate"

    @property
    def latitude(self):
        """Return latitude value of the device."""
        return self.vehicle.get("latitude", 0)

    @property
    def longitude(self):
        """Return longitude value of the device."""
        return self.vehicle.get("longitude", 0)

    @property
    def source_type(self):
        return SourceType.GPS

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the device."""
        attributes = self.vehicle.copy()
        attributes['speed'] = self.vehicle.get('speed', 0)
        return attributes