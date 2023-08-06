# -*- coding: utf-8 -*-

import json
import re

from json_checker import Checker, CheckerError
from six import text_type, string_types

from promium.core.common import get_screenshot


class BaseSoftAssertion(object):

    # TODO is not cleaned in unit tests need use __init__
    assertion_errors = []

    # TODO need fix default message
    @staticmethod
    def _format_message(msg):
        return u"{}\n".format(msg) if msg else u""

    @staticmethod
    def convert_container(container):
        return json.dumps(
            container, indent=4, sort_keys=True, ensure_ascii=False,
            default=lambda obj: text_type(obj)
        ) if not isinstance(container, string_types) else container

    @staticmethod
    def get_text_with_ignore_whitespace_symbols(text):
        """Return text excluding spaces and whitespace_symbols"""
        text_without_whitespace_symbols = (
            text
            .replace(u'\t', u' ')
            .replace(u'\v', u' ')
            .replace(u'\r', u' ')
            .replace(u'\n', u' ')
            .replace(u'\f', u' ')
            .strip()
        )
        text_list = text_without_whitespace_symbols.split(u' ')
        text_list_without_space = [word for word in text_list if word]
        # TODO what happen?
        needful_text = u' '.join(text_list_without_space)
        return needful_text

    def soft_assert_true(self, expr, msg=None):
        """Check that the expression is true."""
        if not expr:
            error = u"Is not true." if not msg else msg
            self.assertion_errors.append(error)
            return error

    def soft_assert_false(self, expr, msg=None):
        """Check that the expression is false."""
        if expr:
            message = u"Is not false." if not msg else msg
            self.assertion_errors.append(message)
            return message

    def soft_assert_equals(self, current, expected, msg=None):
        """Just like self.soft_assert_true(current == expected)"""
        message = (
            u"{base_msg}"
            u"Current - {current}\n"
            u"Expected - {expected}\n".format(
                base_msg=self._format_message(msg),
                current=text_type(current),
                expected=text_type(expected)
            )
        )
        if type(current) != type(expected):
            message += (
                    u"Current and expected has different data types: "
                    u"current is %s, expected is %s" % (
                        type(current), type(expected)
                    )
            )
        return self.soft_assert_true(current == expected, message)

    def soft_assert_not_equals(self, current, expected, msg=None):
        """Just like self.soft_assert_true(current != expected)"""
        message = (
            u"{base_msg}"
            u"Current - {current}\n"
            u"Expected - {expected}\n".format(
                base_msg=self._format_message(msg),
                current=text_type(current),
                expected=text_type(expected)
            )
        )
        self.soft_assert_false(current == expected, message)

    def soft_assert_in(self, member, container, msg=None):
        """Just like self.soft_assert_true(member IN container)"""
        error = (
            u"{base_msg}"
            u"{member} not found in {container}\n".format(
                base_msg=self._format_message(msg),
                member=member,
                container=self.convert_container(container)
            )
        )
        return self.soft_assert_true(member in container, error)

    def soft_assert_not_in(self, member, container, msg=None):
        """Just like self.soft_assert_true(member NOT IN container)"""
        error = (
            u"{base_msg}"
            u"{member} unexpectedly found in {container}\n".format(
                base_msg=self._format_message(msg),
                member=member,
                container=self.convert_container(container)
            )
        )
        return self.soft_assert_true(member not in container, error)

    def soft_assert_less_equal(self, a, b, msg=None):
        """Just like self.soft_assert_true(a <= b)"""
        error = u"{base_msg}{a} not less than or equal to {b}\n".format(
            base_msg=self._format_message(msg), a=a, b=b
        )
        return self.soft_assert_true(a <= b, error)

    def soft_assert_less(self, a, b, msg=None):
        """Just like self.soft_assert_true(a < b)"""
        error = u"{base_msg}{a} not less than {b}\n".format(
            base_msg=self._format_message(msg), a=a, b=b
        )
        return self.soft_assert_true(a < b, error)

    def soft_assert_greater_equal(self, a, b, msg=None):
        """Just like self.soft_assert_true(a >= b)"""
        error = u"{base_msg}{a} not greater than or equal to {b}\n".format(
            base_msg=self._format_message(msg), a=a, b=b
        )
        return self.soft_assert_true(a >= b, error)

    def soft_assert_greater(self, a, b, msg=None):
        """Just like self.soft_assert_true(a > b)"""
        error = u"{base_msg}{a} not greater than {b}\n".format(
            base_msg=self._format_message(msg), a=a, b=b
        )
        return self.soft_assert_true(a > b, error)

    def soft_assert_regexp_matches(self, text, expected_regexp, msg=None):
        """Fail the test unless the text matches the regular expression."""
        pattern = re.compile(expected_regexp)
        result = pattern.search(text)

        if not result:
            error = (
                u"{base_msg}"
                u"Regexp didn't match."
                u"Pattern {pattern} not found in {text}\n".format(
                    base_msg=self._format_message(msg),
                    pattern=text_type(pattern.pattern),
                    text=text_type(text)
                )
            )
            self.assertion_errors.append(error)
            return error

    def soft_assert_disable(self, element, msg=None):
        """Check that the obj hasn't attribute."""
        error = u"{base_msg}{default_msg}".format(
            base_msg=self._format_message(msg),
            default_msg=u"%s is not Disable.\n" % element if not msg else u""
        )
        return self.soft_assert_true(element.get_attribute("disabled"), error)

    def soft_assert_is_none(self, obj, msg=None):
        """Same as self.soft_assert_true(obj is None)."""
        error = u"{base_msg}{default_msg}".format(
            base_msg=self._format_message(msg),
            default_msg=u"%s is not None.\n" % obj if not msg else u""
        )
        return self.soft_assert_true(obj is None, error)

    def soft_assert_is_not_none(self, obj, msg=None):
        """Included for symmetry with self.soft_assert_is_none."""
        error = u"{base_msg}{default_msg}".format(
            base_msg=self._format_message(msg),
            default_msg=u"Unexpectedly None.\n" if not msg else u""
        )
        return self.soft_assert_true(obj is not None, error)

    def soft_assert_is_instance(self, obj, cls, msg=None):
        """Same as self.soft_assert_true(isinstance(obj, cls))"""
        error = u"{base_msg}{default_msg}".format(
            base_msg=self._format_message(msg),
            default_msg=u"%s is not an instance of %s.\n" % (obj, cls) if
            not msg else u""
        )
        return self.soft_assert_true(isinstance(obj, cls), error)

    def soft_assert_equals_text_with_ignore_spaces_and_register(
        self,
        current_text,
        expected_text,
        msg=u'Invalid checked text.'
    ):
        """Checking of text excluding spaces and register"""
        current = self.get_text_with_ignore_whitespace_symbols(current_text)
        expected = self.get_text_with_ignore_whitespace_symbols(expected_text)
        error_pattern = (
            u"%s\nCurrent text without formating: %s"
            u"\nExpected text without formating: %s"
        )
        if not current:
            msg = u"Warning: current text is None!"
        self.soft_assert_equals(
            current.lower(),
            expected.lower(),
            error_pattern % (msg, current_text, expected_text)
        )

    def soft_assert_schemas(self, current, expected, msg=''):
        """
        Example:
            {'test1': int} == {'test1: 1}

        :param dict current: current response
        :param dict expected: expected dict(key: type)
        :param str msg:
        :return error
        """
        try:
            Checker(expected, soft=True).validate(current)
        except CheckerError as e:
            error = u'{}\n{}'.format(msg, e)
            self.assertion_errors.append(error)
            return error

    def assert_keys_and_instances(
        self,
        actual_dict,
        expected_dict,
        can_be_null=None,
        msg=None
    ):
        """
        :param dict actual_dict:
        :param dict expected_dict:
        :param list | None can_be_null: must be if default value None
        :param basestring msg:
        """
        assert actual_dict, u'Actual dict is empty, check your data'

        self.soft_assert_equals(
            sorted(actual_dict.keys()),
            sorted(expected_dict.keys()),
            u'Wrong keys list.'
        )
        for actual_key, actual_value in actual_dict.items():
            self.soft_assert_in(
                member=actual_key,
                container=expected_dict,
                msg=u'Not expected key "{member}".'.format(member=actual_key)
            )
            if actual_key in expected_dict:
                expected_value = (
                    type(None) if
                    actual_value is None and
                    actual_key in (can_be_null or []) else
                    expected_dict[actual_key]
                )
                self.soft_assert_true(
                    expr=isinstance(actual_value, expected_value),
                    msg=(
                        u'Wrong object instance class.\n'
                        u'Key "{key}" value is "{current_type}", '
                        u'expected "{expected_type}". {msg}'.format(
                            key=actual_key,
                            current_type=type(actual_value),
                            expected_type=expected_value,
                            msg=u'(%s)' % msg if msg else u''
                        )
                    )
                )


class RequestSoftAssertion(BaseSoftAssertion):

    @property
    def url(self):
        return self.session.url

    def base_msg(self, msg=None):
        return u"{url}{exception}".format(
            url=u"\n%s" % self.url if self.url else u"",
            exception=(u"\n%s" % msg) if msg else u""
        )


class WebDriverSoftAssertion(BaseSoftAssertion):

    @property
    def driver(self):
        return self.driver

    @property
    def url(self):
        return self.driver.current_url

    @property
    def assertion_screenshot(self):
        return get_screenshot(self.driver)

    def base_msg(self, msg=None):
        return u"\n{url}\nScreenshot - {screenshot}{exception}".format(
            url=self.url,
            screenshot=self.assertion_screenshot,
            exception=(u"\n%s" % msg) if msg else u""
        )

    def soft_assert_page_title(self, expected_title, msg=u"Wrong page title."):
        self.soft_assert_equals(self.driver.title, expected_title, msg)

    def soft_assert_current_url(self, expected_url, msg=u"Wrong current url."):
        self.soft_assert_equals(self.url, expected_url, msg)

    def soft_assert_current_url_contains(self, url_mask, msg=None):
        self.soft_assert_in(url_mask, self.url, msg)

    def soft_assert_element_is_present(self, element, msg=None):
        if not msg:
            msg = (
                u"Element %s=%s is not present on page at current time.\n" % (
                    element.by, element.locator
                )
            )
        self.soft_assert_true(element.is_present(), msg)

    def soft_assert_element_is_not_present(self, element, msg=None):
        if not msg:
            msg = u"Element %s=%s is found on page.\n" % (
                element.by, element.locator
            )
        self.soft_assert_false(element.is_present(), msg)

    def soft_assert_element_is_displayed(self, element, msg=None):
        if not msg:
            msg = u"Element %s=%s is not visible to a user.\n" % (
                element.by, element.locator
            )
        self.soft_assert_true(element.is_displayed(), msg)

    def soft_assert_element_is_not_displayed(self, element, msg=None):
        if not msg:
            msg = u"Element %s=%s is visible to a user.\n" % (
                element.by, element.locator
            )
        self.soft_assert_false(element.is_displayed(), msg)
