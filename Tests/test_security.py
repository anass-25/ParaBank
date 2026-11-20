

from Pages.security_page import SecurityPage
from Tests.test_transfer import login_user


def test_logout(driver):

    login_user(driver)
    security = SecurityPage(driver)
    security.logout()
    security.take_screenshot("TC_SEC_001_logout")
    assert security.is_login_form_visible(), ("BUG: Login form not visible after logout")
    assert not security.is_authenticated(), ("BUG: User still authenticated after logout")


def test_access_after_logout(driver):

    login_user(driver)
    security = SecurityPage(driver)
    security.logout()
    security.open_accounts_directly()
    security.take_screenshot("TC_SEC_002_access_after_logout")
    assert not security.private_account_data_visible(), ("SECURITY BUG: Account data accessible ""after logout")
    assert not security.is_authenticated(), ("SECURITY BUG: Session still active")


def test_browser_back_after_logout(driver):

    login_user(driver)
    security = SecurityPage(driver)
    security.open_accounts_directly()
    security.logout()
    assert security.is_login_form_visible(), ("BUG: Login form not visible after logout")
    driver.back()
    data_visible_after_back = (security.private_account_data_visible())
    print("Private data visible after Back:",data_visible_after_back)
    security.take_screenshot("TC_SEC_003_after_back")
    driver.refresh()
    data_visible_after_refresh = (security.private_account_data_visible())
    print("Private data visible after Refresh:",data_visible_after_refresh)
    security.take_screenshot("TC_SEC_003_after_refresh")
    assert not data_visible_after_back, (
        "SECURITY BUG: Private account data "
        "visible after browser back. "
        f"Visible after refresh: "
        f"{data_visible_after_refresh}"
    )

    assert not data_visible_after_refresh, (
        "SECURITY BUG: Private account data "
        "accessible after refresh"
    )

def test_other_customer_account_access(driver):

    login_user(driver)
    security = SecurityPage(driver)
    account_id = security.get_first_account_id()
    print("Customer A account:", account_id)
    security.logout()
    login_user(driver)
    security.open_account_details(account_id)
    security.take_screenshot("TC_SEC_004_other_customer")
    assert not security.account_details_visible(account_id), ("SECURITY BUG: Customer B can access " "Customer A account details")

def test_sql_injection_login(driver):

    security = SecurityPage(driver)
    payload = "' OR '1'='1"
    security.login(username=payload,password="invalid_password")
    security.take_screenshot("TC_SEC_005_sql_injection")
    assert not security.is_authenticated(), ("SECURITY BUG: Authentication bypass ""with SQL injection payload")


def test_xss_input(driver):

    security = SecurityPage(driver)
    payload = (
        "<script>"
        "window.__xss_test = true"
        "</script>"
    )
    entered_value = security.test_xss_payload(payload)
    security.take_screenshot("TC_SEC_006_xss_input")
    assert entered_value == payload, ("XSS payload was not entered correctly")
    assert driver.execute_script("return window.__xss_test === undefined"), ("SECURITY BUG: XSS payload executed")
