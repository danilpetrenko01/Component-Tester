import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.binary_sensor import (BinarySensorEntity, DOMAIN)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.helpers.config_validation import (PLATFORM_SCHEMA)
from . import TESTER_DOMAIN, TESTER_SERVICES, get_entity

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = [TESTER_DOMAIN]

"""Переменные для бинарного сенсора, считываемые из конфига"""
CONF_NAME = "name"
CONF_CLASS = "class"
CONF_INITIAL_VALUE = "initial_value"
CONF_INITIAL_AVAILABILITY = "initial_availability"

"""Значения по умолчанию"""
DEFAULT_INITIAL_VALUE = "off"
DEFAULT_INITIAL_AVAILABILITY = True

"""Схема платформы бинарного сенсора"""
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Optional(CONF_CLASS): cv.string,
    vol.Optional(CONF_INITIAL_VALUE, default=DEFAULT_INITIAL_VALUE): cv.string,
    vol.Optional(CONF_INITIAL_AVAILABILITY, default=DEFAULT_INITIAL_AVAILABILITY): cv.boolean,
})

"""Сервисы и их схема"""
SERVICE_ON = 'turn_on'
SERVICE_OFF = 'turn_off'
SERVICE_TOGGLE = 'toggle'
SERVICE_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.comp_entity_ids,
})


async def async_setup_platform(hass, config, async_add_entities, _discovery_info=None):
    """Установка платформы бинарного сенсора"""
    sensors = [TesterBinarySensor(config)]
    async_add_entities(sensors, True)

    async def async_tester_service(call):
        """Вызов сервисов"""
        
        _LOGGER.info("{} service called".format(call.service))
        
        if call.service == SERVICE_ON:
            await async_tester_on_service(hass, call)
        if call.service == SERVICE_OFF:
            await async_tester_off_service(hass, call)
        if call.service == SERVICE_TOGGLE:
            await async_tester_toggle_service(hass, call)
 
    if not hasattr(hass.data[TESTER_SERVICES], DOMAIN):
        """Установки сервисов, в случае их отсутствия"""
        _LOGGER.info("installing handlers")
        
        hass.data[TESTER_SERVICES][DOMAIN] = 'installed'
        hass.services.async_register(
            TESTER_DOMAIN, SERVICE_ON, async_tester_service, schema=SERVICE_SCHEMA,
        )
        hass.services.async_register(
            TESTER_DOMAIN, SERVICE_OFF, async_tester_service, schema=SERVICE_SCHEMA,
        )
        hass.services.async_register(
            TESTER_DOMAIN, SERVICE_TOGGLE, async_tester_service, schema=SERVICE_SCHEMA,
        )


class TesterBinarySensor(BinarySensorEntity):
    """Реализация бинарного сенсора"""
    def __init__(self, config):
        """Инициализация"""
        self._name = config.get(CONF_NAME)
        self._class = config.get(CONF_CLASS)
        self._state = config.get(CONF_INITIAL_VALUE)
        self._available = config.get(CONF_INITIAL_AVAILABILITY)
        self._unique_id = self._name.lower().replace(' ', '_')

        _LOGGER.info('TesterBinarySensor: %s created', self._name)

    @property
    def name(self):
        """Возвращает имя"""
        return self._name
        

    @property
    def unique_id(self):
        """Возвращает уникальный Id"""
        return self._unique_id

    @property
    def device_class(self):
        """Возвращает класс сенсора"""
        return self._class

    @property
    def is_on(self):
        """Возвращает True если включен"""
        return self._state == 'on'

    @property
    def available(self):
        """Возвращает True если доступено"""
        return self._available

    def set_available(self, value):
        """Задает доступность устройства"""
        self._available = value
        self.async_schedule_update_ha_state()

    def turn_on(self):
        """Включение устройства"""
        self._state = 'on'
        self.async_schedule_update_ha_state()

    def turn_off(self):
        """Выключение устройства"""
        self._state = 'off'
        self.async_schedule_update_ha_state()

    def toggle(self):
        """Переключение устройства"""
        if self.is_on:
            self.turn_off()
        else:
            self.turn_on()

    @property
    def extra_state_attributes(self):
        """Дополнительная информация"""
        attrs = {
            'friendly_name': self._name,
            'unique_id': self._unique_id,
        }
        return attrs


async def async_tester_on_service(hass, call):
    for entity_id in call.data['entity_id']:
        """Сервис включения бинарного сенсора"""
    
        _LOGGER.info("{} turning on".format(entity_id))
        
        get_entity(hass, DOMAIN, entity_id).turn_on()


async def async_tester_off_service(hass, call):
    for entity_id in call.data['entity_id']:
        """Сервис выключения бинарного сенсора"""
    
        _LOGGER.info("{} turning off".format(entity_id))
        
        get_entity(hass, DOMAIN, entity_id).turn_off()


async def async_tester_toggle_service(hass, call):
    for entity_id in call.data['entity_id']:
        """Сервис переключения бинарного сенсора"""
    
        _LOGGER.info("{} toggling".format(entity_id))
        
        get_entity(hass, DOMAIN, entity_id).toggle()
