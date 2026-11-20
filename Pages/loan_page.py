
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from Pages.base_page import BasePage


class LoanPage(BasePage):

    # =========================
    # LOCATORS
    # =========================

    REQUEST_LOAN_LINK = (
        By.LINK_TEXT, "Request Loan"
    )

    LOAN_AMOUNT = (
        By.ID, "amount"
    )

    DOWN_PAYMENT = (
        By.ID, "downPayment"
    )

    FROM_ACCOUNT = (
        By.ID, "fromAccountId"
    )

    APPLY_BUTTON = (
        By.CSS_SELECTOR,
        "input[value='Apply Now']"
    )

    LOAN_STATUS = (
        By.ID, "loanStatus"
    )

    LOAN_RESPONSE = (
        By.ID, "loanRequestApproved"
    )

    LOAN_DENIED = (
        By.ID, "loanRequestDenied"
    )

    NEW_ACCOUNT_ID = (
        By.ID, "newAccountId"
    )

    ERROR_MESSAGES = (
        By.CSS_SELECTOR, "span.error"
    )

    # =========================
    # CONSTRUCTOR
    # =========================

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    # =========================
    # OPEN LOAN PAGE
    # =========================

    def open_loan_page(self):

        self.wait.until(
            EC.element_to_be_clickable(
                self.REQUEST_LOAN_LINK
            )
        ).click()

        self.wait.until(
            EC.visibility_of_element_located(
                self.LOAN_AMOUNT
            )
        )

    # =========================
    # GET AVAILABLE ACCOUNTS
    # =========================

    def get_available_accounts(self):

        dropdown = Select(
            self.wait.until(
                EC.presence_of_element_located(
                    self.FROM_ACCOUNT
                )
            )
        )

        accounts = []

        for option in dropdown.options:

            value = option.get_attribute("value")

            if value and value.isdigit():
                accounts.append(value)

        return accounts

    # =========================
    # FILL LOAN FORM
    # =========================

    def fill_loan(
        self,
        amount,
        down_payment,
        account_id
    ):

        self.type(
            self.LOAN_AMOUNT,
            str(amount)
        )

        self.type(
            self.DOWN_PAYMENT,
            str(down_payment)
        )

        dropdown = Select(
            self.wait.until(
                EC.element_to_be_clickable(
                    self.FROM_ACCOUNT
                )
            )
        )

        dropdown.select_by_value(
            str(account_id)
        )

    # =========================
    # SUBMIT LOAN
    # =========================

    def submit_loan(self):

        self.wait.until(
            EC.element_to_be_clickable(
                self.APPLY_BUTTON
            )
        ).click()

    # =========================
    # GET LOAN STATUS
    # =========================

    def get_loan_status(self):

        try:

            element = self.wait.until(
                EC.visibility_of_element_located(
                    self.LOAN_STATUS
                )
            )

            return element.text.strip()

        except TimeoutException:
            return ""

    # =========================
    # CHECK APPROVAL
    # =========================

    def is_loan_approved(self):

        status = self.get_loan_status()

        return status.lower() == "approved"

    # =========================
    # CHECK DENIAL
    # =========================

    def is_loan_denied(self):

        status = self.get_loan_status()

        return status.lower() == "denied"

    # =========================
    # GET NEW LOAN ACCOUNT
    # =========================

    def get_new_account_id(self):

        elements = self.driver.find_elements(
            *self.NEW_ACCOUNT_ID
        )

        for element in elements:

            if element.is_displayed():
                return element.text.strip()

        return None

    # =========================
    # GET ERRORS
    # =========================

    def get_errors(self):

        errors = []

        for element in self.driver.find_elements(
            *self.ERROR_MESSAGES
        ):

            if element.is_displayed():

                message = element.text.strip()

                if message:
                    errors.append(message)

        return errors

    # =========================
    # GET PAGE TEXT
    # =========================

    def get_page_text(self):

        return self.driver.find_element(
            By.TAG_NAME,
            "body"
        ).text
