# -*- coding: utf-8 -*-


class PromiumException(Exception):
    pass


class ElementLocationException(PromiumException):
    pass


class LocatorException(PromiumException):
    pass


class BrowserConsoleException(PromiumException):
    pass
