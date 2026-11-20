
from Pages.loan_page import LoanPage
from Pages.account_page import AccountPage
from Tests.test_transfer import login_user

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# =====================================
# HELPER - PREPARE LOAN
# =====================================

def prepare_loan(driver):

    # Register and login
    username = login_user(driver)

    print("Connected user:", username)

    # Open Request Loan page
    loan = LoanPage(driver)
    loan.open_loan_page()

    # Get available accounts
    accounts = loan.get_available_accounts()

    assert accounts, (
        "No bank account available for loan"
    )

    account = accounts[0]

    print("Selected account:", account)

    return loan, account


# =====================================
# HELPER - DISPLAY LOAN RESULT
# =====================================

def print_loan_result(loan, driver):

    status = loan.get_loan_status()
    errors = loan.get_errors()

    print("Loan status:", repr(status))
    print("Validation errors:", errors)
    print("Current URL:", driver.current_url)

    if not status and not errors:
        print("Page content:")
        print(loan.get_page_text())

    return status, errors


# =====================================
# TC_LOAN_001 - VALID LOAN REQUEST
# =====================================

def test_valid_loan_request(driver):

    loan, account = prepare_loan(driver)

    loan.fill_loan(
        amount="100",
        down_payment="20",
        account_id=account
    )

    loan.submit_loan()

    status, errors = print_loan_result(
        loan, driver
    )

    loan.take_screenshot(
        "TC_LOAN_001_valid_request"
    )

    assert status.lower() in (
        "approved",
        "denied"
    ), (
        "BUG: No valid loan decision displayed. "
        f"Status: {status}, Errors: {errors}"
    )


# =====================================
# TC_LOAN_002 - ZERO LOAN AMOUNT
# =====================================

def test_zero_loan_amount(driver):

    loan, account = prepare_loan(driver)

    loan.fill_loan(
        amount="0",
        down_payment="0",
        account_id=account
    )

    loan.submit_loan()

    status, errors = print_loan_result(
        loan, driver
    )

    loan.take_screenshot(
        "TC_LOAN_002_zero_amount"
    )

    assert status.lower() == "denied" or errors, (
        "BUG: Zero loan amount was not rejected "
        "with a visible decision or validation error. "
        f"Status: {status}, Errors: {errors}"
    )

    assert status.lower() != "approved", (
        "BUG: Zero loan amount was approved"
    )


# =====================================
# TC_LOAN_003 - NEGATIVE LOAN AMOUNT
# =====================================

def test_negative_loan_amount(driver):

    loan, account = prepare_loan(driver)

    loan.fill_loan(
        amount="-100",
        down_payment="0",
        account_id=account
    )

    loan.submit_loan()

    status, errors = print_loan_result(
        loan, driver
    )

    loan.take_screenshot(
        "TC_LOAN_003_negative_amount"
    )

    assert status.lower() == "denied" or errors, (
        "BUG: Negative loan amount was not rejected. "
        f"Status: {status}, Errors: {errors}"
    )

    assert status.lower() != "approved", (
        "BUG: Negative loan amount was approved"
    )


# =====================================
# TC_LOAN_004 - ZERO DOWN PAYMENT
# =====================================

def test_zero_down_payment(driver):

    loan, account = prepare_loan(driver)

    loan.fill_loan(
        amount="100",
        down_payment="0",
        account_id=account
    )

    loan.submit_loan()

    status, errors = print_loan_result(
        loan, driver
    )

    loan.take_screenshot(
        "TC_LOAN_004_zero_down_payment"
    )

    assert status.lower() in (
        "approved",
        "denied"
    ), (
        "BUG: No valid loan decision displayed "
        "for zero down payment. "
        f"Status: {status}, Errors: {errors}"
    )


# =====================================
# TC_LOAN_005 - DOWN PAYMENT > LOAN
# =====================================

def test_down_payment_greater_than_loan(driver):

    loan, account = prepare_loan(driver)

    loan.fill_loan(
        amount="100",
        down_payment="200",
        account_id=account
    )

    loan.submit_loan()

    status, errors = print_loan_result(
        loan, driver
    )

    loan.take_screenshot(
        "TC_LOAN_005_excess_down_payment"
    )

    assert status.lower() == "denied" or errors, (
        "BUG: Down payment greater than loan "
        "was not rejected. "
        f"Status: {status}, Errors: {errors}"
    )

    assert status.lower() != "approved", (
        "BUG: Down payment greater than loan "
        "was approved"
    )


# =====================================
# TC_LOAN_006 - INSUFFICIENT FUNDS
# =====================================

def test_insufficient_funds(driver):

    loan, account = prepare_loan(driver)

    # Very large down payment to test
    # insufficient funds behavior
    loan.fill_loan(
        amount="1000000",
        down_payment="900000",
        account_id=account
    )

    loan.submit_loan()

    status, errors = print_loan_result(
        loan, driver
    )

    loan.take_screenshot(
        "TC_LOAN_006_insufficient_funds"
    )

    assert status.lower() == "denied", (
        "BUG: Loan was not denied for "
        "the insufficient-funds scenario. "
        f"Status: {status}, Errors: {errors}"
    )


# =====================================
# TC_LOAN_007 - APPROVED LOAN ACCOUNT
# =====================================

def test_approved_loan_account_visible(driver):

    # Step 1 - Login and open loan page
    loan, account = prepare_loan(driver)

    # Step 2 - Fill loan request
    loan.fill_loan(
        amount="100",
        down_payment="20",
        account_id=account
    )

    # Step 3 - Submit request
    loan.submit_loan()

    # Step 4 - Get decision
    status, errors = print_loan_result(
        loan, driver
    )

    loan.take_screenshot(
        "TC_LOAN_007_approval"
    )

    # Step 5 - Verify approval
    assert status.lower() == "approved", (
        "Loan was not approved. "
        f"Status: {status}, Errors: {errors}"
    )

    # Step 6 - Get loan account ID
    new_account_id = loan.get_new_account_id()

    assert new_account_id, (
        "BUG: Approved loan has no account ID"
    )

    print("New loan account:", new_account_id)

    # Step 7 - Open Accounts Overview
    account_page = AccountPage(driver)

    account_page.open_accounts_overview()

    # Step 8 - Wait for the new account
    try:
        WebDriverWait(driver, 15).until(
            EC.text_to_be_present_in_element(
                (By.TAG_NAME, "body"),
                new_account_id
            )
        )

        print("Loan account found in Accounts Overview")

    except TimeoutException:
        print(
            "Loan account not found after 15 seconds"
        )

    # Step 9 - Read Accounts Overview
    page_text = driver.find_element(
        By.TAG_NAME, "body"
    ).text

    print("Accounts Overview content:")
    print(page_text)

    # Step 10 - Screenshot
    loan.take_screenshot(
        "TC_LOAN_007_account_visible"
    )

    # Step 11 - Verify account persistence
    assert new_account_id in page_text, (
        "BUG: Approved loan account "
        f"{new_account_id} not visible "
        "in Accounts Overview"
    )
