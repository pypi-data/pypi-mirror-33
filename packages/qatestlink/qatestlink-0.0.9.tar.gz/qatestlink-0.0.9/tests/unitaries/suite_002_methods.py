# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""TODO: doc module"""


import logging
from unittest import TestCase
from unittest import skipIf
from qatestlink.core.exceptions.response_exception import ResponseException
from qatestlink.core.models.tl_models import (
    TBuild, TCase, TPlan, TPlatform, TProject, TSuite
)
from qatestlink.core.models.tl_reports import (
    RTCase, RTPlanTotals
)
from qatestlink.core.testlink_manager import TLManager
from qatestlink.core.utils import settings


SETTINGS = settings()
API_DEV_KEY = SETTINGS['dev_key']
SKIP = SETTINGS['tests']['skip']['methods']
SKIP_MESSAGE = SETTINGS['tests']['skip_message']
DATA = SETTINGS['tests']['data']


class TestMethods(TestCase):
    """TODO: doc class"""

    @classmethod
    def setUpClass(cls):
        """TODO: doc method"""
        cls.testlink_manager = TLManager()

    def setUp(self):
        """TODO: doc method"""
        self.assertIsInstance(
            self.testlink_manager, TLManager)
        self.assertIsInstance(
            self.testlink_manager.log, logging.Logger)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_001_method_tprojects(self):
        """TODO: doc method"""
        tprojects = self.testlink_manager.api_tprojects(
            dev_key=API_DEV_KEY)
        self.assertIsInstance(tprojects, list)
        self.assertGreater(len(tprojects), 0)
        for tproject in tprojects:
            self.testlink_manager.log.debug(repr(tproject))
            self.assertIsInstance(tproject, TProject)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_002_method_tproject(self):
        """TODO: doc method"""
        tproject = self.testlink_manager.api_tproject(DATA['tproject_name'])
        self.assertIsInstance(tproject, TProject)
        self.assertEquals(tproject.name, DATA['tproject_name'])

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_003_method_tproject_tplans(self):
        """TODO: doc method"""
        tplans = self.testlink_manager.api_tproject_tplans(DATA['tproject_id'])
        self.assertIsInstance(tplans, list)
        self.assertGreater(len(tplans), 0)
        for tplan in tplans:
            self.testlink_manager.log.debug(repr(tplan))
            self.assertIsInstance(tplan, TPlan)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_004_method_tproject_tsuites_first_level(self):
        """TODO: doc method"""
        tsuites = self.testlink_manager.api_tproject_tsuites_first_level(
            DATA['tproject_id'])
        self.assertIsInstance(tsuites, list)
        self.assertGreater(len(tsuites), 0)
        for tsuite in tsuites:
            self.testlink_manager.log.debug(repr(tsuite))
            self.assertIsInstance(tsuite, TSuite)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_005_method_tplan(self):
        """TODO: doc method"""
        tplan = self.testlink_manager.api_tplan(
            DATA['tproject_name'], DATA['tplan_name'])
        self.assertIsInstance(tplan, TPlan)
        self.assertEquals(tplan.name, DATA['tplan_name'])
        self.assertEquals(tplan.tproject_id, DATA['tproject_id'])

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_006_method_tplan_platforms(self):
        """TODO: doc method"""
        platforms = self.testlink_manager.api_tplan_platforms(
            DATA['tplan_id'])
        self.assertIsInstance(platforms, list)
        self.assertGreater(len(platforms), 0)
        for platform in platforms:
            self.testlink_manager.log.debug(repr(platform))
            self.assertIsInstance(platform, TPlatform)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_007_method_tplan_builds(self):
        """TODO: doc method"""
        builds = self.testlink_manager.api_tplan_builds(DATA['tplan_id'])
        self.assertIsInstance(builds, list)
        self.assertGreater(len(builds), 0)
        for build in builds:
            self.testlink_manager.log.debug(repr(build))
            self.assertIsInstance(build, TBuild)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_008_method_tplan_tsuites(self):
        """TODO: doc method"""
        tsuites = self.testlink_manager.api_tplan_tsuites(DATA['tplan_id'])
        self.assertIsInstance(tsuites, list)
        self.assertGreater(len(tsuites), 0)
        for tsuite in tsuites:
            self.testlink_manager.log.debug(repr(tsuite))
            self.assertIsInstance(tsuite, TSuite)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_009_method_tplan_tcases(self):
        """TODO: doc method"""
        tcases = self.testlink_manager.api_tplan_tcases(DATA['tplan_id'])
        self.assertIsInstance(tcases, list)
        self.assertGreater(len(tcases), 0)
        for tcase in tcases:
            self.testlink_manager.log.debug(repr(tcase))
            self.assertIsInstance(tcase, TCase)
            if tcase.id == DATA['tcase_id']:
                self.assertEquals(
                    tcase.full_external_id,
                    DATA['tcase_full_external_id']
                )

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_010_method_tplan_tbuild_latest(self):
        """TODO: doc method"""
        build = self.testlink_manager.api_tplan_build_latest(
            DATA['tplan_id'])
        self.assertIsInstance(build, TBuild)
        self.assertEquals(build.id, DATA['build_id_two'])
        self.assertEquals(build.name, DATA['build_name_two'])

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_011_method_tplan_totals(self):
        """TODO: doc method"""
        totals = self.testlink_manager.api_tplan_totals(
            DATA['tplan_id'])
        self.assertIsInstance(totals, RTPlanTotals)
        self.assertIsInstance(totals.by_tester, list)
        self.assertIsInstance(totals.by_tester[0]['user_id'], int)
        self.assertIsInstance(totals.by_tester[0]['report_types'], list)
        for by_tester_report_type in totals.by_tester[0]['report_types']:
            self.assertIsInstance(by_tester_report_type['platform_id'], int)
            self.assertIsInstance(by_tester_report_type['qty'], int)
            self.assertIsInstance(by_tester_report_type['report_type'], str)
            self.assertIn(
                by_tester_report_type['report_type'],
                ['p', 'n', 'b', 'f']
            )

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_012_method_tsuite(self):
        """TODO: doc method"""
        tsuite = self.testlink_manager.api_tsuite(
            DATA['tsuite_id'])
        self.assertIsInstance(tsuite, TSuite)
        self.assertEquals(tsuite.name, DATA['tsuite_name'])

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_013_method_tsuite_tsuites(self):
        """TODO: doc method"""
        tsuites = self.testlink_manager.api_tsuite_tsuites(
            DATA['tsuite_id'])
        self.assertIsInstance(tsuites, list)
        for tsuite in tsuites:
            self.assertIsInstance(tsuite, TSuite)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_014_method_tcase_byid(self):
        """TODO: doc method"""
        tcase = self.testlink_manager.api_tcase(
            tcase_id=DATA['tcase_id'])
        self.assertIsInstance(tcase, TCase)
        self.assertEquals(tcase.id, DATA['tcase_id'])

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_015_method_tcase_byexternalid(self):
        """TODO: doc method"""
        tcase = self.testlink_manager.api_tcase(
            external_id=DATA['tcase_full_external_id'])
        self.assertIsInstance(tcase, TCase)
        self.assertEquals(
            tcase.external_id, DATA['tcase_full_external_id'])

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_016_method_tcase_byname(self):
        """TODO: doc method"""
        tcase = self.testlink_manager.api_tcase_by_name(
            DATA['tcase_name'])
        self.assertIsInstance(tcase, TCase)
        self.assertEquals(
            tcase.name, DATA['tcase_name'])

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_017_method_tcase_report(self):
        """TODO: doc method"""
        report = self.testlink_manager.api_tcase_report(
            external_id=DATA['tc_report']['external_id'],
            tplan_id=DATA['tc_report']['tplan_id'],
            build_id=DATA['tc_report']['build_id'],
            platform_id=DATA['tc_report']['platform_id'],
            status=DATA['tc_report']['status']['blocked']
        )
        self.assertIsInstance(report, RTCase)
        self.assertTrue(report.status)
        self.assertEquals(
            report.message, DATA['tc_report']['message'])

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_018_method_user_exist(self):
        """TODO: doc method"""
        is_user = self.testlink_manager.api_user_exist(
            DATA['user_name'])
        self.assertTrue(is_user)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_019_method_about(self):
        """TODO: doc method"""
        about = self.testlink_manager.api_about()
        self.assertIsInstance(about, str)
        self.assertEquals(about, DATA['about'])

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_020_method_say_hello(self):
        """TODO: doc method"""
        say_hello = self.testlink_manager.api_say_hello()
        self.assertIsInstance(say_hello, str)
        self.assertEquals(say_hello, DATA['say_hello'])

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_021_method_ping(self):
        """TODO: doc method"""
        ping = self.testlink_manager.api_ping()
        self.assertIsInstance(ping, str)
        self.assertEquals(ping, DATA['ping'])

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_022_method_repeat(self):
        """TODO: doc method"""
        repeat = self.testlink_manager.api_repeat(DATA['repeat'])
        self.assertIsInstance(repeat, str)
        self.assertEquals(
            repeat, "You said: {}".format(DATA['repeat']))


class TestMethodsRaises(TestCase):
    """Test suite for tests methods

    Arguments:
        TestCase {unittest.TestCase} -- base python class for testing
    """

    @classmethod
    def setUpClass(cls):
        """TODO: doc method"""
        cls.testlink_manager = TLManager()

    def setUp(self):
        """TODO: doc method"""
        self.assertIsInstance(
            self.testlink_manager, TLManager)
        self.assertIsInstance(
            self.testlink_manager.log, logging.Logger)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_001_raises_tproject_notname(self):
        """TODO: doc method"""
        self.assertRaises(
            Exception, self.testlink_manager.api_tproject)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_002_raises_tproject_emptyname(self):
        """TODO: doc method"""
        self.assertRaises(
            Exception,
            self.testlink_manager.api_tproject,
            '')

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_003_raises_tproject_tplans_notid(self):
        """TODO: doc method"""
        self.assertRaises(
            Exception, self.testlink_manager.api_tproject_tplans)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_004_raises_tproject_tplans_notfoundid(self):
        """TODO: doc method"""
        self.assertRaises(
            Exception,
            self.testlink_manager.api_tproject_tplans,
            -1)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_005_raises_tproject_tsuites_first_level_notid(self):
        """TODO: doc method"""
        self.assertRaises(
            Exception, self.testlink_manager.api_tproject_tsuites_first_level)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_006_raises_tproject_tsuites_first_level_notfoundid(self):
        """TODO: doc method"""
        self.assertRaises(
            Exception,
            self.testlink_manager.api_tproject_tsuites_first_level,
            -1)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_007_raises_tplan_notname(self):
        """TODO: doc method"""
        self.assertRaises(
            Exception, self.testlink_manager.api_tplan)

    @skipIf(True, 'Test SKIPPED, waiting for issue https://github.com/viglesiasce/testlink/issues/7') # noqa
    def test_008_raises_tplan_emptytprojectname(self):
        """TODO: doc method"""
        self.assertRaises(
            Exception,
            self.testlink_manager.api_tplan,
            '',
            DATA['tplan_name'])

    @skipIf(True, 'Test SKIPPED, waiting for issue https://github.com/viglesiasce/testlink/issues/7') # noqa
    def test_009_raises_tplan_emptytplanname(self):
        """TODO: doc method"""
        self.assertRaises(
            Exception,
            self.testlink_manager.api_tplan,
            DATA['tproject_name'],
            '')

    @skipIf(True, 'Test SKIPPED, waiting for issue https://github.com/viglesiasce/testlink/issues/7') # noqa
    def test_010_raises_tplan_emptytnames(self):
        """TODO: doc method"""
        self.assertRaises(
            Exception,
            self.testlink_manager.api_tplan,
            '', '')

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_011_raises_tplan_platforms_notname(self):
        """TODO: doc method"""
        self.assertRaises(
            Exception, self.testlink_manager.api_tplan_platforms)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_012_raises_tplan_platforms_notfoundid(self):
        """TODO: doc method"""
        self.assertRaises(
            Exception,
            self.testlink_manager.api_tplan_platforms,
            -1)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_013_raises_tplan_builds_notid(self):
        """TODO: doc method"""
        self.assertRaises(
            Exception, self.testlink_manager.api_tplan_builds)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_014_raises_tplan_builds_notfoundid(self):
        """TODO: doc method"""
        self.assertRaises(
            Exception,
            self.testlink_manager.api_tplan_builds,
            -1)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_015_raises_tplan_tsuites_notid(self):
        """TODO: doc method"""
        self.assertRaises(
            Exception, self.testlink_manager.api_tplan_tsuites)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_016_raises_tplan_tsuites_notfoundid(self):
        """TODO: doc method"""
        self.assertRaises(
            ResponseException,
            self.testlink_manager.api_tplan_tsuites,
            -1)
