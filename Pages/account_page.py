
from decimal import Decimal

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from Pages.base_page import BasePage


class AccountPage(BasePage):

    # ==========================
    # LOCATORS
    # ==========================

    OPEN_ACCOUNT_LINK = (By.LINK_TEXT, "Open New Account")
    ACCOUNT_TYPE = (By.ID, "type")
    FROM_ACCOUNT = (By.ID, "fromAccountId")
    OPEN_BUTTON = (By.CSS_SELECTOR, "input[value='Open New Account']")
    NEW_ACCOUNT_ID = (By.ID, "newAccountId")

    OVERVIEW_LINK = (By.LINK_TEXT, "Accounts Overview")
    ACCOUNT_TABLE = (By.ID, "accountTable")
    TRANSACTION_TABLE = (By.ID, "transactionTable")

    # ==========================
    # 1. OPEN NEW ACCOUNT
    # ==========================

    def open_new_account_page(self):

        self.click(self.OPEN_ACCOUNT_LINK)

        self.wait.until(
            EC.visibility_of_element_located(
                self.ACCOUNT_TYPE
            )
        )

    # ==========================
    # 2. CREATE ACCOUNT
    # ==========================

    def create_account(self, account_type="CHECKING"):

        self.open_new_account_page()

        dropdown = Select(self.find(self.ACCOUNT_TYPE))
        dropdown.select_by_visible_text(account_type)

        def funding_account_ready(driver):

            select = Select(
                driver.find_element(*self.FROM_ACCOUNT)
            )

            accounts = [
                option.get_attribute("value")
                for option in select.options
                if option.get_attribute("value")
                and option.get_attribute("value").isdigit()
            ]

            return accounts if accounts else False

        source_accounts = WebDriverWait(
            self.driver, 20
        ).until(funding_account_ready)

        Select(
            self.find(self.FROM_ACCOUNT)
        ).select_by_value(source_accounts[0])

        self.click(self.OPEN_BUTTON)

        account_element = self.wait.until(
            EC.visibility_of_element_located(
                self.NEW_ACCOUNT_ID
            )
        )

        account_id = account_element.text.strip()

        assert account_id, "New account ID not found"

        print("New account created:", account_id)

        return account_id

    # ==========================
    # 3. ACCOUNTS OVERVIEW
    # ==========================

    def open_accounts_overview(self):

        self.click(self.OVERVIEW_LINK)

        self.wait.until(
            EC.visibility_of_element_located(
                self.ACCOUNT_TABLE
            )
        )

    # ==========================
    # 4. ACCOUNT BALANCE
    # ==========================

    def get_account_balance(self, account_id):

        locator = (
            By.XPATH,
            f"//a[normalize-space()='{account_id}']"
            "/ancestor::tr/td[2]"
        )

        element = self.wait.until(
            EC.visibility_of_element_located(locator)
        )

        balance_text = (
            element.text
            .replace("$", "")
            .replace(",", "")
            .strip()
        )

        balance = Decimal(balance_text)

        print(f"Account {account_id} balance: {balance}")

        return balance

    # ==========================
    # 5. ACCOUNT DETAILS
    # ==========================

    def open_account_details(self, account_id):

        self.click(
            (By.LINK_TEXT, str(account_id))
        )

        self.wait.until(
            EC.visibility_of_element_located(
                self.TRANSACTION_TABLE
            )
        )

        print("Account details opened:", account_id)

    # ==========================
    # 6. GET TRANSACTIONS
    # ==========================

    def get_transactions(self):

        table = self.wait.until(
            EC.visibility_of_element_located(
                self.TRANSACTION_TABLE
            )
        )

        print("========== TRANSACTION DEBUG ==========")

        print("Current URL:", self.driver.current_url)
        print("Table content:")
        print(table.text)

        rows = table.find_elements(
            By.TAG_NAME,
            "tr"
        )

        print("Total rows found:", len(rows))

        transactions = []

        for row in rows:

            cells = row.find_elements(
                By.TAG_NAME,
                "td"
            )

            print(
                "Row cells:",
                [cell.text for cell in cells]
            )

            if len(cells) >= 4:

                transaction = {
                    "date": cells[0].text.strip(),
                    "description": cells[1].text.strip(),
                    "debit": cells[2].text.strip(),
                    "credit": cells[3].text.strip()
                }

                transactions.append(transaction)

        print("Parsed transactions:", transactions)
        print("=======================================")

        return transactions

    # ==========================
    # 7. REFRESH ACCOUNTS
    # ==========================

    def refresh_accounts_overview(self):

        self.driver.refresh()

        self.wait.until(
            EC.visibility_of_element_located(
                self.ACCOUNT_TABLE
            )
        )

        print("Accounts overview refreshed")
