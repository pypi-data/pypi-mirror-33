from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.common.by import By
import os
from mark_utils.color import Color as c
from time import sleep
import pkg_resources
import datetime

pkg_name = 'mark_utils'
geckodriver_file = 'web_driver/geckodriver'
CLASS, ID, XPATH, TAG, LINK = 'CLASS', 'ID', 'XPATH', 'TAG', 'LINK'

proxyIP = '127.0.0.1'
proxyPort = 9150


class Scraper():
    def __init__(self, delay=10, log=False, headless=False, tor=False):
        self.startedAt = datetime.datetime.now()
        self.delay = delay
        self.headless = headless
        self.tor = tor
        self.log = log
        self.log_file = 'geckodriver.log'
        # Binary path
        path = pkg_resources.resource_filename(pkg_name, geckodriver_file)
        profile = webdriver.FirefoxProfile()

        if tor:
            print(c.blue('Warning - Be sure you have Tor browser opened in backgroud!'))
            print('Tor Proxy', c.green('Enabled'))
            profile.set_preference('network.proxy.type', 1)
            profile.set_preference('network.proxy.socks', proxyIP)
            profile.set_preference('network.proxy.socks_port', proxyPort)

        profile.set_preference("browser.cache.disk.enable", False)
        profile.set_preference("browser.cache.memory.enable", False)
        profile.set_preference("browser.cache.offline.enable", False)
        profile.set_preference("network.http.use-cache", False)
        options = Options()
        if headless:
            options.add_argument('-headless')

        self.webBrowser = webdriver.Firefox(
            firefox_profile=profile, executable_path=path, firefox_options=options)

        self.wait = WebDriverWait(self.webBrowser, timeout=delay)

    def openUrl(self, url):
        self.webBrowser.get(url)
        while self.wait_load():
            sleep(0.3)
        if self.log:
            print('Page: {}'.format(c.orange(url)))

    def current_url(self):
        return self.webBrowser.current_url

    def wait_load(self):
        result = self.webBrowser.execute_script('return document.readyState;')
        return True if result != 'complete' else False

    def make_target(type_, name):
        return dict(type=name)

    def get_element_BY(self, target):
        if isinstance(target, dict):
            return self.get_single_element_BY(target)
        if isinstance(target, list):
            return self.get_multiple_element_BY(target)

    def get_single_element_BY(self, target):
        element = None
        assert isinstance(
            target, dict), 'Target must be a dictionary with key:value [type:target]'
        try:
            c_target = target.copy()
            _type, _target = c_target.popitem()

            if _type is CLASS:
                element = self.__get_element_by_class(_target)
            elif _type is ID:
                element = self.__get_element_by_id(_target)
            elif _type is XPATH:
                element = self.__get_element_by_xpath(_target)
            elif _type is TAG:
                element = self.__get_element_by_tag(_target)
            else:
                print('Error - Type ( {} ).'.format(_type))

        except Exception as e:
            print('Exception: {}: {} -> {} - is not present in page: {}'.format(e, c.blue(_type), c.red(_target),
                                                                                c.orange(self.webBrowser.current_url)))

        finally:
            if self.log and element is not None:
                print('{} ---> {}'.format(c.blue(_type), c.green(_target)))
            return element

    def get_multiple_element_BY(self, target_list):
        result = []
        for target in target_list:
            result.append(self.get_single_element_BY(target))
        return result

    def __get_element_by_class(self, className):
        element = self.wait.until(
            expected.visibility_of_element_located((By.CLASS_NAME, className)))
        return element

    def __get_element_by_id(self, idName):
        element = self.wait.until(
            expected.presence_of_element_located((By.ID, idName)))
        return element

    def __get_element_by_xpath(self, xPath):
        element = self.wait.until(
            expected.presence_of_element_located((By.XPATH, xPath)))
        return element

    def __get_element_by_tag(self, tagName):
        element = self.wait.until(
            expected.presence_of_element_located((By.TAG_NAME, tagName)))
        return element

    def get_nested_elements_from_root(self, list_target):
        first_target = list_target[0]
        nested_target = list_target[1:]

        element = self.get_single_element_BY(first_target)

        for target in nested_target:
            element = self.find_elements_BY(element, target)

        return element

    def get_nested_elements(self, element, list_target):
        for target in list_target:
            element = self.find_elements_BY(element, target)
        return element

    def find_elements_BY(self, element, target):
        nested_element = None
        assert isinstance(
            target, dict), 'Target must be a dictionary with key:value [type:target]'
        try:
            c_target = target.copy()
            _type, _target = c_target.popitem()

            if _type is CLASS:
                nested_element = self.__find_elements_by_class(
                    element, _target)
            if _type is ID:
                nested_element = self.__find_elements_by_id(element, _target)
            if _type is XPATH:
                nested_element = self.__find_elements_by_xpath(
                    element, _target)
            if _type is TAG:
                nested_element = self.__find_elements_by_tag(element, _target)
            if _type is LINK:
                nested_element = self.__find_elements_by_partial_link_text(
                    element, _target)

        except Exception as e:
            print('Exception: {}: {} -> {} - is not present in page: {}'.format(e, c.blue(_type), c.red(_target),
                                                                                c.orange(self.webBrowser.current_url)))

        finally:
            if self.log and nested_element is not None:
                print('{} ---> {}'.format(c.blue(_type), c.green(_target)))
            return nested_element

    def __find_elements_by_class(self, element, className):
        nested_element = element.find_elements_by_class_name(className)
        return nested_element

    def __find_elements_by_id(self, element, idName):
        nested_element = element.find_elements_by_id(idName)
        return nested_element

    def __find_elements_by_xPath(self, element, xPath):
        nested_element = element.find_elements_by_xpath(xPath)
        return nested_element

    def __find_elements_by_tag(self, element, tagName):
        nested_element = element.find_elements_by_tag_name(tagName)
        return nested_element

    def __find_elements_by_partial_link_text(self, element, link_text=''):
        nested_element = element.find_element_by_partial_link_text(
            link_text).get_attribute('href')
        return nested_element

    def close(self):
        self.webBrowser.close()
        if os.path.isfile(self.log_file):
            sleep(2)
            os.remove(self.log_file)
        if self.log:
            print('WebDriver closed correctly.')

    def info(self):
        split = '#' * 9
        info = "{}\nScraper v 0.1 \n {} WakeUp at: {}\n{}\n Log: {}\n Headless: {}\n TOR:{}\n {}".format(
            split, split, self.startedAt, split, self.log, self.headless, self.tor, split)
        print()
