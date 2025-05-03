import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.lock import LockEntity
from homeassistant.helpers.config_validation import (PLATFORM_SCHEMA)

_LOGGER = logging.getLogger(__name__)

CONF_NAME = "name"
CONF_INITIAL_VALUE = "initial_value"
CONF_INITIAL_AVAILABILITY = "initial_availability"
DEFAULT_INITIAL_VALUE = "locked"
DEFAULT_INITIAL_AVAILABILITY = True

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Optional(CONF_INITIAL_VALUE, default=DEFAULT_INITIAL_VALUE): cv.string,
    vol.Optional(CONF_INITIAL_AVAILABILITY, default=DEFAULT_INITIAL_AVAILABILITY): cv.boolean,
})

async def async_setup_platform(_hass, config, async_add_entities, _discovery_info=None):
    locks = [TesterLock(config)]
    async_add_entities(locks, True)

class TesterLock(LockEntity):

    def __init__(self, config):
        """Инициализация замка"""
        self._name = config.get(CONF_NAME)
        self._name = self.name[1:]
        self._unique_id = self._name.lower().replace(' ', '_')

        self._state = config.get(CONF_INITIAL_VALUE)
        self._available = config.get(CONF_INITIAL_AVAILABILITY)
        _LOGGER.info('TesterLock: {} created'.format(self._name))

    @property
    def name(self):
        return self._name


    @property
    def unique_id(self):
        return self._unique_id

    @property
    def is_locked(self):
        """Возвращает True если закрыт"""
        return self._state == "locked"

    def lock(self, **kwargs):
        self._state = 'locked'

    def unlock(self, **kwargs):
        self._state = 'unlocked'

    def open(self, **kwargs):
        pass

    @property
    def available(self):
        """Возвращает True если доступен"""
        return self._available

    def set_available(self, value):
        self._available = value
        self.async_schedule_update_ha_state()

    @property
    def extra_state_attributes(self):
        """Возвращает атрибуты состояния устройства"""
        attrs = {
            'friendly_name': self._name,
            'unique_id': self._unique_id,
        }
        return attrs
