from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import time

# Setup Edge WebDriver
options = Options()
options.add_argument("--start-maximized")
service = Service(r"E:\downloads\edgedriver_win64 (1)\msedgedriver.exe")  # Replace with the actual path to msedgedriver.exe
driver = webdriver.Edge(service=service, options=options)

# Base URL of the application
BASE_URL = "http://127.0.0.1:8000"

def handle_alert():
    """Handle JavaScript alert pop-ups."""
    try:
        alert = driver.switch_to.alert
        print("Alert text:", alert.text)  # Print the alert text for debugging
        alert.accept()  # Accept the alert
        time.sleep(1)  # Wait for the alert to close
    except Exception as e:
        print("No alert found:", e)

def test_user_login_invalid():
    """Test User Login with Invalid Credentials"""
    driver.get(f"{BASE_URL}/login")
    time.sleep(2)  # Wait for the page to load
    driver.find_element(By.NAME, "username").send_keys("invaliduser")
    time.sleep(1)  # Slow down typing
    driver.find_element(By.NAME, "password").send_keys("invalidpassword")
    time.sleep(1)  # Slow down typing
    driver.find_element(By.XPATH, "//button[text()='Login']").click()
    time.sleep(2)  # Wait for the page to load
    assert "Invalid username or password" in driver.page_source, "Invalid User Login Test Failed"
    print("Invalid User Login Test Passed")

def test_admin_login_invalid():
    """Test Admin Login with Invalid Credentials"""
    driver.get(f"{BASE_URL}/admin-login")
    time.sleep(2)  # Wait for the page to load
    driver.find_element(By.NAME, "username").send_keys("wrongadmin")
    time.sleep(1)  # Slow down typing
    driver.find_element(By.NAME, "password").send_keys("wrongpassword")
    time.sleep(1)  # Slow down typing
    driver.find_element(By.XPATH, "//button[text()='Login']").click()
    time.sleep(2)  # Wait for the page to load
    assert "Invalid admin credentials" in driver.page_source, "Invalid Admin Login Test Failed"
    print("Invalid Admin Login Test Passed")

def test_user_login():
    """Test User Login Functionality"""
    driver.get(f"{BASE_URL}/login")
    time.sleep(2)  # Wait for the page to load
    driver.find_element(By.NAME, "username").send_keys("sudeepa")
    time.sleep(1)  # Slow down typing
    driver.find_element(By.NAME, "password").send_keys("sudeepa123")
    time.sleep(1)  # Slow down typing
    driver.find_element(By.XPATH, "//button[text()='Login']").click()
    time.sleep(2)  # Wait for the page to load
    handle_alert()  # Handle the login success alert
    print("Current URL:", driver.current_url)
    print(driver.page_source)
    assert "Dashboard" in driver.page_source, "User Login Failed"
    print("User Login Test Passed")

def test_admin_login():
    """Test Admin Login Functionality"""
    driver.get(f"{BASE_URL}/admin-login")
    time.sleep(2)  # Wait for the page to load
    driver.find_element(By.NAME, "username").send_keys("admin")
    time.sleep(1)  # Slow down typing
    driver.find_element(By.NAME, "password").send_keys("admin123")
    time.sleep(1)  # Slow down typing
    driver.find_element(By.XPATH, "//button[text()='Login']").click()
    time.sleep(2)  # Wait for the page to load
    handle_alert()  # Handle the admin login success alert
    print(driver.page_source)
    print(driver.current_url)
    assert "Admin Dashboard" in driver.page_source, "Admin Login Failed"
    print("Admin Login Test Passed")

def test_add_to_wishlist():
    """Test Adding a Book to Wishlist"""
    driver.get(f"{BASE_URL}/book/1")  # Replace with a valid book ID
    time.sleep(2)  # Wait for the page to load
    driver.find_element(By.XPATH, "//button[text()='Add to Wishlist']").click()
    time.sleep(2)  # Wait for the page to reload
    handle_alert()  # Handle the add to wishlist success alert
    print(driver.page_source)
    print(driver.current_url)
    assert "Added to wishlist!" in driver.page_source, "Add to Wishlist Failed"
    print("Add to Wishlist Test Passed")

def test_remove_from_wishlist():
    """Test Removing a Book from Wishlist"""
    driver.get(f"{BASE_URL}/wishlist")
    time.sleep(2)  # Wait for the page to load
    remove_buttons = driver.find_elements(By.XPATH, "//form[contains(@action, '/wishlist/remove')]/button")
    if remove_buttons:
        remove_buttons[0].click()
        time.sleep(2)  # Wait for the page to reload
        handle_alert()  # Handle the remove from wishlist success alert
        print(driver.page_source)
        print(driver.current_url)
        assert "Your wishlist is empty." in driver.page_source or len(remove_buttons) - 1 == len(driver.find_elements(By.XPATH, "//form[contains(@action, '/wishlist/remove')]/button")), "Remove from Wishlist Failed"
        print("Remove from Wishlist Test Passed")
    else:
        print("No books in wishlist to remove. Skipping Remove from Wishlist Test.")

def test_user_logout():
    """Test User Logout Functionality"""
    driver.get(f"{BASE_URL}/logout")
    time.sleep(2)  # Wait for the page to load
    handle_alert()  # Handle the logout success alert
    print(driver.page_source)
    print(driver.current_url)
    assert "Login" in driver.page_source, "Logout Failed"
    print("User Logout Test Passed")

# Run all tests
try:
    test_user_login_invalid()
    test_admin_login_invalid()
    test_user_login()
    test_admin_login()
    test_add_to_wishlist()
    test_remove_from_wishlist()
    test_user_logout()
    print("\nRAN ALL 7 TESTS SUCCESSFULLY")
finally:
    driver.quit()