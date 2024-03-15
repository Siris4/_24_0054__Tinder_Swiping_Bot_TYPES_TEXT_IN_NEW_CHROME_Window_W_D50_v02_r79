from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import os
import time

# constants
# EnvVarMaster =

email = os.environ.get('email', 'Email does not exist')
gmail_password = os.environ.get('gmail_password', 'Password does not exist')

# function to log messages
def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{timestamp} - {message}")


def init_driver():
    chrome_options = Options()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    log_message("webdriver initialized.")
    return driver


def click_element(driver, by, value, description):
    try:
        element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((by, value)))
        log_message(f"Attempting to click {description}.")
        element.click()
        log_message(f"{description} clicked successfully.")
        return True
    except TimeoutException:
        log_message(f"{description} not clickable or not found.")
        return False
    except Exception as e:
        log_message(f"An error occurred while clicking {description}: {e}")
        return False


def switch_to_new_window(driver):
    main_window = driver.current_window_handle
    WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
    new_window = [window for window in driver.window_handles if window != main_window][0]
    driver.switch_to.window(new_window)
    log_message("Switched to new window.")
    return main_window


def enter_email_at_cursor(driver, email):
    try:
        main_window = switch_to_new_window(driver)

        log_message("Locating the email input field...")
        WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
        )

        email_input = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
        log_message(f"Email field located, attempting to enter email: {email}")

        email_input.clear()
        email_input.send_keys(email, Keys.ENTER)

        WebDriverWait(driver, 20).until(
            lambda d: email_input.get_attribute('value') == email
        )

        entered_text = email_input.get_attribute('value')
        log_message(f"Entered text verified: {entered_text}")

        email_input.send_keys(email, Keys.ENTER)

        time.sleep(3)

        email_input.clear()
        email_input.send_keys(gmail_password, Keys.ENTER)

        driver.switch_to.window(main_window)
        log_message("Switched back to the main window.")

        return entered_text == email
    except Exception as e:
        driver.switch_to.window(main_window)  # switches back to main window where Tinder is at
        log_message(f"Failed to enter and verify email: {e}")
        return False


def login_sequence(driver):
    if click_element(driver, By.XPATH, "//div[contains(text(), 'I decline')]", "decline button"):
        log_message("Decline button found and clicked.")
    else:
        log_message("Decline button not found, proceeding with login.")

    if click_element(driver, By.CLASS_NAME, "l17p5q9z", "main login button"):
        if click_element(driver, By.XPATH, "//span[contains(text(), 'English')]", "english language option"):
            click_element(driver, By.CSS_SELECTOR, "a[href*='tinder.onelink.me'] div.l17p5q9z",
                          "additional login button")
            if click_element(driver, By.CSS_SELECTOR, "span.nsm7Bb-HzV7m-LgbsSe-BPrWId", "continue with google button"):
                enter_email_at_cursor(driver, email)


def main():
    driver = init_driver()
    driver.get("https://tinder.com/")
    log_message("navigated to tinder's login page.")

    login_sequence(driver)

    input("press enter to exit...\n")
    driver.quit()


if __name__ == "__main__":
    main()
