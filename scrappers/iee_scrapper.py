"""
Module for ieee scrapper
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


class IeeeScrapper:
    """
        This class contains all the IEEE scrapper methods
    """

    def __init__(self, email, password, query, limit):
        self.email = email
        self.password = password
        self.query = query
        self.limit = limit
        
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--start-maximized")
        self.options.add_experimental_option("detach", True)
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument(
            "--disable-blink-features=AutomationControlled")
        self.browser = webdriver.Chrome(options=self.options)
        self.browser.implicitly_wait(15)
        self.wait = WebDriverWait(self.browser, 20)

    def open_library(self):
        """
        Locates and opens the IEEE database from the university library
        """
        print("[1/5] Opening university library...")
        self.browser.get("https://library.uniquindio.edu.co/databases")
        wait = WebDriverWait(self.browser, 10)
        science_direct_div = self.browser.find_element(
            By.CSS_SELECTOR, "#facingenieraieeeinstituteofelectricalandelectronicsengineersdescubridor")
        divlink = wait.until(
            lambda browser: science_direct_div.find_element(By.CSS_SELECTOR, "a"))
        self.browser.get(divlink.get_attribute("href"))
        print("[OK] Library opened, redirecting to IEEE...")

    def google_login(self):
        """
        Logs into google account
        """
        print("[2/5] Logging into Google...")
        self.browser.find_element(By.ID, "btn-google").click()
        self.browser.find_element(By.TAG_NAME, "input").send_keys(self.email)
        self.browser.find_element(By.ID, "identifierNext").find_element(
            By.TAG_NAME, "button").click()
        time.sleep(2)
        self.browser.find_element(By.NAME, "Passwd").send_keys(self.password)
        self.browser.find_element(By.ID, "passwordNext").find_element(
            By.TAG_NAME, "button").click()
        print("[OK] Google login submitted")

    def iee_search(self, max_pages=10):
        """
        Search for articles on IEEE database and paginate
        """
        print("[3/5] Searching for articles...")
        time.sleep(5)
        try:
            search_input = self.browser.find_element(By.CLASS_NAME, "Typeahead-input")
            search_input.send_keys(self.query)
            search_input.send_keys(Keys.RETURN)
        except Exception:
            search_input = self.browser.find_element(By.CSS_SELECTOR, "input[title='Search term']")
            search_input.send_keys(self.query)
            search_input.send_keys(Keys.RETURN)
            
        time.sleep(8)
        print("[OK] Search submitted")

        # Close cookies popup
        try:
            self.browser.find_element(By.CLASS_NAME, "osano-cm-save").click()
            time.sleep(2)
        except Exception: pass

        max_pages = self.limit // 100 + 1 if self.limit > 0 else 10 # Estimate 100 per page

        current_page = 1
        while current_page <= max_pages:
            print(f"\n--- Processing IEEE Page {current_page} ---")
            
            # Click "Select All on Page"
            try:
                # Wait for results to load
                WebDriverWait(self.browser, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "List-results-items"))
                )
                select_all = self.browser.find_element(By.XPATH, "//label[contains(text(), 'Select All')]")
                self.browser.execute_script("arguments[0].click();", select_all)
                print(f"[OK] Selected articles on page {current_page}")
                time.sleep(2)
            except Exception as e:
                print(f"[WARN] Could not select all on page {current_page}: {e}")

            # Export current page
            print(f"[4/5] Exporting page {current_page}...")
            try:
                self.process_page()
            except Exception as e:
                print(f"[ERROR] Export failed on page {current_page}: {e}")

            # Go to Next Page
            try:
                next_btn = self.browser.find_element(By.CLASS_NAME, "next-btn")
                if "disabled" in next_btn.get_attribute("class"):
                    print("No more pages available.")
                    break
                self.browser.execute_script("arguments[0].click();", next_btn)
                print("Moving to next page...")
                current_page += 1
                time.sleep(5) # Wait for page load
            except Exception:
                print("Next button not found or end of results.")
                break

        self.browser.quit()
        print(f"[DONE] IEEE scraping complete! Processed {current_page} pages.")

    def process_page(self):
        """
        Exports selected articles as BibTeX
        """
        # Click the "Export" button in toolbar
        try:
            export_btn = self.browser.find_element(
                By.XPATH, "//button[contains(text(), 'Export')]")
            export_btn.click()
            print("  -> Clicked Export button")
        except Exception:
            export_btn = self.browser.find_element(
                By.CSS_SELECTOR, ".export-filter button")
            export_btn.click()
            print("  -> Clicked Export button (fallback)")
        time.sleep(4)

        # Click Citations tab
        try:
            citations_nav = self.browser.find_element(
                By.CLASS_NAME, "nav-tabs")
            tabs = citations_nav.find_elements(By.TAG_NAME, "li")
            if len(tabs) > 1:
                tabs[1].find_element(By.TAG_NAME, "a").click()
                print("  -> Clicked Citations tab")
                time.sleep(2)
        except Exception as e:
            print(f"  -> Citations tab issue: {e}")

        # Configurar las opciones de descarga (BibTeX y Abstractos)
        try:
            # Encontrar todas las etiquetas en el modal
            labels = self.browser.find_elements(By.TAG_NAME, "label")
            for label in labels:
                texto = label.text.strip()
                # Si es el botón de BibTeX, hacer clic
                if "BibTeX" in texto:
                    self.browser.execute_script("arguments[0].click();", label)
                    print("  -> Selected format: BibTeX")
                    time.sleep(1)
                # Si es el botón de Citation and Abstract, hacer clic también
                elif "Citation and Abstract" in texto:
                    self.browser.execute_script("arguments[0].click();", label)
                    print("  -> Selected content: Citation and Abstract")
                    time.sleep(1)
            time.sleep(2)
        except Exception as e:
            print(f"  -> [ERROR] Failed to select download options: {e}")

        # Click Download
        try:
            download_btn = self.browser.find_element(
                By.XPATH, "//button[contains(text(), 'Download')]")
            download_btn.click()
            print("  -> Download started!")
        except Exception:
            try:
                download_btn = self.browser.find_element(
                    By.CSS_SELECTOR, ".stats-SearchResults_Citation_Download")
                download_btn.click()
                print("  -> Download started (fallback)!")
            except Exception as e:
                print(f"  -> Download issue: {e}")

        time.sleep(5)

        # Close modal
        try:
            self.browser.find_element(
                By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            time.sleep(2)
        except Exception:
            pass

    def run(self):
        """
        This method executes the scrapper
        """
        self.open_library()
        self.google_login()
        self.iee_search()
