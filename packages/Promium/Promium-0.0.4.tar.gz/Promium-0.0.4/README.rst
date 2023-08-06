========================
Promium
========================

.. image:: https://gitlab.uaprom/uaprom/promium/badges/master/pipeline.svg
    :target: https://gitlab.uaprom/uaprom/promium/commits/master

.. image:: https://gitlab.uaprom/uaprom/promium/badges/master/coverage.svg
    :target: https://gitlab.uaprom/uaprom/promium/commits/master

.. image:: https://img.shields.io/badge/python-2.7%2C%203.5%2C%203.6-blue.svg
    :target: https://pypi.org/project/Promium/

.. image:: https://badge.fury.io/py/Promium.svg
    :target: https://badge.fury.io/py/Promium


Simple selenium wrapper from implemented UI tests

Watch `documentation <http://doc.promium.gitlab.uaprom/index.html>`_

Quick Start
========================

Install
-------

Promium
~~~~~~~

.. code-block:: bash

   pip install promium


Selenium
~~~~~~~~

.. code-block:: bash

   pip install selenium


Driver
~~~~~~~

.. code-block:: bash

   # get actual chrome driver version
   CHROME_DRIVER_VERSION=$(wget http://chromedriver.storage.googleapis.com/LATEST_RELEASE -q -O -)

   # download chrome driver
   wget --no-verbose -O /tmp/chromedriver_linux64.zip https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip

   # unpack
   unzip /tmp/chromedriver_linux64.zip -d /opt/selenium

   # add link from chrome driver
   ln -fs /opt/selenium/chromedriver /usr/bin/chromedriver


Examples
--------

Page Objects
~~~~~~~~~~~~

.. code-block:: python

   from selenium.webdriver.common.by import By

   from promium import Page, Block, Element, InputField, Link


   class ResultBlock(Block):

       title = Link(By.CSS_SELECTOR, 'h3')
       link = Element(By.CSS_SELECTOR, '.f')
       description = Element(By.CSS_SELECTOR, '.st')
       tags = Element.as_list(By.CSS_SELECTOR, '.osl .fl')


   class GoogleResultPage(Page):

       results_blocks = ResultBlock.as_list(By.CSS_SELECTOR, '#rso .srg div.g')


   class GoogleMainPage(Page):

       url = 'https://google.com'
       logo = Element(By.CSS_SELECTOR, '#hplogo')
       search_input = InputField(By.CSS_SELECTOR, '[name="q"]')

       def search(self, text):
           self.search_input.send_keys(text)
           self.search_input.submit()
           return GoogleResultPage(self.driver)



Simple test from google page
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from promium.test_case import WebDriverTestCase

   from tests.pages.google_page import GoogleMainPage


   class TestMainGooglePage(WebDriverTestCase):

       def test_search(self):
           main_page = GoogleMainPage(self.driver)
           main_page.open()
           self.soft_assert_element_is_displayed(main_page.logo)
           result_page = main_page.search('Selenium')
           result_block = result_page.results_blocks.first_item
           self.soft_assert_in('Selenium', result_block.title.text)


Run test
~~~~~~~~

.. code-block:: bash

   # all tests
   pytest tests/

   # all tests in suite
   pytest tests/test_google.py

   # only one test
   pytest tests/test_google.py -k test_search
