import time
import unittest

from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from tests.utils.bistro import BistroService
from tests.utils import test_config, DASHBOARD_URL, LOGIN_URL


class ChargersTest(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.get(LOGIN_URL)

    def tearDown(self):
        self.driver.close()

    def find_element(self, value, by=By.XPATH, wait_time=5):
        self.driver.implicitly_wait(wait_time)
        return self.driver.find_element(
            by=by, value=value
        )

    def login_with_demo_credentials(self):
        username_field = self.find_element(
            value="//input[@name='email']"
        )
        password_field = self.find_element(
            value="//input[@name='password']"
        )
        sign_in_field = self.find_element(
            value ="//*[@id='kt_login_signin_submit']"
        )
        bistro_data = test_config.get('bistro')
        username_field.send_keys(bistro_data['email'])
        time.sleep(1)
        password_field.send_keys(bistro_data['password'])
        time.sleep(1)
        sign_in_field.click()
        time.sleep(3)

    def test_check_chargers_link(self):
        self.login_with_demo_credentials()
        time.sleep(5)
        chargers_field = self.find_element(
            value=(
                "//*[@id='kt_aside_menu']"
                "//span[@translate='MENU.CHARGERS']"
            )
        )
        chargers_field.click()
        page_header = self.find_element(
            value="//h3[@class='card-label']"
        )
        assert page_header.text == "Chargers"

    def test_create_new_charger(self):
        self.login_with_demo_credentials()
        time.sleep(5)

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
