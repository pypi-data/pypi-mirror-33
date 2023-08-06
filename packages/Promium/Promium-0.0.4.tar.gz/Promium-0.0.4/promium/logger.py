# -*- coding: utf-8 -*-

import logging
import os
import py
import pytest
import re
from functools import wraps

from selenium.common.exceptions import TimeoutException


log = logging.getLogger(__name__)


MAX_SYMBOLS = 255
TABS_FORMAT = u" " * 20

MINOR_ERRORS = []
MAJOR_ERRORS = []
SKIPPED_ERRORS = MINOR_ERRORS + MAJOR_ERRORS


def repr_console_errors(console_errors, tabs=TABS_FORMAT):
    return u"\n{tabs_format}".format(tabs_format=tabs).join(
        u">>> [CONSOLE ERROR] %s" % error for error in set(console_errors)
    )


def repr_args(*args, **kwargs):
    return u"{args}{mark}{kwargs}".format(
        args=u", ".join(list(map(lambda x: x, args))) if args else u"",
        kwargs=u", ".join(
            u"%s=%s" % (k, v) for k, v in kwargs.iteritems()
        ) if kwargs else u"",
        mark=u", " if args and kwargs else u""
    )


def is_error_in_skipped_list(e, err):
    if e not in MINOR_ERRORS and e in err:
        log.info(u">>> [SKIPPED ERROR] %s" % err)
    if e in err:
        return True
    return False


def find_console_browser_errors(driver):
    return list(map(
        lambda x: x["message"],
        list(filter(
            lambda x: x["level"] == "SEVERE" and (
                x if not list(filter(
                    lambda e: True if is_error_in_skipped_list(
                        e, x["message"]
                    ) else False,
                    SKIPPED_ERRORS
                )) else None
            ), driver.get_log("browser")
        ))
    ))


def logger_for_element_methods(fn):

    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        try:
            res = fn(self, *args, **kwargs)
        except TimeoutException:
            if os.environ.get('CHECK_CONSOLE'):
                console_errors = find_console_browser_errors(self.driver)
                if console_errors:
                    try:
                        log.warning(
                            u"Browser console js error found:\n"
                            u"{tabs_format}{console_errors}\n"
                            u"{tabs_format}Url: {url}\n"
                            u"{tabs_format}Action: {class_name}"
                            u"({by}={locator})"
                            u".{method}({args})".format(
                                tabs_format=TABS_FORMAT,
                                class_name=self.__class__.__name__,
                                by=self.by,
                                locator=self.locator,
                                method=fn.__name__,
                                args=repr_args(*args, **kwargs),
                                url=self.driver.current_url,
                                console_errors=repr_console_errors(
                                    console_errors
                                )
                            )
                        )
                        if hasattr(self.driver, "console_errors"):
                            self.driver.console_errors.append(
                                u"{console_errors}\n"
                                u"Url: {url}\n"
                                u"Action: {class_name}({by}={locator})"
                                u".{method}({args})\n"
                                u"{end_symbol}".format(
                                    class_name=self.__class__.__name__,
                                    by=self.by,
                                    locator=self.locator,
                                    method=fn.__name__,
                                    args=repr_args(*args, **kwargs),
                                    url=self.driver.current_url,
                                    console_errors=repr_console_errors(
                                        console_errors, tabs=u""
                                    ),
                                    end_symbol=u"-" * 10
                                )
                            )
                    except UnicodeDecodeError:
                        raise Exception(
                            u"Locator must be unicode, found cyrillic symbols."
                        )
                raise
        return res
    return wrapper


def add_logger_to_base_element_classes(cls):
    for name, method in cls.__dict__.items():
        log.info(u"%s, %s" % (name, method))
        if (not name.startswith('_') and
                hasattr(method, '__call__') and name != "lookup"):
            setattr(cls, name, logger_for_element_methods(method))
    return cls


def logger_for_loading_page(fn):

    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        res = fn(self, *args, **kwargs)
        if os.environ.get('CHECK_CONSOLE'):
            console_errors = find_console_browser_errors(self.driver)
            if console_errors:
                log.warning(
                    u"Browser console js error found:\n"
                    u"{tabs_format}{console_errors}\n"
                    u"{tabs_format}Url: {url}\n"
                    u"{tabs_format}Action: wait for page loaded ...".format(
                        tabs_format=TABS_FORMAT,
                        url=self.driver.current_url,
                        console_errors=repr_console_errors(console_errors)
                    )
                )
                if hasattr(self.driver, "console_errors"):
                    self.driver.console_errors.append(
                        u"{console_errors}\n"
                        u"Url: {url}\n"
                        u"Action: wait for page loaded ...\n"
                        u"{end_symbol}".format(
                            url=self.driver.current_url,
                            console_errors=repr_console_errors(
                                console_errors, tabs=u""
                            ),
                            end_symbol=u"-" * 10
                        )
                    )
        return res
    return wrapper


class LoggerFilter(logging.Filter):

    def filter(self, record):
        return record.levelno > 10


class Logger(object):

    def pytest_runtest_setup(self, item):
        item.capturelog_handler = LoggerHandler()
        item.capturelog_handler.setFormatter(logging.Formatter(
            u"%(asctime)-12s%(levelname)-8s%(message)s\n", u"%H:%M:%S"
        ))
        root_logger = logging.getLogger()
        item.capturelog_handler.addFilter(LoggerFilter())
        root_logger.addHandler(item.capturelog_handler)
        root_logger.setLevel(logging.NOTSET)

    @pytest.mark.hookwrapper
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()
        if hasattr(item, "capturelog_handler"):
            if call.when == 'teardown':
                root_logger = logging.getLogger()
                root_logger.removeHandler(item.capturelog_handler)
            if not report.passed:
                longrepr = getattr(report, 'longrepr', None)
                if hasattr(longrepr, 'addsection'):
                    captured_log = item.capturelog_handler.stream.getvalue()
                    if captured_log:
                        longrepr.sections.insert(
                            len(longrepr.sections),
                            (u'Captured log', u"\n%s" % captured_log, u"-")
                        )
            if call.when == 'teardown':
                item.capturelog_handler.close()
                del item.capturelog_handler


class LoggerHandler(logging.StreamHandler):

    def __init__(self):
        logging.StreamHandler.__init__(self)
        self.stream = py.io.TextIO()
        self.records = []

    def close(self):
        logging.StreamHandler.close(self)
        self.stream.close()


def request_logging(request, *args, **kwargs):
    log.info(
        u"HEADERS: {headers}\n"
        u"{tabs}METHOD: {method}\n"
        u"{tabs}LINK: {link}\n"
        u"{tabs}BODY: {body}\n"
        u"{tabs}RESPONSE CONTENT: "
        u"{ellipsis} ({length} symbols)\n"
        u"{tabs}RESPONSE HEADERS: {response_headers}\n"
        .format(
            headers=request.request.headers,
            method=request.request.method,
            link=request.url,
            body=request.request.body,
            content=re.sub(r'\s+', ' ', request.text)[:MAX_SYMBOLS],
            ellipsis=(
                u" ..." if len(request.text) > MAX_SYMBOLS else u""
            ),
            length=len(request.content),
            tabs=u" " * 12,
            response_headers=request.headers
        )
    )
