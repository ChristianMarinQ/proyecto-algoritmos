"""
    This module uses a class to scrape the Scopus Database
"""
import os
import time
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv


class ScienceScraper:
    """
        This class contains all the scopus scrapper methods
    """

    def __init__(self, email, password, query, limit, use_undetected=True, profile_path=None):
        """
        Initialize the scrapper
        """
        self.email = email
        self.password = password
        self.query = query
        self.limit = limit
        if use_undetected:
            # Use undetected-chromedriver which is built to bypass detections
            if profile_path:
                self.options = uc.ChromeOptions()
                self.options.add_argument(f"--user-data-dir={profile_path}")
                try:
                    self.browser = uc.Chrome(options=self.options, version_main=147)
                except Exception:
                    self.browser = uc.Chrome(options=self.options) # Fallback
            else:
                try:
                    self.browser = uc.Chrome(version_main=147)
                except Exception:
                    self.browser = uc.Chrome() # Fallback
        else:
            # Original approach with added protections
            self.options = webdriver.ChromeOptions()

            # Add user data directory if provided
            if profile_path:
                self.options.add_argument(f"--user-data-dir={profile_path}")

            # Standard anti-detection measures
            self.options.add_argument("--start-maximized")
            self.options.add_experimental_option("detach", True)

            # Add realistic user agent
            self.options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

            # Add language preferences
            self.options.add_argument("--lang=en-US,en;q=0.9")

            # Set window size to realistic dimensions
            self.options.add_argument("--window-size=1920,1080")

            # Avoid detection
            self.options.add_argument(
                "--disable-blink-features=AutomationControlled")
            self.options.add_argument("--disable-gpu")
            self.options.add_experimental_option(
                "excludeSwitches", ["enable-automation"])
            self.options.add_experimental_option(
                "useAutomationExtension", False)

            # Add additional arguments that may help
            self.options.add_argument("--no-sandbox")
            self.options.add_argument("--disable-dev-shm-usage")

            # Add preferences to mimic human browser settings
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_settings.popups": 0
            }
            self.options.add_experimental_option("prefs", prefs)

            self.browser = webdriver.Chrome(options=self.options)

            # Execute scripts to avoid detection
            self.browser.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.browser.execute_script(
                "Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 5});")
            self.browser.execute_script(
                "Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});")

            # Additional anti-detection scripts
            self.browser.execute_script(
                "Object.defineProperty(navigator, 'plugins', {get: function() { return [1, 2, 3, 4, 5]; }});")
            self.browser.execute_script(
                "Object.defineProperty(navigator, 'languages', {get: function() { return ['en-US', 'en']; }});")

        self.browser.implicitly_wait(10)
        self.action_chains = ActionChains(self.browser)

    def open_library(self):
        """
        Locates and opens the Scopus database
        """
        self.browser.get("https://library.uniquindio.edu.co/databases")
        wait = WebDriverWait(self.browser, 10)
        science_direct_div = self.browser.find_element(
            By.CSS_SELECTOR, "#facingenierasciencedirectdescubridor")
        divlink = wait.until(
            lambda browser: science_direct_div.find_element(By.CSS_SELECTOR, "a"))
        self.browser.get(divlink.get_attribute("href"))

    def google_login(self):
        """
        Logs into google account
        """
        self.browser.find_element(By.ID, "btn-google").click()
        self.browser.find_element(By.TAG_NAME, "input").send_keys(self.email)
        self.browser.find_element(By.ID, "identifierNext").find_element(
            By.TAG_NAME, "button").click()
        time.sleep(2)
        self.browser.find_element(By.NAME, "Passwd").send_keys(self.password)
        self.browser.find_element(By.ID, "passwordNext").find_element(
            By.TAG_NAME, "button").click()

    def search_articles(self):
        """
        Searches for articles using the provided query
        """
        # Set up explicit wait
        wait = WebDriverWait(self.browser, 30)

        time.sleep(15)
        search_input = self.browser.find_element(By.ID, "qs")
        search_input.send_keys(self.query)
        search_input.send_keys(Keys.RETURN)

        max_pages = self.limit // 100 + 1 if self.limit > 0 else 10 # Estimate 100 per page

        current_page = 1
        while current_page <= max_pages:
            print(f"\n--- Processing ScienceDirect Page {current_page} ---")
            time.sleep(5)

            # Process current page
            try:
                self.process_page()
                print(f"[OK] Page {current_page} exported.")
            except Exception as e:
                print(f"Error processing page {current_page}: {e}")
                break

            # Click Next Page
            try:
                next_page = self.browser.find_element(By.CSS_SELECTOR, "[data-testid='next-page-button']")
                if not next_page.is_enabled():
                    print("Last page reached.")
                    break
                self.browser.execute_script("arguments[0].click();", next_page)
                current_page += 1
                time.sleep(5)
            except Exception:
                try:
                    # Fallback for pagination
                    next_page = self.browser.find_element(By.XPATH, "//span[contains(text(), 'Next')]")
                    next_page.click()
                    current_page += 1
                    time.sleep(5)
                except Exception:
                    print("Next button not found or end of results.")
                    break

        self.browser.quit()
        print(f"[DONE] ScienceDirect scraping complete! Processed {current_page} pages.")

    def process_page(self):
        """
        Process a single page of results - select all, export, and uncheck
        """
        wait = WebDriverWait(self.browser, 30)

        # Find and click the checkbox to select all
        try:
            checkbox_container = wait.until(
                lambda browser: browser.find_element(
                    By.CLASS_NAME, "result-header-controls-container")
            )
            checkbox = checkbox_container.find_element(By.TAG_NAME, "span")
            wait.until(lambda browser: checkbox.is_displayed())
            checkbox.click()
            print("Selected all items")
        except Exception as e:
            print(f"Error selecting all items: {e}")
            raise

        time.sleep(2)

        # Click export button
        try:
            export_button = wait.until(
                lambda browser: browser.find_element(
                    By.CLASS_NAME, "export-all-link-button")
            )
            export_button.click()
            print("Clicked export button")
        except Exception as e:
            print(f"Error clicking export button: {e}")
            raise

        time.sleep(5)

        # Click bibtex export option
        try:

            time.sleep(10)
            export_dialog = wait.until(
                lambda browser: browser.find_element(
                    By.CLASS_NAME, "ExportCitationOptions")
            )
            export_options_container = export_dialog.find_element(
                By.CLASS_NAME, "preview-body")

            export_buttons = export_options_container.find_elements(
                By.TAG_NAME, "button")

            if len(export_buttons) >= 3:
                export_buttons[2].click()  # [1] for ris, 2 for bibtex
                print("Clicked bibtex export button")
            else:
                print(
                    f"Not enough export buttons found. Found {len(export_buttons)}")
                raise Exception("Export buttons not found")
        except Exception as e:
            print(f"Error during export: {e}")
            raise

        time.sleep(3)

        # Uncheck the "select all" checkbox
        try:
            checkbox_container = wait.until(
                lambda browser: browser.find_element(
                    By.CLASS_NAME, "result-header-controls-container")
            )
            checkbox = checkbox_container.find_element(By.TAG_NAME, "span")
            checkbox.click()
            print("Unchecked all items")
        except Exception as e:
            print(f"Error unchecking items: {e}")
            # Don't raise here, as we want to continue to the next page

        time.sleep(2)

    def run(self):
        """
        Runs the scrapper
        """
        self.open_library()
        self.google_login()
        self.search_articles()
