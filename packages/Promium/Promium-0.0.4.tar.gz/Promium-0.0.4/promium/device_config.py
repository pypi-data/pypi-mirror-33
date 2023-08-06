# -*- coding: utf-8 -*-

from collections import namedtuple


USER_AGENT_ANDROID = (
    u"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
    u"AppleWebKit/537.36 (KHTML, like Gecko) "
    u"Chrome/62.0.3202.62 Mobile Safari/537.36"
)

USER_AGENT_IOS = (
    u"Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) "
    u"AppleWebKit/601.1.46 (KHTML, like Gecko) "
    u"Version/9.0 Mobile/13B143 Safari/601.1"
)

Device = namedtuple('Device', 'width height user_agent')

CHROME_DESKTOP_1920_1080 = Device(1920, 1080, '')
CHROME_DESKTOP_1024_768 = Device(1024, 768, '')

ANDROID_360_640 = Device(360, 640, USER_AGENT_ANDROID)
ANDROID_1280_800 = Device(1280, 800, USER_AGENT_ANDROID)
ANDROID_1080_1920 = Device(1080, 1920, USER_AGENT_ANDROID)
IOS_750_1334 = Device(750, 1334, USER_AGENT_IOS)
IOS_1080_1920 = Device(1080, 1920, USER_AGENT_IOS)
