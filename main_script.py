import os
import random
import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException

# Get current Windows username
windows_username = os.getlogin()

def get_profile_number():
    profile_file = "desk/C_Profile_Number.txt"
    try:
        with open(profile_file, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Profile number file not found at {profile_file}")
        return "1"  # Default to Profile 1

profile_number = get_profile_number()

def get_script_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

SCRIPT_DIR = get_script_dir()
AUTH_TOKENS_FILE = os.path.join(SCRIPT_DIR, "desk/Xauth.txt")
USED_TOKENS_FILE = os.path.join(SCRIPT_DIR, "desk/used_auth.txt")
TARGET_URL = "https://x.com"

# Define paths
chromedriver_paths = [r"desk\chromedriver.exe"]
chrome_profiles = [fr"C:\Users\{windows_username}\AppData\Local\Google\Chrome\User Data\Profile {profile_number}"]

def read_url_from_file(file_path):
    try:
        with open(file_path, "r") as file:
            return file.read().strip()
    except Exception as e:
        print(f"Error reading URL from file: {e}")
        return None

def read_key_from_file(file_path):
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
            return lines[0].strip(), lines[1:] if lines else (None, [])
    except Exception as e:
        print(f"Error reading key from file: {e}")
        return None, []

def unlock_wallet(browser):
    try:
        print("Attempting to unlock wallet...")
        input_field = WebDriverWait(browser, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Password']"))
        )
        input_field.clear()
        input_field.send_keys("Aixfly@1122")
        print("Wallet password entered.")

        # Find the button with data-testid='unlock-button' and click it
        button = WebDriverWait(browser, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='unlock-button']"))
        )
        button.click()
        print("Wallet unlock button clicked.")
        return True
    except Exception as e:
        print(f"Wallet unlock failed or not needed: {e}")
        return False

def wait_for_wallet_unlocked(browser, timeout=30):
    try:
        print("Waiting for wallet unlock confirmation...")
        # Wait for an element with data-testid="header-link-copy"
        header_link_xpath = '//*[@data-testid="header-link-copy"]'
        WebDriverWait(browser, timeout).until(
            EC.visibility_of_element_located((By.XPATH, header_link_xpath)))
        print("Wallet unlocked successfully.")
        return True
    except Exception as e:
        print(f"Wallet unlock confirmation not detected: {e}")
        return False

def import_wallet_key(browser):
    try:
        print("Starting wallet key import process...")
        import_url = "chrome-extension://opfgelmcmbiajamepnmloijbpoleiama/popup.html#/import/pkey?onboarding=true"
        browser.get(import_url)
        print("Navigated to import page.")

        input_field = WebDriverWait(browser, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@data-testid='private-key-input']")))

        key_file = "desk/Wallet_Privet_key.txt"
        active_key_file = "desk/Import_key_wallet.txt"
        key, remaining_keys = read_key_from_file(key_file)
        
        if not key:
            print("No key found in Wallet_Privet_key")
            return False

        input_field.clear()
        input_field.send_keys(key)
        print(f"Wallet key entered: {key[:5]}...{key[-5:]}")

        # Save the active key
        with open(active_key_file, "a") as akf:
            akf.write(key + "\n")
        # Update key file
        with open(key_file, "w") as kf:
            kf.writelines(remaining_keys)

        import_btn = WebDriverWait(browser, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='import-wallets-button']")))
        import_btn.click()
        print("Import button clicked.")

        # Verify successful import by checking for "Rainbow is ready to use" text
        WebDriverWait(browser, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Rainbow is ready to use')]")))
        print("Wallet import confirmed: Rainbow is ready to use.")
        return True
    except Exception as e:
        print(f"Wallet key import failed: {e}")
        return False

def twitter_login_with_cookie(driver, auth_token):
    print("Attempting Twitter login with auth token...")
    
    if not auth_token:
        print("No auth token provided")
        return False

    try:
        # Navigate to Twitter
        driver.get(TARGET_URL)
        
        # Set auth token cookie
        script = f"""
        document.cookie = "auth_token={auth_token}; path=/; domain=.x.com; secure";
        location.reload();
        """
        driver.execute_script(script)
        
        # Verify login
        home_xpath = "//a[@href='/home']"
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, home_xpath)))
        print("Twitter login successful.")
        return True
    except Exception as e:
        print(f"Twitter login failed: {e}")
        return False

def complete_developer_portal(driver):
    print("Starting developer portal process...")
    try:
        dev_portal_url = "https://developer.x.com/en/portal/petition/essential/basic-info"
        driver.get(dev_portal_url)
        print(f"Navigated to developer portal: {dev_portal_url}")
        
        # Wait until the first button is available, then click it instantly
        first_button_xpath = "/html/body/div/div/div/div[2]/div/div[3]/button"
        WebDriverWait(driver, 2000).until(
            EC.element_to_be_clickable((By.XPATH, first_button_xpath))
        ).click()
        print("Clicked first button")
        
   #     # Wait until the second element is available, then click it instantly
   #     second_element_xpath = "/html/body/div[1]/div/div/div[2]/div/div[3]/button"
   #     second_element = WebDriverWait(driver, 2000).until(
   #         EC.element_to_be_clickable((By.XPATH, second_element_xpath))
   #     )
   #     second_element.click()
   #     print("Clicked second element")
        
        # Fill textarea instantly when available
        textarea = WebDriverWait(driver, 2000).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/div[2]/div/form/div[3]/textarea")))
        random_paragraph = generate_random_paragraph()
        textarea.clear()
        textarea.send_keys(random_paragraph)
        print("Textarea filled with random text")
        
        # Check all required checkboxes by their input IDs
        checkbox_ids = [
            "feather-form-field-text-5",
            "feather-form-field-text-6",
            "feather-form-field-text-7"
        ]

        for checkbox_id in checkbox_ids:
            try:
                checkbox = WebDriverWait(driver, 1000).until(
                    EC.element_to_be_clickable((By.ID, checkbox_id)))
                driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                time.sleep(0.5)
                if not checkbox.is_selected():
                    checkbox.click()
                print(f"Checkbox with id {checkbox_id} checked")
            except Exception as e:
                print(f"Failed to check checkbox with id {checkbox_id}: {e}")
                return False

        # Submit form
        submit_button = WebDriverWait(driver, 2000).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/div[2]/div/form/div[7]/button[2]")))
        submit_button.click()
        print("Form submitted")
        
        # Verify submission
        try:
            WebDriverWait(driver, 2000).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'success') or contains(text(), 'thank you')]")))
            print("Form submission verified")
            # After successful form submission, complete the developer flow
            if complete_developer_flow(driver):
                return True
            else:
                print("Developer flow completion failed")
                return False
        except:
            print("Form submission might have worked but couldn't verify success message")
            return False
            
    except Exception as e:
        print(f"Developer portal process failed: {str(e)}")
        return False










def complete_developer_flow(driver):
    try:
        print("Starting developer flow completion process...")
        
        # Click on "Projects & Apps" button
        projects_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div/div/div[2]/div[2]/div/div/div/div[2]/a[1]/div/div/span"))
        )
        projects_button.click()
        print("Clicked on Projects Settings")
        
        # Click on "Create App" button
        create_app_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/div[2]/div[2]/div[2]/div[1]/div/div/div[4]/div/div/div/button"))
        )
        create_app_button.click()
        print("Clicked on Setup")
        


        
        # Input first URL
        try:
            input_field1 = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[1]/div/div/div[5]/form/div[2]/input"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", input_field1)
            input_field1.clear()
            input_field1.send_keys("https://dapp.uxlink.io/")
            print("Entered first URL")
        except Exception as e:
            print(f"Could not find first URL input field: {e}")
            return False
        
        # Input second URL
        try:
            input_field2 = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[1]/div/div/div[5]/form/div[1]/div[2]/input"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", input_field2)
            input_field2.clear()
            input_field2.send_keys("https://dapp.uxlink.io/authGateway")
            print("Entered second URL")
        except Exception as e:
            print(f"Could not find second URL input field: {e}")
            return False
        
        # Click on Website checkbox
        try:
            website_checkbox = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[1]/div/div/div[4]/form/div/div[1]/div[1]/span"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", website_checkbox)
            website_checkbox.click()
            print("Clicked Clicked Native App Checkbox")
        except Exception as e:
            print(f"Could not find Clicked Native App Checkbox: {e}")
            return False
        
        # Click Save button
        try:
            save_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[1]/div/div/div[6]/button[2]"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", save_button)
            save_button.click()
            print("Clicked Save button")
            
            # Verify save was successful
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'success') or contains(text(), 'saved')]"))
                )
                print("Settings saved successfully")
            except:
                print("Settings might have saved but couldn't verify success message")
                
        except Exception as e:
            print(f"Could not find Save button: {e}")
            return False

        # Extract Client ID
        client_id_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/p"))
        )
        client_id = client_id_element.text.strip()
        
        # Extract Client Secret
        client_secret_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[1]/div/div/div/div[2]/div[2]/div[2]/p"))
        )
        client_secret = client_secret_element.text.strip()
        
        print(f"Extracted Client ID: {client_id}")
        print(f"Extracted Client Secret: {client_secret}")
        
        # Save to key.txt
        with open(os.path.join(SCRIPT_DIR, "desk/Client_Secret.txt"), "a") as key_file:
            key_file.write(f"{client_id} {client_secret}\n")
        print("Saved Client ID and Secret to Client_Secret.txt")
        
        # Click Done button
        done_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[1]/div/div/div/div[3]/button"))
        )
        done_button.click()
        print("Clicked Done button")
        
        # Click "Yes, I saved it" button using JavaScript when available
        try:
            WebDriverWait(driver, 30).until(
            lambda d: d.execute_script(
                "return document.querySelector('body > div.DialogModal.Modal > div > div > div.Panel-footer > div > button') !== null"
            )
            )
            driver.execute_script(
                "document.querySelector('body > div.DialogModal.Modal > div > div > div.Panel-footer > div > button').click()"
            )
            print('Clicked "Yes, I saved it" button using JavaScript')
            # After clicking, open URL from desk/refer.txt in the same tab
            refer_file = os.path.join("desk", "Uxlink_Refer_Url.txt")
            refer_url = read_url_from_file(refer_file)
            if refer_url:
                print(f"Opening refer URL: {refer_url}")
                driver.get(refer_url)
                try:
                    # Wait for the specific element to appear using the provided XPath
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "/html/body/div/div/div[2]/div[4]/div[1]/section[1]/div")
                        )
                    )
                    print("Verification element found, clicking the target element...")
                    target_xpath = "/html/body/div/div/div[2]/div[1]/div/div/div[2]/div[3]/div"
                    target_element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, target_xpath))
                    )
                    target_element.click()
                    print("Target element clicked.")

                    # Wait for "Connect Wallet" button and click it
                    try:
                        connect_wallet_btn = WebDriverWait(driver, 20).until(
                            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Connect Wallet')]"))
                        )
                        connect_wallet_btn.click()
                        print('"Connect Wallet" button clicked.')
                    except Exception as e:
                        print(f'"Connect Wallet" button not found or click failed: {e}')

                    # Wait for "Rainbow" option and click it
                    try:
                        # Try to click the Rainbow button using JavaScript (shadow DOM)
                        rainbow_clicked = False
                        try:
                            js_code = """
                            const button = document
                              .querySelector("body > w3m-modal")
                              ?.shadowRoot?.querySelector("wui-flex > wui-card > w3m-router")
                              ?.shadowRoot?.querySelector("div > w3m-connect-view")
                              ?.shadowRoot?.querySelector("wui-flex > wui-list-wallet:nth-child(3)")
                              ?.shadowRoot?.querySelector("button");
                            if (button && button.innerText.includes("Rainbow")) {
                              button.click();
                              return true;
                            } else {
                              return false;
                            }
                            """
                            for _ in range(10):
                                result = driver.execute_script(js_code)
                                if result:
                                    print('"Rainbow" option clicked via JS.')
                                    rainbow_clicked = True
                                    break
                                time.sleep(1)
                            if not rainbow_clicked:
                                print('Rainbow button not found via JS!')
                        except Exception as e:
                            print(f'Error clicking Rainbow button via JS: {e}')

                        time.sleep(3)

                        # Open a new tab and switch to it
                        driver.execute_script("window.open('');")
                        driver.switch_to.window(driver.window_handles[-1])
                        print("Opened and switched to new tab.")

                        # Open the extension approval page in the new tab
                        approval_url = "chrome-extension://opfgelmcmbiajamepnmloijbpoleiama/popup.html"
                        driver.get(approval_url)
                        print("Opened approval page in new tab.")

                        # Wait for "Connect to zealy.io" button and click it
                        try:
                            connect_btn_xpath = "//*[contains(text(), 'Connect to UXLINK')]"
                            connect_btn = WebDriverWait(driver, 60).until(
                                EC.element_to_be_clickable((By.XPATH, connect_btn_xpath))
                            )
                            connect_btn.click()
                            print("Clicked 'Connect to Uxlink.")
                        except Exception as e:
                            print(f"'Connect to zealy.io' button not found or not clickable: {e}")

                        # Wait for "Sign" button, reload until available, then click
                        sign_btn_xpath = "/html/body/div/div/div/div/div[2]/div/div[1]/div/div/div/div/div/div[2]/div[2]/div[2]/button"
                        sign_clicked = False
                        max_attempts = 30
                        for attempt in range(max_attempts):
                            try:
                                sign_btn = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, sign_btn_xpath))
                                )
                                sign_btn.click()
                                print("Clicked 'Sign' button.")
                                sign_clicked = True

                                # Wait for the success message to appear
                                success_msg_xpath = "/html/body/div/div/div/div/div[2]/div/div[1]/div/div/div/div[2]"
                                WebDriverWait(driver, 10).until(
                                    EC.visibility_of_element_located((By.XPATH, success_msg_xpath))
                                )
                                print("Success message appeared.")
                                # close the new tab after successful click
                                driver.close()  # Close the new tab
                                # Just switch back to the main tab, do not close the browser
                                driver.switch_to.window(driver.window_handles[0])
                                print("Switched back to main tab.")

                                time.sleep(2)  # Wait for a moment to ensure everything is settled
                                # Wait until /html/body/w3m-modal exists, then remove it and restore scroll
                                try:
                                    WebDriverWait(driver, 10).until(
                                        lambda d: d.execute_script(
                                            "return document.querySelector('body > w3m-modal') !== null"
                                        )
                                    )
                                    # Click the button inside the unsupported chain view in the shadow DOM
                                    js_click = """
                                    try {
                                        let modal = document.querySelector("body > w3m-modal");
                                        if (modal && modal.shadowRoot) {
                                            let router = modal.shadowRoot.querySelector("wui-flex > wui-card > w3m-router");
                                            if (router && router.shadowRoot) {
                                                let unsupported = router.shadowRoot.querySelector("div > w3m-unsupported-chain-view");
                                                if (unsupported && unsupported.shadowRoot) {
                                                    let listItem = unsupported.shadowRoot.querySelector("wui-flex > wui-flex:nth-child(4) > wui-list-item");
                                                    if (listItem && listItem.shadowRoot) {
                                                        let btn = listItem.shadowRoot.querySelector("button");
                                                        if (btn) {
                                                            btn.click();
                                                            return true;
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                        return false;
                                    } catch(e) { return false; }
                                    """
                                    clicked = driver.execute_script(js_click)
                                    if clicked:
                                        print("Clicked system button in unsupported chain view.")
                                    else:
                                        print("System button in unsupported chain view not found or not clickable.")
                                except Exception as e:
                                    print(f"System button in unsupported chain view did not appear or could not be clicked: {e}")


                                # Read Client ID and Client Secret from key.txt (first line)
                                key_file_path = os.path.join(SCRIPT_DIR, "desk/Client_Secret.txt")
                                client_id, client_secret = None, None
                                try:
                                    with open(key_file_path, "r") as f:
                                        lines = [line.strip() for line in f if line.strip()]
                                    if lines:
                                        first_line = lines[0]
                                        parts = first_line.split()
                                        if len(parts) == 2:
                                            client_id, client_secret = parts
                                            # Remove the used line from key.txt
                                            with open(key_file_path, "w") as f:
                                                f.write('\n'.join(lines[1:]) + '\n' if len(lines) > 1 else '')
                                            print(f"Using Client ID: {client_id}, Client Secret: {client_secret}")
                                        else:
                                            print("First line in key.txt does not contain both Client ID and Client Secret.")
                                    else:
                                        print("key.txt is empty.")
                                except Exception as e:
                                    print(f"Error reading or updating Client_Secret.txt: {e}")

                                # Input Client ID and Client Secret into the form fields
                                if client_id and client_secret:
                                    try:
                                        # Input Client ID
                                        client_id_input_xpath = "/html/body/div/div/div[2]/div[4]/div[1]/div/section/div/div/div[2]/div[2]/div[1]/div[2]/div[1]/div/input"
                                        client_id_input = WebDriverWait(driver, 30).until(
                                            EC.element_to_be_clickable((By.XPATH, client_id_input_xpath))
                                        )
                                        client_id_input.clear()
                                        client_id_input.send_keys(client_id)
                                        print("Client ID inputted.")

                                        # Input Client Secret
                                        client_secret_input_xpath = "/html/body/div/div/div[2]/div[4]/div[1]/div/section/div/div/div[2]/div[2]/div[1]/div[2]/div[2]/div/input"
                                        client_secret_input = WebDriverWait(driver, 30).until(
                                            EC.element_to_be_clickable((By.XPATH, client_secret_input_xpath))
                                        )
                                        client_secret_input.clear()
                                        client_secret_input.send_keys(client_secret)
                                        print("Client Secret inputted.")

                                        # Wait for the button to become enabled and click it
                                        submit_btn_xpath = "/html/body/div/div/div[2]/div[4]/div[1]/div/section/div/div/div[2]/div[2]/div[2]/button"
                                        def button_enabled(driver):
                                            btn = driver.find_element(By.XPATH, submit_btn_xpath)
                                            return btn.is_enabled()
                                        WebDriverWait(driver, 30).until(button_enabled)
                                        submit_btn = driver.find_element(By.XPATH, submit_btn_xpath)
                                        submit_btn.click()
                                        print("Submit button enabled and clicked.")

                                        # Wait for the Authorize app button to become clickable and click it instantly
                                        authorize_btn_xpath = "/html/body/div[1]/div/div/div[2]/main/div/div/div[2]/div/div/div[1]/div[3]/button"
                                        try:
                                            authorize_btn = WebDriverWait(driver, 120).until(
                                                EC.element_to_be_clickable((By.XPATH, authorize_btn_xpath))
                                            )
                                            authorize_btn.click()
                                            print("Authorize app button clicked.")
                                        except Exception as e:
                                            print(f"Authorize app button not found or not clickable: {e}")

                                        # Wait for "10 UXUY" text to appear (can take a long time)
                                        uxuy_xpath = "/html/body/div/div/div[2]/div[4]/div[1]/div/section/div/div/div[2]/div[5]/div[2]/div/strong"
                                        try:
                                            WebDriverWait(driver, 600).until(
                                                EC.text_to_be_present_in_element((By.XPATH, uxuy_xpath), "10 UXUY")
                                            )
                                            print('"10 UXUY" text detected.')
                                        except Exception as e:
                                            print(f'"10 UXUY" text not found in time: {e}')

                                        # Click on the next element after "10 UXUY" confirmation
                                        next_btn_xpath = "/html/body/div/div/div[2]/div[1]/div/div/div[2]/div[3]/div"
                                        try:
                                            next_btn = WebDriverWait(driver, 120).until(
                                                EC.element_to_be_clickable((By.XPATH, next_btn_xpath))
                                            )
                                            next_btn.click()
                                            print("Clicked on the next button after 10 UXUY.")
                                        except Exception as e:
                                            print(f"Next button after 10 UXUY not found or not clickable: {e}")

                                        # Wait for and click the final dialog button
                                        dialog_btn_xpath = "/html/body/div[2]/div/div/div/div[2]/div/uxdialog/div/div[1]/div[3]/div"
                                        try:
                                            dialog_btn = WebDriverWait(driver, 120).until(
                                                EC.element_to_be_clickable((By.XPATH, dialog_btn_xpath))
                                            )
                                            dialog_btn.click()
                                            print("Final dialog button clicked.")
                                        except Exception as e:
                                            print(f"Final dialog button not found or not clickable: {e}")

                                        # Wait for "Login" text in the specified element
                                        login_text_xpath = "/html/body/div/div/div[2]/div[1]/div/div/div[2]/div[3]/div/div/div/span[1]"
                                        try:
                                            WebDriverWait(driver, 120).until(
                                                EC.text_to_be_present_in_element((By.XPATH, login_text_xpath), "Login")
                                            )
                                            print('"Login" text detected.')
                                        except Exception as e:
                                            print(f'"Login" text not found: {e}')

                                        # Load the extension connected page
                                        connected_url = "chrome-extension://opfgelmcmbiajamepnmloijbpoleiama/popup.html#/connected"
                                        driver.get(connected_url)
                                        print("Loaded extension connected page.")

                                        # Wait for the button to be available and click it
                                        connect_btn_xpath = "/html/body/div/div/div/div/div[2]/div/div[1]/div/div/div/div[2]/div[2]/div/div/button"
                                        try:
                                            connect_btn = WebDriverWait(driver, 300).until(
                                                EC.element_to_be_clickable((By.XPATH, connect_btn_xpath))
                                            )
                                            connect_btn.click()
                                            print("Clicked connect button on extension page.")
                                        except Exception as e:
                                            print(f"Connect button not found or not clickable: {e}")

                                        # Wait for "No connected apps" text in the specified element
                                        no_apps_xpath = "/html/body/div/div/div/div/div[2]/div/div[1]/div/div/div/div[2]/div/div[1]/div/div[2]"
                                        try:
                                            WebDriverWait(driver, 120).until(
                                                EC.text_to_be_present_in_element((By.XPATH, no_apps_xpath), "No connected apps")
                                            )
                                            print('"No connected apps" text detected. Opening logout URL and closing browser.')
                                            # Open x.com logout page for logout
                                            try:
                                                driver.get("https://x.com/logout")
                                                print("Opened https://x.com/logout for logout.")
                                                # Wait for the Log out button to be available and click it
                                                logout_btn_xpath = "/html/body/div/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div[2]/button[1]"
                                                try:
                                                    logout_btn = WebDriverWait(driver, 30).until(
                                                        EC.element_to_be_clickable((By.XPATH, logout_btn_xpath))
                                                    )
                                                    logout_btn.click()
                                                    print("Clicked on the Log out button.")
                                                except Exception as e:
                                                    print(f"Log out button not found or not clickable: {e}")
                                            except Exception as e:
                                                print(f"Failed to open logout URL: {e}")
                                            time.sleep(2)  # Wait for logout to complete
                                            driver.quit()
                                        except Exception as e:
                                            print(f'"No connected apps" text not found: {e}')
                                    except Exception as e:
                                        print(f"Failed to input Client ID/Secret or click submit: {e}")
                                else:
                                    print("Client ID and/or Client Secret not available, skipping input.")
                                break  # Exit the loop after successful click
                            except Exception as e:
                                print(f"'Sign' button not found or not clickable (attempt {attempt+1}/{max_attempts})")
                                if attempt == 0:
                                    print("Reloading page and trying again...")
                                    driver.refresh()
                    except Exception as e:
                        print(f'"Rainbow" option not found or click failed: {e}')
                except Exception as e:
                    print(f"Verification text not found or click failed: {e}")
            else:
                print("No refer URL found in desk/refer.txt")
        except Exception as e:
            print(f'Could not click "Yes, I saved it" button: {e}')

        # Verify completion
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'success') or contains(text(), 'complete')]"))
            )
            print("Process completed successfully")
        except:
            print("Process might have completed but couldn't verify success message")
        
        return True
            
    except Exception as e:
        print(f"Error in developer flow: {str(e)}")
        return False

























def read_auth_tokens():
    try:
        with open(AUTH_TOKENS_FILE, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Auth tokens file not found at {AUTH_TOKENS_FILE}")
        return []

def mark_token_as_used(token):
    try:
        with open(USED_TOKENS_FILE, 'a') as uf:
            uf.write(f"{token}\n")

        with open(AUTH_TOKENS_FILE, 'r') as f:
            tokens = [line.strip() for line in f if line.strip()]
        
        if token in tokens:
            tokens.remove(token)

        with open(AUTH_TOKENS_FILE, 'w') as f:
            f.write('\n'.join(tokens) + '\n' if tokens else '')

        print(f"Token marked as used and moved to used_auth.txt")
    except Exception as e:
        print(f"Error marking token as used: {e}")

def generate_random_paragraph(min_length=250):
    words = ["Lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit", 
             "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore",
             "magna", "aliqua", "Ut", "enim", "ad", "minim", "veniam", "quis", "nostrud",
             "exercitation", "ullamco", "laboris", "nisi", "ut", "aliquip", "ex", "ea",
             "commodo", "consequat", "Duis", "aute", "irure", "dolor", "in", "reprehenderit",
             "in", "voluptate", "velit", "esse", "cillum", "dolore", "eu", "fugiat", "nulla",
             "pariatur", "Excepteur", "sint", "occaecat", "cupidatat", "non", "proident",
             "sunt", "in", "culpa", "qui", "officia", "deserunt", "mollit", "anim", "id", "est", "laborum"]
    
    paragraph = ""
    while len(paragraph) < min_length:
        sentence = ' '.join(random.sample(words, random.randint(5, 15))).capitalize()
        paragraph += sentence + '. '
        if random.random() > 0.7:
            paragraph += '\n\n'
    
    return paragraph.strip()[:min_length + 300]

def open_chrome_instance(driver_path, profile_path, window_index, url=None):
    print(f"Initializing Chrome instance {window_index}...")
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={profile_path}")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    # Performance optimizations
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--dns-prefetch-disable')
    chrome_options.add_argument('--disable-background-networking')
    chrome_options.add_argument('--disable-preconnect')
    chrome_options.add_argument('--disable-http2')
    chrome_options.add_argument('--disk-cache-size=1')
    chrome_options.add_argument('--media-cache-size=1')

    service = Service(driver_path)
    try:
        browser = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"Failed to initialize Chrome: {e}")
        return None

    # Set window position
    window_width, window_height = 375, 800
    screen_padding_x = 125
    screen_padding_y = 80

    if window_index == 0:
        x_position, y_position = 1, 1
    elif window_index == 1:
        x_position, y_position = window_width + screen_padding_x, 0

    browser.set_window_position(x_position, y_position)

    if url:
        try:
            print(f"Opening URL: {url}")
            browser.get(url)
            time.sleep(2)  # Wait for page to load

            # Step 1: Unlock wallet
            if not unlock_wallet(browser):
                print("Skipping remaining steps due to wallet unlock failure")
                return browser

            # Step 2: Wait for wallet unlocked
            if not wait_for_wallet_unlocked(browser):
                print("Skipping remaining steps due to wallet unlock confirmation failure")
                return browser

            # Step 3: Import wallet key
            if not import_wallet_key(browser):
                print("Skipping remaining steps due to wallet key import failure")
                return browser

            # Step 4: Twitter login
            auth_tokens = read_auth_tokens()
            if not auth_tokens:
                print("No auth tokens available, skipping Twitter login")
                return browser

            auth_token = auth_tokens[0]
            if twitter_login_with_cookie(browser, auth_token):
                mark_token_as_used(auth_token)
                
                # Step 5: Complete developer portal
                if complete_developer_portal(browser):
                    print("All steps completed successfully!")
                    # Close the browser
                    browser.quit()
                    print("Browser closed.")

                    # Re-open with new key (recursive call)
                    driver_path = chromedriver_paths[0]
                    profile_path = chrome_profiles[0]
                    url = read_url_from_file("desk/unlocked.txt")
                    open_chrome_instance(driver_path, profile_path, 0, url)
                    return  # Exit after re-opening
                else:
                    print("Developer portal process failed")
            else:
                print("Twitter login failed")

        except Exception as e:
            print(f"Error during main process: {e}")

    return browser

if __name__ == "__main__":
    driver_path = chromedriver_paths[0]
    profile_path = chrome_profiles[0]
    url = read_url_from_file("desk/unlocked.txt")
    open_chrome_instance(driver_path, profile_path, 0, url)

    # Prevent the script from closing the browser automatically
    input("Press Enter to exit and close the browser...")
