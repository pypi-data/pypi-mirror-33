# -*- coding: utf-8 -*-
"""TODO: doc module"""


import logging
from unittest import TestCase
from unittest import skipIf
from qatestlink.core.testlink_manager import TLManager
from qatestlink.core.utils import settings


SETTINGS = settings()
API_DEV_KEY = SETTINGS['dev_key']
SKIP = SETTINGS['tests']['skip']['connection']
SKIP_MESSAGE = SETTINGS['tests']['skip_message']


class TestConnection(TestCase):
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
    def test_001_connok_bysettings(self):
        """TODO: doc method"""
        self.assertTrue(
            self.testlink_manager.api_login())

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_002_connok_byparam(self):
        """TODO: doc method"""
        self.assertTrue(
            self.testlink_manager.api_login(
                dev_key=API_DEV_KEY))

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_003_connok_notdevkey(self):
        """TODO: doc method"""
        self.assertTrue(
            self.testlink_manager.api_login(
                dev_key=None))


class TestConnectionRaises(TestCase):
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
    def test_001_raises_connemptydevkey(self):
        """TODO: doc method"""
        self.assertRaises(
            Exception,
            self.testlink_manager.api_login, dev_key=' ')
