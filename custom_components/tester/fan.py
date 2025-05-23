from __future__ import annotations
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.fan import (
    SUPPORT_DIRECTION,
    SUPPORT_OSCILLATE,
    SUPPORT_SET_SPEED,
    FanEntity,
)
from homeassistant.helpers.config_validation import (PLATFORM_SCHEMA)

_LOGGER = logging.getLogger(__name__)

"""Переменные для вентилятора, считываемые из конфига"""
CONF_NAME = "name"
CONF_SPEED = "speed"
CONF_SPEED_COUNT = "speed_count"
CONF_OSCILLATE = "oscillate"
CONF_DIRECTION = "direction"
CONF_MODES = "modes"
CONF_INITIAL_AVAILABILITY = "initial_availability"

"""Значения по умолчанию"""
DEFAULT_INITIAL_AVAILABILITY = True

"""Схема платформы вентилятора"""
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Optional(CONF_SPEED, default=False): cv.boolean,
    vol.Optional(CONF_SPEED_COUNT, default=0): cv.positive_int,
    vol.Optional(CONF_OSCILLATE, default=False): cv.boolean,
    vol.Optional(CONF_DIRECTION, default=False): cv.boolean,
    vol.Optional(CONF_MODES, default=[]): vol.All(cv.ensure_list, [cv.string]),
    vol.Optional(CONF_INITIAL_AVAILABILITY, default=DEFAULT_INITIAL_AVAILABILITY): cv.boolean,
})


async def async_setup_platform(_hass, config, async_add_entities, _discovery_info=None):
    """Установка платформы вентилятора"""
    fans = [TesterFan(config)]
    async_add_entities(fans, True)


class TesterFan(FanEntity):
    """Реализация вентилятора"""

    def __init__(self, config):
        """Инициализация."""
        self._name = config.get(CONF_NAME)
        self._unique_id = self._name.lower().replace(' ', '_')
        self._preset_modes = config.get(CONF_MODES, [])
        self._speed_count = config.get(CONF_SPEED_COUNT)
        if config.get(CONF_SPEED, False):
            self._speed_count = 3
        self._percentage = None
        self._preset_mode = None
        self._oscillating = None
        self._direction = None
        self._supported_features = 0
        if self._speed_count > 0:
            self._supported_features |= SUPPORT_SET_SPEED
        if config.get(CONF_OSCILLATE, False):
            self._supported_features |= SUPPORT_OSCILLATE
            self._oscillating = False
        if config.get(CONF_DIRECTION, False):
            self._supported_features |= SUPPORT_DIRECTION
            self._direction = "forward"
        self._available = config.get(CONF_INITIAL_AVAILABILITY)

        _LOGGER.info('TesterFan: {} created'.format(self._name))

    @property
    def name(self) -> str:
        """Возвращает имя"""
        return self._name

    @property
    def unique_id(self):
        """Возвращает уникальный id"""
        return self._unique_id

    @property
    def percentage(self) -> int | None:
        """Возвращает текущую скорость в процентах"""
        return self._percentage

    @property
    def speed_count(self) -> int:
        """Возвращает поддерживаемое вентилятором число скоростей."""
        return self._speed_count

    def set_percentage(self, percentage: int) -> None:
        """Задает скорость вращения в процентах"""
        self._percentage = percentage
        self._preset_mode = None
        self.schedule_update_ha_state()

    @property
    def preset_mode(self) -> str | None:
        """Возвращает текущий пресет, например авто,интервальный и т.д."""
        return self._preset_mode

    @property
    def preset_modes(self) -> list[str] | None:
        """Возвращает список доступных пресетов"""
        return self._preset_modes

    def set_preset_mode(self, preset_mode: str) -> None:
        """Задает пресет работы"""
        if preset_mode in self.preset_modes:
            self._preset_mode = preset_mode
            self._percentage = None
            self.schedule_update_ha_state()
        else:
            raise ValueError(f"Invalid preset mode: {preset_mode}")

    def available(self):
        """Возвращает True если доступено"""
        return self._available

    def set_available(self, value):
        """Задает доступность устройства"""
        self._available = value
        self.async_schedule_update_ha_state()

    def turn_on(
        self,
        speed: str = None,
        percentage: int = None,
        preset_mode: str = None,
        **kwargs,
    ) -> None:
        """Включение вентилятора"""
        if preset_mode:
            self.set_preset_mode(preset_mode)
            return

        if percentage is None:
            percentage = 67

        self.set_percentage(percentage)

    def turn_off(self, **kwargs) -> None:
        """Выключение вентилятора"""
        self.set_percentage(0)

    def set_direction(self, direction: str) -> None:
        """Задает возможность работать в двух направлениях"""
        self._direction = direction
        self.schedule_update_ha_state()

    def oscillate(self, oscillating: bool) -> None:
        """Задает колебание вентилятора"""
        self._oscillating = oscillating
        self.schedule_update_ha_state()

    @property
    def current_direction(self) -> str:
        """Возвращает возможность работать в двух направлениях"""
        return self._direction

    @property
    def oscillating(self) -> bool:
        """Возвращает колебание вентилятора"""
        return self._oscillating

    @property
    def supported_features(self) -> int:
        """Возвращает поддерживаемые возможности"""
        return self._supported_features
