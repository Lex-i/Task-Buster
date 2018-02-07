# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from django.urls import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils.translation import activate


class BasePageElement(object):
    """Base page class that is initialized on every page object class."""

    def __set__(self, obj, value):
        """Sets the text to the value supplied"""
        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element_by_name(self.locator))
        driver.find_element_by_name(self.locator).clear()
        driver.find_element_by_name(self.locator).send_keys(value)

    def __get__(self, obj, owner):
        """Gets the text of the specified object"""
        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element_by_name(self.locator))
        element = driver.find_element_by_name(self.locator)
        return element.get_attribute("value")


class TestGoogleLogin(StaticLiveServerTestCase):

    fixtures = ['allauth_fixture']

    # Initializes a browser in setUp.
    # WebDriverWait is used to make the browser wait
    # a certain amount of time before rising an exception
    # when an element is not found
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.maximize_window()
        self.browser.implicitly_wait(1)
        self.browser.wait = WebDriverWait(self.browser, 20)
        activate('en')

    def tearDown(self):
        self.browser.quit()

    def get_element_by_id(self, element_id):
        return self.browser.wait.until(EC.presence_of_element_located(
            (By.ID, element_id)))

    def get_element_by_xpath(self, xpath):
        return self.browser.wait.until(EC.presence_of_element_located(
            (By.XPATH, xpath)))

    def get_password_element_by_xpath(self, xpath):
        self.browser.wait = WebDriverWait(self.browser, 100)
        self.browser.wait.until(EC.presence_of_element_located(
            (By.XPATH, xpath)))
        return self.browser.wait.until(EC.visibility_of_element_located(
            (By.XPATH, xpath)))
        # self.browser.find_element((By.XPATH, xpath))

    def get_button_by_id(self, element_id):
        return self.browser.wait.until(EC.element_to_be_clickable(
            (By.ID, element_id)))

    def get_full_url(self, namespace):
        return self.live_server_url + reverse(namespace)

    """
    It goes to the home page and:
    checks that the login button is present
    checks that the logout button is not present
    checks that the login button points to the correct url (/accounts/google/login)
    checks that after clicking on the login button, the user gets logged in and it sees the logout button instead.
    a click on the logout button should make the user see the login button again.
    """

    def user_login(self):
        import json
        with open("taskbuster/fixtures/google_user.json") as f:
            credentials = json.loads(f.read())
        self.get_element_by_id("identifierId").send_keys(credentials["email"])
        self.get_button_by_id("identifierNext").click()
        self.get_password_element_by_xpath(
            "//*[@id='password']//input[1]").send_keys(credentials["Passwd"])
        # "//*[@id='password']"
        # for btn in ["passwordNext", "signIn", "submit_approve_access", "ДАЛЕЕ"]:
        self.get_button_by_id("passwordNext").click()
        return

    def test_google_login(self):
        self.browser.get(self.get_full_url("home"))
        google_login = self.get_element_by_id("google_login")
        with self.assertRaises(TimeoutException):
            self.get_element_by_id("logout")
        self.assertEqual(
            google_login.get_attribute("href"),
            self.live_server_url + "/accounts/google/login")
        google_login.click()
        self.user_login()
        # with self.assertRaises(TimeoutException):
        #    self.get_element_by_id("google_login")
        google_logout = self.get_element_by_id("logout")
        google_logout.click()
        google_logout = self.get_element_by_xpath("/html/body/form/button[@type='submit']")
        google_logout.click()
        google_login = self.get_element_by_id("google_login")
