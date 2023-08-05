import logging
from collections import defaultdict
from collections.abc import MutableMapping

try:
    from contextlib import AbstractContextManager
except ImportError:  # NOQA
    class AbstractContextManager:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return None

from typing import Any, Dict, Iterable, Optional, Type, Tuple

import requests
from urlobject import URLObject

from . import authentication, exceptions

KWARGS = Dict[str, Any]

__all__ = (
    'RestEndpoint',
    'Api',
)


class RequestContext(MutableMapping):
    allowed_keys = ('params', 'headers', 'data', 'json')

    def __init__(self):
        self._ctx = defaultdict(dict)
        super(RequestContext, self).__init__()

    def __getitem__(self, key):
        if key in self.allowed_keys:
            return self._ctx[key]
        raise KeyError('Key {} not allowed'.format(key))

    def __setitem__(self, key, value):
        if key in self.allowed_keys:
            self._ctx[key].update(value)
        else:
            raise KeyError('Key {} not allowed'.format(key))

    def __iter__(self):
        return self._ctx.keys()

    def __len__(self):
        pass

    def __delitem__(self, key):
        if key in self.allowed_keys:
            del self._ctx[key]
        else:
            raise KeyError('Key {} not allowed'.format(key))

    def as_dict(self):
        return self._ctx

    def add_header(self, name, value):
        self._ctx['headers'].setdefault(name, value)

    def set_header(self, name, value):
        self._ctx['headers'].update({name: value})

    def add_param(self, name, value):
        self._ctx['params'].setdefault(name, value)

    def set_param(self, name, value):
        self._ctx['params'].update({name: value})

    def add_data(self, name, value):
        self._ctx['data'].setdefault(name, value)

    def set_data(self, name, value):
        self._ctx['data'].update({name: value})

    def add_json(self, d: Dict[str, Optional[Any]]):
        self._ctx['json'].update(d)

    def set_json(self, d: Dict[str, Optional[Any]]):
        self._ctx['json'] = d


class RestEndpoint(object):
    """
    Abstraction of a rest endpoint. It implements the following methods:

    - get: retrieve a single object identified by uid
    - search: search for matching objects
    - list: retrieve all objects optionally filtered and sorted by api
      specific keyword arguments, converted to query parameters.
    - geo_filter: For GEO endpoints only, posts a OpenGIS filter as GeoJSON to
      the endpoint returning a list of results.
    - geo_coords: For GEO endpoints only, sends a request with a longtitude
      and latitude coordinate.

    Any custom endpoint should be added to the 'actions'.

    Defaults for class attributes are considered sane, but are subject to
    change before 0.5 release, based on feedback and usage.
    """
    #: Path of the endpoint
    path = ''  # type: str
    #: Should uid for a get() method be added as path. For example:
    #:    `https://stockapi.example.com/v2/article/{uid}`
    uid_as_path = True  # type: bool
    #: Should we append a slash to the uid. For example
    #:    `https://stockapi.example.com/v2/article/{uid}/`
    uid_append_slash = False
    #: If the uid is not added as path, this specifies the name of the query
    #: parameter.
    uid_query_parameter = None  # type: Optional[str]
    #: Does search require an extra path component, if so what is it. Ex:
    #:    `https://stockapi.example.com/v2/article/find`
    #: None means no extra path.
    search_path = None  # type: Optional[str]
    #: Name for a search parameter. This is the name of a typically free-form
    #: search parameter. The search method accepts positional arguments and
    #: any of these components are added to this parameter.
    search_param_name = 'search'  # type: str
    #: When multiple parameters are provided to the search parameter,
    #: what should be used as separator between parameters.
    search_param_list_separator = '+'  # type: str
    #: Does list require an extra path component, if so what is it. Ex:
    #:    `https://stockapi.example.com/v2/articles/list`
    #: None means no extra path.
    list_path = None  # type: Optional[str]
    #: If lists can be filtered
    list_supports_filters = True  # type: bool
    #: HTTP method for lists: get or post
    list_method = 'get'  # type: str
    #: How to communicate filter arguments
    #: By default the following methods are supported:
    #:
    #: - params: query parameters
    #: - data: post parameters (list_method MUST be post)
    #: - json: post parameters as json data (list_method MUST be post)
    list_filters_via = 'params'  # type: str
    #: Which methods are supported
    supported_filters_via = ('params', 'data', 'json')
    #: Does `geo_filter` require an extra path component, if so what is it. Ex:
    #:    `https://stockapi.example.com/v2/articles/by_region`
    #: None means no extra path.
    geo_filter_path = None  # type: Optional[str]
    #: The envelope name for the filter. For example:
    #:     { 'envelope': {'contains': { 'type': 'Point', 'coordinates': [...]}}}
    #: The envelope is necessary if other data is transmitted through a JSON
    #: body as well. Use `None` to disable generating an envelope.
    geo_filter_envelope = 'geometry'  # type: Optional[str]
    #: Does `geo_coords` require an extra path component, if so what is it. Ex:
    #:    `https://stockapi.example.com/v2/articles/close_to`
    #: None means no extra path.
    geo_coords_path = None  # type: Optional[str]
    #: Name of the longtitude parameter
    geo_coords_lon = 'lon'  # type: str
    #: Name of the latitude parameter
    geo_coords_lat = 'lat'  # type: str
    #: Send paramaters via headers, post data or query string parameters
    geo_coords_via = 'params'  # type: str
    #: Method to use for requests. Only get or post supported
    geo_coords_method = 'get'  # type: str
    #: Global methods supported by this endpoint class
    supported_request_methods = ('get', 'post')
    #: Default headers to always send. Headers that require runtime context
    #: can be added through implementing the `prepare_headers` method.
    default_headers = {
        'Accept': 'application/json',
    }
    #: Supported actions for this endpoint. By default, if not listed here,
    #: a call to the same named method (if implemented) raises an exception.
    #: This is done through `validate_support()` and custom methods are
    # encouraged to implement the same logic, so that classes extending it
    # can deny some of the methods via omission in this list.
    actions = [  # type: Iterable[str]
        'get', 'search', 'list', 'geo_filter', 'geo_coords'
    ]

    def __init__(self, api: 'Api', **kwargs):
        self.api = api
        if 'path' in kwargs:
            self.path = kwargs.pop('path')

        # This will blow up (intentionally) if RestEndpoint() is the last in
        # the MRO and kwargs still contains items. However, if it's not the
        # last in the MRO, we should pass these on.
        # Additional positional arguments are not supported, as this would
        # make an overly complex "endpoints" dictionary on the API object,
        # with very little gain.
        #
        # This isn't considered a bug.
        #
        super().__init__(**kwargs)

    @property
    def url(self) -> URLObject:
        """
        Returns a new instance of a URLObject which consists of the base url
        and path.
        Methods implementing API requests should only request this once per
        request and modify the returned object accordingly.

        :return: The URL for the REST endpoint
        """
        return self.api.url.add_path(self.path)

    def validate_action(self, action_name) -> None:
        if action_name not in self.actions:
            raise RuntimeError(
                '{} does not support the {} method'.format(
                    self.__class__.__name__, action_name
                )
            )

    def validate_filters_via(self) -> None:
        # Headers is explicitedly denied.
        if self.list_filters_via == 'headers' or \
                        self.list_filters_via not in self.supported_filters_via:
            raise RuntimeError(
                'filters via {} unsupported'.format(self.list_filters_via)
            )

    def get_request_method(self, selected: str):
        method = selected.lower()
        msg = "Unsupported method: {}".format(selected)
        if method in self.supported_request_methods:
            try:
                r = getattr(self.api.session, method)
                if callable(r):
                    return r
                else:
                    raise ValueError(msg)
            except AttributeError:
                raise ValueError(msg)
        else:
            raise ValueError(msg)

    def prepare_request_context(self) -> Dict[str, Dict[str, Optional[Any]]]:
        context = RequestContext()
        context['headers'] = self.prepare_headers()
        for key, value in self.api.authenticator.get_request_params().items():
            if key in context:
                if value is not None:
                    context[key].update(value)
            else:
                context[key] = value
        return context.as_dict()

    def prepare_headers(self) -> Dict[str, str]:
        return self.default_headers

    def _add_optional_path(self, path: Optional[str]):
        if path:
            return self.url.add_path(path)
        else:
            return self.url

    def get(self, uid: Any) -> requests.Response:
        self.validate_action('get')
        uid_str = str(uid)
        context = self.prepare_request_context()
        self.api.logger.debug('context = {}'.format(context))
        if self.uid_as_path:
            if self.uid_append_slash:
                if not uid_str.endswith('/'):
                    uid_str += '/'

            url = self.url.add_path(uid_str)
            self.api.logger.debug('Fetching: %s', url)
            self.api.logger.debug('- Context: %r', context)
            return self.api.session.get(url, **context)
        else:
            # Bugreport filed
            # noinspection PyTypeChecker
            context['params'].update({self.uid_query_parameter: str(uid)})
            self.api.logger.debug('Fetching: %s', self.url)
            self.api.logger.debug('- Context: %r', context)
            return self.api.session.get(self.url, **context)

    def search(self, *args, **kwargs) -> requests.Response:
        self.validate_action('search')
        context = self.prepare_request_context()
        if args:
            context['params'][self.search_param_name] = \
                self.search_param_list_separator.join(args)
        context['params'].update(kwargs)
        url = self._add_optional_path(self.search_path)
        return self.api.session.get(url, **context)

    def list(self, **filters) -> requests.Response:
        self.validate_action('list')
        kwargs = self.prepare_request_context()
        request_method = self.get_request_method(self.list_method)
        self.validate_filters_via()
        if kwargs[self.list_filters_via] is not None:
            kwargs[self.list_filters_via].update(filters)
        else:
            kwargs[self.list_filters_via] = filters
        url = self._add_optional_path(self.list_path)
        return request_method(url, **kwargs)

    def geo_filter(self, geofilter: dict) -> requests.Response:
        """
        Default geo filter implementation

        Construction of the filter dictionary is not the responsibility of
        this class, but the class extending it. The filter dict is passed
        straight to requests, which in turn passes it straight to
        :func:`json.dumps`. Whether this is creates valid GeoJSON is up to
        the concrete class to decide.

        The geo filter allows one to post a dictionary representing a
        Geographic filter. An optional envelope can be added if more data is
        sent via the request body.

        :param geofilter:
        :return:
        """
        self.validate_action('geo_filter')
        kwargs = self.prepare_request_context()
        if not self.geo_filter_envelope:
            kwargs['json'].update(geofilter)
        else:
            kwargs['json'].update({self.geo_filter_envelope: geofilter})
        url = self._add_optional_path(self.geo_filter_path)
        return self.api.session.post(url, **kwargs)

    def geo_coords(self, lon: float, lat: float) -> requests.Response:
        self.validate_action('geo_coords')
        kwargs = self.prepare_request_context()
        kwargs[self.geo_coords_via][self.geo_coords_lon] = lon
        kwargs[self.geo_coords_via][self.geo_coords_lat] = lat
        request_method = self.get_request_method(self.geo_coords_method)
        url = self._add_optional_path(self.geo_coords_path)
        return request_method(url, **kwargs)


class Api(AbstractContextManager):
    #: Base URL for the API
    base_url = None  # type: str
    #: Endpoints supported by the API
    #: This dict has a key to point to the endpoint. In most cases this will
    #: correspond with the path, but doesn't limit it to that, so that two
    #: endpoints may be created using the same path. A usec filtering
    #: possiblities are complex that class seperation is a good idea.
    endpoints = None  # type: Dict[str, Tuple[Type[RestEndpoint], KWARGS]]
    #: Authenticator to use
    # type: authentication.RestAuthenticator
    authenticator = authentication.NoAuthenticationRestAuthenticator
    logger_id = 'getrest'  # type: str
    requests_per_second = 0  # type: int

    def __init__(self,
                 base_url: str = None,
                 authenticator: authentication.RestAuthenticator=None):
        if base_url:
            self.base_url = base_url  # NOQA
        if authenticator:
            self.authenticator = authenticator  # NOQA

        self._session = None
        self.logger = logging.getLogger(self.logger_id)
        # Endpoint Objects
        self._eo = {}  # type: Dict[str, RestEndpoint]]
        for key, value in self.endpoints.items():
            klass, kwargs = value
            kwargs = kwargs or {}
            self._eo[key] = klass(self, **kwargs)

        super().__init__()

    @property
    def url(self) -> URLObject:
        return URLObject(self.base_url)

    @property
    def session(self) -> requests.Session:
        if self._session is None:
            self._session = requests.session()
            if self.requests_per_second > 0:
                from .utils import SessionThrottler
                SessionThrottler.register(
                    self._session, self.requests_per_second
                )
            auth_headers = self.authenticator.get_headers()
            if auth_headers is not None:
                self._session.headers.update(auth_headers)
        return self._session

    def __getattr__(self, item) -> RestEndpoint:
        try:
            return self._eo[item]
        except KeyError:
            raise exceptions.NoSuchEndpoint('No endpoint for {}'.format(item))

    def close_session(self) -> None:
        if self._session is not None:
            self._session.close()
            self._session = None
        else:
            self.logger.warning(
                'Close called on non-existing session for %s',
                self.__class__.__name__
            )

    def __exit__(self, exc_type, exc_val, exc_tb) -> Optional[bool]:
        self.close_session()
        return super(Api, self).__exit__(exc_type, exc_val, exc_tb)
