# -*- coding: utf-8 -*-

import os
import datetime

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from promium.waits import wait_for_page_loaded


def scroll_down_page(driver):
    """Scrolls down page"""
    driver.execute_script('jQuery("img.img-ondemand").trigger("appear");')
    wait_for_page_loaded(driver)
    driver.execute_script(
        """
        var f = function(old_height) {
            var height = $$(document).height();
            if (height == old_height) return;
            $$('html, body').animate({scrollTop:height}, 'slow', null,
            setTimeout(function() {f(height)}, 1000)
            );
        }
        f();
        """
    )


# TODO need implemented
def switch_to_window(driver, window_handle):
    """Switches to window"""
    driver.switch_to_window(window_handle)


# TODO need implemented save to storage
def get_screenshot(driver):
    """Gets screenshot"""
    now = datetime.datetime.now().strftime('%d_%H_%M_%S_%f')
    path = os.path.abspath(os.curdir)
    if ':' in path:
        screenshots_folder = path + '\screenshots\\'
    else:
        screenshots_folder = path + '/screenshots/'
    screenshot_name = "{name}_{time}.png".format(name='screenshot', time=now)
    url = screenshots_folder + screenshot_name
    driver.save_screenshot(url)
    return url


# TODO move to base
def control_plus_key(driver, key):
    """Imitations press CONTROL key + any key"""
    (
        ActionChains(driver)
        .key_down(Keys.CONTROL)
        .send_keys(key)
        .key_up(Keys.CONTROL)
        .perform()
    )


# TODO move to base
def set_local_storage(driver, key, value):
    """Sets value in browsers local storage"""
    driver.execute_script(
        "localStorage.setItem('%s', '%s')" % (key, value)
    )
