# -*- coding: utf-8 -*-

import os
import datetime
import logging
import pytest

from selenium.common.exceptions import (
    WebDriverException,
    ElementNotVisibleException,
    InvalidElementStateException,
    InvalidSelectorException,
    NoSuchElementException,
    StaleElementReferenceException
)

from promium.logger import Logger
from promium.core.exceptions import BrowserConsoleException


log = logging.getLogger(__name__)


def pytest_sessionstart(session):
    print(u"Lastfailed:", session.config.cache.get(
        u"cache/{}".format(session.config.lastfailed_file), set()
    ))
    session.run_duration = datetime.datetime.now()
    print(u"\nPytest session start %s\n" % session.run_duration)


@pytest.mark.trylast
def pytest_sessionfinish(session):
    finish = datetime.datetime.now()
    print(u"\n\nPytest session finish %s (duration=%s)\n" % (
        finish, datetime.timedelta(
            seconds=(finish - session.run_duration).seconds
        )
    ))


def pytest_addoption(parser):
    parser.addoption(
        "--capturelog",
        dest="logger",
        default=None,
        action="store_true",
        help="Show log messages for each failed test"
    )
    parser.addoption(
        "--fail-debug-info",
        action="store_true",
        help="Show screenshot and test case urls for each failed test"
    )
    parser.addoption(
        "--duration-time",
        action="store_true",
        help="Show the very slow test"
    )
    parser.addoption(
        "--highlight",
        action="store_true",
        help="Highlighting elements"
    )
    parser.addoption(
        "--chrome",
        action="store_true",
        help="Use chrome browser"
    )
    parser.addoption(
        "--firefox",
        action="store_true",
        help="Use firefox browser"
    )
    parser.addoption(
        "--opera",
        action="store_true",
        help="Use opera browser"
    )
    parser.addoption(
        "--ie",
        action="store_true",
        help="Use ie browser"
    )
    parser.addoption(
        "--edge",
        action="store_true",
        help="Use edge browser"
    )
    parser.addoption(
        "--grid",
        help=(
            "Use selenium grid host for example: '192.168.0.1:4444/wd/hub' "
            "or  with base auth "
            "'test:test-password@192.168.0.1:4444/wd/hub'"
        )
    )
    parser.addoption(
        "--repeat",
        action="store",
        default=1,
        type="int",
        metavar='repeat',
        help='Number of times to repeat each test. Mostly for debug purposes'
    )
    parser.addoption(
        "--check-console",
        action="store_true",
        help="Check browser console js and other errors"
    )


def pytest_generate_tests(metafunc):
    if metafunc.config.option.repeat > 1:
        metafunc.fixturenames.append('repeat')
        metafunc.parametrize('repeat', range(metafunc.config.option.repeat))


@pytest.fixture(autouse=True)
def logger(request):
    return logging.getLogger()


@pytest.mark.trylast
def pytest_runtest_call(item):
    if hasattr(item.config, "assertion_errors"):
        if item.config.assertion_errors:
            msg = u"\n{assertion_errors_list}\n".format(
                assertion_errors_list="\n".join(item.config.assertion_errors)
            )
            raise AssertionError(msg)
    if item.config.getoption("--check-console"):
        if hasattr(item.config, "check_console_errors"):
            browser_console_errors = item.config.check_console_errors()
            if browser_console_errors:
                msg = (
                    u"Browser console js errors found:"
                    u"\n{console_errors}\n".format(
                        console_errors=u"\n".join(
                            browser_console_errors
                        )
                    )
                )
                raise BrowserConsoleException(msg)


@pytest.mark.tryfirst
@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    """pytest failed test report generator"""
    html_plugin = item.config.pluginmanager.getplugin('html')
    outcome = yield
    report = outcome.get_result()
    when = report.when
    excinfo = call.excinfo
    extra = getattr(report, 'extra', [])

    # remove webdriver java traceback
    if excinfo:
        if excinfo.type in [
            ElementNotVisibleException,
            InvalidElementStateException,
            InvalidSelectorException,
            NoSuchElementException,
            StaleElementReferenceException
        ] and report.longrepr:
            report.longrepr.reprtraceback.reprentries[-1].lines = \
                report.longrepr.reprtraceback.reprentries[-1].lines[:2]

    if when == "call" and not report.passed:
        if item.config.getoption("--fail-debug-info"):
            fail_info = u"Fail info not found."
            try:
                if hasattr(item.config, "get_fail_debug"):
                    fail_debug = item.config.get_fail_debug()
                    is_vagga = False
                    for k in (dict(os.environ)).keys():
                        if 'VAGGA' in k:
                            is_vagga = True
                            break
                    if fail_debug[0] == 'webdriver':
                        (
                            url,
                            screenshot,
                            test_case_url,
                            pytest_failed_test_command,
                            vagga_failed_test_command
                        ) = fail_debug[1:]
                        test_case = (
                            u"\nTEST CASE: {}".format(test_case_url)
                            if test_case_url else u''
                        )
                        run_test_command = (
                            u"\nVAGGA COMMAND: {}".format(
                                vagga_failed_test_command
                            ) if is_vagga
                            else u"\nPYTEST COMMAND: {}".format(
                                pytest_failed_test_command
                            )
                        )
                        fail_info = (
                            (
                                u"\nURL: {url}"
                                u"{test_case_url}"
                                u"\nSCREENSHOT: {screenshot}"
                                u"{run_test_command}"
                                u"\n"
                            ).format(
                                url=url,
                                screenshot=screenshot,
                                test_case_url=test_case,
                                run_test_command=run_test_command,
                            )
                        )
                        extra.append(html_plugin.extras.url(
                            screenshot, name=u"SCREENSHOT"
                        ))
                        extra.append(
                            html_plugin.extras.html(
                                u"<img src=\"{img}\" "
                                u"height=\"230\" width=\"auto\" align=\""
                                u"right\" bottom=\"0px\">Screenshot</img>"
                                .format(
                                    img=screenshot
                                )
                            )
                        )
                    elif fail_debug[0] == 'request':
                        (
                            url,
                            status_code,
                            test_case_url,
                            pytest_failed_test_command,
                            vagga_failed_test_command
                        ) = fail_debug[1:]
                        test_case = (
                            u"\nTEST CASE: {}".format(test_case_url)
                            if test_case_url else u''
                        )
                        run_test_command = (
                            u"\nVAGGA COMMAND: {}".format(
                                vagga_failed_test_command
                            ) if is_vagga
                            else u"\nPYTEST COMMAND: {}".format(
                                pytest_failed_test_command
                            )
                        )
                        fail_info = (
                            u"\nURL: {url} (status code: {status_code})"
                            u"{test_case_url}"
                            u"{run_test_command}"
                            u"\n"
                        ).format(
                            url=url,
                            status_code=status_code,
                            test_case_url=test_case,
                            run_test_command=run_test_command,
                        )
                    extra.append(html_plugin.extras.url(
                        url, name=u"URL"
                    ))
                    extra.append(html_plugin.extras.url(
                        test_case_url, name=u"TEST CASE"
                    ))
                    report.extra = extra

            except WebDriverException as e:
                fail_info = (
                    u"\nWebdriver instance must have crushed: {msg}".format(
                        msg=e.msg
                    )
                )
            finally:
                longrepr = getattr(report, 'longrepr', None)
                if hasattr(longrepr, 'addsection'):
                    longrepr.sections.insert(
                        0, (u"Captured stdout %s" % when, fail_info, u"-")
                    )

        if item.config.getoption("--duration-time"):
            duration = call.stop - call.start
            if duration > 120:
                report.sections.append((
                    u"Captured stdout %s" % when,
                    (u"\n\n!!!!! The very slow test. "
                     u"Duration time is %s !!!!!\n\n")
                    % datetime.datetime.fromtimestamp(duration).strftime(
                        u"%M min %S sec"
                    )
                ))


def pytest_configure(config):
    os.environ['PYTHONWARNINGS'] = (
        u'ignore:An HTTPS request has been made, '
        u'ignore:A true SSLContext object is not available, '
        u'ignore:Unverified HTTPS request is being made'
    )
    # TODO add grid url and use config
    grid_host = config.getoption("--grid", '')
    use_grid = 'http+' if grid_host else ''
    if config.getoption("--chrome"):
        os.environ['SE_DRIVER'] = '{}chrome://{}'.format(use_grid, grid_host)
    elif config.getoption("--firefox"):
        os.environ['SE_DRIVER'] = '{}firefox://{}'.format(use_grid, grid_host)
    elif config.getoption("--opera"):
        os.environ['SE_DRIVER'] = '{}opera://{}'.format(use_grid, grid_host)
    elif config.getoption("--ie"):
        os.environ['SE_DRIVER'] = '{}ie://{}'.format(use_grid, grid_host)
    elif config.getoption("--edge"):
        os.environ['SE_DRIVER'] = '{}edge://{}'.format(use_grid, grid_host)
    else:
        os.environ['SE_DRIVER'] = '{}chrome://{}'.format(use_grid, grid_host)
    if config.getoption("--highlight"):
        os.environ['HIGHLIGHT'] = 'Enabled'
    if config.getoption("--capturelog"):
        config.pluginmanager.register(Logger(), "logger")
    if config.getoption("--check-console"):
        os.environ['CHECK_CONSOLE'] = 'True'
    config.lastfailed_file = "lastfailed"
