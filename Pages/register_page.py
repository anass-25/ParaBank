
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def is_registration_successful(self):

    try:
        title = WebDriverWait(self.driver, 15).until(
            EC.visibility_of_element_located(
                self.WELCOME_TITLE
            )
        )

        return "Welcome" in title.text

    except Exception as e:
        print("Registration verification failed:", e)
        return False

from Pages.base_page import BasePage


class RegisterPage(BasePage):

    # Localisateurs du formulaire
    FIRST_NAME = (By.NAME, "customer.firstName")
    LAST_NAME = (By.NAME, "customer.lastName")
    ADDRESS = (By.NAME, "customer.address.street")
    CITY = (By.NAME, "customer.address.city")
    STATE = (By.NAME, "customer.address.state")
    ZIP_CODE = (By.NAME, "customer.address.zipCode")
    PHONE = (By.NAME, "customer.phoneNumber")
    SSN = (By.NAME, "customer.ssn")
    USERNAME = (By.NAME, "customer.username")
    PASSWORD = (By.NAME, "customer.password")
    CONFIRM = (By.NAME, "repeatedPassword")

    # Boutons et liens
    REGISTER_BUTTON = (By.CSS_SELECTOR, "input[value='Register']")
    REGISTER_LINK = (By.LINK_TEXT, "Register")

    # Messages d'erreur
    FIRST_NAME_ERROR = (By.ID, "customer.firstName.errors")
    LAST_NAME_ERROR = (By.ID, "customer.lastName.errors")
    ADDRESS_ERROR = (By.ID, "customer.address.street.errors")
    CITY_ERROR = (By.ID, "customer.address.city.errors")
    STATE_ERROR = (By.ID, "customer.address.state.errors")
    ZIP_CODE_ERROR = (By.ID, "customer.address.zipCode.errors")
    SSN_ERROR = (By.ID, "customer.ssn.errors")
    USERNAME_ERROR = (By.ID, "customer.username.errors")
    PASSWORD_ERROR = (By.ID, "customer.password.errors")
    CONFIRM_ERROR = (By.ID, "repeatedPassword.errors")

    # Message de bienvenue
    WELCOME_TITLE = (By.CSS_SELECTOR, "#rightPanel h1")

    # Déconnexion
    LOGOUT_LINK = (By.LINK_TEXT, "Log Out")

    # Accéder à la page d'inscription
    def registrePage(self):
        self.click(self.REGISTER_LINK)

    # Cliquer sur le bouton Register
    def click_register(self):
        self.click(self.REGISTER_BUTTON)

    # Remplir le formulaire
    def fill_register(self,first_name,last_name,address,city,state,zip_code,phone,ssn,username,password):
        self.type(self.FIRST_NAME, first_name)
        self.type(self.LAST_NAME, last_name)
        self.type(self.ADDRESS, address)
        self.type(self.CITY, city)
        self.type(self.STATE, state)
        self.type(self.ZIP_CODE, zip_code)
        self.type(self.PHONE, phone)
        self.type(self.SSN, ssn)
        self.type(self.USERNAME, username)
        self.type(self.PASSWORD, password)
        self.type(self.CONFIRM, password)

    # Récupérer les erreurs des champs obligatoires
    def get_required_field_errors(self):
        return {
            "first_name": self.get_text(self.FIRST_NAME_ERROR),
            "last_name": self.get_text(self.LAST_NAME_ERROR),
            "address": self.get_text(self.ADDRESS_ERROR),
            "city": self.get_text(self.CITY_ERROR),
            "state": self.get_text(self.STATE_ERROR),
            "zip_code": self.get_text(self.ZIP_CODE_ERROR),
            "ssn": self.get_text(self.SSN_ERROR),
            "username": self.get_text(self.USERNAME_ERROR),
            "password": self.get_text(self.PASSWORD_ERROR)
        }

    # Récupérer l'erreur du nom d'utilisateur
    def get_username_error(self):
        return self.get_text(self.USERNAME_ERROR)

    # Modifier la confirmation du mot de passe
    def enter_confirm_password(self, password):
        self.type(self.CONFIRM, password)

    # Récupérer l'erreur de confirmation
    def get_confirm_password_error(self):
        return self.get_text(self.CONFIRM_ERROR)

    # Vérifier le succès de l'inscription
    def is_registration_successful(self):

        try:
            title = WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located(
                    self.WELCOME_TITLE
                )
            )

            return "Welcome" in title.text

        except Exception as e:
            print("Registration verification failed:", e)
            return False

    # Déconnexion
    def logout(self):
        self.click(self.LOGOUT_LINK)

    # Inscription complète
    def register_user(self,first_name,last_name,address,city,state,zip_code,phone,ssn,username,password):
        self.fill_register(first_name,last_name,address,city,state,zip_code,phone,ssn,username,password)
        self.click_register()
