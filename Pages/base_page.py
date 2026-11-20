
from pathlib import Path
from datetime import datetime

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    # Cliquer sur un élément
    def click(self, locator):
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()

    # Saisir du texte dans un champ
    def type(self, locator, text):
        element = self.wait.until(EC.visibility_of_element_located(locator))
        element.clear()
        element.send_keys(text)

    # Récupérer le texte d'un élément
    def get_text(self, locator):
        element = self.wait.until(EC.visibility_of_element_located(locator))
        return element.text

    # Vérifier si un élément est affiché
    def is_displayed(self, locator):
        element = self.wait.until(EC.visibility_of_element_located(locator))
        return element.is_displayed()

    # Rechercher un élément
    def find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    # Récupérer la valeur d'un champ
    def get_field_value(self, locator):
        element = self.wait.until(EC.visibility_of_element_located(locator))
        return element.get_attribute("value")

    def take_screenshot(self, name):

        folder = (Path(__file__).resolve().parent.parent/ "screenshots")
        folder.mkdir(parents=True,exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = folder / f"{name}_{timestamp}.png"
        success = self.driver.save_screenshot(str(filename))

        if not success:
            raise RuntimeError(f"Impossible d'enregistrer le screenshot : {filename}")
        print(f"\nScreenshot saved: {filename}")
        return str(filename)
