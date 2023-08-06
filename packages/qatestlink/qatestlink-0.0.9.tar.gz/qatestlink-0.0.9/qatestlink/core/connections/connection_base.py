# -*- coding: utf-8 -*-
"""module qatestlink.core.connections"""


import requests


class ConnectionBase(object):
    """TODO: doc class"""

    _host = None
    _port = None
    _xmlrpc_route = None
    _is_https = None
    _url = None
    _log = None

    def __init__(self, log, host='localhost', port=80,
                 xmlrpc_route='lib/api/xmlrpc/v1/xmlrpc.php', is_https=False):
        """TODO: doc method"""
        self._host = host
        self._port = port
        self._xmlrpc_route = xmlrpc_route
        self._is_https = is_https
        self._log = log
        # Format Testlink XMLRPC url
        self._url = self.__url_format()

    def __url_format(self):
        url = "{}{}:{}/{}"
        url_prefix = 'http://'
        if self._is_https:
            url_prefix = 'https://'
        return url.format(
            url_prefix,
            self._host,
            self._port,
            self._xmlrpc_route)

    def post(self, headers, req_data):
        """
        :Args:
            headers: {'Content-Type':'application/xml'}
            data: <methodCall>...</methodCall>
        """
        self._log.info("POST request:")
        self._log.debug("    url={}".format(self._url))
        self._log.debug("    headers={}".format(headers))
        self._log.debug("    data={}".format(req_data))
        response = requests.post(
            self._url,
            headers=headers,
            data=req_data)
        self._log.info("POST response:")
        self._log.info("    status_code={}".format(
            response.status_code))
        self._log.debug("    data={}".format(
            response.text))
        return response
