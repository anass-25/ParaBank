
import uuid
from decimal import Decimal

import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from Pages.login_page import LoginPage
from Pages.register_page import RegisterPage
from Pages.transfer_page import TransferPage
from Pages.account_page import AccountPage


REGISTER_URL = "https://parabank.parasoft.com/parabank/register.htm"
HOME_URL = "https://parabank.parasoft.com/parabank/index.htm"

PASSWORD = "Test@12345"


def create_user(driver):

    username = "user_" + uuid.uuid4().hex[:10]
    driver.get(REGISTER_URL)
    register = RegisterPage(driver)
    register.fill_register(first_name="John",last_name="Smith",address="123 Main Street",city="New York",state="NY",zip_code="10001",phone="1234567890",ssn="123456789",username=username,password=PASSWORD)
    register.click_register()
    assert register.is_registration_successful(), "Registration failed"
    print("Registration successful:", username)
    register.logout()
    return username, PASSWORD


def login_user(driver):

    username, password = create_user(driver)
    driver.get(HOME_URL)
    login = LoginPage(driver)
    login.confirm_login(username, password)
    assert login.is_successful_login(), "Login failed"
    print("Login successful:", username)
    return username


def prepare_two_accounts(driver):

    login_user(driver)
    account_page = AccountPage(driver)
    new_account_id = str(account_page.create_account("CHECKING")).strip()
    print("New account created:", new_account_id)
    transfer = TransferPage(driver)
    transfer.open_transfer_page()


    def two_accounts_ready(driver):

        from_accounts, to_accounts = transfer.get_available_accounts()
        print("FROM accounts:", from_accounts)
        print("TO accounts:", to_accounts)
        sources = [
            account for account in from_accounts
            if account != new_account_id
        ]
        if sources and new_account_id in to_accounts:
            return sources[0], new_account_id
        return False

    source, destination = WebDriverWait(driver,20,poll_frequency=1).until(two_accounts_ready,message="Two distinct accounts not available")
    print("Source account:", source)
    print("Destination account:", destination)
    return transfer, source, destination


def get_balance(driver, account_id):

    accounts = AccountPage(driver)
    accounts.open_accounts_overview()
    return accounts.get_account_balance(account_id)


def verify_balances_unchanged(driver,source,destination,source_before,destination_before):

    source_after = get_balance(driver, source)
    destination_after = get_balance(driver, destination)
    assert source_after == source_before, "Source balance changed unexpectedly"

    assert destination_after == destination_before, "Destination balance changed unexpectedly"


def test_valid_transfer(driver):

    transfer, source, destination = prepare_two_accounts(driver)
    source_before = get_balance(driver, source)
    destination_before = get_balance(driver, destination)
    transfer.open_transfer_page()
    transfer.transfer_money(amount=100,from_account=source,to_account=destination)
    transfer.take_screenshot("TC_TRF_001_valid_transfer")
    print("URL:", driver.current_url)
    print("PAGE CONTENT:")
    print(driver.find_element(By.ID, "rightPanel").text)
    source_after = get_balance(driver, source)
    destination_after = get_balance(driver, destination)
    print("Source before:", source_before)
    print("Source after:", source_after)
    print("Destination before:", destination_before)
    print("Destination after:", destination_after)
    assert source_after == source_before - Decimal("100"), "Source account was not debited correctly"
    assert destination_after == destination_before + Decimal("100"), "Destination account was not credited correctly"

def test_zero_amount_transfer(driver):

    transfer, source, destination = prepare_two_accounts(driver)
    source_before = get_balance(driver, source)
    destination_before = get_balance(driver, destination)
    transfer.open_transfer_page()
    transfer.transfer_money(amount=0,from_account=source,to_account=destination)
    transfer.take_screenshot("TC_TRF_002_zero_amount")
    assert not transfer.is_transfer_successful(), "Zero amount transfer was accepted"
    verify_balances_unchanged(driver, source, destination,source_before, destination_before)

def test_negative_transfer(driver):

    transfer, source, destination = prepare_two_accounts(driver)
    source_before = get_balance(driver, source)
    destination_before = get_balance(driver, destination)
    print("Source before:", source_before)
    print("Destination before:", destination_before)
    transfer.open_transfer_page()
    transfer.transfer_money(amount=-100,from_account=source,to_account=destination)
    transfer.take_screenshot("TC_TRF_003_negative_amount")
    source_after = get_balance(driver, source)
    destination_after = get_balance(driver, destination)
    print("Source after:", source_after)
    print("Destination after:", destination_after)
    assert source_after == source_before, (f"BUG: Negative transfer changed source balance. "f"Before={source_before}, After={source_after}")
    assert destination_after == destination_before, (f"BUG: Negative transfer changed destination balance. "f"Before={destination_before}, After={destination_after}")


def test_empty_amount(driver):

    transfer, source, destination = prepare_two_accounts(driver)
    source_before = get_balance(driver, source)
    destination_before = get_balance(driver, destination)
    transfer.open_transfer_page()
    transfer.transfer_money(amount="",from_account=source,to_account=destination)
    transfer.take_screenshot("TC_TRF_004_empty_amount")
    assert not transfer.is_transfer_successful(), "Empty amount transfer was accepted"
    verify_balances_unchanged(driver, source, destination,source_before, destination_before)


def test_decimal_amount(driver):

    transfer, source, destination = prepare_two_accounts(driver)
    source_before = get_balance(driver, source)
    destination_before = get_balance(driver, destination)
    transfer.open_transfer_page()
    transfer.transfer_money(amount="1.50",from_account=source,to_account=destination)
    transfer.take_screenshot("TC_TRF_005_decimal_amount")
    source_after = get_balance(driver, source)
    destination_after = get_balance(driver, destination)
    print("Source before:", source_before)
    print("Source after:", source_after)
    print("Destination before:", destination_before)
    print("Destination after:", destination_after)
    assert source_after == source_before - Decimal("1.50"), "Source balance incorrect"
    assert destination_after == destination_before + Decimal("1.50"), "Destination balance incorrect"


def test_alphabetical_amount(driver):

    transfer, source, destination = prepare_two_accounts(driver)
    source_before = get_balance(driver, source)
    destination_before = get_balance(driver, destination)
    transfer.open_transfer_page()
    transfer.transfer_money(amount="fjkd",from_account=source,to_account=destination)
    transfer.take_screenshot("TC_TRF_006_alphabetical_amount")
    assert not transfer.is_transfer_successful(), "Alphabetical amount transfer was accepted"
    verify_balances_unchanged(driver, source, destination,source_before, destination_before)


def test_insufficient_funds(driver):

    transfer, source, destination = prepare_two_accounts(driver)
    source_before = get_balance(driver, source)
    destination_before = get_balance(driver, destination)
    amount = source_before + Decimal("1000.00")
    print("Available balance:", source_before)
    print("Requested transfer:", amount)
    transfer.open_transfer_page()
    transfer.transfer_money(amount=str(amount),from_account=source,to_account=destination)
    transfer.take_screenshot("TC_TRF_007_insufficient_funds")
    source_after = get_balance(driver, source)
    destination_after = get_balance(driver, destination)
    print("Source after:", source_after)
    print("Destination after:", destination_after)
    assert source_after == source_before, (f"BUG: Insufficient funds transfer changed source balance. "f"Before={source_before}, After={source_after}, "f"Requested={amount}")
    assert destination_after == destination_before, (f"BUG: Insufficient funds transfer changed destination balance. "f"Before={destination_before}, After={destination_after}")


def test_transfer_between_distinct_accounts(driver):

    transfer, source, destination = prepare_two_accounts(driver)
    source_before = get_balance(driver, source)
    destination_before = get_balance(driver, destination)
    transfer.open_transfer_page()
    transfer.transfer_money(amount=100,from_account=source,to_account=destination)
    transfer.take_screenshot("TC_TRF_008_debit_credit")
    source_after = get_balance(driver, source)
    destination_after = get_balance(driver, destination)
    print("Source before:", source_before)
    print("Source after:", source_after)
    print("Destination before:", destination_before)
    print("Destination after:", destination_after)
    assert source_after == source_before - Decimal("100"), "Incorrect debit"
    assert destination_after == destination_before + Decimal("100"), "Incorrect credit"



def test_transfer_same_account(driver):

    transfer, source, destination = prepare_two_accounts(driver)
    balance_before = get_balance(driver, source)
    transfer.open_transfer_page()
    transfer.transfer_money(amount=100,from_account=source,to_account=source)
    transfer.take_screenshot("TC_TRF_009_same_account")
    balance_after = get_balance(driver, source)
    assert balance_after == balance_before, "Balance changed after same-account transfer"

def test_transfer_history(driver):

    transfer, source, destination = prepare_two_accounts(driver)
    source_before = get_balance(driver, source)
    transfer.open_transfer_page()
    transfer.transfer_money(amount=100,from_account=source,to_account=destination)
    transfer.take_screenshot("TC_TRF_010_transfer_confirmation")
    source_after = get_balance(driver, source)
    assert source_after == source_before - Decimal("100"), "Transfer was not debited"
    accounts = AccountPage(driver)
    accounts.open_accounts_overview()
    accounts.open_account_details(source)
    WebDriverWait(driver, 15).until(
        lambda d: any(
            "$100.00" in row.text
            for row in d.find_elements(
                By.CSS_SELECTOR,
                "#transactionTable tbody tr"
            )
        )
    )
    rows = driver.find_elements(By.CSS_SELECTOR,"#transactionTable tbody tr")
    matching = [row for row in rows if "$100.00" in row.text]
    accounts.take_screenshot("TC_TRF_010_history")
    assert matching, "Transfer transaction not found in history"
