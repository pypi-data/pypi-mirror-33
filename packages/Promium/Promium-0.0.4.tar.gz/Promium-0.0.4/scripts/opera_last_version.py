import requests
from bs4 import BeautifulSoup


def get_opera_last_version():
    response = requests.get(
        url='https://ftp.opera.com/pub/opera/desktop/',
        verify=False,
        timeout=10
    )
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.findAll('a')
    versions = [
        link.get('href').replace('/', '')
        for link in links
        if link.get('href') not in ['../', 'desktop/']
    ]
    last_version = versions[-1]
    return last_version


if __name__ == "__main__":
    print(get_opera_last_version())
