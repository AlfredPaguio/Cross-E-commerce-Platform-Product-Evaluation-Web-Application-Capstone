import time
import os
import json
import base64

from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.service import Service

from bs4 import BeautifulSoup

# from webdriver_manager.chrome import ChromeDriverManager

from webscraper import sentiment


class Webscraper:
    def __init__(self):
        # service = Service(ChromeDriverManager().install())

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
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-sh-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-logging')
        options.add_argument('disable-infobars')
        options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
        options.add_experimental_option("mobileEmulation", mobile_emulation)
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)

        options.headless = True

        # set webdriver
        self.driver = webdriver.Chrome(executable_path=os.environ.get('CHROMEDRIVER_PATH'), chrome_options=options)
        self.driver.maximize_window()
        self.driver.implicitly_wait(15)
        print('Create scraper instance: Success')

    def land_first_page(self, input_link):
        self.driver.get(input_link)

    # Shopee
    def find_product_info_shopee(self, soup_text):
        print('Getting product info..')

        soup = BeautifulSoup(soup_text, 'lxml')

        prod_name = soup.find('div', class_='_3Iuey2').text

        try:
            prod_price = soup.find('div', class_='_2ebSoR').text
        except AttributeError:
            # prices in flash sales
            prod_price = soup.find('div', class_='_1oOw3J').text

        prod_rating = soup.find('div', class_='u4PHcM').text

        prod_sold = soup.find('div', class_='product-review__sold-count').select_one('div').text
        prod_sold_end = prod_sold.find(' Sold')

        # get description from meta to avoid getting errors when the description from the page is full of images
        prod_desc = soup.find('meta', attrs={'name': 'description'})

        # Shop rating and response rate
        div = soup.find_all('div', class_='_2hdgiL')
        shop_rating = div[1].find_next('div', class_='_2HsjnQ').text
        shop_response_rate = div[2].find_next('div', class_='_2HsjnQ').text

        # Category
        scripts = soup.find_all('script', type='application/ld+json')

        for script in scripts:
            json_object = json.loads(script.text)

            if json_object['@type'] == 'BreadcrumbList':
                category = json_object['itemListElement'][1]['item']['name']
                category_link = json_object['itemListElement'][1]['item']['@id']

        # Image
        prod_image_raw = self.driver.find_element(
            By.CSS_SELECTOR,
            'img[class="product-carousel__item _35N8Pu"]'
        ).screenshot_as_png

        prod_image_encoded = base64.b64encode(prod_image_raw).decode('utf-8')

        print('Getting product info: Success')
        return {
            'prod_name': prod_name,
            'prod_price': prod_price,
            'prod_rating': prod_rating,
            'prod_sold': prod_sold[:prod_sold_end],
            'prod_desc': prod_desc["content"],
            'prod_image': prod_image_encoded,
            'shop_rating': shop_rating,
            'shop_res_rate': shop_response_rate,
            'category': category,
            'category_link': category_link
        }

    def find_product_reviews_shopee(self, url):

        if '/product/' in url:
            # print('mobile url')
            start = url.find('/product/')
            end = url.find('?smtt=0')
            split_ = url[start:end].split('/')

            review_url = f'https://shopee.ph/shop/{split_[2]}/item/{split_[3]}/rating'
        else:
            # print('desktop url')
            start = url.find('-i.')
            end = url.find('?sp_atk')
            split_ = url[start:end].split('.')

            review_url = f'https://shopee.ph/shop/{split_[1]}/item/{split_[2]}/rating'

        self.driver.get(review_url)

        print('Getting Reviews..')
        reviews_loaded = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((
            By.CSS_SELECTOR,
            'div[class="app-container"]'
        )))

        if reviews_loaded:
            print('Reviews loaded: Success')
            print('Running initial loop')
            for _ in range(5):
                reviews = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    'div[class="xSd-kj"]'
                )

                self.driver.execute_script('arguments[0].scrollIntoView(true);', reviews[-1])
                time.sleep(1.5)

                # optimize - need to scroll also less than 50 if total reviews is less than 50
                if len(reviews) >= 50:
                    break

            print('Getting Reviews..')
            time.sleep(3)
            review_soup = BeautifulSoup(self.driver.page_source, 'lxml')
            all_reviews = review_soup.find_all('div', class_='xSd-kj')

            reviews = []
            for review in all_reviews:
                author = review.find_next('div', class_='_33kUIp').text

                date_time = review.find_next('div', class_='yu9aaY').text

                # div.class from inspect element from div.class from driver.page_source is different.
                # used the element from driver.page_source as div.class 'iLqFOu' not working
                try:
                    comment = review.find_next('div', class_='pqiYNA').text
                except AttributeError:
                    comment = review.find_next('div', class_='iLqFOu').text

                review_sentiment = sentiment.do_sentiment(comment)

                reviews.append(
                    {
                        'author': author,
                        'date_time': date_time,
                        'comment': comment,
                        'review_sentiment': review_sentiment
                    }
                )
            print('Getting reviews: Success')
            return reviews

    # ----------------------------------------------------------------------------------------------------------------#

    # Lazada
    def find_product_info_lazada(self, soup_text):
        print('Getting product info..')
        # scroll down to product name to trigger lazy load
        soup = BeautifulSoup(soup_text, 'lxml')

        prod_name = soup.find('h1', class_='pdp-mod-product-title').text

        prod_price = soup.find('div', class_="pdp-mod-product-price").select_one(
            'span', class_='pdp-price pdp-price_type_bold').text

        prod_rating = soup.find('span', class_='review-count').text

        try:
            prod_sold = soup.find('span', class_='crazy-deal-details-soldtext').text
            end = prod_sold.find('sold')
            prod_sold = prod_sold[:end].strip(' ')
        except AttributeError:
            prod_sold = 'Lazada Flash Sale feature only'

        prod_desc = soup.find('meta', attrs={'name': 'og:description'})

        # Shop seller rating and chat response rate
        div = soup.find_all('div', class_="info-content")
        shop_rating = div[0].find_next(['div', 'p'], class_="seller-info-value").text
        shop_response_rate = div[2].find_next(['div', 'p'], class_="seller-info-value").text

        # Category
        scripts = soup.find_all('script', type='application/ld+json')

        for script in scripts:
            json_object = json.loads(script.text)

            if json_object['@type'] == 'BreadcrumbList':
                try:
                    category = json_object['itemListElement'][0]['name']
                    category_link = json_object['itemListElement'][0]['item']
                except IndexError:
                    category = 'Breadcrumblist Empty'
                    category_link = 'BreadCrumbList Empty'

        prod_image_raw = self.driver.find_element(
            By.CSS_SELECTOR,
            'div[class="mod-pdp-item-gallery-inner"]'
        ).screenshot_as_png

        prod_image_encoded = base64.b64encode(prod_image_raw).decode('utf-8')

        print('Getting product info: Success')
        return {
            'prod_name': prod_name,
            'prod_price': prod_price,
            'prod_rating': prod_rating,
            'prod_sold': prod_sold,
            'prod_desc': prod_desc['content'],
            'prod_image': prod_image_encoded,
            'shop_rating': shop_rating,
            'shop_res_rate': shop_response_rate,
            'category': category,
            'category_link': category_link
        }

    def find_product_reviews_lazada(self, shop_id, item_id):
        review_url = f'https://my-m.lazada.com.ph/review/product-reviews?itemId={item_id}&skuId={shop_id}&spm=a2o4l' \
                     f'.pdp_revamp_css.pdp_top_tab.rating_and_review&wh_weex=true '

        self.driver.get(review_url)

        print('Getting Reviews..')
        reviews_loaded = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((
            By.CSS_SELECTOR,
            'div[class="rax-scrollview"]'
        )))

        if reviews_loaded:
            print('Reviews loaded: Success')
            print('Running initial loop')
            for _ in range(5):
                reviews = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    'div[class="review-item"]'
                )

                self.driver.execute_script('arguments[0].scrollIntoView(true);', reviews[-1])
                time.sleep(1.5)

                if len(reviews) == 50:
                    break

            print('Getting Reviews..')
            time.sleep(3)
            review_soup = BeautifulSoup(self.driver.page_source, 'lxml')
            all_reviews = review_soup.find_all('div', class_="review-item")

            reviews = []
            for review in all_reviews:
                spans = review.find_all_next('span')
                author = spans[1].text
                date_time = spans[2].text
                comment = spans[3].text
                review_sentiment = sentiment.do_sentiment(comment)

                reviews.append(
                    {
                        'author': author,
                        'date_time': date_time,
                        'comment': comment,
                        'review_sentiment': review_sentiment
                    }
                )
            print('Getting reviews: Success')
            return reviews
