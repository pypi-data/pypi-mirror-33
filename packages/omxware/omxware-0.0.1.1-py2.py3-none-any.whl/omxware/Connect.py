"""
LabBook Connection Package.

It provides generic HTTP methods (GET, POST, DELETE) for connecting to the LabBook platform. All the
authentication cookies will be maintained.
"""
import requests, json, omxware
import urllib3
from requests.exceptions import ConnectionError
from omxware.ServiceException import ServiceException, ServiceStatusCode, ServiceConnectionException

# Disable the SSL warning
urllib3.disable_warnings()


class Connection:
    """OMXWare connect class"""

    def __init__(self, hosturl):
        self.hosturl = hosturl

    def connect(self):
        """Connect to the OMXWare services"""
        self._session = requests.Session()

    def get(self, methodurl, headers, payload=None):
        """Issue a HTTP GET request

        Arguments:
          methodurl -- relative path to the GET method
          headers -- HTTP headers
          payload -- (optional) additional payload (HTTP body)
        """
        if self._session is None:
            raise Exception("No connection has been established")

        response = self._session.get(self.hosturl + methodurl, verify=False, params=payload, headers=headers)
        if response.status_code < 200 or response.status_code >= 300:
            raise self._process_http_response(response)
        return response

    def post(self, methodurl, parameters=None, headers=None, files=None):
        """Issue a HTTP POST request

        Arguments:
        methodurl -- relative path to the POST method
        parameters -- (optional) form parameters
        headers -- (optional) HTTP headers
        files -- (optional) multi-part form file content
        """
        if self._session is None:
            raise Exception("No connection has been established")

        response = self._session.post(self.hosturl + methodurl, data=parameters, verify=False, headers=headers,
                                      files=files)
        if response.status_code < 200 or response.status_code >= 300:
            raise self._process_http_response(response)
        return response

    def delete(self, methodurl, headers, payload=None):
        """Issue a HTTP DELETE request

        Arguments:
        methodurl -- relative path to the POST method
        headers -- HTTP headers
        payload -- (optional) additional payload (HTTP body)
        """
        if self._session is None:
            raise Exception("No connection has been established")

        response = self._session.delete(self.hosturl + methodurl, verify=False, params=payload, headers=headers)
        if response.status_code < 200 or response.status_code >= 300:
            raise self._process_http_response(response)
        return response

    def disconnect(self):
        """Disconnect from OMXWare services"""
        if self._session is None:
            raise Exception("No connection has been established")

        self._session.close()
        self._session = None

    def _process_http_response(self, response):
        """Internal method for processing HTTP response"""
        try:
            responseJ = json.loads(response.text)
        except SyntaxError:
            return ServiceException(response.text, response.status_code)
        except ValueError:
            return ServiceException(response.text, response.status_code)
        return ServiceException(responseJ['message'], response.status_code)
