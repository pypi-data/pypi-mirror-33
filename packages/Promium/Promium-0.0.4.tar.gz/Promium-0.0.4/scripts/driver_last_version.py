import sys
import requests


GITHUB_URL = 'https://api.github.com/repos'
GECKODRIVER = {
    'url': '{}/mozilla/geckodriver/releases/latest'.format(GITHUB_URL),
    'key': 'tag_name'
}
OPERADRIVER = {
    'url': '{}/operasoftware/operachromiumdriver/releases/latest'.format(
        GITHUB_URL
    ),
    'key': 'name'
}


def get_driver_last_version(driver_name):
    if driver_name == 'geckodriver':
        driver = GECKODRIVER
    elif driver_name == 'operadriver':
        driver = OPERADRIVER
    else:
        raise Exception('Driver name must be "geckodriver" or "operadriver"')
    response = requests.get(url=driver['url'], verify=False, timeout=10).json()
    version = response[driver['key']]
    return version


if __name__ == "__main__":
    print(get_driver_last_version(sys.argv[1]))
