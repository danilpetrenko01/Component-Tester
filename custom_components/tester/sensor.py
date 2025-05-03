import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import DOMAIN, SensorDeviceClass
from homeassistant.const import (ATTR_ENTITY_ID,
                                 CONF_UNIT_OF_MEASUREMENT,
                                 CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                                 CONCENTRATION_PARTS_PER_MILLION,
                                 FREQUENCY_GIGAHERTZ,
                                 PERCENTAGE,
                                 POWER_VOLT_AMPERE,
                                 POWER_VOLT_AMPERE_REACTIVE,
                                 PRESSURE_HPA,
                                 SIGNAL_STRENGTH_DECIBELS,
                                 VOLUME_CUBIC_METERS,
                                 )
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from . import COMPONENT_DOMAIN, COMPONENT_SERVICES, get_entity_from_domain

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = [COMPONENT_DOMAIN]
CONF_NAME = "name"
CONF_CLASS = "class"
CONF_INITIAL_VALUE = "initial_value"
CONF_INITIAL_AVAILABILITY = "initial_availability"
CONF_PERSISTENT = "persistent"

DEFAULT_INITIAL_VALUE = 0
DEFAULT_INITIAL_AVAILABILITY = True
DEFAULT_PERSISTENT = False

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Optional(CONF_CLASS): cv.string,
    vol.Optional(CONF_INITIAL_VALUE, default=DEFAULT_INITIAL_VALUE): cv.string,
    vol.Optional(CONF_INITIAL_AVAILABILITY, default=DEFAULT_INITIAL_AVAILABILITY): cv.boolean,
    vol.Optional(CONF_PERSISTENT, default=DEFAULT_PERSISTENT): cv.boolean,
    vol.Optional(CONF_UNIT_OF_MEASUREMENT, default=""): cv.string,
})

SERVICE_SET = 'set'
SERVICE_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.comp_entity_ids,
    vol.Required('value'): cv.string,
})

UNITS_OF_MEASUREMENT = {
    SensorDeviceClass.APPARENT_POWER: POWER_VOLT_AMPERE,  # apparent power (VA)
    SensorDeviceClass.BATTERY: PERCENTAGE,  # % of battery that is left
    SensorDeviceClass.CO: CONCENTRATION_PARTS_PER_MILLION,  # ppm of CO concentration
    SensorDeviceClass.CO2: CONCENTRATION_PARTS_PER_MILLION,  # ppm of CO2 concentration
    SensorDeviceClass.HUMIDITY: PERCENTAGE,  # % of humidity in the air
    SensorDeviceClass.ILLUMINANCE: "lm",  # current light level (lx/lm)
    SensorDeviceClass.NITROGEN_DIOXIDE: CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,  # µg/m³ of nitrogen dioxide
    SensorDeviceClass.NITROGEN_MONOXIDE: CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,  # µg/m³ of nitrogen monoxide
    SensorDeviceClass.NITROUS_OXIDE: CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,  # µg/m³ of nitrogen oxide
    SensorDeviceClass.OZONE: CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,  # µg/m³ of ozone
    SensorDeviceClass.PM1: CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,  # µg/m³ of PM1
    SensorDeviceClass.PM10: CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,  # µg/m³ of PM10
    SensorDeviceClass.PM25: CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,  # µg/m³ of PM2.5
    SensorDeviceClass.SIGNAL_STRENGTH: SIGNAL_STRENGTH_DECIBELS,  # signal strength (dB/dBm)
    SensorDeviceClass.SULPHUR_DIOXIDE: CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,  # µg/m³ of sulphur dioxide
    SensorDeviceClass.TEMPERATURE: "C",  # temperature (C/F)
    SensorDeviceClass.PRESSURE: PRESSURE_HPA,  # pressure (hPa/mbar)
    SensorDeviceClass.POWER: "kW",  # power (W/kW)
    SensorDeviceClass.CURRENT: "A",  # current (A)
    SensorDeviceClass.ENERGY: "kWh",  # energy (Wh/kWh/MWh)
    SensorDeviceClass.FREQUENCY: FREQUENCY_GIGAHERTZ,  # energy (Hz/kHz/MHz/GHz)
    SensorDeviceClass.POWER_FACTOR: PERCENTAGE,  # power factor (no unit, min: -1.0, max: 1.0)
    SensorDeviceClass.REACTIVE_POWER: POWER_VOLT_AMPERE_REACTIVE,  # reactive power (var)
    SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS: CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,  # µg/m³ of vocs
    SensorDeviceClass.VOLTAGE: "V",  # voltage (V)
    SensorDeviceClass.GAS: VOLUME_CUBIC_METERS,  # gas (m³)
}


async def async_setup_platform(hass, config, async_add_entities, _discovery_info=None):
    sensors = [TesterSensor(config)]
    async_add_entities(sensors, True)

    async def async_tester_service(call):
        """Call tester service handler."""
        _LOGGER.info("{} service called".format(call.service))
        await async_tester_set_service(hass, call)

    if not hasattr(hass.data[COMPONENT_SERVICES], DOMAIN):
        _LOGGER.info("installing handlers")
        hass.data[COMPONENT_SERVICES][DOMAIN] = 'installed'
        hass.services.async_register(
            COMPONENT_DOMAIN, SERVICE_SET, async_tester_service, schema=SERVICE_SCHEMA,
        )


class TesterSensor(RestoreEntity):
    """Реализация сенсора."""

    def __init__(self, config):
        """Инициализация сенсора"""
        self._name = config.get(CONF_NAME)
        self._name = self.name[1:]
        self._unique_id = self._name.lower().replace(' ', '_')
        self._class = config.get(CONF_CLASS)
        self._state = config.get(CONF_INITIAL_VALUE)
        self._available = config.get(CONF_INITIAL_AVAILABILITY)
        self._persistent = config.get(CONF_PERSISTENT)

        # Единици измерения
        self._unit_of_measurement = config.get(CONF_UNIT_OF_MEASUREMENT)
        if not self._unit_of_measurement and self._class in UNITS_OF_MEASUREMENT.keys():
            self._unit_of_measurement = UNITS_OF_MEASUREMENT[self._class]

        _LOGGER.info('TesterSensor: %s created', self._name)

    async def async_added_to_hass(self) -> None:

        await super().async_added_to_hass()
        state = await self.async_get_last_state()
        if not self._persistent or not state:
            return
        self._state = state.state

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def device_class(self):
        """Класс сенсора."""
        return self._class

    @property
    def state(self):
        """Состояние сенсора"""
        return self._state

    def set(self, value):
        self._state = value
        self.async_schedule_update_ha_state()

    @property
    def available(self):
        """True если доступен."""
        return self._available

    def set_available(self, value):
        self._available = value
        self.async_schedule_update_ha_state()

    @property
    def extra_state_attributes(self):
        """Атрибуты состояния"""
        attrs = {
            'friendly_name': self._name,
            'unique_id': self._unique_id,
        }
        return attrs

    @property
    def unit_of_measurement(self):
        """Единицы измерения."""
        return self._unit_of_measurement


async def async_tester_set_service(hass, call):
    for entity_id in call.data['entity_id']:
        value = call.data['value']
        _LOGGER.info("{} set(value={})".format(entity_id, value))
        get_entity_from_domain(hass, DOMAIN, entity_id).set(value)
