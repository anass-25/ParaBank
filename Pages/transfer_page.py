
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC

from Pages.base_page import BasePage


class TransferPage(BasePage):

    TRANSFER_LINK = (By.LINK_TEXT, "Transfer Funds")

    AMOUNT_INPUT = (By.ID, "amount")
    FROM_ACCOUNT = (By.ID, "fromAccountId")
    TO_ACCOUNT = (By.ID, "toAccountId")
    TRANSFER_BUTTON = (By.CSS_SELECTOR,"input[value='Transfer']")
    SUCCESS_TITLE = (By.CSS_SELECTOR, "#rightPanel h1")

    def open_transfer_page(self):

        self.click(self.TRANSFER_LINK)
        self.wait.until(EC.visibility_of_element_located(self.AMOUNT_INPUT))

    def enter_amount(self, amount):

        self.type(self.AMOUNT_INPUT, str(amount))

    def wait_for_account_option(self, locator, account_id):

        account_id = str(account_id)

        def option_exists(driver):

            dropdown = Select(driver.find_element(*locator))
            values = [option.get_attribute("value") for option in dropdown.options]
            return account_id in values
        self.wait.until(option_exists,message=f"Account {account_id} not available")

    def select_from_account(self, account_id):

        self.wait_for_account_option(self.FROM_ACCOUNT,account_id)

        dropdown = Select(self.find(self.FROM_ACCOUNT))

        dropdown.select_by_value(str(account_id))

    def select_to_account(self, account_id):

        self.wait_for_account_option(
            self.TO_ACCOUNT,
            account_id
        )

        dropdown = Select(self.find(self.TO_ACCOUNT))

        dropdown.select_by_value(str(account_id))

    def get_available_accounts(self):

        from_dropdown = Select(self.find(self.FROM_ACCOUNT))
        to_dropdown = Select(self.find(self.TO_ACCOUNT))

        from_accounts = [
            option.get_attribute("value")
            for option in from_dropdown.options
            if option.get_attribute("value")
        ]

        to_accounts = [
            option.get_attribute("value")
            for option in to_dropdown.options
            if option.get_attribute("value")
        ]

        return from_accounts, to_accounts

    def click_transfer(self):

        self.click(self.TRANSFER_BUTTON)

    def transfer_money(self, amount, from_account, to_account):

        self.enter_amount(amount)

        self.select_from_account(from_account)

        self.select_to_account(to_account)

        self.click_transfer()

    def is_transfer_successful(self):

        try:
            self.wait.until(
                EC.text_to_be_present_in_element(
                    self.SUCCESS_TITLE,
                    "Transfer Complete"
                )
            )

            return True

        except Exception:

            return False

    def get_transfer_error(self):

        errors = self.driver.find_elements(
            By.CSS_SELECTOR,
            "#rightPanel p.error"
        )

        return " ".join(
            element.text
            for element in errors
            if element.is_displayed()
        )
