import os
import time
import shutil
import glob
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains

BTN_PATH = "//button/span[text()='Siguiente']/parent::button"
BASE_URL = "https://research-ebsco-com.crai.referencistas.com"
SEARCH_BOX_ID = "search-input"
RESULT_LIST_ID = "result-list"
LOAD_MORE_BUTTON = "//button[@data-auto='show-more-button' and contains(text(), 'Mostrar más resultados')]"

class SageScraper:
    """
        This class uses the logic from the user's reference scrapper_service.py 
        to download from EBSCOhost (replaces the old Sage approach).
    """
    def __init__(self, email, password, query, limit):
        self.email = email
        self.password = password
        self.query = query
        self.limit = limit
        # Ruta absoluta al directorio del proyecto (carpeta padre del scrapper)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.download_dir = os.path.join(project_root, "researchFiles")
        os.makedirs(self.download_dir, exist_ok=True)
        
        options = Options()
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,
            "plugins.always_open_pdf_externally": True,
            "browser.helperApps.neverAsk.saveToDisk": "application/x-research-info-systems,application/x-bibtex,text/x-bibtex,text/plain"
        }
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("detach", True)
        self.browser = webdriver.Chrome(options=options)
        self.browser.execute_cdp_cmd(
            "Page.setDownloadBehavior",
            {"behavior": "allow", "downloadPath": self.download_dir}
        )
        self.browser.maximize_window()

    def log_into_library(self):
        print("[1/5] Logging into library via EBSCO proxy...")
        self.browser.get(BASE_URL)
        btn_google = WebDriverWait(self.browser, 15).until(
            ec.element_to_be_clickable((By.ID, "btn-google"))
        )
        btn_google.click()
        if len(self.browser.window_handles) > 1:
            self.browser.switch_to.window(self.browser.window_handles[-1])
        
        WebDriverWait(self.browser, 15).until(
            ec.presence_of_element_located((By.ID, "identifierId"))
        ).send_keys(self.email)
        
        WebDriverWait(self.browser, 15).until(
            ec.element_to_be_clickable((By.XPATH, BTN_PATH))
        ).click()
        
        WebDriverWait(self.browser, 15).until(
            ec.presence_of_element_located((By.NAME, "Passwd"))
        ).send_keys(self.password)
        
        WebDriverWait(self.browser, 15).until(
            ec.element_to_be_clickable((By.XPATH, "//span[text()='Siguiente']/.."))
        ).click()
        
        WebDriverWait(self.browser, 30).until(
            ec.presence_of_element_located((By.ID, SEARCH_BOX_ID))
        )
        print("[OK] Login completado.")

    def get_article_title(self, idx):
        try:
            title_xpath = f"//div[@id='record-{idx}-detail']/div/h2/a"
            title_element = WebDriverWait(self.browser, 3).until(
                ec.presence_of_element_located((By.XPATH, title_xpath))
            )
            title = title_element.text.strip()
            safe_title = ''.join(c if c.isalnum() or c in ' -_' else '_' for c in title)
            return safe_title[:50]
        except:
            return f"article_{idx}"

    def wait_for_download_complete(self, timeout=30):
        start_time = time.time()
        while time.time() - start_time < timeout:
            # No hay descargas en curso
            if not glob.glob(os.path.join(self.download_dir, "*.crdownload")) and \
                    not glob.glob(os.path.join(self.download_dir, "*.tmp")):
                # Detectar .bib, .bibtex o .txt
                if (glob.glob(os.path.join(self.download_dir, "*.bib")) or
                        glob.glob(os.path.join(self.download_dir, "*.bibtex")) or
                        glob.glob(os.path.join(self.download_dir, "*.txt"))):
                    time.sleep(1)
                    return True
            time.sleep(0.5)
        return False

    def rename_last_downloaded_file(self, new_name):
        files = glob.glob(os.path.join(self.download_dir, "*"))
        # Incluir .bib, .bibtex y .txt
        valid_files = [f for f in files if f.endswith('.bib') or
                       f.endswith('.bibtex') or f.endswith('.txt')]
        if not valid_files:
            return False
        
        latest_file = max(valid_files, key=os.path.getmtime)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"EBSCO_{new_name}_{timestamp}.bib"
        new_path = os.path.join(self.download_dir, new_filename)
        try:
            shutil.move(latest_file, new_path)
            return True
        except:
            return False

    def load_more_results(self):
        try:
            load_more_btn = WebDriverWait(self.browser, 20).until(
                ec.element_to_be_clickable((By.XPATH, LOAD_MORE_BUTTON))
            )
            self.browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", load_more_btn)
            time.sleep(3)
            self.browser.execute_script("arguments[0].click();", load_more_btn)
            time.sleep(10)
            return True
        except:
            return False

    def search_and_download(self):
        print(f"[3/5] Iniciando búsqueda para '{self.query}'...")
        caja = WebDriverWait(self.browser, 20).until(
            ec.presence_of_element_located((By.ID, "search-input"))
        )
        caja.clear()
        caja.send_keys(self.query, Keys.RETURN)

        WebDriverWait(self.browser, 30).until(
            ec.presence_of_element_located((By.ID, "result-list"))
        )
        time.sleep(2)

        results_processed = 0
        successful_downloads = 0
        current_result_idx = 1

        print(f"[4/5] Extrayendo uno a uno (límite: {self.limit})...")
        while successful_downloads < self.limit:
            try:
                print(f"Procesando resultado #{current_result_idx}...")
                btn_id = f"record-{current_result_idx}-tools-toggle-button"

                try:
                    tool_button = self.browser.find_element(By.ID, btn_id)
                except NoSuchElementException:
                    print("Cargando más resultados...")
                    if not self.load_more_results():
                        break
                    try:
                        tool_button = self.browser.find_element(By.ID, btn_id)
                    except NoSuchElementException:
                        break

                article_title = self.get_article_title(current_result_idx)

                button = WebDriverWait(self.browser, 10).until(
                    ec.presence_of_element_located((By.ID, btn_id))
                )
                self.browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                time.sleep(1)
                self.browser.execute_script("arguments[0].click();", button)
                time.sleep(1)

                menu_xpath = f"//li[@id='record-{current_result_idx}-tools-item-3']"
                download_option = WebDriverWait(self.browser, 10).until(
                    ec.element_to_be_clickable((By.XPATH, menu_xpath))
                )
                self.browser.execute_script("arguments[0].click();", download_option)
                time.sleep(1)

                meta_option = WebDriverWait(self.browser, 10).until(
                    ec.element_to_be_clickable((By.XPATH, "//li[text()='Solo metadatos']"))
                )
                self.browser.execute_script("arguments[0].click();", meta_option)
                time.sleep(1)

                bibtex_radio = WebDriverWait(self.browser, 10).until(
                    ec.element_to_be_clickable((By.XPATH, "//span[contains(translate(., 'bibtex', 'BIBTEX'), 'BIBTEX')]/ancestor::label"))
                )
                self.browser.execute_script("arguments[0].click();", bibtex_radio)
                time.sleep(1)

                download_button = WebDriverWait(self.browser, 5).until(
                    ec.element_to_be_clickable((By.XPATH, "//button[text()='Descargar']"))
                )
                self.browser.execute_script("arguments[0].click();", download_button)

                if self.wait_for_download_complete(timeout=20):
                    if self.rename_last_downloaded_file(f"{current_result_idx}_{article_title}"):
                        successful_downloads += 1

                try:
                    close_btn = WebDriverWait(self.browser, 5).until(
                        ec.element_to_be_clickable((By.XPATH, "//button[@title='Cerrar']"))
                    )
                    self.browser.execute_script("arguments[0].click();", close_btn)
                except:
                    try:
                        ActionChains(self.browser).send_keys(Keys.ESCAPE).perform()
                    except:
                        pass
                time.sleep(1)

                results_processed += 1
                current_result_idx += 1

            except TimeoutException:
                current_result_idx += 1
                continue
            except Exception as e:
                try:
                    self.browser.execute_script("document.body.click();")
                    ActionChains(self.browser).send_keys(Keys.ESCAPE).perform()
                except:
                    pass
                current_result_idx += 1
                continue

        print(f"[DONE] Proceso finalizado. Descargados {successful_downloads}.")

    def run(self):
        try:
            self.log_into_library()
            self.search_and_download()
        finally:
            self.browser.quit()
