import time
import unittest

from seleniumwire import webdriver
from selenium.webdriver.common.by import By

from tests.utils.bistro import BistroService
from tests.utils import test_config, DASHBOARD_URL, LOGIN_URL


class LoginTest(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome('./chromedriver')
        self.driver.get(LOGIN_URL)

    def find_element(self, value, by=By.XPATH, wait_time=5):
        self.driver.implicitly_wait(wait_time)
        return self.driver.find_element(
            by=by, value=value
        )

    def test_login_invalid_credentials(self):
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

    def test_login_valid_credentials(self):
        username_field = self.find_element(value="//input[@name='email']")
        password_field = self.find_element(
            value="//input[@name='password']"
        )
        sign_in_field = self.find_element(
            by=By.ID, value='kt_login_signin_submit'
        )

        bistro_data = test_config.get('bistro')
        username_field.send_keys(bistro_data['email'])
        time.sleep(1)
        password_field.send_keys(bistro_data['password'])
        time.sleep(1)
        sign_in_field.click()
        time.sleep(3)
        self.driver.get(DASHBOARD_URL)

        headers = None
        for req in self.driver.requests:
            if req.url == DASHBOARD_URL:
                headers = req.headers

        bistro_service = BistroService.initialize(headers=headers)

        response = bistro_service.add_charger(
            name='UMKA PUNJAC',
            model='FIAT',
            vendor='KINEZ',
            address='PODRINJSKA 4',
        )

        assert response['name'] == 'UMKA PUNJAC'

    def tearDown(self):
        self.driver.close()
