
import re
from pathlib import Path
from datetime import datetime

import pytest
from selenium import webdriver


BASE_URL = ("https://parabank.parasoft.com/parabank/index.htm")

@pytest.fixture
def driver():
    browser = webdriver.Chrome()
    browser.maximize_window()
    browser.get(BASE_URL)
    yield browser
    browser.quit()

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        browser = item.funcargs.get("driver")
        if browser is None:
            return
        folder = (Path(__file__).resolve().parent/ "screenshots")
        folder.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        safe_name = re.sub(r"[^a-zA-Z0-9_-]","_",item.name)
        filename = folder / (f"FAILED_{safe_name}_{timestamp}.png")
        try:
            browser.save_screenshot(str(filename))
            print(f"\nFailure screenshot: {filename}")
        except Exception as error:
            print(f"Screenshot error: {error}")
