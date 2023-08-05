import os

from django.core.management.base import BaseCommand

from ...exceptions import SamlException
from ...settings import create_saml_settings


class Command(BaseCommand):
    """
    Command to create the saml_settings.json file.
    """
    help = 'Create the saml_settings.json settings file.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-d', '--dir',
            default=None,
            help='Directory for the saml_settings.json file.'
        )

    def handle(self, *args, **options):
        settings_dir = options.get('path')

        if settings_dir is None:
            from django.conf import settings
            try:
                settings_dir = os.path.dirname(os.path.abspath(settings.SETTINGS_FILEPATH))
            except AttributeError:
                raise SamlException(
                    "'SETTINGS_FILEPATH' is not in your settings.py. " +
                    "Would you kindly add the following line: 'SETTINGS_FILEPATH = __file__'?")

        settings_path = os.path.join(settings_dir, 'saml_settings.json')
        create_saml_settings(settings_path)
