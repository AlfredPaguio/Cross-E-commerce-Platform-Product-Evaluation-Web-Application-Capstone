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


class Webscraper:
    def __init__(self):
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
        self.driver = webdriver.Chrome(options=options, service=service)
        self.driver.maximize_window()
        self.driver.implicitly_wait(15)
        print('Create scraper instance: Success')

    def land_first_page(self, input_link):
        self.driver.get(input_link)

    # Shopee
    def find_product_info_shopee(self):
        print('Getting product info..')

        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        try:
            prod_name = soup.find('div', class_='_26jnYM typo-r16 two-line-text').text
        except AttributeError:
            # Mall
            prod_name = soup.find('div', class_='JuNyef').text

        try:
            prod_price = soup.find('div', class_='GNcIuD typo-m18').text
        except AttributeError:
            prod_price = soup.find('div', class_='_1oOw3J').text

        prod_rating = soup.find('div', class_='E35R5h').text

        prod_sold = soup.find('div', class_='product-review__sold-count').select_one('div').text
        prod_sold_end = prod_sold.find(' Sold')

        # get description from meta to avoid getting errors when the description from the page is full of images
        prod_desc = soup.find('meta', attrs={'name': 'description'})

        # Shop rating and response rate
        div = soup.find_all('div', class_='Mh34aP')
        shop_rating = div[1].find_next('div', class_='Y9Ery0').text
        shop_response_rate = div[2].find_next('div', class_='Y9Ery0').text

        # Category
        scripts = soup.find_all('script', type='application/ld+json')

        for script in scripts:
            json_object = json.loads(script.text)

            if json_object['@type'] == 'BreadcrumbList':
                category = json_object['itemListElement'][1]['item']['name']
                category_link = json_object['itemListElement'][1]['item']['@id']

        # Image
        # prod_image_raw = self.driver.find_element(
        #     By.CSS_SELECTOR,
        #     'div[class="stardust-carousel"]'
        # ).screenshot_as_png
        #
        # prod_image_encoded = base64.b64encode(prod_image_raw).decode('utf-8')

        try:
            prod_image_ = soup.find('img', class_='product-carousel__item _1AkNaT')

            try:
                prod_image = prod_image_['src']
            except TypeError:
                prod_image = "url_for('static',filename='images/broken-image.png')"

        except AttributeError:
            prod_image_ = soup.find('video', class_='product-video__video')

            try:
                prod_image = prod_image_['poster']
            except TypeError:
                prod_image = "url_for('static',filename='images/broken-image.png')"

        print('Getting product info: Success')
        return {
            'prod_name': prod_name,
            'prod_price': prod_price,
            'prod_rating': prod_rating,
            'prod_sold': prod_sold[:prod_sold_end],
            'prod_desc': prod_desc["content"],
            'prod_image': prod_image,
            'shop_rating': shop_rating,
            'shop_res_rate': shop_response_rate,
            'category': category,
            'category_link': category_link,
            'sku': 'Lazada Only'
        }

    def find_product_reviews_shopee(self):
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
        # time.sleep(2)
        review_soup = BeautifulSoup(self.driver.page_source, 'lxml')
        all_reviews = review_soup.find_all('div', class_='xSd-kj')

        reviews = []
        for review in all_reviews[:50]:
            author = review.find_next('div', class_='_33kUIp').text

            date_time = review.find_next('div', class_='yu9aaY').text

            # div.class from inspect element from div.class from driver.page_source is different.
            # used the element from driver.page_source as div.class 'iLqFOu' not working
            try:
                comment = review.find_next('div', class_='iLqFOu').text
            except AttributeError:
                comment = review.find_next('div', class_='pqiYNA').text

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

    def find_recommendations_shopee(self):
        scroll = self.driver.find_elements(
            By.CSS_SELECTOR,
            'div[class="item-card-list__item-card-wrapper"]'
        )

        print('Running initial loop')
        if scroll:
            add = 3
            for _ in range(5):
                self.driver.execute_script('arguments[0].scrollIntoView(true);', scroll[add])
                add += 3
                time.sleep(1.5)

        # time.sleep(3)
        soup = BeautifulSoup(self.driver.page_source, 'lxml')

        recommended_products = soup.find_all('div', class_='item-card-list__item-card-wrapper')

        print('Getting product recommendations..')

        recommended_products_list = []
        for recommended in recommended_products:
            if recommended.text == '':
                continue
            else:
                link = recommended.find_next('a', href=True)
                name = recommended.find_next('div', class_='tu81r+ OTeZxR').text
                price = recommended.find_next('div', class_='Mf5O4D yEHyRY').text
                image = recommended.find_next('img', class_='gO-UHJ c63hlp')

                recommended_products_list.append(
                    {
                        'recommendation_link': f'https://shopee.ph{link["href"]}',
                        'recommendation_name': name,
                        'recommendation_price': price,
                        'recommendation_image': image['src']
                    }
                )
        print('Getting product recommendations: Success')
        return recommended_products_list

    # ----------------------------------------------------------------------------------------------------------------#

    # Lazada
    def find_product_info_lazada(self):
        print('Getting product info..')
        # scroll down to product name to trigger lazy load
        soup = BeautifulSoup(self.driver.page_source, 'lxml')

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

            if json_object['@type'] == 'Product':
                sku = json_object['sku']

        try:
            prod_image_ = soup.find('div', class_='mod-pdp-item-gallery-video-item').find('img')
            prod_image = prod_image_['src']
        except AttributeError:
            prod_image_ = soup.find('div', class_='slick-slide slick-active').find('img')
            prod_image = prod_image_['src']

        # prod_image_raw = self.driver.find_element(
        #     By.CSS_SELECTOR,
        #     'div[class="mod-pdp-item-gallery-inner"]'
        # ).screenshot_as_png
        #
        # prod_image_encoded = base64.b64encode(prod_image_raw).decode('utf-8')

        print('Getting product info: Success')
        return {
            'prod_name': prod_name,
            'prod_price': prod_price,
            'prod_rating': prod_rating,
            'prod_sold': prod_sold,
            'prod_desc': prod_desc['content'],
            'prod_image': prod_image,
            'shop_rating': shop_rating,
            'shop_res_rate': shop_response_rate,
            'category': category,
            'category_link': category_link,
            'sku': sku
        }

    def find_product_reviews_lazada(self):
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
        # time.sleep(2)
        review_soup = BeautifulSoup(self.driver.page_source, 'lxml')
        all_reviews = review_soup.find_all('div', class_="review-item")

        reviews = []
        for review in all_reviews[:50]:
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

    def find_recommendations_lazada(self):
        print('Running initial loop')
        scroll = self.driver.find_elements(
            By.CSS_SELECTOR,
            'div[class="product-card__container "]'
        )

        if scroll:
            add = 3
            for _ in range(5):
                self.driver.execute_script('arguments[0].scrollIntoView(true);', scroll[add])
                add += 3
                time.sleep(1.5)

        soup = BeautifulSoup(self.driver.page_source, 'lxml')

        recommended_products = soup.find_all('div', class_='product-card__container')

        print('Getting product recommendations..')

        recommended_products_list = []
        for recommended in recommended_products:

            image_ = recommended.find_next('div', class_='picture-wrapper')
            image = image_.find('img', class_='image image_loaded')

            if image is None:
                continue
            else:
                link = recommended.find_next('a', href=True)
                name = recommended.find_next('div', class_='product-card__name').text
                price = recommended.find_next('span', class_='product-card__price-current').text

                recommended_products_list.append(
                    {
                        'recommendation_link': f'https:{link["href"]}',
                        'recommendation_name': name,
                        'recommendation_price': price,
                        'recommendation_image': image['src']
                    }
                )

        print('Getting product recommendations: Success')
        return recommended_products_list
