import time
import unittest

from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from tests.utils import LOGIN_URL, test_config


class LoginTest(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
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

    def tearDown(self):
        self.driver.close()

    def test_login_with_valid_credentials(self):
        username_field = self.find_element(
            value="//input[@name='email']")
        password_field = self.find_element(
            value="//input[@name='password']")
        sign_in_field = self.find_element(
            value="//*[@id='kt_login_signin_submit']"
        )

        bistro_data = test_config.get('bistro')
        username_field.send_keys(bistro_data['email'])
        time.sleep(1)
        password_field.send_keys(bistro_data['password'])
        time.sleep(1)
        sign_in_field.click()

        header_element = self.find_element(
            by=By.ID, value="kt_header_menu"
        )

    def test_contact_us_on_platform_page_navigation(self):
        contact_us_field = self.find_element(
            value=(
                "//a[@class='text-primary ml-10 "
                "font-weight-bolder font-size-h5']"
            )
        )

        time.sleep(1)
        contact_us_field.click()
        time.sleep(1)

        contact_up_page_is_opened = self.find_element(
            value=(
                "//div[@class='elementor-container "
                "elementor-column-gap-no']"
            )
        )
