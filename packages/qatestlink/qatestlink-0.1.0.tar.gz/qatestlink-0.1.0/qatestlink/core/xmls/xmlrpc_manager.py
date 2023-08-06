# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""XMLRPC managers"""


from dicttoxml import dicttoxml
from qatestlink.core.exceptions.response_exception import ResponseException
from qatestlink.core.xmls.route_type import RouteType
import xmltodict


class XMLRPCManager(object):
    """
    Manage all XMLRPCManager requests,
     responses and handle errors. This class
     store all official methods names used
     on original XMLRPC php class
    """

    log = None
    headers = None
    handler = None
    req_dict = None

    def __init__(self, log):
        """Instance for XMLRPC requests manager

        Arguments:
            log {logging.Logger} -- logger func ready to log messages
        """
        self.log = log
        self.headers = {'Content-Type': 'application/xml'}
        self.req_dict = {
            "methodName": "",
            "params": {}
        }

    def parse_response(self, response):
        """Parse response from call to requests library from XML string format
            to 'dict' ready to create/update/find/add/delete Elements on it

        Arguments:
            response {requests.post()} -- Response of call on requests library

        Raises:
            Exception -- if code of response XMLRPC request is not 200

        Returns:
            str -- xml as string text
        """
        if response.status_code != 200:
            raise Exception(
                "status_code invalid: code={}".format(
                    response.status_code))
        return xmltodict.parse(response.text)

    def parse_errors(self, response_as_dict):
        """Find Testlink XMLRPC error structure and raise it's founds

        Arguments:
            response_as_dict {dict} -- dict parsed from XML string

        Raises:
            Exception -- Bad params
            ResponseException -- if error structure it's found
        """
        if not isinstance(response_as_dict, dict):
            raise Exception("Bad param 'response_as_dict' value provided")
        res_value = response_as_dict.get(
            'methodResponse')['params']['param']['value']
        err_info = res_value.get(
            'array')['data']['value']['struct']['member']
        raise ResponseException(
            self.log,
            code=err_info[0]['value']['int'],
            message=err_info[1]['value']['string']
        )

    def req_create(self, dev_key, route_type, params=True):
        """Update property 'req_dict' to add route_type and param or params if
            enabled

        Arguments:
            dev_key {str} -- developer key for Testlink
            route_type {RouteType} -- string to refer XMLRPC testlink call

        Keyword Arguments:
            params {bool} -- enable multiple params using <struct> tree
                (default: {True})
        """
        self.req_dict.update({
            "methodName": route_type.value
        })
        if params:
            self.req_dict.update({
                "params": {
                    "struct": {
                        "member": [
                            {"name": "devKey", "value": dev_key}
                        ]
                    }
                }
            })
            return
        self.req_dict.update({
            "params": {
                "struct": {
                    "name": "devKey",
                    "value": dev_key
                }
            }
        })

    def req_params(self):
        """Obtains params from XML request"""
        params = self.req_dict.get('params')['struct']['member']
        if not params:
            raise ResponseException(
                self.log,
                code=601,
                message="Call to req_create first")
        return params

    def req_check_dev_key(self, dev_key):
        """String xml object ready to use on API call

        Arguments:
            dev_key {str} -- string for Testlink API_KEY

        Returns:
            str -- XML request with parsed params
        """
        self.req_create(dev_key, RouteType.TLINK_CHECK_DEV_KEY, params=False)
        xml = dicttoxml(
            self.req_dict, custom_root='methodCall', attr_type=False)
        return xml

    def req_tprojects(self, dev_key):
        """Obtains all test projects created on remote testlink database,

            TODO: can filter with any property+value combination

        Arguments:
            dev_key {str} -- string of developer key provided by Testlink
                (default: {value obtained from JSON settings file})

        Returns:
            str -- string xml object ready to use on API call
        """
        self.req_dict.update({
            "methodName": RouteType.TPROJECTS.value
        })
        self.req_dict.update({
            "params": {
                "struct": {
                    "name": "devKey",
                    "value": dev_key
                }
            }
        })
        xml = dicttoxml(
            self.req_dict, custom_root='methodCall', attr_type=False)
        return xml

    def req_tproject_by_name(self, dev_key, tproject_name):
        """Obtains all test projects created on remote testlink database, can
            filter by name

        Arguments:
            dev_key {str} -- string of developer key provided by Testlink
                (default: {value obtained from JSON settings file})
            tproject_name {[type]} -- [description]

        Raises:
            Exception -- [description]

        Returns:
            str -- string xml object ready to use on API call
        """
        if not tproject_name:
            raise Exception("Can't call XMLRPC without param, tproject_name")
        self.req_create(dev_key, RouteType.TPROJECT_BY_NAME, params=True)
        self.req_params().append(
            {"name": "testprojectname", "value": tproject_name}
        )
        xml = dicttoxml(
            self.req_dict, custom_root='methodCall', attr_type=False)
        return xml

    def req_tproject_tplans(self, dev_key, tproject_id):
        """Obtains all test plans asigned to test project created on remote
            testlink database, can filter by project id

        Arguments:
            dev_key {str} -- string of developer key provided by Testlink
                (default: {value obtained from JSON settings file})
            tproject_id {str} -- ID of Testlink Test Project to filter Testlink
                Test Plan

        Raises:
            Exception -- [description]

        Returns:
            str -- string xml object ready to use on API call
        """
        if not tproject_id:
            raise Exception("Can't call XMLRPC without param, tproject_id")
        self.req_create(dev_key, RouteType.TPROJECT_TEST_PLANS, params=True)
        self.req_params().append(
            {"name": "testprojectid", "value": tproject_id}
        )
        xml = dicttoxml(
            self.req_dict, custom_root='methodCall', attr_type=False)
        return xml

    def req_tproject_tsuites_first_level(self, dev_key, tproject_id):
        """Obtains all test suites of first level into test project created on
            remote testlink database, can filter by project id

        Arguments:
            Arguments:
            dev_key {str} -- string of developer key provided by Testlink
                (default: {value obtained from JSON settings file})
            tproject_id {str} -- ID of Testlink Test Project to filter Testlink
                Test Plan

        Raises:
            Exception -- [description]

        Returns:
            str -- string xml object ready to use on API call
        """
        if not tproject_id:
            raise Exception("Can't call XMLRPC without param, tproject_id")
        self.req_create(
            dev_key,
            RouteType.TPROJECT_TSUITES_FIRST_LEVEL,
            params=True)
        self.req_params().append(
            {"name": "testprojectid", "value": tproject_id}
        )
        xml = dicttoxml(
            self.req_dict, custom_root='methodCall', attr_type=False)
        return xml

    def req_tplan_by_name(self, dev_key, tproject_name, tplan_name):
        """Obtains all test projects created on remote testlink database, can
            filter by name

        Arguments:
            dev_key {str} -- string of developer key provided by Testlink
                (default: {value obtained from JSON settings file})
            tproject_name {str} -- NAME of Testlink Test Project data
            tplan_name {str} -- NAME of Testlink Test Plan data

        Raises:
            Exception -- [description]

        Returns:
            str -- string xml object ready to use on API call
        """
        if not tproject_name:
            raise Exception("Can't call XMLRPC without param, tproject_name")
        if not tplan_name:
            raise Exception("Can't call XMLRPC without param, tplan_name")
        self.req_create(dev_key, RouteType.TPLAN_BY_NAME, params=True)
        self.req_params().append(
            [
                {"name": "testprojectname", "value": tproject_name},
                {"name": "testplanname", "value": tplan_name}
            ]
        )
        xml = dicttoxml(
            self.req_dict, custom_root='methodCall', attr_type=False)
        return xml

    def req_tplan_platforms(self, dev_key, tplan_id):
        """Obtains all platforms asigned to test plan created on remote
            testlink database, can filter by test plan name

        Arguments:
            dev_key {str} -- string of developer key provided by Testlink
                (default: {value obtained from JSON settings file})
            tplan_id {int} -- ID of Testlink Test Plan data

        Raises:
            Exception -- [description]

        Returns:
            str -- string xml object ready to use on API call
        """
        if not tplan_id:
            raise Exception("Can't call XMLRPC without param, tplan_id")
        self.req_create(dev_key, RouteType.TPLAN_PLATFORMS, params=True)
        self.req_params().append(
            {"name": "testplanid", "value": tplan_id}
        )
        xml = dicttoxml(
            self.req_dict, custom_root='methodCall', attr_type=False)
        return xml

    def req_tplan_builds(self, dev_key, tplan_id):
        """Obtains all platforms asigned to test plan created on remote
            testlink database, can filter by test plan id

        Arguments:
            dev_key {str} -- string of developer key provided by Testlink
                (default: {value obtained from JSON settings file})
            tplan_id {int} -- ID of Testlink Test Plan data

        Raises:
            Exception -- [description]

        Returns:
            str -- string xml object ready to use on API call
        """
        if not tplan_id:
            raise Exception("Can't call XMLRPC without param, tplan_id")
        self.req_create(dev_key, RouteType.TPLAN_BUILDS, params=True)
        self.req_params().append(
            {"name": "testplanid", "value": tplan_id}
        )
        xml = dicttoxml(
            self.req_dict, custom_root='methodCall', attr_type=False)
        return xml

    def req_tplan_tsuites(self, dev_key, tplan_id):
        """Obtains all test suites asigned to test plan created on remote
            testlink database, can filter by test plan id

        Arguments:
            dev_key {str} -- string of developer key provided by Testlink
                (default: {value obtained from JSON settings file})
            tplan_id {int} -- ID of Testlink Test Plan data

        Raises:
            Exception -- [description]

        Returns:
            str -- string xml object ready to use on API call
        """
        if not tplan_id:
            raise Exception("Can't call XMLRPC without param, tplan_id")
        self.req_create(dev_key, RouteType.TPLAN_BUILDS, params=True)
        self.req_params().append(
            {"name": "testplanid", "value": tplan_id}
        )
        xml = dicttoxml(
            self.req_dict, custom_root='methodCall', attr_type=False)
        return xml

    def req_tplan_tcases(self, dev_key, tplan_id):
        """Obtains all test cases asigned to test plan created on remote
            testlink database, can filter by test plan id

        Arguments:
            dev_key {str} -- string of developer key provided by Testlink
                (default: {value obtained from JSON settings file})
            tplan_id {int} -- ID of Testlink Test Plan data

        Raises:
            Exception -- [description]

        Returns:
            str -- string xml object ready to use on API call
        """
        if not tplan_id:
            raise Exception("Can't call XMLRPC without param, tplan_id")
        self.req_create(dev_key, RouteType.TPLAN_TCASES, params=True)
        self.req_params().append(
            {"name": "testplanid", "value": tplan_id}
        )
        xml = dicttoxml(
            self.req_dict, custom_root='methodCall', attr_type=False)
        return xml

    def req_tplan_build_latest(self, dev_key, tplan_id):
        """Obtains latest build by choosing the maximum build id for a specific
            test plan remote testlink database, can filter by test plan id

        Arguments:
            dev_key {str} -- string of developer key provided by Testlink
                (default: {value obtained from JSON settings file})
            tplan_id {int} -- ID of Testlink Test Plan data

        Raises:
            Exception -- Bad params

        Returns:
            str -- string xml object ready to use on API call
        """
        if not tplan_id:
            raise Exception("Can't call XMLRPC without param, tplan_id")
        self.req_create(dev_key, RouteType.TPLAN_BUILD_LATEST, params=True)
        self.req_params().append(
            {"name": "testplanid", "value": tplan_id}
        )
        xml = dicttoxml(
            self.req_dict, custom_root='methodCall', attr_type=False)
        return xml

    def req_tplan_totals(self, dev_key, tplan_id):
        """Obtains latest totals by choosing the maximum tplan id on remote
            testlink database, can filter by test plan id

        Arguments:
            dev_key {str} -- string of developer key provided by Testlink
                (default: {value obtained from JSON settings file})
            tplan_id {int} -- ID of Testlink Test Plan data

        Raises:
            Exception -- Bad params

        Returns:
            str -- string xml object ready to use on API call
        """
        if not tplan_id:
            raise Exception("Can't call XMLRPC without param, tplan_id")
        self.req_create(dev_key, RouteType.TPLAN_TOTALS, params=True)
        self.req_params().append(
            {"name": "testplanid", "value": tplan_id}
        )
        xml = dicttoxml(
            self.req_dict, custom_root='methodCall', attr_type=False)
        return xml

    def req_tsuite_by_id(self, dev_key, tsuite_id):
        """Obtains one test suite created on remote testlink database, can
            filter by test plan id

        Arguments:
            dev_key {str} -- string of developer key provided by Testlink
                (default: {value obtained from JSON settings file})
            tsuite_id {int} -- ID of Testlink Test Suite data

        Raises:
            Exception -- Bad params

        Returns:
            str -- string xml object ready to use on API call
        """
        if not tsuite_id:
            raise Exception("Can't call XMLRPC without param, tsuite_id")
        self.req_create(dev_key, RouteType.TSUITE_BY_ID, params=True)
        self.req_params().append(
            {"name": "testsuiteid", "value": tsuite_id}
        )
        xml = dicttoxml(
            self.req_dict, custom_root='methodCall', attr_type=False)
        return xml

    def req_tsuite_tsuites_by_id(self, dev_key, tsuite_id):
        """Obtains all test suites down of one test suite created on remote
            testlink database, can filter by test plan id

        Arguments:
            dev_key {str} -- string of developer key provided by Testlink
                (default: {value obtained from JSON settings file})
            tsuite_id {int} -- ID of Testlink Test Suite data

        Raises:
            Exception -- Bad params

        Returns:
            str -- string xml object ready to use on API call
        """
        if not tsuite_id:
            raise Exception("Can't call XMLRPC without param, tsuite_id")
        self.req_create(dev_key, RouteType.TSUITE_TSUITES, params=True)
        self.req_params().append(
            {"name": "testsuiteid", "value": tsuite_id}
        )
        xml = dicttoxml(
            self.req_dict, custom_root='methodCall', attr_type=False)
        return xml

    def req_tcase_by_id_or_external(self, dev_key,
                                    tcase_id=None, external_id=None):
        """Obtains one test case created on remote testlink database, can
            filter by test case id (int) or external id (str)

        Arguments:
            dev_key {str} -- string of developer key provided by Testlink
                (default: {value obtained from JSON settings file})
            tcase_id {int} -- ID of Testlink Test Case data (default: None)
            external_id {str} -- tc_full_external_id of Testlink Test Case
                data (default: None)

        Raises:
            Exception -- Bad params

        Returns:
            str -- string xml object ready to use on API call
        """
        if tcase_id and external_id:
            raise Exception(
                ("Can't call XMLRPC without both params,"
                 "choose one of : [tcase_id, external_id]"))
        if not tcase_id and not external_id:
            raise Exception(
                ("Can't call XMLRPC without any params,"
                 "choose one of : [tcase_id, external_id]"))
        self.req_create(dev_key, RouteType.TCASE_BY_IDS, params=True)
        if isinstance(tcase_id, int):
            self.req_params().append(
                {"name": "testcaseid", "value": int(tcase_id)}
            )
        if external_id:
            self.req_params().append(
                {"name": "testcaseexternalid", "value": str(external_id)}
            )
        xml = dicttoxml(
            self.req_dict, custom_root='methodCall', attr_type=False)
        return xml

    def req_tcase_by_name(self, dev_key, tcase_name):
        """Obtains one test case created on remote testlink database, can
            filter by test case name (str)

        Arguments:
            dev_key {str} -- string of developer key provided by Testlink
                (default: {value obtained from JSON settings file})
            tcase_name {str} -- NAME of Testlink Test Case data

        Raises:
            Exception -- Bad params

        Returns:
            str -- string xml object ready to use on API call
        """
        if not tcase_name:
            raise Exception("Can't call XMLRPC without param, tcase_name")
        self.req_create(dev_key, RouteType.TCASE_ID_BY_NAME, params=True)
        self.req_params().append(
            {"name": "testcasename", "value": tcase_name}
        )
        xml = dicttoxml(
            self.req_dict, custom_root='methodCall', attr_type=False)
        return xml

    def req_tcase_report(self, **kwargs):
        """Reports a result for a single test case

        Keyword Arguments:
            tcase_id {[type]} -- [description] (default: {None})
            external_id {[type]} -- [description] (default: {None})
            tplan_id {[type]} -- [description] (default: {None})
            status {[type]} -- [description] (default: {None})
            build_id {[type]} -- [description] (default: {None})
            build_name {[type]} -- [description] (default: {None})
            notes {[type]} -- [description] (default: {None})
            duration {[type]} -- [description] (default: {None})
            guess {[type]} -- [description] (default: {None})
            bug_id {[type]} -- [description] (default: {None})
            platform_id {[type]} -- [description] (default: {None})
            platform_name {[type]} -- [description] (default: {None})
            custom_fields {[type]} -- [description] (default: {None})
            overwrite {[type]} -- [description] (default: {None})
            user_name {[type]} -- [description] (default: {None})
            timestamp {[type]} -- [description] (default: {None})
            dev_key {[type]} -- [description] (default: {None})

        Returns:
            [type] -- [description]
        """
        if kwargs.get("tcase_id") and kwargs.get("external_id"):
            raise Exception(
                ("Can't call XMLRPC without both params,"
                 "choose one of : [tcase_id, external_id]"))
        if not kwargs.get("tcase_id") and not kwargs.get("external_id"):
            raise Exception(
                ("Can't call XMLRPC without any params,"
                 "choose one of : [tcase_id, external_id]"))
        if not kwargs.get("tplan_id"):
            raise Exception(
                "Can't call XMLRPC without any param 'tplan_id' ]")
        if not kwargs.get("status"):
            raise Exception(
                "Can't call XMLRPC without any param 'status' ]")
        if not kwargs.get("build_id"):
            raise Exception(
                "Can't call XMLRPC without any param 'build_id' ]")
        if not kwargs.get("platform_id"):
            raise Exception(
                "Can't call XMLRPC without any param 'platform_id' ]")
        self.req_create(
            kwargs.get("dev_key"),
            RouteType.TCASE_REPORT_RESULT,
            params=True)
        if kwargs.get("tcase_id"):
            self.req_params().append(
                {"name": "testcaseid", "value": int(kwargs.get("tcase_id"))}
            )
        if kwargs.get("external_id"):
            self.req_params().append(
                {"name": "testcaseexternalid", "value": str(
                    kwargs.get("external_id"))}
            )
        if kwargs.get("tplan_id"):
            self.req_params().append(
                {"name": "testplanid", "value": str(kwargs.get("tplan_id"))}
            )
        if kwargs.get("status"):
            self.req_params().append(
                {"name": "status", "value": str(kwargs.get("status"))}
            )
        if kwargs.get("build_id"):
            self.req_params().append(
                {"name": "buildid", "value": int(kwargs.get("build_id"))}
            )
        if kwargs.get("build_name"):
            self.req_params().append(
                {"name": "buildname", "value": str(kwargs.get("build_name"))}
            )
        if kwargs.get("notes"):
            self.req_params().append(
                {"name": "notes", "value": str(kwargs.get("notes"))}
            )
        if kwargs.get("duration"):
            self.req_params().append(
                {"name": "execduration", "value": int(kwargs.get("duration"))}
            )
        if kwargs.get("guess"):
            self.req_params().append(
                {"name": "guess", "value": int(kwargs.get("guess"))}
            )
        if kwargs.get("bug_id"):
            self.req_params().append(
                {"name": "bugid", "value": int(kwargs.get("bug_id"))}
            )
        if kwargs.get("platform_id"):
            self.req_params().append(
                {"name": "platformid", "value": int(
                    kwargs.get("platform_id"))}
            )
        if kwargs.get("platform_name"):
            self.req_params().append(
                {"name": "platformname", "value": str(
                    kwargs.get("platform_name"))}
            )
        if kwargs.get("custom_fields"):
            # noqa : param real name 'customfields'
            # noqa : array of member>(name+value>type)
            raise NotImplementedError("Open an issue at Github")
        if kwargs.get("overwrite"):
            self.req_params().append(
                {"name": "overwrite", "value": bool(
                    kwargs.get("overwrite"))}
            )
        if kwargs.get("user_name"):
            self.req_params().append(
                {"name": "user", "value": str(kwargs.get("user_name"))}
            )
        if kwargs.get("timestamp"):
            self.req_params().append(
                {"name": "timestamp", "value": str(kwargs.get("timestamp"))}
            )
        xml = dicttoxml(
            self.req_dict, custom_root='methodCall', attr_type=False)
        return xml

    def req_user_exist(self, dev_key, user_name):
        """String xml object ready to use on API call

        Arguments:
            dev_key {str} -- string for Testlink API_KEY
            user_name {str} -- NAME of Testlink user

        Returns:
            str -- XML request with parsed params
        """
        self.req_create(dev_key, RouteType.TLINK_USER_EXIST, params=True)
        self.req_params().append(
            {"name": "user", "value": user_name}
        )
        xml = dicttoxml(
            self.req_dict, custom_root='methodCall', attr_type=False)
        return xml

    def req_about(self):
        """String xml object ready to use on API call

        Returns:
            str -- XML request with parsed params
        """
        self.req_create(None, RouteType.TLINK_ABOUT, params=False)
        xml = dicttoxml(
            self.req_dict, custom_root='methodCall', attr_type=False)
        return xml

    def req_say_hello(self):
        """String xml object ready to use on API call

        Returns:
            str -- XML request with parsed params
        """
        self.req_create(None, RouteType.TLINK_SAY_HELLO, params=False)
        xml = dicttoxml(
            self.req_dict, custom_root='methodCall', attr_type=False)
        return xml

    def req_ping(self):
        """String xml object ready to use on API call

        Returns:
            str -- XML request with parsed params
        """
        self.req_create(None, RouteType.TLINK_PING, params=False)
        xml = dicttoxml(
            self.req_dict, custom_root='methodCall', attr_type=False)
        return xml

    def req_repeat(self, repeat):
        """String xml object ready to use on API call

        Returns:
            str -- XML request with parsed params
        """
        if not repeat:
            raise Exception("Can't call XMLRPC without param, repeat")
        self.req_create(None, RouteType.TLINK_REPEAT, params=True)
        self.req_params().append(
            {"name": "str", "value": repeat}
        )
        xml = dicttoxml(
            self.req_dict, custom_root='methodCall', attr_type=False)
        return xml
