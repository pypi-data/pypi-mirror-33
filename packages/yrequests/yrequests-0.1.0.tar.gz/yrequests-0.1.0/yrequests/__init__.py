# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import requests

from builtins import bytes
from builtins import str
from copy import deepcopy


class YRequests(object):
    """ Class to make simple requests. It is a wrapper of `requests` module, but
    it try to handle all errors.

    How to use:

    >>> from yrequests import YRequests
    >>> req = YRequests()
    >>> result = req.get('http://url.com/a/b/c', params={'q': 'apple'})
    >>> if result['ok']:
    >>>     print(result['text'])  # or result['json']
    >>>     # do stuffs when everything is fine
    >>> else:
    >>>     print(result['error'])  # or result['status_code']
    >>>     # do stuffs when an error occurs
    >>>

    You can also use `post`, `put`, `delete`, `head` and `options`. These
    (HTTP) methods receive the same parameters of `requests` module. If need
    instructions of how `requests` module works take a look at:
        http://docs.python-requests.org/en/master/user/quickstart/

    The `result` is a `dict` object:

    >>> result = {
    >>>     'ok': <bool>,
    >>>     'error': <str|None>,
    >>>     'error_type': <str|None>,
    >>>     'response': <requests.response|None>,
    >>>     'headers': <dict>,
    >>>     'status_code': <int|None>,
    >>>     'content_type': <str|None>,
    >>>     'text': <str|None>,
    >>>     'json': <str|None>,
    >>> }
    >>>

    Result keys:
    - ok: True if everything is fine. Always check this value.
    - error: Textual error (when `ok` is False).
    - error_type: A string with the error type code:
        general: General error.
        connection: DNS problem, connection refused, etc. The only exception is
        timed out that has its own code (above).
        timeout: Connection timed out.
        http: HTTP errors as 404, 403, 500, etc.
        json: "Content-Type" header is indicated as JSON but the content is not
            a valid JSON.
    - response: A response object of request (same of `requests` module). You
        can use as fallback to check informations that are not handled by this
        class.
    - headers: Dictionary with the response headers (same of `requests.response`
        module).
    - status_code: Integer of HTTP status code (200, 404, 500, etc).
    - content_type: The "Content-Type" header value.
    - text: The content of response (if any). It's always unicode.
    - json: A dictionary of the content if the "Content-Type" header is
        indicated as JSON.
    """

    ERROR_GENERAL = 'general'
    ERROR_CONNECTION = 'connection'
    ERROR_TIMEOUT = 'timeout'
    ERROR_HTTP = 'http'
    ERROR_JSON = 'json'

    def __init__(self, timeout=60, headers=None):
        """
        :param timeout: Default timeout (seconds) for all requests.
        :param headers: Default headers (`dict`) for all requests.
        """
        self.headers = headers or {}
        self.timeout = timeout

    def __get_result_tpl(self):
        return {
            'ok': False,
            'error': None,
            'error_type': None,
            'response': None,
            'headers': {},
            'status_code': None,
            'content_type': None,
            'text': None,
            'json': None,
        }

    def __e_to_str(self, e):
        if isinstance(e, bytes):
            e = e.decode('utf-8')
        else:
            e = str(e)
        return e

    def __req(self, method, *args, **kwargs):
        """ Make a request. The `args` and `kwargs` are passed to
        the respective `requests.<method>`.

        The first parameter is required and indicates the HTTP method. The
        others parameters will be passed to the `requests` function.

        The `headers` and `timeout` parameters are filled using the headers and
        timeout passed in the constructor (`__init__`). If this method received
        a `headers` or `timeout` it will override the defaults values. The
        `headers` parameter only overrides the specified keys of default
        headers.

        This method always returns a `dict` object (result):

        >>> result = {
        >>>     'ok': <bool>,
        >>>     'error': <str|None>,
        >>>     'error_type': <str|None>,
        >>>     'response': <requests.response|None>,
        >>>     'headers': <dict>,
        >>>     'status_code': <int|None>,
        >>>     'content_type': <str|None>,
        >>>     'text': <str|None>,
        >>>     'json': <str|None>,
        >>> }
        >>>

        Result keys:
        - ok: True if everything is fine. Always check this value.
        - error: Textual error (when `ok` is False).
        - error_type: A string with the error type code:
            general: General error.
            connection: DNS problem, connection refused, etc. The only exception is
            timed out that has its own code (above).
            timeout: Connection timed out.
            http: HTTP errors as 404, 403, 500, etc.
            json: "Content-Type" header is indicated as JSON but the content is not
                a valid JSON.
        - response: A response object of request (same of `requests` module). You
            can use as fallback to check informations that are not handled by this
            class.
        - headers: Dictionary with the response headers (same of `requests.response`
            module).
        - status_code: Integer of HTTP status code (200, 404, 500, etc).
        - content_type: The "Content-Type" header value.
        - text: The content of response (if any). It's always unicode.
        - json: A dictionary of the content if the "Content-Type" header is
            indicated as JSON.

        :param method: A string with the HTTP method (GET, POST, PUT, DELETE,
            HEAD, OPTIONS).
        :param args: Positional arguments for `requests.<method>`.
        :param kwargs: Keyword arguments arguments for `requests.<method>`.
        :return Result dictionary.
        """
        result = self.__get_result_tpl()
        kwargs = deepcopy(kwargs)
        headers = {}

        if 'timeout' not in kwargs and self.timeout:
            kwargs['timeout'] = self.timeout

        if self.headers:
            headers.update(self.headers)

        if 'headers' in kwargs:
            headers.update(kwargs['headers'])

        kwargs['headers'] = headers

        request_func_methods = {
            'GET': requests.get,
            'POST': requests.post,
            'PUT': requests.put,
            'DELETE': requests.delete,
            'HEAD': requests.head,
            'OPTIONS': requests.options,
        }

        request_func = request_func_methods.get(method)

        if request_func is None:
            result['error'] = 'Method %s is not allowed' % method
            result['error_type'] = self.ERROR_GENERAL
            return result

        try:
            response = request_func(*args, **kwargs)
        except requests.ConnectionError as e:
            result['error'] = self.__e_to_str(e)
            result['error_type'] = self.ERROR_CONNECTION
            return result
        except requests.Timeout as e:
            result['error'] = self.__e_to_str(e)
            result['error_type'] = self.ERROR_TIMEOUT
            return result
        except Exception as e:
            result['error'] = self.__e_to_str(e)
            result['error_type'] = self.ERROR_CONNECTION
            return result

        result['response'] = response
        result['headers'] = response.headers
        result['status_code'] = response.status_code
        try:
            result['content_type'] = response.headers['content-type']
        except KeyError:
            result['content_type'] = None

        if isinstance(response.text, str):
            result['text'] = response.text

        is_json = False
        if result['content_type'] and '/json' in result['content_type']:
            is_json = True

        if is_json:
            try:
                result['json'] = response.json()
            except (ValueError, TypeError):
                result['error'] = 'The content is not a valid JSON.'
                result['error_type'] = self.ERROR_JSON
                return result

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            result['error'] = self.__e_to_str(e)
            result['error_type'] = self.ERROR_HTTP
            return result
        except Exception as e:
            result['error'] = self.__e_to_str(e)
            result['error_type'] = self.ERROR_GENERAL
            return result

        result['ok'] = True
        return result

    def get(self, *args, **kwargs):
        return self.__req('GET', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.__req('POST', *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.__req('PUT', *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.__req('DELETE', *args, **kwargs)

    def head(self, *args, **kwargs):
        return self.__req('head', *args, **kwargs)

    def options(self, *args, **kwargs):
        return self.__req('OPTIONS', *args, **kwargs)
