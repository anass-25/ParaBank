
from datetime import datetime
from decimal import Decimal
from urllib.parse import urlparse, parse_qs

import pytest
from selenium.webdriver.common.by import By

from Pages.account_page import AccountPage
from Pages.transactions_page import TransactionPage

from Tests.test_transfer import login_user


def get_existing_transaction(driver):
    """
    Find a real transaction in the account history.
    Return its ID, date, amount and account.
    """
    account = AccountPage(driver)
    account.open_accounts_overview()

    links = driver.find_elements(
        By.CSS_SELECTOR,
        "#accountTable tbody a"
    )

    account_ids = [
        link.text.strip()
        for link in links
        if link.text.strip().isdigit()
    ]

    for account_id in account_ids:
        account.open_account_details(account_id)

        rows = driver.find_elements(
            By.CSS_SELECTOR,
            "#transactionTable tbody tr"
        )

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")

            if len(cells) < 4:
                continue

            link = cells[1].find_elements(
                By.TAG_NAME, "a"
            )

            if not link:
                continue

            url = link[0].get_attribute("href")
            ids = parse_qs(urlparse(url).query).get("id")

            if not ids:
                continue

            debit = TransactionPage.parse_amount(
                cells[2].text
            )
            credit = TransactionPage.parse_amount(
                cells[3].text
            )

            amount = debit if debit != 0 else credit

            if amount <= 0:
                continue

            return {
                "id": ids[0],
                "date": cells[0].text.strip(),
                "amount": amount,
                "account": account_id,
                "description": cells[1].text.strip()
            }

        account.open_accounts_overview()

    pytest.skip(
        "Aucune transaction réelle disponible "
        "pour effectuer cette recherche."
    )


def open_search(driver, account_id):
    page = TransactionPage(driver)
    page.open_find_transactions()
    page.select_account(account_id)
    return page


def date_for_search(date_text):
    """
    Convert a displayed date to MM-dd-yyyy.
    """
    formats = [
        "%m-%d-%Y",
        "%m/%d/%Y",
        "%Y-%m-%d"
    ]

    for fmt in formats:
        try:
            date = datetime.strptime(date_text, fmt)
            return date.strftime("%m-%d-%Y")
        except ValueError:
            continue

    pytest.skip(
        f"Format de date non reconnu: {date_text}"
    )


# =====================================
# TC_TXN_001 - SEARCH BY ID
# =====================================

def test_search_by_transaction_id(driver):
    login_user(driver)

    transaction = get_existing_transaction(driver)

    page = open_search(
        driver, transaction["account"]
    )

    page.search_by_id(transaction["id"])

    results = page.get_transactions()

    page.take_screenshot("TC_TXN_001_search_by_id")

    assert results, (
        "Aucune transaction trouvée pour un ID existant"
    )

    assert any(
        item["id"] == transaction["id"]
        for item in results
    ), "La transaction recherchée est absente"


# =====================================
# TC_TXN_002 - SEARCH BY DATE
# =====================================

def test_search_by_date(driver):
    login_user(driver)

    transaction = get_existing_transaction(driver)

    date = date_for_search(transaction["date"])

    page = open_search(
        driver, transaction["account"]
    )

    page.search_by_date(date)

    results = page.get_transactions()

    page.take_screenshot("TC_TXN_002_search_by_date")

    assert results, "Aucune transaction trouvée"

    assert any(
        item["id"] == transaction["id"]
        for item in results
    ), "La transaction attendue est absente"

    assert all(
        date_for_search(item["date"]) == date
        for item in results
    ), "Résultat avec une date incorrecte"


# =====================================
# TC_TXN_003 - SEARCH BY DATE RANGE
# =====================================

def test_search_by_date_range(driver):
    login_user(driver)

    transaction = get_existing_transaction(driver)

    date = date_for_search(transaction["date"])

    page = open_search(
        driver, transaction["account"]
    )

    page.search_by_date_range(date, date)

    results = page.get_transactions()

    page.take_screenshot("TC_TXN_003_date_range")

    assert results, "Aucune transaction trouvée"

    assert any(
        item["id"] == transaction["id"]
        for item in results
    ), "La transaction attendue est absente"

    assert all(
        date_for_search(item["date"]) == date
        for item in results
    ), "Transaction hors intervalle"


# =====================================
# TC_TXN_004 - SEARCH BY AMOUNT
# =====================================

def test_search_by_amount(driver):
    login_user(driver)

    transaction = get_existing_transaction(driver)

    amount = transaction["amount"]

    page = open_search(
        driver, transaction["account"]
    )

    page.search_by_amount(str(amount))

    results = page.get_transactions()

    page.take_screenshot("TC_TXN_004_search_by_amount")

    assert results, "Aucune transaction trouvée"

    assert any(
        item["id"] == transaction["id"]
        for item in results
    ), "Transaction attendue absente"

    assert all(
        page.parse_amount(item["debit"]) == amount
        or page.parse_amount(item["credit"]) == amount
        for item in results
    ), "Montant incorrect dans les résultats"


# =====================================
# TC_TXN_005 - UNKNOWN TRANSACTION ID
# =====================================


def test_unknown_transaction_id(driver):

    login_user(driver)

    page = TransactionPage(driver)

    page.open_find_transactions()

    accounts = page.get_available_accounts()

    print("Available accounts:", accounts)

    assert accounts, (
        "Aucun compte disponible dans Find Transactions"
    )

    page.select_account(accounts[0])

    unknown_id = "999999999999999"

    page.search_by_id(unknown_id)

    results = page.get_transactions()

    print("Search results:", results)
    print("Validation errors:", page.get_errors())

    page.take_screenshot(
        "TC_TXN_005_unknown_transaction_id"
    )

    assert not results, (
        "BUG: Une transaction a été trouvée "
        "pour un identifiant supposé inexistant"
    )

# =====================================
# TC_TXN_006 - REVERSED DATE RANGE
# =====================================



def test_reversed_date_range(driver):

    login_user(driver)

    page = TransactionPage(driver)
    page.open_find_transactions()

    accounts = page.get_available_accounts()

    assert accounts, "Aucun compte disponible"

    page.select_account(accounts[0])

    page.search_by_date_range(
        "12-31-2026",
        "01-01-2026"
    )

    errors = page.get_errors()
    results = page.get_transactions()

    print("Validation errors:", errors)
    print("Transactions:", results)

    page.take_screenshot(
        "TC_TXN_006_reversed_date_range"
    )

    # Detect malformed rows
    invalid_rows = [
        transaction
        for transaction in results
        if (
            transaction["date"] == "NaN-NaN-NaN"
            or transaction["description"] == "undefined"
            or transaction["id"] == "undefined"
        )
    ]

    assert not invalid_rows, (
        "BUG: ParaBank affiche des transactions "
        f"invalides pour un intervalle inversé: {invalid_rows}"
    )

    assert errors or not results, (
        "BUG: L'intervalle inversé n'est pas rejeté "
        "et retourne des transactions"
    )

# =====================================
# TC_TXN_007 - TRANSFER DETAILS
# =====================================

def test_transfer_transaction_details(driver):
    login_user(driver)

    transaction = get_existing_transaction(driver)

    if "transfer" not in transaction["description"].lower():
        pytest.skip(
            "La transaction trouvée n'est pas un virement"
        )

    page = TransactionPage(driver)

    page.open_transaction_details(
        transaction["id"]
    )

    page.take_screenshot("TC_TXN_007_transfer_details")

    body = page.get_page_text()

    assert transaction["id"] in body, (
        "Identifiant de transaction absent"
    )

    amount = transaction["amount"]

    assert (
        f"${amount:,.2f}" in body
        or f"{amount:.2f}" in body
    ), "Montant du virement incorrect"

    assert transaction["account"] in body, (
        "Compte du virement absent du détail"
    )
