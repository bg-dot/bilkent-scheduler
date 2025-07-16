# ders_sections.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


from datetime import datetime
import requests
import time

HAFTA_SIRASI = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

def gun_hesaplama(num):
    return HAFTA_SIRASI[num - 1] if 1 <= num <= 5 else "Bilinmeyen Gün"

def kullanicidan_donem_secimi():
    yil = datetime.now().year
    ay = datetime.now().month

    if 3 <= ay <= 6:
        print("Lütfen Bakmak İstediğiniz Dönemi Seçiniz: \n[1]-Spring\n[2]-Summer")
        secim = input("Seçim: ")
        yil -= 1
        return (2 if secim == "1" else 3, yil)

    elif 6 < ay <= 11:
        print("Lütfen Bakmak İstediğiniz Dönemi Seçiniz: \n[1]-Summer\n[2]-Fall")
        secim = input("Seçim: ")
        return (3 if secim == "1" else 1, yil)

    else:
        print("Lütfen Bakmak İstediğiniz Dönemi Seçiniz: \n[1]-Fall\n[2]-Spring")
        secim = input("Seçim: ")
        if secim == "1" and ay < 3:
            yil -= 1
        return (1 if secim == "1" else 2, yil)

def dersi_sec_ve_saatleri_getir(browser, course_code, lesson_code, semester_code):
    ders_bulundu = False
    wait = WebDriverWait(browser, 5)
    dersin_sections = []

    rows = browser.find_elements(By.CLASS_NAME, "scrollingContent")[0].find_elements(By.TAG_NAME, "tr")

    for row in rows:
        if row.get_attribute("id") == lesson_code:
            ders_bulundu = True
            row.click()
            time.sleep(1)
            tbody = wait.until(EC.presence_of_element_located((By.ID, "sections")))
            sections = tbody.find_elements(By.TAG_NAME, "tr")[1:-1]

            for i, _ in enumerate(sections, start=1):
                syllabus_url = f"https://stars.bilkent.edu.tr/syllabus/view/{course_code}/{lesson_code[-3:]}/{semester_code}?section={i}"
                browser.get(syllabus_url)
                parser = BeautifulSoup(requests.get(syllabus_url).content, "html.parser")

                try:
                    instructor = browser.find_element(By.XPATH, "/html/body/div/table/tbody/tr[1]/td/div[6]").text
                except:
                    instructor = "Bilinmiyor"

                lecture_hours = parser.find("div", class_="RollOverTable").find("tbody").find_all("tr")
                section_schedule = []

                for row in lecture_hours[:14]:
                    tds = row.find_all("td")
                    for idx, td in enumerate(tds):
                        cls = td.get("class")
                        if cls in [["cl_ders_DY"], ["cl_lab_LL"]]:
                            saat_info = tds[0].string
                            gun_info = idx
                            event = "ders" if cls == ["cl_ders_DY"] else "lab"
                            section_schedule.append({gun_hesaplama(gun_info): (event, saat_info)})

                dersin_sections.append({
                    "section": i,
                    "instructor": instructor,
                    "times": section_schedule
                })

                time.sleep(1)
            break

    if not ders_bulundu:
        print("Öyle Bir Ders Bulunamadı...")

    return dersin_sections



def main(semester_code):
    course_code = input("Please Enter the Department: ").upper()
    url = f"https://stars.bilkent.edu.tr/homepage/offerings.php?COURSE_CODE={course_code}&SEMESTER={semester_code}"
    options = Options()
    options.add_argument("--log-level=3")  # INFO=0, WARNING=1, LOG_ERROR=2, LOG_FATAL=3
    service = Service(log_path='NUL')  # Windows'ta konsola log bastırma
    browser = webdriver.Chrome(service=service, options=options)
    browser.get(url)
    try:
        Select(browser.find_element(By.ID, "SEMESTER")).select_by_value(semester_code)
        time.sleep(5)
    except:
        print("Dönem seçimi yapılamadı.")
        browser.quit()
        return []

    try:
        wait = WebDriverWait(browser, 5)
        tbody = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "scrollingContent")))
        rows = tbody.find_elements(By.TAG_NAME, "tr")
    except TimeoutException:
        print("Baktığınız Departmanın Offeringsleri Hala Açılmamıştır...")
        browser.quit()
        return []

    print("\nBu Dönem Açılan Dersler:")
    for row in rows:
        print(f"Course ID: {row.get_attribute('id')} | Title: {row.get_attribute('title')}")

    lesson_code = input("\nLütfen Almak İstediğiniz Dersin Kodunu Giriniz: ")
    dersler = dersi_sec_ve_saatleri_getir(browser, course_code, lesson_code, semester_code)

    browser.quit()
    return dersler
