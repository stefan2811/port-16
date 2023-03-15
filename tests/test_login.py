import time
import unittest
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

class LoginTest(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.get(
            'https://staging.benjoenergy.com/fe-apps/auth/login'
        )

    def find_element(self, value, by=By.XPATH, wait_time=5):
        self.driver.implicitly_wait(wait_time)
        return self.driver.find_element(
            by=by, value=value
        )
    
    def test_login_with_incorect_password(self):
        username_field = self.find_element(value="//input[@name='email']")
        password_field = self.find_element(
            value="//input[@name='password']"
        )
        time.sleep(1)
        username_field.send_keys('ccc')
        time.sleep(1)
        password_field.send_keys('Demo1')

        invalid_message_element = self.find_element(
            value="//div[@class='fv-help-block']"
        )
        time.sleep(1)
        assert invalid_message_element.text == "Email is invalid"

    def tearDown(self):
        self.driver.close()

    def test_login_with_valid_credentials(self):        
        username_field = self.find_element(value="//input[@name='email']")
        password_field = self.find_element( value="//input[@name='password']")
        sign_in_field = self.find_element(value = "//*[@id='kt_login_signin_submit']")
       
        time.sleep(1)
        username_field.send_keys('demo.user@benjoenergy.com')
        time.sleep(1)
        password_field.send_keys('P326RZMeFcXFurW.')
        time.sleep(1)
        sign_in_field.click()

        # element = WebDriverWait(self.driver, 10).until(
        #     EC.presence_of_element_located(By.ID, "kt_header_menu")
        # )
        header_element = self.find_element(
            by=By.ID, value="kt_header_menu"
        )
    
    def test_contact_us_on_platform_page_navigation(self):
         contact_us_field = self.find_element(value="//a[@class='text-primary ml-10 font-weight-bolder font-size-h5']")

         time.sleep(1)
         contact_us_field.click()
         time.sleep(1)

         contact_up_page_is_opened = self.find_element(value="//div[@class='elementor-container elementor-column-gap-no']")