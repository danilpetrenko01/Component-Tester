import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.config_validation import (PLATFORM_SCHEMA)

_LOGGER = logging.getLogger(__name__)

"""Переменные для переключателя, считываемые из конфига"""
CONF_NAME = "name"
CONF_INITIAL_VALUE = "initial_value"
CONF_INITIAL_AVAILABILITY = "initial_availability"

"""Значения по умолчанию"""
DEFAULT_INITIAL_VALUE = "off"
DEFAULT_INITIAL_AVAILABILITY = True

"""Схема платформы замка"""
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Optional(CONF_INITIAL_VALUE, default=DEFAULT_INITIAL_VALUE): cv.string,
    vol.Optional(CONF_INITIAL_AVAILABILITY, default=DEFAULT_INITIAL_AVAILABILITY): cv.boolean,
})

async def async_setup_platform(_hass, config, async_add_entities, _discovery_info=None):
      """Установка платформы сенсора"""
    switches = [TesterSwitch(config)]
    async_add_entities(switches, True)

class TesterSwitch(SwitchEntity):
    """Реализация переключателя"""

    def __init__(self, config):
        """Инициализация переключателя"""
        self._name = config.get(CONF_NAME)
        self._unique_id = self._name.lower().replace(' ', '_')
        self._state = config.get(CONF_INITIAL_VALUE)
        self._available = config.get(CONF_INITIAL_AVAILABILITY)
        
        _LOGGER.info('TesterSwitch: {} created'.format(self._name))

    @property
    def name(self):
         """Возвращает имя"""
        return self._name

    @property
    def unique_id(self):
         """Возвращает уникальный id"""
        return self._unique_id

    @property
    def is_on(self):
        """Возвращает True если включен."""
        return self._state == "on"

    @property
    def available(self):
        """Возвращает True если доступен"""
        return self._available

    def set_available(self, value):
        """Задает доступность устройства"""
        self._available = value
        self.async_schedule_update_ha_state()

    def turn_on(self, **kwargs):
        """Включение переключателя"""
        self._state = 'on'

    def turn_off(self, **kwargs):
        """Выключение переключателя"""
        self._state = 'off'

    @property
    def extra_state_attributes(self):
        """Дополнительная информация"""
        attrs = {
            'friendly_name': self._name,
            'unique_id': self._unique_id,
        }
        return attrs
