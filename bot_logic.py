from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import time
import os
from openpyxl import Workbook

# Login-Daten laden
load_dotenv("Passwort.env")
USERNAME = os.getenv("CONCERTO_USERNAME")
PASSWORD = os.getenv("CONCERTO_PASSWORD")

# Nur diese Distributoren ins Vergleichs-Tab aufnehmen
ERLAUBTE_DISTRIBUTOREN = [
    "TD SYNNEX Switzerland GmbH",
    "ALSO Schweiz AG",
    "INGRAM MICRO GmbH",
    "Alltron AG"
]

def run_bot(artikelnummern, output_path):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 15)

    driver.get("https://www.concertopro.ch/anmeldung-concerto-einkaufsplattform/")

    try:
        driver.execute_script("document.querySelector('#cn-accept-cookie')?.click();")
    except:
        pass

    try:
        username_field = wait.until(EC.presence_of_element_located((By.ID, "USERNAME")))
        password_field = driver.find_element(By.ID, "PASSWORD")
        username_field.send_keys(USERNAME)
        password_field.send_keys(PASSWORD)
        login_button = driver.find_element(By.XPATH, "//input[@type='submit' and @name='LOGIN']")
        login_button.click()
    except:
        print("Login übersprungen oder fehlgeschlagen")

    time.sleep(5)

    all_data = []
    vergleichsdaten = {}  # {artikelnummer: {distributor: (preis, bestand)}}

    for artikelnummer in artikelnummern:
        try:
            driver.switch_to.default_content()
            left_frame = driver.find_element(By.NAME, "left")
            driver.switch_to.frame(left_frame)

            suchfeld = wait.until(EC.presence_of_element_located((By.NAME, "ProdNrSearch")))
            suchfeld.clear()
            suchfeld.send_keys(artikelnummer)
            suchfeld.send_keys(Keys.RETURN)
            time.sleep(5)

            driver.switch_to.default_content()
            main_frame = driver.find_element(By.NAME, "main")
            driver.switch_to.frame(main_frame)

            artikel_link = wait.until(EC.presence_of_element_located((By.XPATH, f"//a[contains(text(), '{artikelnummer}')]")))
            artikel_link.click()
            time.sleep(5)

            rows = driver.find_elements(By.XPATH, "//tr")
            distributors, prices, quantities = [], [], []
            seen_distributors = set()
            vergleichsdaten[artikelnummer] = {}

            for row in rows:
                try:
                    dist_el = row.find_elements(By.XPATH, ".//td[contains(@class, 'distributor-name gray-top-border')]")
                    if dist_el:
                        name = dist_el[0].text.strip().split("\n")[0]
                        if name in seen_distributors:
                            continue
                        seen_distributors.add(name)

                        price_cell = row.find_elements(By.XPATH, ".//td[contains(@class, 'gray-white-border')]")
                        if len(price_cell) > 1:
                            your_price_el = price_cell[1].find_element(By.XPATH, ".//font[@class='DataFONT']")
                            your_price = your_price_el.text.strip().replace("'", "")
                        else:
                            your_price = "N/A"

                        quantity = "N/A"
                        quantity_elements = row.find_elements(By.XPATH, ".//td[contains(@class, 'gray-white-border')]//font[@class='DataFONT']")
                        for q in quantity_elements:
                            qt = q.text.strip()
                            if qt.isdigit():
                                quantity = qt
                                break
                            if qt.startswith("(") and qt.endswith(")"):
                                quantity = qt[1:-1]
                                break
                            if "check" in qt:
                                quantity = qt.split(" ")[0][1:-1]
                                break

                        distributors.append(name)
                        prices.append(your_price)
                        quantities.append(quantity)

                        if name in ERLAUBTE_DISTRIBUTOREN:
                            vergleichsdaten[artikelnummer][name] = (your_price, quantity)

                except:
                    continue

            row = [artikelnummer]
            for i in range(len(distributors)):
                row.append(distributors[i])
                row.append(prices[i])
                row.append(quantities[i])
            all_data.append(row)

        except Exception as e:
            print(f"Fehler bei Artikel {artikelnummer}: {e}")
            continue

    driver.quit()

    # Excel-Datei erstellen
    wb = Workbook()
    ws1 = wb.active
    ws1.title = "Übersicht"

    # Tabellenblatt 1 – flache Übersicht wie gehabt
    max_distributors = max((len(row) - 1) // 3 for row in all_data) if all_data else 0
    header = ["Artikelnummer"]
    for i in range(max_distributors):
        header.extend([f"Distributor{i+1}", f"Preis{i+1}", f"Lagerbestand{i+1}"])
    ws1.append(header)
    for row in all_data:
        ws1.append(row)

    # Tabellenblatt 2 – Vergleichsübersicht
    ws2 = wb.create_sheet(title="Vergleich")

    vergleichs_header = ["Artikelnummer"]
    for dist in ERLAUBTE_DISTRIBUTOREN:
        vergleichs_header.append(f"{dist} (Preis)")
        vergleichs_header.append(f"{dist} (Bestand)")
    ws2.append(vergleichs_header)

    for artikel, daten in vergleichsdaten.items():
        row = [artikel]
        for dist in ERLAUBTE_DISTRIBUTOREN:
            preis, bestand = daten.get(dist, ("", ""))
            row.extend([preis, bestand])
        ws2.append(row)

    wb.save(output_path)
