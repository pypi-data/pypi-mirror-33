import inspect
import os
from typing import Dict, Optional, Tuple, TypeVar

KT = str
VT_co = TypeVar('VT_co', covariant=True)
NOT_IMPLEMENTED = 'Subclasses must implement.'
ostr = Optional[str]


__all__ = (
    'RestAuthenticator',
    'ApiKeyAuthenticator',
    'ApiKeyViaQueryAuthenticator',
    'ApiKeyViaJSONAuthenticator',
    'NoAuthenticationRestAuthenticator',
    'KeyViaFileMixin',
    'KeyFromSettingsMixin',
)


class RestAuthenticator(object):
    #: How request params are sent:
    #: - params: via query string parameters
    #: - headers: via HTTP headers
    #: - data: via POST data
    #: - json: via JSON POST data
    request_params_via = 'headers'

    def __init__(self):
        self._params = {}  # type: Dict[KT, VT_co]
        self.init_params()
        super(RestAuthenticator, self).__init__()

    def init_params(self):
        pass

    def get_request_params(self) -> Dict[KT, Optional[Dict[KT, VT_co]]]:
        if self.request_params_via == 'headers':
            return {'headers': None}
        if not self._params:
            return {self.request_params_via: None}
        return {self.request_params_via: self._params}

    def get_headers(self) -> Optional[Dict[KT, VT_co]]:
        if self.request_params_via == 'headers':
            return self._params or None
        return None


class NoAuthenticationRestAuthenticator(RestAuthenticator):
    pass


class ApiKeyAuthenticator(RestAuthenticator):
    key_name = 'App-Key'  # type: str
    key = ''  # type: str

    def init_params(self):
        self._params[self.key_name] = self.get_key()

    def get_key(self) -> str:
        """
        Return the value for the API key used for authentication.

        This method should return the value of the API key used for
        authentication. By default it returns `self.key`, which is
        generally not a good way to store authentication information.

        This method is therefore the authoritative way to obtain the actual
        value of the API key and is for developers of authenticators to
        implement more sane logic.

        :return: The API key
        """
        return self.key


class KeyViaFileMixin(object):
    keyfile = ''  # type: str

    def __init__(self, keyfile: str = None, **kwargs):
        if keyfile:
            self.keyfile = keyfile
        super(KeyViaFileMixin, self).__init__(**kwargs)

    def keyfile_exists(self) -> Tuple[bool, str]:
        if self.keyfile.startswith(os.sep):
            return os.path.exists(self.keyfile), self.keyfile

        path = os.path.join(
            os.path.dirname(inspect.getfile(self.__class__)),
            self.keyfile
        )
        return os.path.exists(path), path

    def get_key(self) -> str:
        if not self.key:
            exists, path = self.keyfile_exists()
            if exists:
                with open(path, 'rt') as f:
                    self.key = f.readline().strip()
                    f.close()
            else:
                raise OSError('Keyfile does not exist')
        return self.key


class KeyFromSettingsMixin(object):
    #: Name of the setting to import. This is assumed to be resolvable by name,
    #: unless `settings_module` is also set.
    settings_name = None  # type: ostr
    #: The module to import in dotted string form. The setting is assumed to
    #: be an attribute of this module, with the name provided in
    #: `settings_name`.
    settings_module = None  # type: ostr
    #: Django support: if this value is not None, assume settings are from
    #: Django's setting support.
    django_setting = None  # type: ostr
    #: If the referenced setting is a dict. For example, if your Django
    #: setting contains:
    #:    MYAPI = { 'apikey': 'supersecret', 'url': 'http://api.example.com' }
    #: Then `django_settings_is_dict` must be set to True and
    #: `django_setting_dict_key` to 'apikey', and finally `django_setting`
    #: must be set to 'MYAPI'.
    django_setting_is_dict = False
    #: Key to use if the setting is a dictionary. See above.
    django_setting_dict_key = ''

    def __init__(self,
                 settings_name: str=None,
                 settings_module: str=None,
                 django_setting: str=None,
                 django_setting_is_dict: bool=None,
                 django_setting_dict_key: str='', **kwargs):
        if settings_name:
            self.settings_name = settings_name
        if settings_module:
            self.settings_module = settings_module
        if django_setting:
            self.django_setting = django_setting
        if django_setting_dict_key:
            self.django_setting_dict_key = django_setting_dict_key
        if django_setting_is_dict is not None:
            self.django_setting_is_dict = django_setting_is_dict

        super(KeyFromSettingsMixin, self).__init__(**kwargs)

    def get_settings_value(self) -> str:
        if self.settings_name is not None and self.django_setting is not None:
            raise AttributeError('Both settings_name and django_setting are '
                                 'configured. This is ambigious and thus not '
                                 'supported.')
        if self.settings_module is not None and self.settings_name is not None:
            from importlib import import_module

            package = None
            if self.settings_module.startswith('.'):
                package = self.__module__

            mod = import_module(self.settings_module, package=package)
            return getattr(mod, self.settings_name)

        if self.settings_name is not None:
            return self.settings_name
        raise NotImplementedError(NOT_IMPLEMENTED)

    def from_django_settings(self) -> ostr:
        if self.django_setting is None:
            return None
        else:  # NOQA
            # noinspection PyUnresolvedReferences,PyPackageRequirements
            from django.conf import settings

            if self.django_setting_is_dict:
                d = getattr(settings, self.django_setting)
                value = d.get(self.django_setting_dict_key)
            else:
                value = settings.get(self.django_setting)
            return value

    def get_key(self) -> str:
        try:
            return self.get_settings_value()
        except NotImplementedError:
            value = self.from_django_settings()
            if value is None:
                raise NotImplementedError('No settings mechanism implemented')
            return value


class ApiKeyViaQueryAuthenticator(ApiKeyAuthenticator):
    request_params_via = 'params'
    key_name = 'apikey'  # type: str


class ApiKeyViaJSONAuthenticator(ApiKeyAuthenticator):
    request_params_via = 'json'
    key_name = 'apikey'
