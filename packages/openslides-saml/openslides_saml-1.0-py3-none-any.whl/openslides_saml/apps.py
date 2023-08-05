import os
import sys

from django.apps import AppConfig

from . import (
    __description__,
    __license__,
    __url__,
    __verbose_name__,
    __version__,
)
from .exceptions import SamlException


class SamlAppConfig(AppConfig):
    name = 'openslides_saml'
    verbose_name = __verbose_name__
    description = __description__
    version = __version__
    license = __license__
    url = __url__
    angular_site_module = True
    js_files = [
        'static/js/openslides_saml/base.js',
        'static/js/openslides_saml/site.js',
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            import onelogin.saml2  # noqa
        except ImportError:
            raise SamlException('Could not import onelogin.saml2. Is python-saml3 installed?')

        try:
            import settings
        except ImportError:
            # When testing, we cannot import settings here..
            pass

    def ready(self):
        # Import all required stuff.
        from django.conf import settings
        from .urls import urlpatterns
        from .settings import SamlSettings

        try:
            settings_dir = os.path.dirname(os.path.abspath(settings.SETTINGS_FILEPATH))
        except AttributeError:
            raise SamlException(
                "'SETTINGS_FILEPATH' is not in your settings.py. " +
                "Would you kindly add the following line: 'SETTINGS_FILEPATH = __file__'?")

        # Instanciate the SamlSettings, if the worker is run normally. Here,
        # the class is loaded the first time and by providing the settings_path
        # the internal state is set to this path.
        if sys.argv[1] != 'create-saml-settings':
            SamlSettings(settings_dir)

        # Make the urls available for openslides
        self.urlpatterns = urlpatterns

    def get_angular_constants(self):
        from .settings import SamlSettings
        saml_settings = {
            'name': 'SAMLSettings',
            'value': SamlSettings.get_general_settings()}
        return [saml_settings]
