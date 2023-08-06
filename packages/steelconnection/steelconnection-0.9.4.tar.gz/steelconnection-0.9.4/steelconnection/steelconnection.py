# coding: utf-8

"""SteelConnection

Convienience objects for making REST API calls
to Riverbed SteelConnect Manager.

Usage:
    sconnect = steelconnection.SConAPI(scm_name, username, password)

    Optional keyword api_version can be used to specify an API version number.
    Currently there is only one API version: '1.0'.

    Once you have instantiated an object as shown above,
    you can use the object to make calls to the REST API.

    For example, to get all nodes in the realm:
    nodes = sconnect.config.get('nodes')
    ... or in a specifc org:
    nodes = sconnect.config.get('/org/' + orgid + '/nodes')  
    
    Any call that does not result in a success (HTTP status code 200)
    will raise an exception, so calls should be wrapped in a try/except pair.
"""


import getpass
import json
import requests
import sys
import traceback
import warnings

from .__version__ import __version__
from .exceptions import AuthenticationError, APINotEnabled
from .exceptions import BadRequest, InvalidResource
from .lookup import _LookUp
from .input_tools import get_username, get_password, get_password_once


class SConAPI(object):
    r"""Make REST API calls to Riverbed SteelConnect Manager.
    
    :param str controller: hostname or IP address of SteelConnect Manager.
    :param str username: (optional) Admin account name.
    :param str password: (optional) Admin account password.
    :param str api_version: (optional) REST API version.
    :returns: Dictionary or List of Dictionaries based on request.
    :rtype: dict, or list
    """

    def __init__(
        self,
        controller,
        username=None,
        password=None,
        api_version='1.0',
    ):
        r"""Create a new steelconnection object.

        :param str controller: hostname or IP address of SteelConnect Manager.
        :param str username: (optional) Admin account name.
        :param str password: (optional) Admin account password.
        :param str api_version: (optional) REST API version.
        :returns: Dictionary or List of Dictionaries based on request.
        :rtype: dict, or list
        """
        self.controller = controller
        self.username = username
        self.password = password
        self.api_version = api_version
        self.session = requests.Session()
        self.result = None
        self.response = None
        self.headers = {
            'Accept': 'application/json',
            'Content-type': 'application/json',
        }
        self.__version__ = __version__
        self.lookup = _LookUp(self)
        self._authenticate(username, password)
        self.scm_version = self._get_scm_version()

    def get(self, resource, params=None):
        r"""Send a GET request to the SteelConnect.Config API.

        :param str resource: api resource to get.
        :param dict params: (optional) Dictionary of query parameters.
        :returns: Dictionary or List of Dictionaries based on request.
        :rtype: dict, or list
        """
        self.response = self.session.get(
            url=self.url('config', resource),
            auth=(self.username, self.password) if self.username else None,
            headers=self.headers,
            params=params,
        )
        self.result = self._get_result(self.response)
        if self.result is None:
            exception = self._determine_exception(self.response)
            if exception:
                raise exception
        return self.result

    def getstatus(self, resource, params=None):
        r"""Send a GET request to the SteelConnect.Reporting API.

        :param str resource: api resource to get.
        :param dict params: (optional) Dictionary of query parameters.
        :returns: Dictionary or List of Dictionaries based on request.
        :rtype: dict, or list
        """
        self.response = self.session.get(
            url=self.url('reporting', resource),
            auth=(self.username, self.password) if self.username else None,
            headers=self.headers,
            params=params,
        )
        self.result = self._get_result(self.response)
        if self.result is None:
            exception = self._determine_exception(self.response)
            if exception:
                raise exception
        return self.result

    def delete(self, resource, data=None, params=None):
        r"""Send a DELETE request to the SteelConnect.Config API.

        :param str resource: api resource to get.
        :param dict data: (optional) Dictionary of 'body' data to be sent.
        :param dict params: (optional) Dictionary of query parameters.
        :returns: Dictionary or List of Dictionaries based on request.
        :rtype: dict, or list
        """
        self.response = self.session.delete(
            url=self.url('config', resource),
            auth=(self.username, self.password) if self.username else None,
            headers=self.headers,
            params=params,
            data=json.dumps(data) if data and isinstance(data, dict) else data
        )
        self.result = self._get_result(self.response)
        if self.result is None:
            exception = self._determine_exception(self.response)
            if exception:
                raise exception
        return self.result

    def post(self, resource, data=None):
        r"""Send a POST request to the SteelConnect.Config API.

        :param str resource: api resource to get.
        :param dict data: (optional) Dictionary of 'body' data to be sent.
        :returns: Dictionary or List of Dictionaries based on request.
        :rtype: dict, or list
        """
        self.response = self.session.post(
            url=self.url('config', resource),
            auth=(self.username, self.password) if self.username else None,
            headers=self.headers,
            data=json.dumps(data) if data and isinstance(data, dict) else data
        )
        self.result = self._get_result(self.response)
        if self.result is None:
            exception = self._determine_exception(self.response)
            if exception:
                raise exception
        return self.result

    def put(self, resource, data=None, params=None):
        r"""Send a PUT request to the SteelConnect.Config API.

        :param str resource: api resource to get.
        :param dict data: (optional) Dictionary of 'body' data to be sent.
        :param dict params: (optional) Dictionary of query parameters.
        :returns: Dictionary or List of Dictionaries based on request.
        :rtype: dict, or list
        """
        self.response = self.session.put(
            url=self.url('config', resource),
            auth=(self.username, self.password) if self.username else None,
            headers=self.headers,
            params=params,
            data=json.dumps(data) if data and isinstance(data, dict) else data
        )
        self.result = self._get_result(self.response)
        if self.result is None:
            exception = self._determine_exception(self.response)
            if exception:
                raise exception
        return self.result

    def url(self, api, resource):
        r"""Combine attributes and resource as a url string.

        :param str api: api route, usually 'config' or 'reporting'.
        :param str resource: resource path.
        :returns: Complete URL path to access resource.
        :rtype: str
        """        
        resource = resource[1:] if resource.startswith('/') else resource
        return 'https://{0}/api/scm.{1}/{2}/{3}'.format(
            self.controller, api, self.api_version, resource,
        )

    def savefile(self, filename):
        r"""Save binary return data to a file.

        :param str filename: Where to save the response.content.
        """       
        with open(filename, 'wb') as f:
            f.write(self.response.content)

    def _get_result(self, response):
        r"""Return response data as native Python datatype.

        :param requests.response response: Response from HTTP request.
        :returns: Dictionary or List of Dictionaries based on response.
        :rtype: dict, list, or None
        """
        if not response.ok:
            if response.text and 'Queued' in response.text:
                # work-around for get:'/node/{node_id}/image_status'
                return response.json()
            return None
        if response.headers['Content-Type'] == 'application/octet-stream':
            message = ' '.join(
                "Binary data returned."
                "Use '.savefile(filename)' method"
                "or access using '.response.content'."
            )
            return {'status': message}
        if not response.json():
            return {}
        elif 'items' in response.json():
            return response.json()['items']
        else:
            return response.json()

    def _determine_exception(self, response):
        r"""Return an appropriate exception if required.

        :param requests.response response: Response from HTTP request.
        :returns: Exception if non-200 response code else None.
        :rtype: BaseException, or None
        """
        if not response.ok:
            error = _error_string(response)
            if response.status_code == 400:
                exception = BadRequest(error)
            elif response.status_code == 401:
                exception = AuthenticationError(error)
            elif response.status_code == 404:
                exception = InvalidResource(error)
            elif response.status_code == 502:
                exception = APINotEnabled(error)
            else:
                exception = RuntimeError(error)
            return exception

    def _authenticate(self, username=None, password=None):
        r"""Attempt authentication.

        Makes GET request against 'orgs' (because 'status' is not 
        available 2.8).  If neither username or password are provided,
        will make the request without auth, to see if requests package
        can authenticate using basic auth.

        :param str username: (optional) Admin account name.
        :param str password: (optional) Admin account password.
        :returns: None.
        :rtype: None
        """
        attempt_netrc_auth = username is None and password is None
        if attempt_netrc_auth:
            try:
                self.get('orgs')
            except AuthenticationError:
                pass
            else:
                return
        self.username, self.password = self._get_auth(username, password)
        self.get('orgs')

    def _get_auth(self, username=None, password=None):
        """Prompt for username and password if not provided.

        :param str username: (optional) Admin account name.
        :param str password: (optional) Admin account password.
        :returns: Tuple of strings as (username, password).
        :rtype: (str, str)
        """
        username = get_username() if username is None else username
        password = get_password_once() if password is None else password 
        return username, password

    def _get_scm_version(self):
        """Get version and build number of SteelConnect Manager.

        :returns: SteelConnect Manager version and build number.
        :rtype: str
        """
        try:
            status = self.get('status')
        except InvalidResource:
            return '2.8 or earlier.'
        else:
            scm_version = status.get('scm_version'), status.get('scm_build')
            return '.'.join(s for s in scm_version if s)

    def __bool__(self):
        """Return the success of the last request.

        :returns: True of False if last request succeeded.
        :rtype: bool
        """
        return False if self.response is None else self.response.ok 

    def __repr__(self):
        """Return a string consisting of class name, controller, and api.

        :returns: Information about this object.
        :rtype: str
        """
        details = ', '.join([
            "controller: '{0}'".format(self.controller),
            "scm version: '{0}'".format(self.scm_version),
            "api version: '{0}'".format(self.api_version),
            "response: '{0}'".format(self.response),
        ])
        return '{0}({1})'.format(self.__class__.__name__, details)


def _error_string(response):
    r"""Summarize error conditions and return as a string.

    :param requests.response response: Response from HTTP request.
    :returns: A multiline string summarizing the error.
    :rtype: str
    """
    details = ''
    if response.text:
        try:
            details = response.json()
            details = details.get('error', {}).get('message', '')
        except ValueError:
            pass
    error = '{0} - {1}{2}\nURL: {3}\nData Sent: {4}'.format(
        response.status_code,
        response.reason,
        '\nDetails: ' + details if details else '',
        response.url,
        repr(response.request.body),
    )
    return error


class SConAPIwithoutExceptions(SConAPI):
    r"""Make REST API calls to Riverbed SteelConnect Manager.

    This version of the class does not generate exceptions
    when an HTTP response has a non-200 series status code.
    
    :param str controller: hostname or IP address of SteelConnect Manager.
    :param str username: (optional) Admin account name.
    :param str password: (optional) Admin account password.
    :param str api_version: (optional) REST API version.
    :returns: Dictionary or List of Dictionaries based on request.
    :rtype: dict, or list
    """    

    def _determine_exception(self, response):
        r"""Return None to short-circuit the exception process.

        :param requests.response response: Response from HTTP request.
        :returns: None.
        :rtype: None
        """
        return None
