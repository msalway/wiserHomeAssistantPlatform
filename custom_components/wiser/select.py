import logging

from .const import (
    ATTR_TIME_PERIOD,
    DATA,
    DEFAULT_BOOST_TEMP_TIME,
    DOMAIN,
    MANUFACTURER,
    WISER_SERVICES
)

from .helpers import get_device_name, get_unique_id, get_identifier
from .schedules import WiserScheduleEntity

import voluptuous as vol
from homeassistant.const import ATTR_MODE
from homeassistant.components.select import SelectEntity
from homeassistant.core import callback
from homeassistant.helpers import entity_platform
from homeassistant.helpers.dispatcher import async_dispatcher_connect

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Wiser climate device."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]
    wiser_selects = []

    if data.wiserhub.hotwater:
        _LOGGER.debug("Setting up Hot Water mode select")
        wiser_selects.extend([WiserHotWaterModeSelect(data)])

    # Add SmartPlugs (if any)
    if data.wiserhub.devices.smartplugs.count > 0:
        _LOGGER.debug("Setting up Smartplug mode select")
        for plug in data.wiserhub.devices.smartplugs.all:
            wiser_selects.extend([
                WiserSmartPlugModeSelect(data, plug.id)
            ])
    
    if data.wiserhub.devices.lights.count > 0:
        _LOGGER.debug("Setting up Light mode select")
        for light in data.wiserhub.devices.lights.all:
            wiser_selects.extend([
                WiserLightModeSelect(data, light.id)
            ])

    if data.wiserhub.devices.shutters.count > 0:
        _LOGGER.debug("Setting up Shutter mode select")
        for shutter in data.wiserhub.devices.shutters.all:
            wiser_selects.extend([
                WiserShutterModeSelect(data, shutter.id)
            ])

    async_add_entities(wiser_selects)


    # Setup services
    platform = entity_platform.async_get_current_platform()

    if data.wiserhub.hotwater:
        platform.async_register_entity_service(
            WISER_SERVICES["SERVICE_SET_HOTWATER_MODE"],
            {
                vol.Required(ATTR_MODE): vol.In(data.wiserhub.hotwater.available_modes),
            },
            "async_set_mode"
        )

        platform.async_register_entity_service(
            WISER_SERVICES["SERVICE_BOOST_HOTWATER"],
            {
                vol.Optional(ATTR_TIME_PERIOD, default=DEFAULT_BOOST_TEMP_TIME): vol.Coerce(int),
            },
            "async_boost"
        )

    if data.wiserhub.devices.smartplugs:
        platform.async_register_entity_service(
            WISER_SERVICES["SERVICE_SET_SMARTPLUG_MODE"],
            {
                vol.Required(ATTR_MODE): vol.In(data.wiserhub.devices.smartplugs.available_modes),
            },
            "async_set_mode"
        )
    
    if data.wiserhub.devices.lights:
        platform.async_register_entity_service(
            WISER_SERVICES["SERVICE_SET_LIGHT_MODE"],
            {
                vol.Required(ATTR_MODE): vol.In(data.wiserhub.devices.lights.available_modes),
            },
            "async_set_mode"
        )
    
    if data.wiserhub.devices.shutters:
        platform.async_register_entity_service(
            WISER_SERVICES["SERVICE_SET_SHUTTER_MODE"],
            {
                vol.Required(ATTR_MODE): vol.In(data.wiserhub.devices.shutters.available_modes),
            },
            "async_set_mode"
        )


class WiserSelectEntity(SelectEntity):
    def __init__(self, data):
        """Initialize the sensor."""
        self._data = data
        _LOGGER.info(f"{self._data.wiserhub.system.name} {self.name} initalise")

    async def async_force_update(self):
        await self._data.async_update(no_throttle=True)

    @property
    def should_poll(self):
        """We don't want polling so return false."""
        return False

    @property
    def name(self):
        """Return Name of device."""
        return self._name

    @property
    def options(self) -> list[str]:
        return self._options

    @callback
    async def async_set_mode(self, mode):
        _LOGGER.error(f"Set mode service is not available on this entity")

    @callback
    async def async_boost(self, time_period: int):
        _LOGGER.error(f"Boost service is not available on this entity")

    async def async_added_to_hass(self):
        """Subscribe for update from the hub."""

        async def async_update_state():
            """Update sensor state."""
            await self.async_update_ha_state(True)

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, f"{self._data.wiserhub.system.name}-HubUpdateMessage", async_update_state
            )
        )


class WiserHotWaterModeSelect(WiserSelectEntity, WiserScheduleEntity):

    def __init__(self, data): 
        """Initialize the sensor."""
        super().__init__(data)
        self._hotwater = self._data.wiserhub.hotwater
        self._options = self._hotwater.available_modes
        self._schedule = self._hotwater.schedule

    async def async_update(self):
        """Async update method."""
        self._hotwater = self._data.wiserhub.hotwater
        self._schedule = self._hotwater.schedule
    
    @property
    def name(self):
        """Return Name of device."""
        return f"{get_device_name(self._data, 0, 'Hot Water')} Mode"

    @property
    def current_option(self) -> str:
        return self._hotwater.mode

    def select_option(self, option: str) -> None:
        _LOGGER.debug("Setting hot water mode to {option}")
        self._hotwater.mode = option
        self._hotwater.cancel_overrides()
        self.hass.async_create_task(self.async_force_update())

    @property
    def unique_id(self):
        """Return unique Id."""
        return get_unique_id(self._data, "hotwater", "mode-select", 0)

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
                "name": get_device_name(self._data, 0),
                "identifiers": {(DOMAIN, get_identifier(self._data, 0))},
                "manufacturer": MANUFACTURER,
                "model": self._data.wiserhub.system.product_type,
                "sw_version": self._data.wiserhub.system.firmware_version,
                "via_device": (DOMAIN, self._data.wiserhub.system.name),
            }

    @callback
    async def async_set_mode(self, mode):
        _LOGGER.info(f"Setting Hot Water to {mode} mode")
        await self.hass.async_add_executor_job(
            self.select_option, mode
        )
        await self.async_force_update()

    @callback
    async def async_boost(self, time_period: int):
        _LOGGER.info(f"Boosting Hot Water for {time_period}m")
        await self.hass.async_add_executor_job(
            self._data.wiserhub.hotwater.boost, time_period
        )
        await self.async_force_update()


class WiserSmartPlugModeSelect(WiserSelectEntity,WiserScheduleEntity ):

    def __init__(self, data, smartplug_id):
        """Initialize the sensor."""
        self._smartplug_id = smartplug_id
        super().__init__(data)
        self._smartplug = self._data.wiserhub.devices.smartplugs.get_by_id(self._smartplug_id)
        self._options = self._smartplug.available_modes
        self._schedule = self._smartplug.schedule


    async def async_update(self):
        """Async update method."""
        self._smartplug = self._data.wiserhub.devices.smartplugs.get_by_id(self._smartplug_id)
        self._schedule = self._smartplug.schedule
    
    @property
    def name(self):
        """Return Name of device."""
        return f"{get_device_name(self._data, self._smartplug_id)} Mode"

    @property
    def current_option(self) -> str:
        return self._smartplug.mode

    def select_option(self, option: str) -> None:
        if option and option in self._options:
            _LOGGER.debug("Setting smartplug mode to {option}")
            self._smartplug.mode = option
            self.hass.async_create_task(self.async_force_update())
        else:
            _LOGGER.error(f"{option} is not a valid Smart Plug mode.  Please choose from {self._options}")
    
    @property
    def unique_id(self):
        """Return unique ID for the plug."""
        return get_unique_id(self._data, self._smartplug.product_type, "mode-select", self._smartplug_id)

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
                "name": get_device_name(self._data, self._smartplug_id),
                "identifiers": {(DOMAIN, get_identifier(self._data, self._smartplug_id))},
                "manufacturer": MANUFACTURER,
                "model": self._smartplug.product_type,
                "sw_version": self._smartplug.firmware_version,
                "via_device": (DOMAIN, self._data.wiserhub.system.name),
            }

    @callback
    async def async_set_mode(self, mode):
        _LOGGER.info(f"Setting {self._smartplug.name} to {mode} mode")
        await self.hass.async_add_executor_job(
            self.select_option, mode
        )
        await self.async_force_update()
        

class WiserLightModeSelect(WiserSelectEntity,WiserScheduleEntity ):

    def __init__(self, data, light_id):
        """Initialize the sensor."""
        self._light_id = light_id
        super().__init__(data)
        self._light = self._data.wiserhub.devices.lights.get_by_id(self._light_id)
        self._options = self._light.available_modes
        self._schedule = self._light.schedule

        _LOGGER.info(f"{self._data.wiserhub.system.name} {self.name} init")


    async def async_update(self):
        """Async update method."""
        self._light = self._data.wiserhub.devices.lights.get_by_id(self._light_id)
        self._schedule = self._light.schedule
    
    @property
    def name(self):
        """Return Name of device."""
        return f"{get_device_name(self._data, self._light_id)} Mode"

    @property
    def current_option(self) -> str:
        return self._light.mode

    def select_option(self, option: str) -> None:
        _LOGGER.debug("Setting light mode to {option}")
        self._light.mode = option
        self.hass.async_create_task(self.async_force_update())
    
    @property
    def unique_id(self):
        """Return unique ID for the plug."""
        return get_unique_id(self._data, self._light.product_type, "mode-select", self._light_id)

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
                "name": get_device_name(self._data, self._light_id),
                "identifiers": {(DOMAIN, get_identifier(self._data, self._light_id))},
                "manufacturer": MANUFACTURER,
                "model": self._light.product_type,
                "sw_version": self._light.firmware_version,
                "via_device": (DOMAIN, self._data.wiserhub.system.name),
            }

    @callback
    async def async_set_mode(self, mode):
        _LOGGER.info(f"Setting {self._light.name} to {mode} mode")
        await self.hass.async_add_executor_job(
            self.select_option, mode
        )
        await self.async_force_update()



class WiserShutterModeSelect(WiserSelectEntity,WiserScheduleEntity ):

    def __init__(self, data, shutter_id):
        """Initialize the sensor."""
        self._shutter_id = shutter_id
        super().__init__(data)
        self._shutter = self._data.wiserhub.devices.shutters.get_by_id(self._shutter_id)
        self._options = self._shutter.available_modes
        self._schedule = self._shutter.schedule

        _LOGGER.info(f"{self._data.wiserhub.system.name} {self.name} init")


    async def async_update(self):
        """Async update method."""
        self._shutter = self._data.wiserhub.devices.shutters.get_by_id(self._shutter_id)
        self._schedule = self._shutter.schedule
  
    @property
    def name(self):
        """Return Name of device."""
        return f"{get_device_name(self._data, self._shutter_id)} Mode"

    @property
    def current_option(self) -> str:
        return self._shutter.mode

    def select_option(self, option: str) -> None:
        _LOGGER.debug("Setting shutter mode to {option}")
        self._shutter.mode = option
        self.hass.async_create_task(self.async_force_update())
  
    @property
    def unique_id(self):
        """Return unique ID for the plug."""
        return get_unique_id(self._data, self._shutter.product_type, "mode-select", self._shutter_id)

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
                "name": get_device_name(self._data, self._shutter_id),
                "identifiers": {(DOMAIN, get_identifier(self._data, self._shutter_id))},
                "manufacturer": MANUFACTURER,
                "model": self._shutter.product_type,
                "sw_version": self._shutter.firmware_version,
                "via_device": (DOMAIN, self._data.wiserhub.system.name),
            }

    @callback
    async def async_set_mode(self, mode):
        _LOGGER.info(f"Setting {self._shutter.name} to {mode} mode")
        await self.hass.async_add_executor_job(
            self.select_option, mode
        )
        await self.async_force_update()

