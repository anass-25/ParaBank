
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from Pages.base_page import BasePage


class SecurityPage(BasePage):

    BASE_URL = "https://parabank.parasoft.com/parabank"

    LOGOUT_LINK = (
        By.LINK_TEXT, "Log Out"
    )

    LOGIN_BUTTON = (
        By.CSS_SELECTOR,
        "input[value='Log In']"
    )

    USERNAME = (
        By.NAME, "username"
    )

    PASSWORD = (
        By.NAME, "password"
    )

    ACCOUNT_LINK = (
        By.LINK_TEXT, "Accounts Overview"
    )

    ACCOUNT_ROWS = (
        By.CSS_SELECTOR,
        "#accountTable tbody tr"
    )

    LOGIN_ERROR = (
        By.CSS_SELECTOR,
        "p.error"
    )

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    # =========================
    # LOGOUT
    # =========================

    def logout(self):

        self.wait.until(
            EC.element_to_be_clickable(
                self.LOGOUT_LINK
            )
        ).click()

    # =========================
    # LOGIN FORM VISIBLE
    # =========================

    def is_login_form_visible(self):

        try:
            self.wait.until(
                EC.visibility_of_element_located(
                    self.USERNAME
                )
            )

            self.wait.until(
                EC.visibility_of_element_located(
                    self.PASSWORD
                )
            )

            return True

        except TimeoutException:
            return False

    # =========================
    # PRIVATE PAGE ACCESS
    # =========================

    def open_accounts_directly(self):

        self.driver.get(
            self.BASE_URL + "/overview.htm"
        )

    # =========================
    # CHECK ACCOUNT DATA
    # =========================

    def private_account_data_visible(self):

        rows = self.driver.find_elements(
            *self.ACCOUNT_ROWS
        )

        for row in rows:

            if row.is_displayed():

                account_links = row.find_elements(
                    By.CSS_SELECTOR,
                    "a[href*='activity.htm']"
                )

                if account_links:
                    return True

        return False

    # =========================
    # LOGIN
    # =========================

    def login(self, username, password):

        self.driver.get(
            self.BASE_URL + "/index.htm"
        )

        self.wait.until(
            EC.visibility_of_element_located(
                self.USERNAME
            )
        ).send_keys(username)

        self.wait.until(
            EC.visibility_of_element_located(
                self.PASSWORD
            )
        ).send_keys(password)

        self.wait.until(
            EC.element_to_be_clickable(
                self.LOGIN_BUTTON
            )
        ).click()

    # =========================
    # LOGIN SUCCESS
    # =========================

    def is_authenticated(self):

        return bool(
            self.driver.find_elements(
                *self.LOGOUT_LINK
            )
        )

    # =========================
    # GET ACCOUNT ID
    # =========================

    def get_first_account_id(self):

        self.open_accounts_directly()

        account_links = self.wait.until(
            EC.presence_of_all_elements_located(
                (
                    By.CSS_SELECTOR,
                    "#accountTable a[href*='activity.htm']"
                )
            )
        )

        return account_links[0].text.strip()

    # =========================
    # OPEN ACCOUNT DETAILS
    # =========================

    def open_account_details(self, account_id):

        self.driver.get(
            self.BASE_URL
            + f"/activity.htm?id={account_id}"
        )

    # =========================
    # CHECK ACCOUNT DETAILS
    # =========================

    def account_details_visible(self, account_id):

        body = self.driver.find_element(
            By.TAG_NAME, "body"
        ).text

        return (
            "Account Details" in body
            and account_id in body
        )

    # =========================
    # XSS TEST
    # =========================

    def test_xss_payload(self, payload):

        self.driver.get(
            self.BASE_URL + "/index.htm"
        )

        username = self.wait.until(
            EC.visibility_of_element_located(
                self.USERNAME
            )
        )

        username.clear()
        username.send_keys(payload)

        return username.get_attribute("value")
