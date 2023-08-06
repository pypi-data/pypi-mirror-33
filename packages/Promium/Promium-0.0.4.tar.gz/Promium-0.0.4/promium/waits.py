# -*- coding: utf-8 -*-

import logging
import requests
import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    UnexpectedAlertPresentException,
    WebDriverException,
    TimeoutException
)

from promium.core.exceptions import PromiumException


log = logging.getLogger(__name__)

JQUERY_LOAD_TIME = 20
AJAX_LOAD_TIME = 20
ANIMATION_LOAD_TIME = 20


def enable_jquery(driver):
    """Enables jquery"""
    driver.execute_script(
        """
        jqueryUrl =
        'https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js';
        if (typeof jQuery == 'undefined') {
            var script = document.createElement('script');
            var head = document.getElementsByTagName('head')[0];
            var done = false;
            script.onload = script.onreadystatechange = (function() {
                if (!done && (!this.readyState || this.readyState == 'loaded'
                        || this.readyState == 'complete')) {
                    done = true;
                    script.onload = script.onreadystatechange = null;
                    head.removeChild(script);

                }
            });
            script.src = jqueryUrl;
            head.appendChild(script);
        };
        """
    )


def wait(driver, seconds=10, poll_frequency=.5, ignored_exceptions=None):
    """Waits in seconds"""
    return WebDriverWait(
        driver=driver,
        timeout=seconds,
        poll_frequency=poll_frequency,
        ignored_exceptions=ignored_exceptions or [WebDriverException]
    )


def wait_until(driver, expression, seconds=10, msg=None):
    """Waits until expression execution"""
    try:
        return wait(driver, seconds).until(expression, msg)
    except TimeoutException:
        # TODO validate console errors
        raise


def wait_until_not(driver, expression, seconds=10, msg=None):
    """Waits until not expression execution"""
    try:
        return wait(driver, seconds).until_not(expression, msg)
    except TimeoutException:
        # TODO validate console errors
        raise


def wait_for_ajax(driver):
    """Waits for execution ajax"""
    try:
        jquery_script = 'return typeof jQuery != "undefined"'
        enable_jquery(driver)
        wait_until(
            driver=driver,
            expression=lambda d: d.execute_script(jquery_script),
            seconds=JQUERY_LOAD_TIME,
            msg='jQuery undefined (waiting time: %s sec)' % JQUERY_LOAD_TIME
        )
        ajax_script = 'return jQuery.active == 0;'
        wait_until(
            driver=driver,
            expression=lambda d: d.execute_script(ajax_script),
            seconds=AJAX_LOAD_TIME,
            msg='Ajax timeout (waiting time: %s sec)' % AJAX_LOAD_TIME
        )
    except TimeoutException:
        # TODO validate console errors
        raise


def wait_for_animation(driver):
    """Waits for execution animation"""
    enable_jquery(driver)
    jquery_script = 'return jQuery(":animated").length == 0;'
    return wait_until(
        driver=driver,
        expression=lambda d: d.execute_script(jquery_script),
        seconds=ANIMATION_LOAD_TIME,
        msg='Animation timeout (waiting time: %s sec)' % ANIMATION_LOAD_TIME
    )


def wait_for_page_loaded(driver):
    """Waits for page loaded"""
    try:
        wait_for_ajax(driver)
        wait_for_animation(driver)
    # TODO need fix, don't understand
    except UnexpectedAlertPresentException as e:
        alert_is_present = EC.alert_is_present()
        if alert_is_present(driver):
            driver.switch_to_alert()
            alert = driver.switch_to_alert()
            e.alert_text = alert.text
            if e.alert_text == u"Stop downloading new page?":
                pass
            else:
                alert.dismiss()
                raise e


def wait_for_alert(driver):
    """Wait for alert"""
    return wait_until(
        driver=driver,
        expression=EC.alert_is_present(),
        seconds=10,
        msg=u"Alert is not present."
    )


def wait_for_status_code(url, status_code=200, tries=10):
    """Waits for status code"""
    for _ in range(tries):
        response = requests.get(url, verify=False)
        if response.status_code == status_code:
            return response
        time.sleep(1)
    raise PromiumException('')


def wait_until_new_window_is_opened(driver, original_window):
    """Waits until new window is opened"""
    # TODO need testing
    wait_until(
        driver,
        EC.new_window_is_opened(driver.window_handles),
        msg=u"New window didn't open"
    )
    window_handles = driver.window_handles
    window_handles.remove(original_window)
    return window_handles[0]
