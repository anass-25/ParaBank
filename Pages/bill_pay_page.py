
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from Pages.base_page import BasePage


class BillPayPage(BasePage):

    # LOCATORS
    PAYEE_NAME = (By.NAME, "payee.name")
    ADDRESS = (By.NAME, "payee.address.street")
    CITY = (By.NAME, "payee.address.city")
    STATE = (By.NAME, "payee.address.state")
    ZIP_CODE = (By.NAME, "payee.address.zipCode")
    PHONE = (By.NAME, "payee.phoneNumber")
    ACCOUNT = (By.NAME, "payee.accountNumber")
    VERIFY_ACCOUNT = (By.NAME, "verifyAccount")
    AMOUNT = (By.NAME, "amount")
    FROM_ACCOUNT = (By.NAME, "fromAccountId")

    BILL_PAY_LINK = (By.LINK_TEXT, "Bill Pay")
    SEND_PAYMENT = (
        By.CSS_SELECTOR,
        "input[value='Send Payment']"
    )

    SUCCESS_MESSAGE = (By.ID, "rightPanel")
    PAYMENT_ERRORS = (By.CSS_SELECTOR, "#rightPanel .error")

    # OUVRIR BILL PAY
    def open_bill_pay_page(self):

        self.click(self.BILL_PAY_LINK)

        self.wait.until(
            EC.visibility_of_element_located(self.PAYEE_NAME)
        )

    # REMPLIR LE FORMULAIRE
    def fill_bill_pay(
        self, name, address, city, state,
        zip_code, phone, account,
        verify_account, amount
    ):

        self.type(self.PAYEE_NAME, name)
        self.type(self.ADDRESS, address)
        self.type(self.CITY, city)
        self.type(self.STATE, state)
        self.type(self.ZIP_CODE, zip_code)
        self.type(self.PHONE, phone)
        self.type(self.ACCOUNT, account)
        self.type(self.VERIFY_ACCOUNT, verify_account)
        self.type(self.AMOUNT, str(amount))

    # RÉCUPÉRER LES COMPTES
    def get_available_accounts(self):

        dropdown = Select(self.find(self.FROM_ACCOUNT))

        accounts = []

        for option in dropdown.options:

            account_id = option.get_attribute("value")

            if account_id:
                accounts.append(account_id)

        return accounts

    # SÉLECTIONNER LE COMPTE
    def select_from_account(self, account_id):

        dropdown = Select(self.find(self.FROM_ACCOUNT))

        dropdown.select_by_value(str(account_id))

    # ENVOYER LE PAIEMENT
    def click_send_payment(self):

        self.click(self.SEND_PAYMENT)

    # VÉRIFIER LE SUCCÈS

    def is_payment_successful(self):

        try:
            self.wait.until(
                EC.text_to_be_present_in_element(
                    self.SUCCESS_MESSAGE,
                    "Bill Payment Complete"
                )
            )

            self.wait.until(
                EC.text_to_be_present_in_element(
                    self.SUCCESS_MESSAGE,
                    "was successful"
                )
            )

            return True

        except TimeoutException:

            print("Payment confirmation not found")

            return False

    # RÉCUPÉRER LES ERREURS
    def get_payment_errors(self):

        error_elements = self.driver.find_elements(
            *self.PAYMENT_ERRORS
        )

        errors = []

        for element in error_elements:

            if element.is_displayed():

                message = element.text.strip()

                if message:
                    errors.append(message)

        return errors
