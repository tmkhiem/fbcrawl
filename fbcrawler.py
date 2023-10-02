import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoAlertPresentException

from urllib.parse import urlparse

from datetime import datetime
import os
import csv
import sys
import dateparser

links_file_to_visit = sys.argv[1]
result_file = links_file_to_visit.replace('txt', 'tsv')
print(f'Loading links from {links_file_to_visit} --> {result_file}')

with open(links_file_to_visit, 'r') as f:
    links = [line.strip() for line in f.readlines()]

previous_results_files = os.listdir()
previous_results_files = [f for f in previous_results_files if f.endswith('.tsv')]

# Check if the result file exists
for previous_results_file in previous_results_files:
    try:
        if os.path.isfile(result_file):
            # Load all the URLs from the result file
            urls_visited = set()
            with open(result_file, 'r', newline='') as f:
                reader = csv.reader(f, delimiter='\t')
                next(reader)  # Skip the header row
                for row in reader:
                    urls_visited.add(row[0])
    except:
        print('Error loading result file:', result_file)
        continue

options = webdriver.FirefoxOptions()
options.binary_location = r"D:\tools\FirefoxPortable\App\Firefox64\firefox.exe"
options.headless = True

browser = webdriver.Firefox(options=options)

try:
    alert = Alert(browser)
    alert.dismiss()
except NoAlertPresentException:
    pass  # No alert is present, do nothing


def parse_time(timestr: str) -> datetime:
    return dateparser.parse(timestr)

def try_get_element(xpath, retries=3, timeout=10, refresh_action=None):
    for retry in range(retries):
        try:
            if refresh_action is not None:
                refresh_action()
            element = WebDriverWait(browser, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            return element
        except TimeoutException:
            print('Retry', retry)
            time.sleep(0.5)


#xpathDateOuter = "//span[contains(text(), 'Tháng')]"
xpathCloseButton = '//div[@role="dialog"]//div[@aria-label="Close"]//i'
xpathDateOuter = "//span/span/a/span"
xpathDateInner = "//span[@role='tooltip']"
xpathImg = "//img[@data-visualcompletion='media-vc-image']"

results = []

def visit_link(url: str):    
    browser.get(url)
    time.sleep(0.5)

    closeButton = try_get_element(xpathCloseButton)
    if closeButton is not None:
        print('Closing dialog...')
        closeButton.click()

    print('Getting outer...')
    elementDateOuter = try_get_element(xpathDateOuter)

    print('Getting inner...')
    elementDateInner = try_get_element(xpathDateInner, timeout=2, retries=25, refresh_action=lambda: ActionChains(
        browser).move_to_element(elementDateOuter).perform())

    print('Getting img...')
    elementImg = try_get_element(xpathImg)

    img_date_str = elementDateInner.text

    img_url = elementImg.get_attribute('src')

    return {"url": url, "img_url": img_url, "img_date_str": img_date_str}


for i in range(len(links)):
    link = links[i]
    
    if link in urls_visited:
        print(f'Already visited {i+1}/{len(links)}: {link}')
        continue

    print(f'Visiting {i+1}/{len(links)}: {link}')

    try:
        result = visit_link(link)
    except Exception as e:
        print(e)
        result = {"url": link, "img_url": '',
                  "img_date_str": '', "error": str(e)}

    results.append(result)

    with open(result_file, 'w', newline='\n', encoding='utf8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['url', 'img_url', 'date_str', 'year',
                        'month', 'day', 'hour', 'minute', 'filename', 'error'])
        for result in results:

            try:
                if result['img_date_str']:
                    img_date = parse_time(result['img_date_str'])
                else:
                    img_date = datetime(1970, 1, 1)
            except:
                img_date = datetime(1970, 1, 1)

            try:
                filename = os.path.basename(urlparse(result['img_url']).path)
            except:
                filename = ''

            writer.writerow([
                result['url'],
                result['img_url'],
                result['img_date_str'],
                img_date.year,
                img_date.month,
                img_date.day,
                img_date.hour,
                img_date.minute,
                filename,
                ''])

browser.quit()
