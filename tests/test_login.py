import time
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By


class LoginTest(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome('./chromedriver')
        self.driver.get(
            'http://localhost:8000/fe-apps/auth/login'
        )

    def find_element(self, value, by=By.XPATH, wait_time=5):
        self.driver.implicitly_wait(wait_time)
        return self.driver.find_element(
            by=by, value=value
        )

    def test_first(self):
        username_field = self.find_element(value="//input[@name='email']")
        password_field = self.find_element(
            value="//input[@name='password']"
        )
        username_field.send_keys('ccc')
        password_field.send_keys('Demo1')

        invalid_message_element = self.find_element(
            value="//div[@class='fv-help-block']"
        )
        assert invalid_message_element.text == "Email is invalid"

    def tearDown(self):
        self.driver.close()
