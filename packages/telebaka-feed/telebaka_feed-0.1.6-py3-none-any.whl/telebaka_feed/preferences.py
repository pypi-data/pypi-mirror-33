from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import StringPreference


feed = Section('feed')


@global_preferences_registry.register
class VKAPIToken(StringPreference):
    section = feed
    name = 'vk_api_token'
    default = ''
