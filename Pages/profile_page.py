
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from Pages.base_page import BasePage


class ProfilePage(BasePage):

    # =========================
    # LOCATORS
    # =========================

    UPDATE_PROFILE_LINK = (
        By.LINK_TEXT, "Update Contact Info"
    )

    FIRST_NAME = (
        By.ID, "customer.firstName"
    )

    LAST_NAME = (
        By.ID, "customer.lastName"
    )

    ADDRESS = (
        By.ID, "customer.address.street"
    )

    CITY = (
        By.ID, "customer.address.city"
    )

    STATE = (
        By.ID, "customer.address.state"
    )

    ZIP_CODE = (
        By.ID, "customer.address.zipCode"
    )

    PHONE = (
        By.ID, "customer.phoneNumber"
    )

    UPDATE_BUTTON = (
        By.CSS_SELECTOR,
        "input[value='Update Profile']"
    )

    SUCCESS_TITLE = (
        By.XPATH,
        "//h1[normalize-space()='Profile Updated']"
    )

    ERROR_MESSAGES = (
        By.CSS_SELECTOR,
        "span.error"
    )

    # =========================
    # CONSTRUCTOR
    # =========================

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    # =========================
    # OPEN PROFILE PAGE
    # =========================

    def open_profile_page(self):

        self.wait.until(
            EC.element_to_be_clickable(
                self.UPDATE_PROFILE_LINK
            )
        ).click()

        self.wait.until(
            EC.visibility_of_element_located(
                self.ADDRESS
            )
        )

    # =========================
    # UPDATE ONE FIELD
    # =========================

    def set_field(self, locator, value):

        element = self.wait.until(
            EC.visibility_of_element_located(
                locator
            )
        )

        element.clear()
        element.send_keys(str(value))

    # =========================
    # UPDATE PROFILE FIELDS
    # =========================

    def update_fields(
        self,
        first_name=None,
        last_name=None,
        address=None,
        city=None,
        state=None,
        zip_code=None,
        phone=None
    ):

        fields = {
            "first_name": (self.FIRST_NAME, first_name),
            "last_name": (self.LAST_NAME, last_name),
            "address": (self.ADDRESS, address),
            "city": (self.CITY, city),
            "state": (self.STATE, state),
            "zip_code": (self.ZIP_CODE, zip_code),
            "phone": (self.PHONE, phone)
        }

        for field_name, (locator, value) in fields.items():

            if value is not None:

                self.set_field(locator, value)

                print(
                    f"Updated {field_name}: {value}"
                )

    # =========================
    # READ FIELD VALUE
    # =========================

    def get_field(self, locator):

        element = self.wait.until(
            EC.visibility_of_element_located(
                locator
            )
        )

        return element.get_attribute("value") or ""

    # =========================
    # COMPLETE REQUIRED FIELDS
    # =========================

    def fill_required_fields(self):

        required_fields = {
            self.FIRST_NAME: "John",
            self.LAST_NAME: "Smith",
            self.ADDRESS: "123 Main Street",
            self.CITY: "New York",
            self.STATE: "NY",
            self.ZIP_CODE: "10001"
        }

        for locator, default_value in required_fields.items():

            current_value = self.get_field(locator)

            if not current_value.strip():

                self.set_field(
                    locator,
                    default_value
                )

        print("Required profile fields completed")

    # =========================
    # SUBMIT PROFILE
    # =========================

    def submit(self):

        self.wait.until(
            EC.element_to_be_clickable(
                self.UPDATE_BUTTON
            )
        ).click()

    # =========================
    # CHECK SUCCESS
    # =========================

    def is_update_successful(self):

        try:

            self.wait.until(
                EC.visibility_of_element_located(
                    self.SUCCESS_TITLE
                )
            )

            print("Profile update confirmed")

            return True

        except TimeoutException:

            print(
                "Profile update confirmation not found"
            )

            print(
                "Current URL:",
                self.driver.current_url
            )

            body = self.driver.find_element(
                By.TAG_NAME,
                "body"
            )

            print(
                "Page content:",
                body.text
            )

            return False

    # =========================
    # GET VALIDATION ERRORS
    # =========================

    def get_errors(self):

        try:

            self.wait.until(
                lambda driver: any(
                    element.is_displayed()
                    and element.text.strip()
                    for element in driver.find_elements(
                        *self.ERROR_MESSAGES
                    )
                )
            )

        except TimeoutException:
            pass

        errors = []

        elements = self.driver.find_elements(
            *self.ERROR_MESSAGES
        )

        for element in elements:

            if element.is_displayed():

                message = element.text.strip()

                if message:
                    errors.append(message)

        return errors

    # =========================
    # REFRESH PROFILE
    # =========================

    def refresh_profile(self):

        self.driver.refresh()

        self.wait.until(
            EC.visibility_of_element_located(
                self.ADDRESS
            )
        )

    # =========================
    # GET ALL PROFILE DATA
    # =========================

    def get_profile_data(self):

        return {
            "first_name": self.get_field(
                self.FIRST_NAME
            ),
            "last_name": self.get_field(
                self.LAST_NAME
            ),
            "address": self.get_field(
                self.ADDRESS
            ),
            "city": self.get_field(
                self.CITY
            ),
            "state": self.get_field(
                self.STATE
            ),
            "zip_code": self.get_field(
                self.ZIP_CODE
            ),
            "phone": self.get_field(
                self.PHONE
            )
        }
