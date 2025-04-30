from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time
import os

USERNAME = os.getenv("CONCERTO_USERNAME", "")
PASSWORD = os.getenv("CONCERTO_PASSWORD", "")

def run_bot(artikelnummern, output_path):
    options = Options()
    options.binary_location = "/usr/bin/chromium"  # Render-spezifisch
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        wait = WebDriverWait(driver, 20)
        driver.get("https://www.concertopro.ch/anmeldung-concerto-einkaufsplattform/")

        wait.until(EC.presence_of_element_located((By.NAME, "user"))).send_keys(USERNAME)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        try:
            cookie_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Akzeptieren')]"))
            )
            cookie_button.click()
        except:
            pass

        results = []

        for nummer in artikelnummern:
            driver.get("https://www.concertopro.ch/produkte/")
            wait.until(EC.presence_of_element_located((By.NAME, "FormProdNrSearch")))

            suchfeld = driver.find_element(By.NAME, "FormProdNrSearch")
            suchfeld.clear()
            suchfeld.send_keys(nummer)
            suchfeld.send_keys(Keys.RETURN)
            time.sleep(2)

            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.prodDetailsLink"))).click()
                time.sleep(2)

                tabelle = driver.find_element(By.CLASS_NAME, "prodSuppliers")
                zeilen = tabelle.find_elements(By.TAG_NAME, "tr")

                for zeile in zeilen[1:]:
                    spalten = zeile.find_elements(By.TAG_NAME, "td")
                    if len(spalten) >= 3:
                        haendler = spalten[0].text.strip()
                        preis = spalten[1].text.strip()
                        lager = spalten[2].text.strip()
                        results.append({
                            "Manufacturer Number": nummer,
                            "Händler": haendler,
                            "Preis": preis,
                            "Lager": lager
                        })

            except Exception:
                results.append({
                    "Manufacturer Number": nummer,
                    "Händler": "❌ Nicht gefunden",
                    "Preis": "-",
                    "Lager": "-"
                })

        df = pd.DataFrame(results)
        df.to_excel(output_path, index=False)

    finally:
        driver.quit()
