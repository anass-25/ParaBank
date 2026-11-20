
import uuid
import pytest

from selenium.webdriver.support import expected_conditions as EC
from Pages.register_page import RegisterPage


REGISTER_URL = ("https://parabank.parasoft.com/parabank/register.htm")

def generate_username():
    return "user_" + uuid.uuid4().hex[:10]

def fill_valid_form(page, username):
    page.fill_register(first_name="John",last_name="Smith",address="123 Main Street",city="New York",state="NY",zip_code="10001",phone="1234567890",ssn="123456789",username=username,password="Test@12345")

# TC_REG_001 - Inscription valide
def test_register_valid_user(driver):
    driver.get(REGISTER_URL)
    page = RegisterPage(driver)
    fill_valid_form(page, generate_username())
    page.click_register()
    assert page.is_registration_successful()
    page.take_screenshot("TC_REG_001_success")

# TC_REG_002 - Tous les champs vides
def test_register_empty_fields(driver):
    driver.get(REGISTER_URL)
    page = RegisterPage(driver)
    page.click_register()
    errors = page.get_required_field_errors()
    assert "First name is required." in errors["first_name"]
    assert "Last name is required." in errors["last_name"]
    assert "Address is required." in errors["address"]
    assert "City is required." in errors["city"]
    assert "State is required." in errors["state"]
    assert "Zip Code is required." in errors["zip_code"]
    assert "Social Security Number is required." in errors["ssn"]
    assert "Username is required." in errors["username"]
    assert "Password is required." in errors["password"]
    page.take_screenshot("TC_REG_002_empty_fields")


# TC_REG_003 - Username déjà existant
def test_register_existing_username(driver):
    driver.get(REGISTER_URL)
    page = RegisterPage(driver)
    username = generate_username()
    fill_valid_form(page, username)
    page.click_register()
    assert page.is_registration_successful()
    page.logout()
    driver.get(REGISTER_URL)
    fill_valid_form(page, username)
    page.click_register()
    error = page.get_username_error()
    assert "This username already exists" in error
    page.take_screenshot("TC_REG_003_duplicate_username")


# TC_REG_004 - Mots de passe différents
def test_register_password_mismatch(driver):
    driver.get(REGISTER_URL)
    page = RegisterPage(driver)
    fill_valid_form(page, generate_username())
    page.enter_confirm_password("DifferentPassword123")
    page.click_register()
    error = page.get_confirm_password_error()
    assert "Passwords did not match" in error
    page.take_screenshot("TC_REG_004_password_mismatch")


# TC_REG_005 - Prénom vide
def test_register_empty_first_name(driver):
    driver.get(REGISTER_URL)
    page = RegisterPage(driver)
    fill_valid_form(page, generate_username())
    page.type(page.FIRST_NAME, "")
    page.click_register()
    error = page.get_text(page.FIRST_NAME_ERROR)
    assert "First name is required." in error
    page.take_screenshot("TC_REG_005_first_name_error")


# TC_REG_006 - Nom vide
def test_register_empty_last_name(driver):
    driver.get(REGISTER_URL)
    page = RegisterPage(driver)
    fill_valid_form(page, generate_username())
    page.type(page.LAST_NAME, "")
    page.click_register()
    error = page.get_text(page.LAST_NAME_ERROR)
    assert "Last name is required." in error
    page.take_screenshot("TC_REG_006_last_name_error")


# TC_REG_007 - SSN vide
def test_register_empty_ssn(driver):
    driver.get(REGISTER_URL)
    page = RegisterPage(driver)
    fill_valid_form(page, generate_username())
    page.type(page.SSN, "")
    page.click_register()
    error = page.get_text(page.SSN_ERROR)
    assert "Social Security Number is required." in error
    page.take_screenshot("TC_REG_007_ssn_error")


# TC_REG_008 - Mot de passe vide
def test_register_empty_password(driver):
    driver.get(REGISTER_URL)
    page = RegisterPage(driver)
    fill_valid_form(page, generate_username())
    page.type(page.PASSWORD, "")
    page.type(page.CONFIRM, "")
    page.click_register()
    error = page.get_text(page.PASSWORD_ERROR)
    assert "Password is required." in error
    page.take_screenshot("TC_REG_008_password_error")


# TC_REG_009 - Caractères spéciaux
@pytest.mark.parametrize(
    "special_input",
    [
        "<script>alert('XSS')</script>",
        "' OR '1'='1",
        "<img src=x onerror=alert(1)>"
    ],
    ids=["script", "sql_text", "img"]
)
def test_register_special_characters(driver, special_input):
    driver.get(REGISTER_URL)
    page = RegisterPage(driver)
    fill_valid_form(page, generate_username())
    page.type(page.FIRST_NAME, special_input)
    page.click_register()
    assert not EC.alert_is_present()(driver)
    assert "HTTP Status 500" not in driver.page_source
    safe_id = {
        "<script>alert('XSS')</script>": "script",
        "' OR '1'='1": "sql_text",
        "<img src=x onerror=alert(1)>": "img"
    }[special_input]
    page.take_screenshot(f"TC_REG_009_special_characters_{safe_id}")


# TC_REG_010 - Username unique
def test_register_unique_username(driver):
    driver.get(REGISTER_URL)
    page = RegisterPage(driver)
    username = generate_username()
    fill_valid_form(page, username)
    actual_username = page.get_field_value(page.USERNAME)
    assert actual_username == username
    page.click_register()
    assert page.is_registration_successful()
    welcome = page.get_text(page.WELCOME_TITLE)
    assert username in welcome
    page.take_screenshot("TC_REG_010_unique_username")
