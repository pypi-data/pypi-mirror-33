# -*- coding: utf-8 -*-
"""All method names used on official XMLRPC calls"""


from enum import Enum


class RouteType(Enum):
    """
    Official doc:
        https://github.com/viglesiasce/testlink/blob/master/lib/api/xmlrpc.class.php

    All REQUEST methods names to use on classes:
        XmlBase
            XmlRequest
            XmlResponse

    Documented Enumerator
        use intellisense to improve development
    """

    # TestProjects

    """TODO
    Args:
        devKey:string
            authorization dev key
    """
    TPROJECT_CREATE = 'tl.createTestProject'

    """TODO
    Args:
        devKey:string
            authorization dev key
    """
    TPROJECTS = 'tl.getProjects'

    """TODO
    Args:
        devKey:string
            authorization dev key
    """
    TPROJECT_BY_NAME = 'tl.getTestProjectByName'

    """TODO
    Args:
        devKey:string
            authorization dev key
    """
    TPROJECT_TEST_PLANS = 'tl.getProjectTestPlans'

    """TODO
    Args:
        devKey:string
            authorization dev key
    """
    TPROJECT_TSUITES_FIRST_LEVEL = 'tl.getFirstLevelTestSuitesForTestProject'

    # TestPlans

    """TODO
    Args:
        devKey:string
            authorization dev key
    """
    TPLAN_CREATE = 'tl.createTestPlan'

    """TODO
    Args:
        devKey:string
            authorization dev key
    """
    TPLAN_ADD_TCASE = 'tl.addTestCaseToTestPlan'

    """TODO
    Args:
        devKey:string
            authorization dev key
    """
    TPLAN_BY_NAME = 'tl.getTestPlanByName'

    """TODO
    Args:
        devKey:string
            authorization dev key
    """
    TPLAN_PLATFORMS = 'tl.getTestPlanPlatforms'

    """TODO
    Args:
        devKey:string
            authorization dev key
    """
    TPLAN_TOTALS = 'tl.getTotalsForTestPlan'

    """TODO
    Args:
        devKey:string
            authorization dev key
    """
    TPLAN_BUILDS = 'tl.getBuildsForTestPlan'

    """TODO
    Args:
        devKey:string
            authorization dev key
    """
    TPLAN_BUILD_LATEST = 'tl.getLatestBuildForTestPlan'

    """TODO
    Args:
        devKey:string
            authorization dev key
    """
    TPLAN_EXEC_LATEST = 'tl.getLastExecutionResult'

    """TODO
    Args:
        devKey:string
            authorization dev key
    """
    TPLAN_TSUITES = 'tl.getTestSuitesForTestPlan'

    """TODO
    Args:
        devKey:string
            authorization dev key
    """
    TPLAN_TCASES = 'tl.getTestCasesForTestPlan'
    # Builds

    """TODO
    Args:
        devKey:string
            authorization dev key
    """
    BUILD_CREATE = 'tl.createBuild'
    # Testsuites

    """TODO
    Args:
        devKey:string
            authorization dev key
    """
    TSUITE_CREATE = 'tl.createTestSuite'

    """TODO
    Args:
        devKey:string
            authorization dev key
    """
    TSUITE_TSUITES = 'tl.getTestSuitesForTestSuite'

    """TODO
    Args:
        devKey:string
            authorization dev key
    """
    TSUITE_BY_ID = 'tl.getTestSuiteByID'

    """TODO
    Args:
        devKey:string
            authorization dev key
    """
    TSUITE_TCASES = 'tl.getTestCasesForTestSuite'
    # Requirements

    """TODO
    Args:
        devKey:string
            authorization dev key
    """
    REQ_ASSIGN = 'tl.assignRequirements'
    # Testcases

    """TODO
    Args:
        devKey:string
            authorization dev key
    """
    TCASE_REPORT_RESULT = 'tl.reportTCResult'

    """TODO
    Args:
        devKey:string
            authorization dev key
    """
    TCASE_EXEC_RESULT = 'tl.setTestCaseExecutionResult'

    """TODO
    Args:
        devKey:string
            authorization dev key
    """
    TCASE_CREATE = 'tl.createTestCase'

    """TODO
    Args:
        devKey:string
            authorization dev key
    """
    TCASE_ID_BY_NAME = 'tl.getTestCaseIDByName'

    """TODO
    Args:
        devKey:string
            authorization dev key
    """
    TCASE_CUSTOM_FIELD_DESIGN_VALUE = 'tl.getTestCaseCustomFieldDesignValue'

    """TODO
    Args:
        devKey:string
            authorization dev key
    """
    TCASE_ATTACHMENTS = 'tl.getTestCaseAttachments'

    """
    Args:
        devKey:string
            authorization dev key
        testcaseid:int
            optional, if does not is present
            testcaseexternalid must be present
        testcaseexternalid:int
            optional, if does not is present
            testcaseid must be present
        version:int
            optional, if does not is present
            max version number will be retuned
    """
    TCASE_BY_IDS = 'tl.getTestCase'

    # Utils
    """TODO:
    I really don't know objetive of this method
    Also don't know about mixed type
    Args:
        devKey:string
            authorization dev key
        nodeID:mixed
    """
    TLINK_FULL_PATH = 'tl.getFullPath'

    """
    Args:
        devKey:string
            authorization dev key
        executionid: int
    Response:
       resultInfo:mixed
           status: true/false of success
           id: result id or error code
           message: optional message for error message string
    """
    TLINK_EXEC_DELETE = 'tl.deleteExecution'

    """
    Args:
        devKey:string
            authorization dev key
        user:string
            user name
    Response:
        true if everything OK, otherwise error structure
    """
    TLINK_USER_EXIST = 'tl.doesUserExist'

    """
    Args:
        devKey:string
            authorization dev key
    Response:
        true if everything OK, otherwise error structure
    """
    TLINK_CHECK_DEV_KEY = 'tl.checkDevKey'

    """
    Args:
        without args
    Response:
        string
             Testlink API Version {version} initially written
             by Asiel Brumfield with contributions by
             TestLink development Team
    """
    TLINK_ABOUT = 'tl.about'

    """
    TODO: official developer said this don't work
    This method is meant primarily for testing
    and debugging during development
    Args:
        without args
    Response:
        bool: if state changed returns True, False if not
    """
    TLINK_TMODE_TOGGLE = 'tl.setTestMode'

    """
    Just and alias for TLINK_SAY_HELLO request
    Args:
        without args
    Response:
        string: "Hello!"
    """
    TLINK_PING = 'tl.ping'

    """
    Just return a message
    Args:
        without args
    Response:
        string: "Hello!"
    """
    TLINK_SAY_HELLO = 'tl.sayHello'

    """
    Just return your message contained on another message
    Args:
        str: string message to be contained
    Response:
        string: "You said: {str arg}"
    """
    TLINK_REPEAT = 'tl.repeat'
