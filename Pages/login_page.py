
from selenium.webdriver.common.by import By
from Pages.base_page import BasePage


class LoginPage(BasePage):

    # Locators
    USERNAME_INPUT = (By.NAME, "username")
    PASSWORD_INPUT = (By.NAME, "password")

    LOGIN_BUTTON = (By.CSS_SELECTOR, "input[value='Log In']")

    ERROR_MESSAGE = (By.CSS_SELECTOR, "#rightPanel p.error")

    WELCOME_TITLE = (By.CSS_SELECTOR, "#rightPanel h1")

    LOGOUT_LINK = (By.LINK_TEXT, "Log Out")

    def enter_username(self, username):
        self.type(self.USERNAME_INPUT, username)

    def enter_password(self, password):
        self.type(self.PASSWORD_INPUT, password)

    def confirm_login(self, username, password):
        self.enter_username(username)
        self.enter_password(password)
        self.click(self.LOGIN_BUTTON)

    def get_login_error(self):
        return self.get_text(self.ERROR_MESSAGE)

    def is_successful_login(self):
        title = self.get_text(self.WELCOME_TITLE)
        return "Accounts Overview" in title

    def logout(self):
        self.click(self.LOGOUT_LINK)
