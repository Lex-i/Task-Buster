# -*- coding: utf-8 -*-
from selenium import webdriver
from django.urls import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils.translation import activate
from datetime import date
from django.utils import formats


class HomeNewVisitorTest(StaticLiveServerTestCase):

    # It opens the browser and it waits for 3 seconds if needs to (if the page is not loaded)
    def setUp(self):
        activate('en')
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    # runs after each test to close the browser
    def tearDown(self):
        self.browser.quit()

    def get_full_url(self, namespace):
        return self.live_server_url + reverse(namespace)
        # +self.live_server_url gives you the local host url
        # +reverse gives you the relative url of a given namespace, here /
        # +The resulting function gives you the absolute url of that namespace (the sum of the previous two)

    # + The next method tests that the home page title contains the word TaskBuster
    def test_home_title(self):
        self.browser.get(self.get_full_url("home"))
        self.assertIn("TaskBuster", self.browser.title)

    # + The next method tests that the h1 text has the desired color
    def test_h1_css(self):
        self.browser.get(self.get_full_url("home"))
        h1 = self.browser.find_element_by_tag_name("h1")
        self.assertEqual(h1.value_of_css_property("color"),
                         "rgb(32, 3, 76)")
    # + The method checks that when going to the corresponding url we don’t see the Not Found 404 page
    def test_home_files(self):
        self.browser.get(self.live_server_url + "/robots.txt")
        self.assertNotIn("Not Found", self.browser.title)
        self.browser.get(self.live_server_url + "/humans.txt")
        self.assertNotIn("Not Found", self.browser.title)

    def test_internationalization(self):
        for lang, h1_text in [('en', 'Welcome to TaskBuster!'),
                              ('ca', 'Benvingut a TaskBuster!'),
                              ('ru', 'Добро пожаловать в TaskBuster!')]:
            activate(lang)
            self.browser.get(self.get_full_url("home"))
            h1 = self.browser.find_element_by_tag_name("h1")
            self.assertEqual(h1.text, h1_text)

    # In the Home Page, we will show today’s date and time using both local and non-local formats
    def test_localization(self):
        today = date.today()
        for lang in ['en', 'ca']:
            activate(lang)
            self.browser.get(self.get_full_url("home"))
            local_date = self.browser.find_element_by_id("local-date")
            non_local_date = self.browser.find_element_by_id("non-local-date")
            self.assertEqual(formats.date_format(today, use_l10n=True),
                             local_date.text)
            self.assertEqual(today.strftime('%Y-%m-%d'), non_local_date.text)

    # display the current time here in Moscow (using the default time zone), the UTC time, and the time in New York
    def test_time_zone(self):
        self.browser.get(self.get_full_url("home"))
        tz = self.browser.find_element_by_id("time-tz").text
        utc = self.browser.find_element_by_id("time-utc").text
        ny = self.browser.find_element_by_id("time-ny").text
        self.assertNotEqual(tz, utc)
        self.assertNotIn(ny, [tz, utc])
