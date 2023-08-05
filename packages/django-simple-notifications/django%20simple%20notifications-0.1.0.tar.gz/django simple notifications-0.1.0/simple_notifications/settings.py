# Notifications settings file.
#
# Please consult the docs for more information about each setting.
from django.conf import settings as _settings


DEFAULTS = {
    'SHOW_NOTIFICATIONS_TO_ANONYMOUS_USER': False,
    'USE_CDN_BOOTSTRAP': True
}

settings = {"SIMPLE_NOTIFICATIONS": DEFAULTS.copy()}
settings["SIMPLE_NOTIFICATIONS"].update(getattr(_settings, "SIMPLE_NOTIFICATIONS", {}))
