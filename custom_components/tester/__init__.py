import logging
from distutils import util
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.service import verify_domain_control
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.exceptions import HomeAssistantError
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

TESTER_DOMAIN = 'tester'
TESTER_SERVICES = 'tester-services'

SERVICE_AVAILABILE = 'set_available'
SERVICE_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.comp_entity_ids,
    vol.Required('value'): cv.boolean,
})

async def async_setup(hass, config):
    """Установки интеграции"""
    hass.data[TESTER_SERVICES] = {}
    
    _LOGGER.debug('setup')
    
    @verify_domain_control(hass, TESTER_DOMAIN)
    async def async_tester_service_set_available(call) -> None:
        """вызов сервисов."""
        _LOGGER.info("{} service called".format(call.service))
        await async_tester_set_availability_service(hass, call)
    hass.services.async_register(TESTER_DOMAIN, SERVICE_AVAILABILE, async_tester_service_set_available)
    return True


def get_entity(hass, domain, entity_id):
    component = hass.data.get(domain)
    if component is None:
        raise HomeAssistantError("{} component not set up".format(domain))
    entity = component.get_entity(entity_id)
    if entity is None:
        raise HomeAssistantError("{} not found".format(entity_id))
    return entity

async def async_tester_set_availability_service(hass, call):
    entity_id = call.data['entity_id']
    value = call.data['value']
    if not type(value)==bool:
        value = bool(util.strtobool(value))
    domain = entity_id.split(".")[0]
    
    _LOGGER.info("{} set_avilable(value={})".format(entity_id, value))
    
    get_entity(hass, domain, entity_id).set_available(value)