
from Pages.profile_page import ProfilePage
from Tests.test_transfer import login_user



def test_update_address(driver):

    login_user(driver)
    profile = ProfilePage(driver)
    profile.open_profile_page()
    profile.fill_required_fields()
    new_address = "456 New Street"
    profile.update_fields(address=new_address)
    profile.submit()
    profile.take_screenshot("TC_PROF_001_update_address")
    assert profile.is_update_successful(), ("BUG: Profile update was not confirmed")
    profile.open_profile_page()
    actual_address = profile.get_field(profile.ADDRESS)
    assert actual_address == new_address, (f"BUG: Expected {new_address}, "f"got {actual_address}")


def test_update_city_and_state(driver):

    login_user(driver)
    profile = ProfilePage(driver)
    profile.open_profile_page()
    profile.fill_required_fields()
    new_city = "Boston"
    new_state = "MA"
    profile.update_fields(city=new_city,state=new_state)
    profile.submit()
    profile.take_screenshot("TC_PROF_002_city_state")
    assert profile.is_update_successful(), ("BUG: Profile update was not confirmed")
    profile.open_profile_page()
    actual_city = profile.get_field(profile.CITY)
    actual_state = profile.get_field(profile.STATE)
    assert actual_city == new_city, (f"BUG: Expected {new_city}, got {actual_city}")
    assert actual_state == new_state, (f"BUG: Expected {new_state}, got {actual_state}")


def test_update_phone(driver):

    login_user(driver)
    profile = ProfilePage(driver)
    profile.open_profile_page()
    profile.fill_required_fields()
    new_phone = "5551234567"
    profile.update_fields(phone=new_phone)
    profile.submit()
    profile.take_screenshot("TC_PROF_003_update_phone")
    assert profile.is_update_successful(), ("BUG: Profile update was not confirmed")
    profile.open_profile_page()
    actual_phone = profile.get_field(profile.PHONE)
    assert actual_phone == new_phone, (f"BUG: Expected {new_phone}, got {actual_phone}")


def test_empty_required_fields(driver):

    login_user(driver)
    profile = ProfilePage(driver)
    profile.open_profile_page()
    profile.update_fields(
        first_name="",
        last_name="",
        address="",
        city="",
        state="",
        zip_code=""
    )
    profile.submit()
    errors = profile.get_errors()
    print("Validation errors:", errors)
    profile.take_screenshot("TC_PROF_004_empty_required")
    assert errors, ("BUG: No validation messages displayed ""for empty required fields")
    assert not profile.is_update_successful(), ("BUG: Empty required fields were accepted")


def test_profile_persistence_after_refresh(driver):

    login_user(driver)
    profile = ProfilePage(driver)
    profile.open_profile_page()
    profile.fill_required_fields()
    new_address = "789 Test Avenue"
    new_city = "Chicago"
    new_state = "IL"
    profile.update_fields(
        address=new_address,
        city=new_city,
        state=new_state
    )
    profile.submit()
    profile.take_screenshot("TC_PROF_005_after_update")
    assert profile.is_update_successful(), ("BUG: Profile update was not confirmed")
    profile.open_profile_page()
    profile.refresh_profile()
    actual_address = profile.get_field(profile.ADDRESS)
    actual_city = profile.get_field(profile.CITY)
    actual_state = profile.get_field(profile.STATE)
    profile.take_screenshot("TC_PROF_005_persistence")
    assert actual_address == new_address, (
        f"BUG: Address was not persisted. "
        f"Expected {new_address}, got {actual_address}"
    )
    assert actual_city == new_city, (
        f"BUG: City was not persisted. "
        f"Expected {new_city}, got {actual_city}"
    )
    assert actual_state == new_state, (
        f"BUG: State was not persisted. "
        f"Expected {new_state}, got {actual_state}"
    )
