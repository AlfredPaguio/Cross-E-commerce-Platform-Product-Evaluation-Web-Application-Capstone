import random
import time

from fake_useragent import UserAgent
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

service = Service(ChromeDriverManager().install())

ua = UserAgent()
# user_agent = ua.chrome
mobile_user_agent = [
    'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.61 Mobile ' \
    'Safari/537.36 ',
    'Mozilla/5.0 (Linux; Android 13; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.61 Mobile '
    'Safari/537.36 ',
    'Mozilla/5.0 (Linux; Android 13; SM-A102U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.61 Mobile '
    'Safari/537.36 ',
    'Mozilla/5.0 (Linux; Android 13; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.61 Mobile '
    'Safari/537.36 ',
    'Mozilla/5.0 (Linux; Android 13; SM-N960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.61 Mobile '
    'Safari/537.36 ',
    'Mozilla/5.0 (Linux; Android 13; LM-Q720) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.61 Mobile '
    'Safari/537.36 ',
    'Mozilla/5.0 (Linux; Android 13; LM-X420) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.61 Mobile '
    'Safari/537.36 ',
    'Mozilla/5.0 (Linux; Android 13; LM-Q710(FGN)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.61 Mobile '
    'Safari/537.36 '
]

mobile_emulation = {"deviceName": "iPhone 12 Pro"}
# mobile_emulation = {"deviceName": "Nest Hub"}

options = webdriver.ChromeOptions()

options.add_argument(f'user-agent={random.choice(mobile_user_agent)}')
options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
options.add_argument('--disable-blink-features=AutomationControlled')
# print(user_agent)
options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
options.add_experimental_option("mobileEmulation", mobile_emulation)
options.add_experimental_option('useAutomationExtension', False)
options.headless = True

capabilities = options.to_capabilities()

driver = webdriver.Chrome(options=options, desired_capabilities=capabilities, service=service)

driver.maximize_window()
driver.implicitly_wait(15)

url = 'https://shopee.ph/%E3%80%90Hot-Sale%E3%80%91aquaflask-hydro-flask-tumbler-aqua-flask-thermoflask-tumbler' \
      '-hydroflask-40oz-handle-cover-i.828027281.18763269243?sp_atk=bdb1e81d-de63-4099-972d-f7817497bdd3&xptdk' \
      '=bdb1e81d-de63-4099-972d-f7817497bdd3 '

driver.get(url)
time.sleep(5)
print(driver.page_source)
driver.quit()

