
from datetime import datetime
from decimal import Decimal

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Pages.base_page import BasePage


class TransactionPage(BasePage):

    FIND_TRANSACTIONS_LINK = (
        By.LINK_TEXT, "Find Transactions"
    )

    ACCOUNT_SELECT = (
        By.ID, "accountId"
    )

    TRANSACTION_ID = (
        By.ID, "transactionId"
    )

    TRANSACTION_DATE = (
        By.ID, "transactionDate"
    )

    FROM_DATE = (
        By.ID, "fromDate"
    )

    TO_DATE = (
        By.ID, "toDate"
    )

    AMOUNT = (
        By.ID, "amount"
    )

    RESULT_TABLE = (
        By.ID, "transactionTable"
    )

    RESULT_ROWS = (
        By.CSS_SELECTOR,
        "#transactionTable tbody tr"
    )

    ERROR_MESSAGES = (
        By.CSS_SELECTOR,
        ".error, [id$='.errors']"
    )

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def open_find_transactions(self):
        self.wait.until(
            EC.element_to_be_clickable(
                self.FIND_TRANSACTIONS_LINK
            )
        ).click()

        self.wait.until(
            EC.visibility_of_element_located(
                self.TRANSACTION_ID
            )
        )

    def select_account(self, account_id):
        from selenium.webdriver.support.ui import Select

        element = self.wait.until(
            EC.presence_of_element_located(
                self.ACCOUNT_SELECT
            )
        )

        Select(element).select_by_value(
            str(account_id)
        )

    def enter_value(self, locator, value):
        element = self.wait.until(
            EC.visibility_of_element_located(
                locator
            )
        )
        element.clear()
        element.send_keys(str(value))

    def click_find(self, locator):
        self.wait.until(
            EC.element_to_be_clickable(
                locator
            )
        ).click()

    def search_by_id(self, transaction_id):
        self.enter_value(
            self.TRANSACTION_ID, transaction_id
        )
        self.click_find(
            (By.ID, "findById")
        )

    def search_by_date(self, date):
        self.enter_value(
            self.TRANSACTION_DATE, date
        )
        self.click_find(
            (By.ID, "findByDate")
        )

    def search_by_date_range(self, start, end):
        self.enter_value(
            self.FROM_DATE, start
        )
        self.enter_value(
            self.TO_DATE, end
        )
        self.click_find(
            (By.ID, "findByDateRange")
        )

    def search_by_amount(self, amount):
        self.enter_value(
            self.AMOUNT, amount
        )
        self.click_find(
            (By.ID, "findByAmount")
        )

    def get_transactions(self):
        try:
            self.wait.until(
                EC.visibility_of_element_located(
                    self.RESULT_TABLE
                )
            )
        except Exception:
            return []

        rows = self.driver.find_elements(
            *self.RESULT_ROWS
        )

        transactions = []

        for row in rows:
            cells = row.find_elements(
                By.TAG_NAME, "td"
            )

            if len(cells) < 4:
                continue

            links = cells[1].find_elements(
                By.TAG_NAME, "a"
            )

            transaction_id = None

            if links:
                href = links[0].get_attribute("href") or ""

                if "id=" in href:
                    transaction_id = href.split(
                        "id=", 1
                    )[1].split("&")[0]

            transactions.append({
                "date": cells[0].text.strip(),
                "description": cells[1].text.strip(),
                "debit": cells[2].text.strip(),
                "credit": cells[3].text.strip(),
                "id": transaction_id
            })

        return transactions

    def get_errors(self):
        elements = self.driver.find_elements(
            *self.ERROR_MESSAGES
        )

        return [
            element.text.strip()
            for element in elements
            if element.is_displayed()
            and element.text.strip()
        ]

    def get_page_text(self):
        return self.driver.find_element(
            By.TAG_NAME, "body"
        ).text

    def open_transaction_details(self, transaction_id):
        self.driver.get(
            "https://parabank.parasoft.com/"
            "parabank/transaction.htm?id="
            f"{transaction_id}"
        )

        self.wait.until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "body")
            )
        )

    @staticmethod
    def parse_amount(value):
        cleaned = (
            str(value)
            .replace("$", "")
            .replace(",", "")
            .strip()
        )

        return Decimal(cleaned) if cleaned else Decimal("0")

    from selenium.webdriver.support.ui import Select

    # Add this method inside TransactionPage

    def get_available_accounts(self):

        dropdown = self.wait.until(
            EC.presence_of_element_located(
                self.ACCOUNT_SELECT
            )
        )

        select = Select(dropdown)

        accounts = []

        for option in select.options:

            account_id = option.get_attribute("value")

            if account_id and account_id.isdigit():
                accounts.append(account_id)

        return accounts

    def get_valid_transactions(self):

        transactions = self.get_transactions()

        valid_transactions = []

        for transaction in transactions:

            date = transaction["date"]
            description = transaction["description"]
            transaction_id = transaction["id"]

            if date == "NaN-NaN-NaN":
                continue

            if description == "undefined":
                continue

            if transaction_id in (None, "undefined"):
                continue

            valid_transactions.append(transaction)

        return valid_transactions


