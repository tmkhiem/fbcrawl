import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.firefox.service import Service

from urllib.parse import urlparse

from datetime import datetime
import os
import csv
import dateparser
from pathlib import Path
import argparse

try:
    with open('path_driver.txt', 'r') as f:
        driver_binary_path = f.read().strip()
except:
    driver_binary_path = 'geckodriver.exe'

try:
    with open('path_firefox.txt', 'r') as f:
        firefox_binary_path = f.read().strip()
except:
    firefox_binary_path = 'App\\Firefox64\\firefox.exe'

parser = argparse.ArgumentParser()
parser.add_argument('input', type=str, help='Path to the input links file')
parser.add_argument('-o', '--output', type=str, help='Path to the output tsv file', default='')
parser.add_argument('-g', '--gecko', type=str, help='Path to the geckodriver', default=driver_binary_path)
parser.add_argument('-f', '--firefox', type=str, help='Path to the firefox binary', default=firefox_binary_path)
args = parser.parse_args()

links_file_to_visit = args.input
if args.output:
    result_file = args.output
else:
    result_file = os.path.join('outputs', os.path.basename(links_file_to_visit.replace('txt', 'tsv')))

print(f' - Loading links from {links_file_to_visit}')

with open(links_file_to_visit, 'r') as f:
    links = [line.strip() for line in f.readlines()]

print(' - Loaded', len(links), 'links')
print(' - Saving results to', result_file)
print()

output_directory = Path('outputs').mkdir(parents=True, exist_ok=True)
previous_results_files = os.listdir('outputs')
previous_results_files = [f for f in previous_results_files if f.endswith('.tsv')]
urls_visited = set()

results = []
previous_results = []

# Check if the result file exists
if not args.output:
    for previous_results_file in previous_results_files:
        try:
            if os.path.isfile(os.path.join('outputs', previous_results_file)):
                # Load all the URLs from the result file
                init_results = os.path.join('outputs', previous_results_file) == result_file

                with open(os.path.join('outputs', previous_results_file), 'r', newline='') as f:
                    reader = csv.reader(f, delimiter='\t')
                    next(reader)  # Skip the header row
                    for row in reader:
                        urls_visited.add(row[0])
                        if init_results:
                            results.append({
                                'url': row[0],
                                'img_url': row[1],
                                'img_date_str': row[2],
                                'year': row[3],
                                'month': row[4],
                                'day': row[5],
                                'hour': row[6],
                                'minute': row[7],
                                'filename': row[8],
                                'error': row[9],
                            })
                
                if init_results>0:
                    print(' - Found previous results file:', previous_results_file, 'with', len(results), 'results')
        except Exception as e:
            print('Error loading result file:', previous_results_file, ' --> skipped')
            continue

options = webdriver.FirefoxOptions()
options.binary_location = args.firefox
options.add_argument('-headless')

browser = webdriver.Firefox(options=options, service=Service(executable_path=args.gecko))

try:
    alert = Alert(browser)
    alert.dismiss()
except NoAlertPresentException:
    pass  # No alert is present, do nothing

try:
    with open('path_driver.txt', 'w') as f:
        f.write(args.gecko)
except:
    pass

try:
    with open('path_firefox.txt', 'w') as f:
        f.write(args.firefox)
except:
    pass

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

xpathCloseButton = '//div[@role="dialog"]//div[@aria-label="Close"]'
xpathDateOuter = "//span/span/a/span"
xpathDateInner = "//span[@role='tooltip']"
xpathImg = "//img[@data-visualcompletion='media-vc-image']"



def visit_link(url: str):    
    browser.get(url)
    time.sleep(0.5)

    closeButton = try_get_element(xpathCloseButton)
    if closeButton is not None:
        print('    [×] Closing dialog...')
        closeButton.click()

    print('    [□] Getting outer date...')
    elementDateOuter = try_get_element(xpathDateOuter)

    print('    [■] Getting inner date...')
    elementDateInner = try_get_element(xpathDateInner, timeout=2, retries=25, refresh_action=lambda: ActionChains(
        browser).move_to_element(elementDateOuter).perform())

    print('    [▒] Getting img...')
    elementImg = try_get_element(xpathImg)

    img_date_str = elementDateInner.text
    img_url = elementImg.get_attribute('src')

    return {"url": url, "img_url": img_url, "img_date_str": img_date_str}

def write_results(result_file, results):
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

try:
    for i in range(len(links)):
        link = links[i]
        
        if link in urls_visited:
            print(f' [ ] Already visited {i+1}/{len(links)}: {link}')
            continue

        print(f' [-]-> Visiting {i+1}/{len(links)}: {link}')

        try:
            result = visit_link(link)
        except Exception as e:
            print(e)
            result = {"url": link, "img_url": '',
                    "img_date_str": '', "error": str(e)}

        results.append(result)

except KeyboardInterrupt:
    print('Interrupted. Saving results and closing browser...')
finally:    
    write_results(result_file, results)
    print(f'Written {len(results)} results to', result_file)

browser.quit()