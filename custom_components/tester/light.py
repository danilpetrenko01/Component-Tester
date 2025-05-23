from __future__ import annotations
import logging
import pprint
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ATTR_HS_COLOR,
    ATTR_EFFECT,
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR,
    SUPPORT_COLOR_TEMP,
    SUPPORT_EFFECT,
    LightEntity,
)
from homeassistant.helpers.config_validation import (PLATFORM_SCHEMA)
from . import TESTER_DOMAIN

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = [TESTER_DOMAIN]

"""Переменные для лампы, считываемые из конфига"""
CONF_NAME = "name"
CONF_INITIAL_VALUE = "initial_value"
CONF_SUPPORT_BRIGHTNESS = "support_brightness"
CONF_INITIAL_BRIGHTNESS = "initial_brightness"
CONF_SUPPORT_COLOR = "support_color"
CONF_INITIAL_COLOR = "initial_color"
CONF_SUPPORT_COLOR_TEMP = "support_color_temp"
CONF_INITIAL_COLOR_TEMP = "initial_color_temp"
CONF_SUPPORT_WHITE_VALUE = "support_white_value"
CONF_INITIAL_WHITE_VALUE = "initial_white_value"
CONF_INITIAL_AVAILABILITY = "initial_availability"
CONF_SUPPORT_EFFECT = "support_effect"
CONF_INITIAL_EFFECT = "initial_effect"
CONF_INITIAL_EFFECT_LIST = "initial_effect_list"

"""Значения по умолчанию"""
DEFAULT_INITIAL_VALUE = "on"
DEFAULT_SUPPORT_BRIGHTNESS = True
DEFAULT_INITIAL_BRIGHTNESS = 255
DEFAULT_SUPPORT_COLOR = False
DEFAULT_INITIAL_COLOR = [0, 100]
DEFAULT_SUPPORT_COLOR_TEMP = False
DEFAULT_INITIAL_COLOR_TEMP = 240
DEFAULT_SUPPORT_WHITE_VALUE = False
DEFAULT_INITIAL_WHITE_VALUE = 240
DEFAULT_INITIAL_AVAILABILITY = True
DEFAULT_SUPPORT_EFFECT = False
DEFAULT_INITIAL_EFFECT = "none"
DEFAULT_INITIAL_EFFECT_LIST = ["rainbow", "none"]

"""Схема платформы лампы"""
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Optional(CONF_INITIAL_VALUE, default=DEFAULT_INITIAL_VALUE): cv.string,
    vol.Optional(CONF_SUPPORT_BRIGHTNESS, default=DEFAULT_SUPPORT_BRIGHTNESS): cv.boolean,
    vol.Optional(CONF_INITIAL_BRIGHTNESS, default=DEFAULT_INITIAL_BRIGHTNESS): cv.byte,
    vol.Optional(CONF_SUPPORT_COLOR, default=DEFAULT_SUPPORT_COLOR): cv.boolean,
    vol.Optional(CONF_INITIAL_COLOR, default=DEFAULT_INITIAL_COLOR): cv.ensure_list,
    vol.Optional(CONF_SUPPORT_COLOR_TEMP, default=DEFAULT_SUPPORT_COLOR_TEMP): cv.boolean,
    vol.Optional(CONF_INITIAL_COLOR_TEMP, default=DEFAULT_INITIAL_COLOR_TEMP): cv.byte,
    vol.Optional(CONF_SUPPORT_WHITE_VALUE, default=DEFAULT_SUPPORT_WHITE_VALUE): cv.boolean,
    vol.Optional(CONF_INITIAL_WHITE_VALUE, default=DEFAULT_INITIAL_WHITE_VALUE): cv.byte,
    vol.Optional(CONF_INITIAL_AVAILABILITY, default=DEFAULT_INITIAL_AVAILABILITY): cv.boolean,
    vol.Optional(CONF_SUPPORT_EFFECT, default=DEFAULT_SUPPORT_EFFECT): cv.boolean,
    vol.Optional(CONF_INITIAL_EFFECT, default=DEFAULT_INITIAL_EFFECT): cv.string,
    vol.Optional(CONF_INITIAL_EFFECT_LIST, default=DEFAULT_INITIAL_EFFECT_LIST): cv.ensure_list
})


async def async_setup_platform(_hass, config, async_add_entities, _discovery_info=None):
    """Установка платформы лампы"""
    lights = [TesterLight(config)]
    async_add_entities(lights, True)


class TesterLight(LightEntity):

    def __init__(self, config):
        """Инициализация лампы"""
        self._name = config.get(CONF_NAME)
        self._state = config.get(CONF_INITIAL_VALUE)
        self._unique_id = self._name.lower().replace(' ', '_')
        self._hs_color = None
        self._ct = None
        self._color_mode = None
        self._effect = None
        self._effect_list = None
        self._brightness = None
        self._features = 0
        self._color_modes = ['onoff'];
        if config.get(CONF_SUPPORT_BRIGHTNESS):
            self._features |= SUPPORT_BRIGHTNESS
            self._brightness = config.get(CONF_INITIAL_BRIGHTNESS)
            self._color_modes.append('brightness')
        if config.get(CONF_SUPPORT_COLOR):
            self._features |= SUPPORT_COLOR
            self._hs_color = config.get(CONF_INITIAL_COLOR)
            self._color_mode = "hs"
            self._color_modes.append('hs')
        if config.get(CONF_SUPPORT_COLOR_TEMP):
            self._features |= SUPPORT_COLOR_TEMP
            self._ct = config.get(CONF_INITIAL_COLOR_TEMP)
            self._color_mode = "ct"
            self._color_modes.append('color_temp')
        if config.get(CONF_SUPPORT_EFFECT):
            self._features |= SUPPORT_EFFECT
            self._effect = config.get(CONF_INITIAL_EFFECT)
            self._effect_list = config.get(CONF_INITIAL_EFFECT_LIST)
        self._available = config.get(CONF_INITIAL_AVAILABILITY)
        
        _LOGGER.info('TesterLight: %s created', self._name)

    @property
    def name(self):
        """Возвращает имя"""
        return self._name


    @property
    def unique_id(self):
        """Возвращает уникальный id"""
        return self._unique_id

    @property
    def is_on(self) -> bool:
        """Возвращает True если лампа включена"""
        return self._state.lower() == "on"

    @property
    def supported_features(self):
        """Помечает поддерживаемые опции"""
        return self._features

    @property
    def supported_color_modes(self):
        """Возвращает поддерживаемые цветовые режимы"""
        return self._color_modes

    def turn_on(self, **kwargs):
        """Включение света"""
        hs_color = kwargs.get(ATTR_HS_COLOR, None)
        if hs_color is not None and self._features & SUPPORT_COLOR:
            self._color_mode = "hs"
            self._hs_color = hs_color
            self._ct = None

        ct = kwargs.get(ATTR_COLOR_TEMP, None)
        if ct is not None and self._features & SUPPORT_COLOR_TEMP:
            self._color_mode = "ct"
            self._ct = ct
            self._hs_color = None

        brightness = kwargs.get(ATTR_BRIGHTNESS, None)
        if brightness is not None:
            self._brightness = brightness

        effect = kwargs.get(ATTR_EFFECT, None)
        if effect is not None and self._features & SUPPORT_EFFECT:
            self._effect = effect

        _LOGGER.info("turn_on: {}".format(pprint.pformat(kwargs)))
        
        self._state = "on"

    def turn_off(self, **kwargs):
        """Выключение света"""
        
        _LOGGER.info("turn_off: {}".format(pprint.pformat(kwargs)))
        
        self._state = "off"

    @property
    def brightness(self):
        """Возвращает яркость лампы"""
        return self._brightness

    @property
    def hs_color(self) -> tuple[float, float] | None:
        """Возвращает цвет в формате hs"""
        if self._color_mode == "hs":
            return self._hs_color
        return None

    @property
    def color_temp(self) -> int | None:
        """Возвращает цветовую температуру"""
        if self._color_mode == "ct":
            return self._ct
        return None

    @property
    def available(self):
        """Возвращает True если доступено"""
        return self._available

    @property
    def effect_list(self) -> list:
        """Возвращает список поддерживаемых эффектов"""
        return self._effect_list

    @property
    def effect(self) -> str:
        """Возвращает текущий эффект"""
        return self._effect

    def set_available(self, value):
        """Задает доступность устройства"""
        self._available = value
        self.async_schedule_update_ha_state()

    @property
    def extra_state_attributes(self):
        """Дополнительная информация"""

        attrs = {
            name: value for name, value in (
                ('friendly_name', self._name),
                ('brightness', self._brightness),
                ('hs_color', self._hs_color),
                ('color_temp', self._ct),
                ('color_mode', self._color_mode),
                ('effect', self._effect),
                ('effect_list', self._effect_list),
                ('available', self._available),
            ) if value is not None
        }

        return attrs
