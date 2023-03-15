import time
import unittest
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By


class ChargersTest(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.get(
            'https://staging.benjoenergy.com/fe-apps/auth/login'
        )

    def tearDown(self):
        self.driver.close()

    def find_element(self, value, by=By.XPATH, wait_time=5):
        self.driver.implicitly_wait(wait_time)
        return self.driver.find_element(
            by=by, value=value
        )
    def login_with_demo_credentials(self):
        username_field = self.find_element(value="//input[@name='email']")
        password_field = self.find_element( value="//input[@name='password']")
        sign_in_field = self.find_element(value = "//*[@id='kt_login_signin_submit']")
        time.sleep(1)
        username_field.send_keys('demo.user@benjoenergy.com')
        time.sleep(1)
        password_field.send_keys('P326RZMeFcXFurW.')
        time.sleep(1)
        sign_in_field.click()

    def test_create_new_chargers(self):
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