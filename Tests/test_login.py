
import uuid

import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Pages.register_page import RegisterPage
from Pages.login_page import LoginPage


REGISTER_URL = "https://parabank.parasoft.com/parabank/register.htm"
HOME_URL = "https://parabank.parasoft.com/parabank/index.htm"
PRIVATE_URL = "https://parabank.parasoft.com/parabank/overview.htm"

PASSWORD = "Test@12345"

EXPECT_CASE_SENSITIVE = True


def create_user(driver):
    username = "user_" + uuid.uuid4().hex[:10]
    driver.get(REGISTER_URL)
    register = RegisterPage(driver)
    register.fill_register(first_name="John",last_name="Smith",address="123 Main Street",city="New York",state="NY",zip_code="10001",phone="1234567890",ssn="123456789",username=username,password=PASSWORD)
    register.click_register()
    assert register.is_registration_successful(), \
        "Registration failed"
    print("Registration successful:", username)
    register.logout()
    return username, PASSWORD

def assert_login_refused(driver, login):
    error_message = login.get_login_error()
    assert error_message.strip(), \
        "Expected a non-empty login error message"
    logout_links = driver.find_elements(By.LINK_TEXT, "Log Out")
    assert len(logout_links) == 0, \
        "Unexpected authenticated session"
    print("Login correctly refused")
    print("Error message:", error_message)
    return error_message

def test_register_then_login(driver):
    username, password = create_user(driver)
    driver.get(HOME_URL)
    login = LoginPage(driver)
    login.confirm_login(username, password)
    assert login.is_successful_login(), \
        "Login failed"
    print("Login successful")
    login.take_screenshot("TC_LOGIN_001_success")

def test_login_incorrect_password(driver):

    username, _ = create_user(driver)
    driver.get(HOME_URL)
    login = LoginPage(driver)
    login.confirm_login(username,"WrongPassword123")
    error_message = assert_login_refused(driver, login)
    assert "could not be verified" in error_message.lower(), \
        f"Unexpected error message: {error_message}"
    login.take_screenshot("TC_LOGIN_002_wrong_password")

def test_username_unknown(driver):

    username = "unknown_" + uuid.uuid4().hex[:10]
    driver.get(HOME_URL)
    login = LoginPage(driver)
    login.confirm_login(username,"anass1234")
    error_message = assert_login_refused(driver, login)
    assert "could not be verified" in error_message.lower(), \
        f"Unexpected error message: {error_message}"
    login.take_screenshot("TC_LOGIN_003_unknown_username")


def test_username_empty(driver):

    driver.get(HOME_URL)
    login = LoginPage(driver)
    login.confirm_login("",PASSWORD)
    error_message = assert_login_refused(driver, login)
    assert "please enter a username and password" in error_message.lower(), \
        f"Unexpected error message: {error_message}"
    login.take_screenshot("TC_LOGIN_004_empty_username")


def test_password_empty(driver):

    username, _ = create_user(driver)
    driver.get(HOME_URL)
    login = LoginPage(driver)
    login.confirm_login(username,"")
    error_message = assert_login_refused(driver, login)
    assert "please enter a username and password" in error_message.lower(), \
        f"Unexpected error message: {error_message}"
    login.take_screenshot("TC_LOGIN_005_empty_password")


def test_two_empty_fields(driver):

    driver.get(HOME_URL)
    login = LoginPage(driver)
    login.confirm_login("", "")
    error_message = assert_login_refused(driver, login)
    assert "please enter a username and password" in error_message.lower(), \
        f"Unexpected error message: {error_message}"
    login.take_screenshot("TC_LOGIN_006_empty_fields")

def test_relogin_after_logout(driver):

    username, password = create_user(driver)
    driver.get(HOME_URL)
    login = LoginPage(driver)
    login.confirm_login(username, password)
    assert login.is_successful_login(), \
        "Re-login failed"
    print("Re-login successful")
    login.take_screenshot("TC_LOGIN_007_relogin")

def test_private_page_without_login(driver):

    driver.get(PRIVATE_URL)

    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return document.readyState") == "complete")
    accounts_table = driver.find_elements(By.ID, "accountTable")
    assert len(accounts_table) == 0, \
        "Private account table is accessible"
    logout_links = driver.find_elements(By.LINK_TEXT, "Log Out")
    assert len(logout_links) == 0, \
        "Unexpected authenticated session"
    print("No private account table or authenticated session found")
    login = LoginPage(driver)
    login.take_screenshot("TC_LOGIN_008_private_access")


@pytest.mark.parametrize(
    "sql_input",
    [
        "' OR '1'='1",
        "admin' --",
        "' OR 1=1 --"
    ],
    ids=["or_condition", "sql_comment", "or_numeric"]
)
def test_login_sql_injection(driver, sql_input):

    driver.get(HOME_URL)

    login = LoginPage(driver)

    login.confirm_login(sql_input, "WrongPassword123")

    # Attendre le chargement du document
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script(
            "return document.readyState"
        ) == "complete"
    )

    # Capturer l'état réel avant les assertions
    print("Current URL:", driver.current_url)
    print("Page title:", driver.title)

    error_elements = driver.find_elements(
        By.CSS_SELECTOR, "#rightPanel p.error"
    )

    if error_elements:
        print("Error:", error_elements[0].text)
    else:
        print("No standard login error message found")

    # Enregistrer la capture pour inspection
    login.take_screenshot(
        "TC_LOGIN_009_sql_injection"
    )

    # Vérifier l'absence de session authentifiée
    logout_links = driver.find_elements(
        By.LINK_TEXT, "Log Out"
    )

    assert len(logout_links) == 0, \
        "Potential authentication bypass: Log Out link found"

    # Vérifier l'absence de données de comptes
    account_tables = driver.find_elements(
        By.ID, "accountTable"
    )

    assert len(account_tables) == 0, \
        "Potential authentication bypass: account table found"

    # Vérifier l'absence d'erreur serveur visible
    assert "HTTP Status 500" not in driver.page_source, \
        "Server error detected"

    print("No visible authentication bypass detected")


def test_login_username_uppercase(driver):
    username, password = create_user(driver)
    driver.get(HOME_URL)
    login = LoginPage(driver)
    uppercase_username = username.upper()
    login.confirm_login(uppercase_username,password)
    WebDriverWait(driver, 10).until(lambda d: (len(d.find_elements(By.LINK_TEXT, "Log Out")) > 0 or len(d.find_elements(By.CSS_SELECTOR, "#rightPanel p.error")) > 0))
    authenticated = len(driver.find_elements(By.LINK_TEXT, "Log Out")) > 0
    print("Original username:", username)
    print("Uppercase username:", uppercase_username)
    print("Login accepted:", authenticated)
    assert authenticated == (not EXPECT_CASE_SENSITIVE), \
        "Username case sensitivity differs from the expected rule"
    login.take_screenshot("TC_LOGIN_010_uppercase_username")
