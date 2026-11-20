from decimal import Decimal, InvalidOperation
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pytest
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from Pages.account_page import AccountPage
from Pages.bill_pay_page import BillPayPage
from Tests.test_transfer import login_user


PAYEE = {
    "name": "John Smith",
    "address": "123 Main Street",
    "city": "New York",
    "state": "NY",
    "zip_code": "10001",
    "phone": "1234567890",
    "account": "123456",
    "verify_account": "123456",
    "amount": "100",
}


def read_balance(driver, account_id):
    """Open the overview and read the current balance."""
    page = AccountPage(driver)
    page.open_accounts_overview()
    return page.get_account_balance(account_id)


def setup_bill_payment(driver):
    """Register/login and prepare a source account."""
    username = login_user(driver)
    print("Connected user:", username)
    bill = BillPayPage(driver)
    bill.open_bill_pay_page()
    accounts = bill.get_available_accounts()
    assert accounts, "No account available for payment"
    account_id = accounts[0]
    balance_before = read_balance(driver, account_id)
    print("Source account:", account_id)
    print("Balance before:", balance_before)
    bill.open_bill_pay_page()
    bill.select_from_account(account_id)
    return bill, account_id, balance_before


def send_payment(bill, **overrides):
    fields = {**PAYEE, **overrides}
    bill.fill_bill_pay(**fields)
    bill.click_send_payment()


def get_confirmation(driver):
    text = driver.find_element(By.ID, "rightPanel").text
    print("Payment page:", text)
    return text


def assert_confirmation(driver, bill, account_id, amount):
    assert bill.is_payment_successful(), (
        "Payment confirmation was not displayed. " + get_confirmation(driver)
    )
    confirmation = get_confirmation(driver)
    assert str(account_id) in confirmation, (
        f"Confirmation does not mention source account {account_id}: {confirmation}"
    )
    expected_amount = f"${Decimal(amount):,.2f}"
    assert expected_amount in confirmation, (
        f"Confirmation does not mention {expected_amount}: {confirmation}"
    )



def check_balance(driver, account_id, expected):

    def balance_updated(driver):

        page = AccountPage(driver)

        driver.refresh()

        page.wait.until(
            EC.visibility_of_element_located(
                page.ACCOUNT_TABLE
            )
        )

        actual = page.get_account_balance(account_id)

        print(
            f"Expected: {expected}, Actual: {actual}"
        )

        return actual == expected

    page = AccountPage(driver)
    page.open_accounts_overview()

    try:
        WebDriverWait(
            driver,
            20,
            poll_frequency=2
        ).until(balance_updated)

    except TimeoutException:

        actual = page.get_account_balance(account_id)

        pytest.fail(
            f"BUG: Balance not updated. "
            f"Expected={expected}, Actual={actual}"
        )





def read_transactions(driver, account_id):

    page = AccountPage(driver)

    page.open_accounts_overview()
    page.open_account_details(account_id)

    def transactions_loaded(driver):

        driver.refresh()

        page.wait.until(
            EC.visibility_of_element_located(
                page.TRANSACTION_TABLE
            )
        )

        transactions = page.get_transactions()

        print("Transactions:", transactions)

        return transactions if transactions else False

    try:
        return WebDriverWait(
            driver,
            20,
            poll_frequency=2
        ).until(transactions_loaded)

    except TimeoutException:

        pytest.fail(
            f"BUG: No transactions found "
            f"for account {account_id} "
            f"after waiting 20 seconds."
        )



def payment_in_history(transactions, amount):

    expected_amount = Decimal(str(amount))

    for item in transactions:

        description = item.get(
            "description", ""
        ).lower()

        raw_debit = (
            item.get("debit", "")
            .replace("$", "")
            .replace(",", "")
            .strip()
        )

        if not raw_debit:
            continue

        try:
            debit = Decimal(raw_debit)
        except InvalidOperation:
            continue

        if (
            "bill" in description
            and "payment" in description
            and debit == expected_amount
        ):
            return True

    return False



    for item in transactions:
        description = item.get("description", "").lower()
        raw_debit = item.get("debit", "").replace("$", "").replace(",", "").strip()
        if not raw_debit:
            continue
        try:
            debit = Decimal(raw_debit)
        except InvalidOperation:
            continue
        if "bill" in description and "payment" in description and debit == Decimal(amount):
            return True
    return False




def assert_rejected_payment(
    driver,
    bill,
    account_id,
    balance_before,
    case_name
):
    panel_text = get_confirmation(driver)
    errors = bill.get_payment_errors()

    amount_field = driver.find_element(
        By.NAME, "amount"
    )

    validation = driver.execute_script(
        """
        return {
            value: arguments[0].value,
            valid: arguments[0].validity.valid,
            message: arguments[0].validationMessage
        };
        """,
        amount_field
    )

    print("Test case:", case_name)
    print("Application errors:", errors)
    print("HTML validation:", validation)

    assert "Bill Payment Complete" not in panel_text, (
        f"BUG: {case_name} was accepted"
    )

    balance_after = read_balance(driver, account_id)

    assert balance_after == balance_before, (
        f"BUG: Balance changed after {case_name}. "
        f"Before={balance_before}, After={balance_after}"
    )

    assert errors or not validation["valid"], (
        f"BUG: {case_name} was not explicitly rejected. "
        f"Application errors={errors}, HTML validation={validation}"
    )

def test_valid_bill_payment(driver):
    bill, account_id, before = setup_bill_payment(driver)
    send_payment(bill, amount="100")
    assert_confirmation(driver, bill, account_id, "100")
    bill.take_screenshot("TC_BILL_001_valid_payment")
    check_balance(driver, account_id, before - Decimal("100.00"))
    print("TC_BILL_001 PASSED")


def test_empty_payee_name(driver):
    bill, account_id, before = setup_bill_payment(driver)
    send_payment(bill, name="")
    bill.take_screenshot("TC_BILL_002_empty_payee_name")
    assert_rejected_payment(driver, bill, account_id, before, "empty payee name")
    print("TC_BILL_002 PASSED")


def test_invalid_payee_account(driver):
    bill, account_id, before = setup_bill_payment(driver)
    send_payment(bill, account="ABC123", verify_account="ABC123")
    bill.take_screenshot("TC_BILL_003_invalid_payee_account")
    assert_rejected_payment(driver, bill, account_id, before, "invalid payee account")
    print("TC_BILL_003 PASSED")


def test_different_payee_account(driver):
    bill, account_id, before = setup_bill_payment(driver)
    send_payment(bill, account="123456", verify_account="123457")
    bill.take_screenshot("TC_BILL_004_different_payee_account")
    errors = bill.get_payment_errors()
    assert any("account" in error.lower() for error in errors), (
        f"Missing account mismatch validation. Actual errors: {errors}"
    )
    assert_rejected_payment(driver, bill, account_id, before, "account mismatch")
    print("TC_BILL_004 PASSED")


def test_negative_amount(driver):
    bill, account_id, before = setup_bill_payment(driver)
    send_payment(bill, amount="-100")
    bill.take_screenshot("TC_BILL_005_negative_amount")
    assert_rejected_payment(driver, bill, account_id, before, "negative amount")
    print("TC_BILL_005 PASSED")


def test_zero_amount(driver):
    bill, account_id, before = setup_bill_payment(driver)
    send_payment(bill, amount="0")
    bill.take_screenshot("TC_BILL_006_zero_amount")
    assert_rejected_payment(driver, bill, account_id, before, "zero amount")
    print("TC_BILL_006 PASSED")


def test_valid_decimal_amount(driver):
    bill, account_id, before = setup_bill_payment(driver)
    send_payment(bill, amount="125.50")
    assert_confirmation(driver, bill, account_id, "125.50")
    bill.take_screenshot("TC_BILL_007_valid_decimal_amount")
    check_balance(driver, account_id, before - Decimal("125.50"))
    print("TC_BILL_007 PASSED")


def test_bill_payment_history(driver):
    bill, account_id, before = setup_bill_payment(driver)
    send_payment(bill, amount="100")
    assert_confirmation(driver, bill, account_id, "100")
    bill.take_screenshot("TC_BILL_008_payment_confirmation")
    transactions = read_transactions(driver, account_id)
    assert payment_in_history(transactions, "100"), (
        "BUG: Payment confirmed but no matching $100 bill-payment debit "
        f"was found in account {account_id} history: {transactions}"
    )
    print("TC_BILL_008 PASSED")
