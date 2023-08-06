# -*- coding: utf-8 -*-
"""Testlink Managers"""


from qatestlink.core.connections.connection_base import ConnectionBase
from qatestlink.core.logger_manager import LoggerManager
from qatestlink.core.models.tl_models import (
    TBuild, TCase, TPlan, TPlatform, TProject, TSuite
)
from qatestlink.core.models.tl_reports import (
    RTCase, RTPlanTotals
)
from qatestlink.core.utils import settings as settings_func
from qatestlink.core.xmls.xmlrpc_manager import XMLRPCManager


PATH_CONFIG = 'qatestlink/configs/settings.json'


class TLManager(object):
    """
    This class allows to send, handle and interpretate reponses
     to/from testlink api XMLRPC
    """

    _settings_path = None
    _settings = None
    _logger_manager = None
    _xml_manager = None
    _conn = None

    log = None

    def __init__(self, file_path=None, file_name=None, settings=None):
        """
        This instance allow to handle requests+reponses to/from XMLRPC
        just need settings_path and settings dict loaded to works

        :Args:
            settings_path: Path for search JSON
                file with settings values
            settings: Load settings at default path,
                'qatestlink/configs/settings.json'
        """
        if not settings:
            if not file_path or not file_name:
                settings = settings_func()
            else:
                settings = settings_func(
                    file_path=file_path,
                    file_name=file_name)
        self._settings = settings
        self._logger_manager = LoggerManager(
            self._settings.get('log_level'))
        self.log = self._logger_manager.log
        self._xml_manager = XMLRPCManager(self.log)
        # generate url using settings
        conn = self._settings.get('connection')
        self._conn = ConnectionBase(
            self.log,
            host=conn.get('host'),
            port=conn.get('port'),
            is_https=conn.get('is_https'))

    def api_login(self, dev_key=None):
        """Call to method named 'checkDevKey' for testlink XMLRPC

        Keyword Arguments:
            dev_key {str} -- string of developer key provided by Testlink
                (default: {value obtained from JSON settings file})

        Returns:
            bool -- check if developer key it's valid for Testlink
        """
        if not dev_key:
            dev_key = self._settings.get('dev_key')
        req_data = self._xml_manager.req_check_dev_key(dev_key)
        res = self._conn.post(self._xml_manager.headers, req_data)
        res_dict = self._xml_manager.parse_response(res)
        res_value = res_dict.get(
            'methodResponse')['params']['param']['value']
        if res_value.get('boolean'):
            return bool(res_value.get('boolean'))
        self._xml_manager.parse_errors(res_dict)

    def api_tprojects(self, dev_key=None):
        """Call to method named 'tl.getProjects' for testlink XMLRPC

        Keyword Arguments:
            dev_key {str} -- string of developer key provided by Testlink
                (default: {value obtained from JSON settings file})

        Returns:
            list(TProject) -- list of object model for Testlink Test Project
                data
        """
        if not dev_key:
            dev_key = self._settings.get('dev_key')
        req_data = self._xml_manager.req_tprojects(dev_key)
        res = self._conn.post(self._xml_manager.headers, req_data)
        res_dict = self._xml_manager.parse_response(res)
        res_param = res_dict.get(
            'methodResponse')['params']['param']['value']
        data_list = res_param.get('array')['data']['value']
        tprojects = list()
        for data_properties in data_list:
            properties = data_properties['struct']['member']
            tproject = TProject(properties)
            tprojects.append(tproject)
        return tprojects

    def api_tproject(self, tproject_name, dev_key=None):
        """Call to method named 'tl.getTestProjectByName' for testlink XMLRPC

        Arguments:
            tproject_name {str} -- name of testlink Test Project

        Keyword Arguments:
            dev_key {str} -- string of developer key provided by Testlink
                (default: {value obtained from JSON settings file})

        Returns:
            TProject -- object model for Testlink Test Project data
        """
        if not dev_key:
            dev_key = self._settings.get('dev_key')
        req_data = self._xml_manager.req_tproject_by_name(
            dev_key, tproject_name)
        res = self._conn.post(self._xml_manager.headers, req_data)
        res_dict = self._xml_manager.parse_response(res)
        res_param = res_dict.get(
            'methodResponse')['params']['param']['value']
        data_properties = res_param['struct']['member']
        return TProject(data_properties)

    def api_tproject_tplans(self, tproject_id, dev_key=None):
        """Call to method named 'tl.getProjectTestPlans' for testlink XMLRPC

        Arguments:
            tproject_id {int} -- ID of Testlink Test Project to get Testlink
                Test Plan

        Keyword Arguments:
            dev_key {str} -- string of developer key provided by Testlink
                (default: {value obtained from JSON settings file})

        Returns:
            list(TPlan) -- list of object model for Testlink Test Plan data
        """
        if not dev_key:
            dev_key = self._settings.get('dev_key')
        req_data = self._xml_manager.req_tproject_tplans(
            dev_key, tproject_id)
        res = self._conn.post(self._xml_manager.headers, req_data)
        res_dict = self._xml_manager.parse_response(res)
        res_param = res_dict.get(
            'methodResponse')['params']['param']['value']
        data_list = res_param.get('array')['data']['value']
        tplans = list()
        for data_properties in data_list:
            properties = data_properties['struct']['member']
            tplan = TPlan(properties)
            tplans.append(tplan)
        return tplans

    def api_tproject_tsuites_first_level(self, tproject_id, dev_key=None):
        """Call to method named 'tl.getFirstLevelTestSuitesForTestProject' for
            testlink XMLRPC

        Arguments:
            tproject_id {int} -- ID of Testlink Test Project to get Testlink
                Test Plan

        Keyword Arguments:
            dev_key {str} -- string of developer key provided by Testlink
                (default: {value obtained from JSON settings file})

        Returns:
            list(TSuite) -- list of object model for Testlink Test Suite
                data
        """
        if not dev_key:
            dev_key = self._settings.get('dev_key')
        req_data = self._xml_manager.req_tproject_tsuites_first_level(
            dev_key, tproject_id)
        res = self._conn.post(self._xml_manager.headers, req_data)
        res_dict = self._xml_manager.parse_response(res)
        res_param = res_dict.get(
            'methodResponse')['params']['param']['value']
        data_list = res_param.get('array')['data']['value']
        tsuites = list()
        try:
            for data_properties in data_list:
                properties = data_properties['struct']['member']
                tsuite = TSuite(properties)
                tsuites.append(tsuite)
            return tsuites
        except TypeError:
            raise self._xml_manager.parse_errors(res_dict)

    def api_tplan(self, tproject_name, tplan_name, dev_key=None):
        """Call to method named 'tl.getTestPlanByName' for testlink XMLRPC

        Arguments:
            tproject_name {str} -- NAME of Testlink Test Project to get
                Testlink Test Project
            tplan_name {str} -- NAME of Testlink Test Project to get Testlink
                Test Plan

        Keyword Arguments:
            dev_key {str} -- string of developer key provided by Testlink
                (default: {value obtained from JSON settings file})

        Returns:
            TPlan -- object model for Testlink Test Plan data
        """
        if not dev_key:
            dev_key = self._settings.get('dev_key')
        req_data = self._xml_manager.req_tplan_by_name(
            dev_key, tproject_name, tplan_name)
        res = self._conn.post(self._xml_manager.headers, req_data)
        res_dict = self._xml_manager.parse_response(res)
        res_param = res_dict.get(
            'methodResponse')['params']['param']['value']
        data_properties = res_param.get(
            'array')['data']['value']['struct']['member']
        return TPlan(data_properties)

    def api_tplan_platforms(self, tplan_id, dev_key=None):
        """Call to method named 'tl.getTestPlanPlatforms' for testlink XMLRPC

        Arguments:
            tplan_id {int} -- ID of Testlink Test Project to get Testlink
                Test Plan

        Keyword Arguments:
            dev_key {str} -- string of developer key provided by Testlink
                (default: {value obtained from JSON settings file})

        Returns:
            list(TPlatform) -- list of object model for Testlink Platform data
        """
        if dev_key is None:
            dev_key = self._settings.get('dev_key')
        req_data = self._xml_manager.req_tplan_platforms(dev_key, tplan_id)
        res = self._conn.post(self._xml_manager.headers, req_data)
        res_dict = self._xml_manager.parse_response(res)
        res_param = res_dict.get(
            'methodResponse')['params']['param']['value']
        data_list = res_param.get('array')['data']['value']
        tplatforms = list()
        for data_properties in data_list:
            properties = data_properties['struct']['member']
            tplatform = TPlatform(properties)
            tplatforms.append(tplatform)
        return tplatforms

    def api_tplan_builds(self, tplan_id, dev_key=None):
        """Call to method named 'tl.getBuildsForTestPlan' for testlink XMLRPC

        Arguments:
            tplan_id {int} -- ID of Testlink Test Project to get Testlink
                Test Plan

        Keyword Arguments:
            dev_key {str} -- string of developer key provided by Testlink
                (default: {value obtained from JSON settings file})

        Returns:
            list(TBuild) -- list of object model for Testlink Build data
        """
        if not dev_key:
            dev_key = self._settings.get('dev_key')
        req_data = self._xml_manager.req_tplan_builds(dev_key, tplan_id)
        res = self._conn.post(self._xml_manager.headers, req_data)
        res_dict = self._xml_manager.parse_response(res)
        res_param = res_dict.get(
            'methodResponse')['params']['param']['value']
        data_list = res_param.get('array')['data']['value']
        tbuilds = list()
        for data_properties in data_list:
            properties = data_properties['struct']['member']
            tbuild = TBuild(properties)
            tbuilds.append(tbuild)
        return tbuilds

    def api_tplan_tsuites(self, tplan_id, dev_key=None):
        """Call to method named 'tl.getTestSuitesForTestPlan' for testlink
            XMLRPC

        Arguments:
            tplan_id {int} -- ID of Testlink Test Project to get Testlink
                Test Plan

        Keyword Arguments:
            dev_key {str} -- string of developer key provided by Testlink
                (default: {value obtained from JSON settings file})

        Returns:
            list(TSuite) -- list of object model for Testlink Test Suite data
        """
        if not dev_key:
            dev_key = self._settings.get('dev_key')
        req_data = self._xml_manager.req_tplan_tsuites(dev_key, tplan_id)
        res = self._conn.post(self._xml_manager.headers, req_data)
        res_dict = self._xml_manager.parse_response(res)
        res_param = res_dict.get(
            'methodResponse')['params']['param']['value']
        data_list = res_param.get('array')['data']['value']
        tsuites = list()
        try:
            for data_properties in data_list:
                properties = data_properties['struct']['member']
                tsuite = TSuite(properties)
                tsuites.append(tsuite)
            return tsuites
        except TypeError:
            raise self._xml_manager.parse_errors(res_dict)

    def api_tplan_tcases(self, tplan_id, dev_key=None):
        """Call to method named 'tl.getTestCasesForTestPlan' for testlink
            XMLRPC

        Arguments:
            tplan_id {int} -- ID of Testlink Test Project to get Testlink
                Test Plan

        Keyword Arguments:
            dev_key {str} -- string of developer key provided by Testlink
                (default: {value obtained from JSON settings file})

        Returns:
            list(TCase) -- list of object model for Testlink Test Case data
        """
        if dev_key is None:
            dev_key = self._settings.get('dev_key')
        req_data = self._xml_manager.req_tplan_tcases(dev_key, tplan_id)
        res = self._conn.post(self._xml_manager.headers, req_data)
        res_dict = self._xml_manager.parse_response(res)
        res_param = res_dict.get(
            'methodResponse')['params']['param']['value']
        data_list = res_param.get('struct')['member']
        tcases = list()
        for data_properties in data_list:
            # TODO: make all assigned builds reporting to models,
            # not just first
            properties = data_properties.get(
                'value')['struct']['member'][0]['value']['struct']['member']
            tcase = TCase(properties)
            tcases.append(tcase)
        return tcases

    def api_tplan_build_latest(self, tplan_id, dev_key=None):
        """TODO: doc"""
        if dev_key is None:
            dev_key = self._settings.get('dev_key')
        req_data = self._xml_manager.req_tplan_build_latest(dev_key, tplan_id)
        res = self._conn.post(self._xml_manager.headers, req_data)
        res_dict = self._xml_manager.parse_response(res)
        res_param = res_dict.get(
            'methodResponse')['params']['param']['value']
        properties = res_param.get('struct')['member']
        return TBuild(properties)

    def api_tplan_totals(self, tplan_id, dev_key=None):
        """TODO: doc"""
        if dev_key is None:
            dev_key = self._settings.get('dev_key')
        req_data = self._xml_manager.req_tplan_totals(dev_key, tplan_id)
        res = self._conn.post(self._xml_manager.headers, req_data)
        res_dict = self._xml_manager.parse_response(res)
        res_param = res_dict.get(
            'methodResponse')['params']['param']['value']
        properties = res_param.get('struct')['member']
        return RTPlanTotals(properties)

    def api_tsuite(self, tsuite_id, dev_key=None):
        """TODO: doc"""
        if dev_key is None:
            dev_key = self._settings.get('dev_key')
        req_data = self._xml_manager.req_tsuite_by_id(dev_key, tsuite_id)
        res = self._conn.post(self._xml_manager.headers, req_data)
        res_dict = self._xml_manager.parse_response(res)
        try:
            res_param = res_dict.get(
                'methodResponse')['params']['param']['value']
            properties = res_param.get('struct')['member']
            return TSuite(properties)
        except TypeError:
            raise self._xml_manager.parse_errors(res_dict)

    def api_tsuite_tsuites(self, tsuite_id, dev_key=None):
        """TODO: doc"""
        if dev_key is None:
            dev_key = self._settings.get('dev_key')
        req_data = self._xml_manager.req_tsuite_tsuites_by_id(
            dev_key, tsuite_id)
        res = self._conn.post(self._xml_manager.headers, req_data)
        res_dict = self._xml_manager.parse_response(res)
        res_param = res_dict.get(
            'methodResponse')['params']['param']['value']
        data_list = res_param.get('struct')['member']
        tsuites = list()
        for data_properties in data_list:
            properties = data_properties['value']['struct']['member']
            tsuite = TSuite(properties)
            tsuites.append(tsuite)
        return tsuites

    def api_tcase(self, tcase_id=None, external_id=None, dev_key=None):
        """TODO: doc"""
        if dev_key is None:
            dev_key = self._settings.get('dev_key')
        req_data = self._xml_manager.req_tcase_by_id_or_external(
            dev_key, tcase_id=tcase_id, external_id=external_id)
        res = self._conn.post(self._xml_manager.headers, req_data)
        res_dict = self._xml_manager.parse_response(res)
        res_param = res_dict.get(
            'methodResponse')['params']['param']['value']
        properties = res_param.get(
            'array')['data']['value']['struct']['member']
        return TCase(properties)

    def api_tcase_by_name(self, tcase_name, dev_key=None):
        """TODO: doc"""
        if dev_key is None:
            dev_key = self._settings.get('dev_key')
        req_data = self._xml_manager.req_tcase_by_name(
            dev_key, tcase_name)
        res = self._conn.post(self._xml_manager.headers, req_data)
        res_dict = self._xml_manager.parse_response(res)
        res_param = res_dict.get(
            'methodResponse')['params']['param']['value']
        properties = res_param.get(
            'array')['data']['value']['struct']['member']
        return TCase(properties)

    def api_tcase_report(self, **kwargs):
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
        if not kwargs.get('dev_key'):
            kwargs['dev_key'] = self._settings.get('dev_key')
        req_data = self._xml_manager.req_tcase_report(**kwargs)
        res = self._conn.post(self._xml_manager.headers, req_data)
        res_dict = self._xml_manager.parse_response(res)
        res_param = res_dict.get(
            'methodResponse')['params']['param']['value']
        properties = res_param.get(
            'array')['data']['value']['struct']['member']
        return RTCase(properties)

    def api_user_exist(self, user_name, dev_key=None):
        """Call to method named 'tl.doesUserExist' for testlink XMLRPC

        Keyword Arguments:
            user_name {str} -- NAME of remote testlink user
            dev_key {str} -- string of developer key provided by Testlink
                (default: {value obtained from JSON settings file})

        Returns:
            bool -- check if user name it's valid for Testlink
        """
        if not dev_key:
            dev_key = self._settings.get('dev_key')
        req_data = self._xml_manager.req_user_exist(dev_key, user_name)
        res = self._conn.post(self._xml_manager.headers, req_data)
        res_dict = self._xml_manager.parse_response(res)
        res_value = res_dict.get(
            'methodResponse')['params']['param']['value']
        if res_value.get('boolean'):
            return bool(res_value.get('boolean'))
        self._xml_manager.parse_errors(res_dict)

    def api_about(self):
        """Call to method named 'tl.about' for testlink XMLRPC

        Returns:
            str -- Message predefined by Testlink code
        """
        req_data = self._xml_manager.req_about()
        res = self._conn.post(self._xml_manager.headers, req_data)
        res_dict = self._xml_manager.parse_response(res)
        res_value = res_dict.get(
            'methodResponse')['params']['param']['value']
        return str(res_value.get('string'))

    def api_say_hello(self):
        """Call to method named 'tl.sayHello' for testlink XMLRPC

        Returns:
            str -- Message predefined by Testlink code
        """
        req_data = self._xml_manager.req_say_hello()
        res = self._conn.post(self._xml_manager.headers, req_data)
        res_dict = self._xml_manager.parse_response(res)
        res_value = res_dict.get(
            'methodResponse')['params']['param']['value']
        return str(res_value.get('string'))

    def api_ping(self):
        """Call to method named 'tl.ping' for testlink XMLRPC

        Returns:
            str -- Message predefined by Testlink code
        """
        req_data = self._xml_manager.req_ping()
        res = self._conn.post(self._xml_manager.headers, req_data)
        res_dict = self._xml_manager.parse_response(res)
        res_value = res_dict.get(
            'methodResponse')['params']['param']['value']
        return str(res_value.get('string'))

    def api_repeat(self, repeat):
        """Call to method named 'tl.repeat' for testlink XMLRPC

        Returns:
            str -- Message predefined by Testlink code
        """
        req_data = self._xml_manager.req_repeat(repeat)
        res = self._conn.post(self._xml_manager.headers, req_data)
        res_dict = self._xml_manager.parse_response(res)
        res_value = res_dict.get(
            'methodResponse')['params']['param']['value']
        return str(res_value.get('string'))
