# -*- coding: utf-8 -*-

import logging
import os
import pytest
import requests

from six.moves.urllib.parse import urlsplit, urlunsplit

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions
# from selenium.webdriver.opera.options import Options as OperaOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from promium.assertions import WebDriverSoftAssertion, RequestSoftAssertion
from promium.device_config import CHROME_DESKTOP_1920_1080
# from tests.config import OPERA_BINARY_LOCATION, CHECK_TEST_CASE
from promium.core.exceptions import PromiumException
from promium.core.common import get_screenshot
from promium.logger import request_logging, logger_for_loading_page


log = logging.getLogger(__name__)

ENV_VAR = 'SE_DRIVER'

DRIVERS = {
    'firefox': 'Firefox',
    'chrome': 'Chrome',
    'opera': 'Opera',
    'ie': 'IE',
    'edge': 'Edge'
}

DOWNLOAD_PATH = "/tmp"


def get_chrome_opera_options(options, device):
    options.add_argument("--no-sandbox")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--dns-prefetch-disable")
    options.add_argument("--no-first-run")
    options.add_argument("--verbose")
    options.add_argument("--enable-logging --v=1")
    options.add_argument("--test-type")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-notifications")
    options.add_argument("--window-size={},{}".format(
        device.width,
        device.height,
    ))
    if device.user_agent:
        options.add_argument("--user-agent={}".format(
            device.user_agent,
        ))
    prefs = {
        "download.default_directory": DOWNLOAD_PATH,
        "download.directory_upgrade": True,
        'prompt_for_download': False
    }
    options.add_experimental_option("prefs", prefs)
    return options


def get_chrome_options(device):
    options = ChromeOptions()
    options = get_chrome_opera_options(options, device)
    return options


def get_opera_options(device):
    options = ChromeOptions()
    # TODO need fix
    # options.binary_location = OPERA_BINARY_LOCATION
    options = get_chrome_opera_options(options, device)
    return options


def get_firefox_profile(device):
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.startup.homepage", "about:blank")
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.dir", DOWNLOAD_PATH)
    profile.set_preference(
        "browser.helperApps.neverAsk.saveToDisk",
        "application/zip"
    )
    profile.set_preference("startup.homepage_welcome_url", "about:blank")
    profile.set_preference(
        "startup.homepage_welcome_url.additional", "about:blank"
    )
    profile.set_preference("pdfjs.disabled", True)
    if device.user_agent:
        profile.set_preference("general.useragent.override", device.user_agent)
    profile.update_preferences()
    return profile


def get_firefox_options(device):
    firefox_options = FirefoxOptions()
    firefox_options.add_argument("-no-remote")
    firefox_options.add_argument("-width {}".format(device.width))
    firefox_options.add_argument("-height {}".format(device.height))
    return firefox_options


def create_driver(device, env_var=ENV_VAR):
    """
    Examples:

        - 'chrome://'
        - 'firefox://'
        - 'opera://'
        - 'ie://'
        - 'edge://'
        - 'http+chrome://host:port/wd/hub'

    """
    browser_profile = None

    driver_dsn = os.environ.get(env_var)
    if not driver_dsn:
        raise RuntimeError(
            u'Selenium WebDriver is not set in the {} environment variable'
            .format(env_var)
        )

    try:
        scheme, netloc, url, _, _ = urlsplit(driver_dsn)
    except ValueError:
        # TODO need implemented
        raise ValueError(u'Invalid url: {}'.format(driver_dsn))

    if scheme in DRIVERS:
        if scheme == "chrome":
            return webdriver.Chrome(chrome_options=get_chrome_options(device))
        elif scheme == "firefox":
            return webdriver.Firefox(
                firefox_profile=get_firefox_profile(device),
                firefox_options=get_firefox_options(device)
            )
        elif scheme == "opera":
            return webdriver.Opera(options=get_opera_options(device))
        elif scheme == "ie":
            return webdriver.Ie()
        elif scheme == "edge":
            return webdriver.Edge()
        return getattr(webdriver, DRIVERS[scheme])()
    elif scheme.startswith('http+'):
        proto, _, client = scheme.partition('+')
        if not netloc:
            raise ValueError(
                u'Network address is not specified: {}'.format(driver_dsn)
            )
        capabilities = getattr(DesiredCapabilities, client.upper(), None)
        capabilities["loggingPrefs"] = {
            "performance": "ALL", "server": "ALL", "client": "ALL",
            "driver": "ALL", "browser": "ALL"
        }
        if capabilities is None:
            raise ValueError(u'Unknown client specified: {}'.format(client))
        command_executor = urlunsplit(
            (proto, netloc, url, None, None)
        )
        if client == "chrome":
            capabilities.update(get_chrome_options(device).to_capabilities())
        elif client == "firefox":
            capabilities.update(get_firefox_options(device).to_capabilities())
            browser_profile = get_firefox_profile(device)
        elif client == "opera":
            capabilities.update(get_opera_options(device).to_capabilities())
            capabilities['browserName'] = 'opera'
        try:
            driver = webdriver.Remote(
                command_executor=command_executor,
                desired_capabilities=capabilities,
                browser_profile=browser_profile
            )
        except WebDriverException:
            log.warning(u"[SETUP] Second try for remote driver connection.")
            driver = webdriver.Remote(
                command_executor=command_executor,
                desired_capabilities=capabilities,
                browser_profile=browser_profile
            )
        return driver

    raise ValueError(u'Unknown driver specified: {}'.format(driver_dsn))


class TestCase(object):
    test_case_url = None
    assertion_errors = None
    path_to_test = None

    def get_path_to_test(self, method):
        return u"{path}.py -k {test_name}".format(
            path=u'/'.join(str(self.__module__).split(u'.')[1:]),
            test_name=method.__name__
        )

    def get_failed_test_command(self, name):
        if name == 'pytest':
            command = 'py.test'
        elif name == 'vagga':
            command = 'vagga run-tests --'
        else:
            raise PromiumException('Name must be "pytest" or "vagga"')
        return (
            u"{command} {path_to_test} --fail-debug-info --capturelog".format(
                command=command,
                path_to_test=self.path_to_test
            )
        )


class WebDriverTestCase(TestCase, WebDriverSoftAssertion):
    driver = None
    device = CHROME_DESKTOP_1920_1080  # default data
    excluded_browser_console_errors = []

    @logger_for_loading_page
    def get_url(self, url):
        self.driver.get(url)

    def check_console_errors(self):
        if hasattr(self.driver, "console_errors"):
            if self.driver.console_errors:
                browser_console_errors = self.driver.console_errors
                if self.excluded_browser_console_errors:
                    try:
                        return list(map(
                            lambda x: x, list(filter(
                                lambda x: x if not list(filter(
                                    lambda e: (
                                        True if e["msg"] in x and e["comment"]
                                        else False
                                    ),
                                    self.excluded_browser_console_errors
                                )) else None, browser_console_errors
                            ))
                        ))
                    except Exception as e:
                        raise PromiumException(
                            u"Please check your excluded errors list. "
                            u"Original exception is: %s" % e.message
                        )
                return browser_console_errors
        return []

    def setup_method(self, method):
        self.assertion_errors = []
        self.path_to_test = self.get_path_to_test(method)
        pytest.config.get_fail_debug = self.get_fail_debug
        pytest.config.assertion_errors = self.assertion_errors
        pytest.config.check_console_errors = self.check_console_errors
        if hasattr(method, 'device'):
            self.device = method.device.args[0]
        self.driver = create_driver(self.device)
        self.driver.console_errors = []
        if (
            'ie' not in os.environ['SE_DRIVER'] and
            'opera' not in os.environ['SE_DRIVER']
        ):
            self.driver.set_window_size(self.device.width, self.device.height)

    def teardown_method(self, method):
        self.driver.console_errors = []
        if self.driver:
            self.driver.quit()
        # TODO need fix
        # if not self.test_case_url and CHECK_TEST_CASE:
        #     raise PromiumException("Test don't have a test case url.")

    def get_fail_debug(self):
        """Failed test report generator"""
        alerts = 0
        try:
            while self.driver.switch_to.alert:
                alert = self.driver.switch_to.alert
                print(u'Unexpected ALERT: %s\n' % alert.text)
                alerts += 1
                alert.dismiss()
        except:
            if alerts != 0:
                print(u'')
            pass
        url = self.driver.current_url
        screenshot = get_screenshot(self.driver)
        pytest_failed_test_command = self.get_failed_test_command('pytest')
        vagga_failed_test_command = self.get_failed_test_command('vagga')
        return (
            'webdriver',
            url,
            screenshot,
            self.test_case_url,
            pytest_failed_test_command,
            vagga_failed_test_command
        )


class RequestTestCase(TestCase, RequestSoftAssertion):
    session = None

    def setup_method(self, method):
        self.path_to_test = self.get_path_to_test(method)
        self.session = requests.session()
        self.session.url = (
            u'Use self.get_response(url) for request tests or '
            u'util methods for api tests!'
        )
        self.assertion_errors = []
        pytest.config.assertion_errors = self.assertion_errors
        pytest.config.get_fail_debug = self.get_fail_debug

    def teardown_method(self, method):
        if self.session:
            self.session.close()
        # TODO need fix
        # if not self.test_case_url and CHECK_TEST_CASE:
        #     raise PromiumException("Test don't have a test case url.")

    def get_fail_debug(self):
        """Failed test report generator"""
        if not hasattr(self.session, 'status_code'):
            self.session.status_code = None
        pytest_failed_test_command = self.get_failed_test_command('pytest')
        vagga_failed_test_command = self.get_failed_test_command('vagga')
        return (
            u'request',
            self.session.url,
            self.session.status_code,
            self.test_case_url,
            pytest_failed_test_command,
            vagga_failed_test_command
        )

    def get_response(self, url, timeout=10, **kwargs):
        self.session.url = url
        self.session.status_code = None
        response = self.session.get(
            url,
            timeout=timeout,
            verify=False,
            hooks=dict(response=request_logging),
            **kwargs
        )
        self.session.status_code = response.status_code
        return response
