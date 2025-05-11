import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import DOMAIN, SensorDeviceClass
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_DEVICE_CLASS,
    ATTR_UNIT_OF_MEASUREMENT,
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_MILLION,
    CONF_UNIT_OF_MEASUREMENT,
    LIGHT_LUX,
    PERCENTAGE,
    POWER_VOLT_AMPERE_REACTIVE,
    SIGNAL_STRENGTH_DECIBELS,
    UnitOfApparentPower,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfPressure,
    UnitOfVolume,
)
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from . import TESTER_DOMAIN, TESTER_SERVICES, get_entity

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = [TESTER_DOMAIN]

"""Переменные для сенсора, считываемые из конфига"""
CONF_NAME = "name"
CONF_CLASS = "class"
CONF_INITIAL_VALUE = "initial_value"
CONF_INITIAL_AVAILABILITY = "initial_availability"

"""Значения по умолчанию"""
DEFAULT_INITIAL_VALUE = 0 
DEFAULT_INITIAL_AVAILABILITY = True
DEFAULT_PERSISTENT = False

"""Схема платформы замка"""
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({ 
    vol.Required(CONF_NAME): cv.string,
    vol.Optional(CONF_CLASS): cv.string,
    vol.Optional(CONF_INITIAL_VALUE, default=DEFAULT_INITIAL_VALUE): cv.string,
    vol.Optional(CONF_INITIAL_AVAILABILITY, default=DEFAULT_INITIAL_AVAILABILITY): cv.boolean,
    vol.Optional(CONF_UNIT_OF_MEASUREMENT, default=""): cv.string,
})

"""Сервис и его схема"""
SERVICE_SET = 'set'
SERVICE_SCHEMA = vol.Schema({ 
    vol.Required(ATTR_ENTITY_ID): cv.comp_entity_ids,
    vol.Required('value'): cv.string,
})

"""Единицы измерения для различных классов сенсора"""
UNITS_OF_MEASUREMENT = { 
    SensorDeviceClass.APPARENT_POWER: UnitOfApparentPower.VOLT_AMPERE,  
    SensorDeviceClass.BATTERY: PERCENTAGE, 
    SensorDeviceClass.CO: CONCENTRATION_PARTS_PER_MILLION,  
    SensorDeviceClass.CO2: CONCENTRATION_PARTS_PER_MILLION,  
    SensorDeviceClass.CURRENT: UnitOfElectricCurrent.AMPERE, 
    SensorDeviceClass.ENERGY: UnitOfEnergy.KILO_WATT_HOUR,  
    SensorDeviceClass.FREQUENCY: UnitOfFrequency.GIGAHERTZ, 
    SensorDeviceClass.GAS: UnitOfVolume.CUBIC_METERS,  
    SensorDeviceClass.HUMIDITY: PERCENTAGE,  
    SensorDeviceClass.ILLUMINANCE: LIGHT_LUX,  
    SensorDeviceClass.NITROGEN_DIOXIDE: CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,  
    SensorDeviceClass.NITROGEN_MONOXIDE: CONCENTRATION_MICROGRAMS_PER_CUBIC_METER, 
    SensorDeviceClass.NITROUS_OXIDE: CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,  
    SensorDeviceClass.OZONE: CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,  
    SensorDeviceClass.PM1: CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,  
    SensorDeviceClass.PM10: CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,  
    SensorDeviceClass.PM25: CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,  
    SensorDeviceClass.SIGNAL_STRENGTH: SIGNAL_STRENGTH_DECIBELS,  
    SensorDeviceClass.SULPHUR_DIOXIDE: CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,  
    SensorDeviceClass.TEMPERATURE: "C",  
    SensorDeviceClass.PRESSURE: UnitOfPressure.HPA, 
    SensorDeviceClass.POWER: UnitOfPower.KILO_WATT,     
    SensorDeviceClass.POWER_FACTOR: PERCENTAGE,  
    SensorDeviceClass.REACTIVE_POWER: POWER_VOLT_AMPERE_REACTIVE, 
    SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS: CONCENTRATION_MICROGRAMS_PER_CUBIC_METER, 
    SensorDeviceClass.VOLTAGE: UnitOfElectricPotential.VOLT,  
}


async def async_setup_platform(hass, config, async_add_entities, _discovery_info=None):
    """Установка платформы сенсора"""
    sensors = [TesterSensor(config)] 
    async_add_entities(sensors, True)

    async def async_tester_service(call):
        """Вызов сервисов"""
        
        _LOGGER.info("{} service called".format(call.service))
        
        await async_tester_set_service(hass, call)

    if not hasattr(hass.data[TESTER_SERVICES], DOMAIN):
         """Установки сервисов, в случае их отсутствия"""
    
        _LOGGER.info("installing handlers")
        
        hass.data[TESTER_SERVICES][DOMAIN] = 'installed'
        hass.services.async_register(
            TESTER_DOMAIN, SERVICE_SET, async_tester_service, schema=SERVICE_SCHEMA,
        )


class TesterSensor(RestoreEntity):
    """Реализация сенсора."""

    def __init__(self, config):
        """Инициализация сенсора"""
        self._name = config.get(CONF_NAME)
        self._unique_id = self._name.lower().replace(' ', '_')
        self._class = config.get(CONF_CLASS)
        self._state = config.get(CONF_INITIAL_VALUE)
        self._available = config.get(CONF_INITIAL_AVAILABILITY)
        self._unit_of_measurement = config.get(CONF_UNIT_OF_MEASUREMENT)
        if not self._unit_of_measurement and self._class in UNITS_OF_MEASUREMENT.keys():
            self._unit_of_measurement = UNITS_OF_MEASUREMENT[self._class]

        _LOGGER.info('TesterSensor: %s created', self._name)

    @property
    def name(self):
        """Возвращает имя"""
        return self._name

    @property
    def unique_id(self):
         """Возвращает уникальный id"""
        return self._unique_id

    @property
    def device_class(self):
        """Возвращает класс сенсора"""
        return self._class

    @property
    def state(self):
        """Возвращает значение сенсора"""
        return self._state

    def set(self, value):
        """Задает значение сенсора"""
        self._state = value
        self.async_schedule_update_ha_state()

    @property
    def available(self):
        """Возвращает True если доступен"""
        return self._available

    def set_available(self, value):
        """Задает доступность устройства"""
        self._available = value
        self.async_schedule_update_ha_state()

    @property
    def extra_state_attributes(self):
        """Дополнительная информация"""
        attrs = {
            'friendly_name': self._name,
            'unique_id': self._unique_id,
        }
        return attrs

    @property
    def unit_of_measurement(self):
        """Возвращает единицы измерения"""
        return self._unit_of_measurement


async def async_tester_set_service(hass, call):
    for entity_id in call.data['entity_id']:
        """Сервис установки значения сенсора"""
        value = call.data['value']
        
        _LOGGER.info("{} set(value={})".format(entity_id, value))
        
        get_entity(hass, DOMAIN, entity_id).set(value)
