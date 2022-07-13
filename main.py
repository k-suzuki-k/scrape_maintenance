import datetime
import time
import csv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

t_delta = datetime.timedelta(hours=9)
JST = datetime.timezone(t_delta, 'JST')
now = datetime.datetime.now(JST)
web_scraping_date = f'{now:%Y%m%d%H%M%S}'

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(r"C:\Users\XXXX\chromedriver_win32\chromedriver", options=options)

driver.get("https://network.informatica.com/s/event-landing")
driver.implicitly_wait(5)

while True:
    try:
        btn = driver.find_element(By.XPATH, '//*[@id="tab-1"]/slot/c-help-event-list/div[3]/a')
        btn.click()
    except NoSuchElementException:
        break

html = driver.page_source.encode("utf-8")
soup = BeautifulSoup(html, "html.parser")

elems = soup.select('a[href^="https://network.informatica.com/s/eventdetails"]')
maintenance_links = [elem.attrs["href"] for elem in elems]

for no, maintenance_link in enumerate(maintenance_links, start=1):
    driver.get(maintenance_link)
    time.sleep(5)
    html = driver.page_source.encode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    header = soup.select_one(".in-event-heading")
    description = soup.select_one(".description")
    event_datetime = soup.select_one(".in-event-datetime")
    event_location = soup.select_one(".in-event-location")
    if "NorthEast 1 Azure" in event_location.get_text(strip=True):
        check_flag = True
    else:
        check_flag = False

    maintenance = []
    maintenance.append(no)
    maintenance.append(web_scraping_date)
    maintenance.append(check_flag)
    maintenance.append(maintenance_link)
    maintenance.append(header.get_text(strip=True))
    maintenance.append(description.get_text("\n", strip=True))
    maintenance.append(event_datetime.get_text(strip=True))
    maintenance.append(event_location.get_text(strip=True))

    with open("maintenance.tsv", "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(maintenance)

driver.quit()
