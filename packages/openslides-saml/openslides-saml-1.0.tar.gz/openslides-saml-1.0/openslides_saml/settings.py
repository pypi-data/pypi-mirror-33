import json
import os

from onelogin.saml2.settings import OneLogin_Saml2_Settings

from .exceptions import SamlException


README = """\
Take care of this folder that could contain private key. Be sure that this folder never is published.

OpenSlides SAML plugin expects that certs for the SP could be stored in this folder as:

 * sp.key     Private Key
 * sp.crt     Public cert
 * sp_new.crt Future Public cert

Also you can use other cert to sign the metadata of the SP using the:

 * metadata.key
 * metadata.crt"""


def create_saml_settings(settings_path: str, template: str=None, **context: str) -> None:
    """
    Creates the SAML settings file 'saml_settings.json'
    """
    settings_path = os.path.realpath(settings_path)
    if template is None:
        with open(os.path.join(os.path.dirname(__file__), 'saml_settings.json.tpl')) as template_file:
            template = template_file.read()

    content = template % context
    with open(settings_path, 'w') as settings_file:
        settings_file.write(content)

    # create cert folder and add thr README
    cert_dir = os.path.join(os.path.dirname(settings_path), 'certs')
    os.makedirs(cert_dir, exist_ok=True)

    # create README there
    readme_path = os.path.join(cert_dir, 'README')
    if not os.path.isfile(readme_path):
        with open(readme_path, 'w') as readme:
            readme.write(README)
        print("Written README into the certs folder: {}".format(cert_dir))
    print("Created SAML settings at: {}".format(settings_path))


class SamlSettings():
    state = {}

    def __init__(self, settings_dir=None):
        """
        When provoding the settings_path, the settings are reloaded.
        """
        if settings_dir:
            self.state['settings_dir'] = settings_dir
            self.load_settings()

    def load_settings(self):
        settings_dir = self.state['settings_dir']
        settings_path = os.path.join(settings_dir, 'saml_settings.json')
        if not os.path.isfile(settings_path):
            create_saml_settings(settings_path)

        content = None
        try:
            with open(settings_path, 'r') as settings_file:
                content = json.load(settings_file)
        except IOError:
            raise SamlException(
                "Could not read settings file located at: {}".format(settings_path))
        except json.JSONDecodeError:
            raise SamlException(
                "The settings file located at {} could not be loaded.".format(settings_path))

        # Extract general settings
        if 'generalSettings' not in content:
            raise SamlException("The saml_settings.json does not contain 'generalSettings'!")
        generalSettings = content.pop('generalSettings')

        self.check_generalSettings(generalSettings)
        self.state['generalSettings'] = generalSettings

        # Extract the attribute mapping from the json file and validate it
        if 'attributeMapping' not in content:
            raise SamlException("The saml_settings.json does not contain 'attributeMapping'!")
        mapping = content.pop('attributeMapping')

        self.check_mapping(mapping)
        self.state['mapping'] = mapping

        # Extract the custom request settings
        requestSettings = {}
        if 'requestSettings' in content:
            requestSettings = content.pop('requestSettings')
            self.check_requestSettings(requestSettings)
        self.state['requestSettings'] = requestSettings

        settings = OneLogin_Saml2_Settings(content, custom_base_path=settings_dir)
        self.state['settings'] = settings

    def check_generalSettings(self, settings):
        if not isinstance(settings, dict):
            raise SamlException('The generalSettings have to be a dict.')
        if 'loginButtonText' not in settings:
            raise SamlException('The loginButtonText is not given.')
        if not isinstance(settings['loginButtonText'], str):
            raise SamlException('The loginButtonText has to be a string.')
        if 'changePasswordUrl' not in settings:
            raise SamlException('The changePasswordUrl is not given.')
        if not isinstance(settings['changePasswordUrl'], str):
            raise SamlException('The changePasswordUrl has to be a string.')

    def check_mapping(self, mapping):
        one_lookup_true = False

        if not isinstance(mapping, dict):
            raise SamlException('The attributeMapping is not a dict.')
        for key, value in mapping.items():
            if not isinstance(key, str):
                raise SamlException('The key "{}" has to be a string.'.format(key))
            if not isinstance(value, list):
                raise SamlException('The value from key "{}" has to be a list.'.format(key))
            if not len(value) == 2:
                raise SamlException('The value from key "{}" has ot two entries.'.format(key))
            if not isinstance(value[0], str):
                raise SamlException('The first value from key "{}" has to be a string.'.format(key))
            if not isinstance(value[1], bool):
                raise SamlException('The second value from key "{}" has to be a boolean.'.format(key))
            if value[1]:
                one_lookup_true = True

        if not one_lookup_true:
            raise SamlException('At least one attribute has to be used as a lookup value.')

    def check_requestSettings(self, settings):
        if not isinstance(settings, dict):
            raise SamlException('The requestSettings have to be a dict')
        if 'https' in settings and settings['https'] not in ('on', 'off'):
            raise SamlException('The https value must be "on" or "off"')

    @classmethod
    def get(cls):
        return cls().state['settings']

    @classmethod
    def get_general_settings(cls):
        return cls().state['generalSettings']

    @classmethod
    def get_attribute_mapping(cls):
        return cls().state['mapping']

    @classmethod
    def get_request_settings(cls):
        return cls().state['requestSettings']
