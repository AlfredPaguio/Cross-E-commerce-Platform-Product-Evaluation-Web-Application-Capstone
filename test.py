import time
import json
import os
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from webscraper import sentiment

service = Service(ChromeDriverManager().install())

# random user agent for Chrome
ua = UserAgent()
user_agent = ua.chrome

# emulate mobile view
mobile_emulation = {"deviceName": "iPhone 12 Pro"}

# set chrome options
options = webdriver.ChromeOptions()
options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')

options.add_argument(f'user-agent={user_agent}')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-extensions')
options.add_argument('--disable-logging')
options.add_argument('disable-infobars')
options.add_argument('--disable-notifications')
options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
options.add_experimental_option("mobileEmulation", mobile_emulation)
options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
options.add_experimental_option('useAutomationExtension', False)
# options.headless = True

# set webdriver
driver = webdriver.Chrome(options=options, service=service)
driver.maximize_window()
driver.implicitly_wait(15)

driver.get('https://www.lazada.com.ph/products/fashion-korean-style-bomber-jacket-i433476025-s1573344305.html?spm'
           '=a2o4l.homepwa.jfy.dJFY_all_2.45d8359d6HE9vd&pvid=f4ea0461-528a-4e4a-ac28-6d9b49ef6c65&search=jfy'
           '&channelLpJumpArgs=catIdLv1%3A%3Bhp_click_channelId%3A%3BchannelId%3Acrowd_list%231061013310%3BcategoryId'
           '%3A&scm=1007.17519.162103.0')

time.sleep(3)
soup = BeautifulSoup(driver.page_source, 'lxml')

scripts = soup.find_all('script', type='application/ld+json')

for script in scripts:
    json_object = json.loads(script.text)

    if json_object['@type'] == 'Product':
        gg = json_object['sku']