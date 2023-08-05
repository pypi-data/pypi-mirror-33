from dpaste.settings.base import *
from pathlib import Path

DEBUG = os.environ.get('DEBUG', '1') == '1'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'dpaste.db',
    }
}

SECRET_KEY = 'changeme'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INSTALLED_APPS += ('sslserver',)

# Optionally run the runserver as `manage.py runsslserver` to locally
# test correct cookie and csp behavior.
if not 'runsslserver' in sys.argv:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Personal templates folder
TEMPLATES[0]['DIRS'] += [
    str(Path(__file__).parents[1].resolve() / 'templates_personal')
]

# Replace AppConfig with Custom AppConfig

from dpaste.apps import dpasteAppConfig
from django.utils.translation import ugettext_lazy as _

class ProductionDpasteAppConfig(dpasteAppConfig):
    SLUG_LENGTH = 8
    LEXER_DEFAULT = 'js'
    EXPIRE_CHOICES = (
        ('onetime', _(u'One Time Snippet')),
        (3600, _(u'Expire in one hour')),
        (3600 * 24, _('Expire in one day')),
        (3600 * 24 * 7, _('Expire in one week')),
        (3600 * 24 * 31, _('Expire in one month')),
    )
    EXPIRE_DEFAULT = 3600 * 24 * 7

INSTALLED_APPS.remove('dpaste.apps.dpasteAppConfig')
INSTALLED_APPS.append('dpaste.settings.local.ProductionDpasteAppConfig')
