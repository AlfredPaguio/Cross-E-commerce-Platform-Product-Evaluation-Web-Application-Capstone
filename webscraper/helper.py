import re
import pandas as pd
from urllib.parse import urlparse
from flask import session
from webscraper.productdetails import ProductDetails
from webscraper import db
import random
import string


class UrlHelper():
    # def __init__(self): do nothing

    # topic : https://stackoverflow.com/questions/205923/best-way-to-handle-security-and-avoid-xss-with-user-entered
    # -urls answer : https://stackoverflow.com/a/205967
    def sanitizeUrl(self, url: str):
        return re.sub(r"[^-A-Za-z0-9+&@#/%?=~_|!:,.;\(\)]", "", url)

    # https://docs.python.org/3/library/urllib.parse.html
    def rebuild_url(self, url: str):
        sanitized_url = self.sanitizeUrl(url)
        parsed_url = urlparse(sanitized_url)._replace(query='', fragment='', params='')
        return parsed_url.geturl()

    def get_hostname(self, url: str):
        return urlparse(url).hostname or ''


class HelpMe():

    # https://stackoverflow.com/questions/4391697/find-the-index-of-a-dict-within-a-list-by-matching-the-dicts-value
    # modified 
    # See /tests/find_index_of_dictionary.py for example
    def dict_isvalue_exist(self, _list, _key, value):
        for i, _dictionary in enumerate(_list):
            if _dictionary[_key] == value:
                return True
        return False

    def list_find_index_of_dict(self, lst, key, value):
        for i, dic in enumerate(lst):
            if dic[key] == value:
                return i
        return 0

    def reorder_list_of_products(self, product: ProductDetails):
        if session['list_of_products']:
            if len(session['list_of_products']) > 1:
                session['list_of_products'].insert(0, product.get_details)
                session['list_of_products'].pop(2)
            else:
                session['list_of_products'].insert(0, product.get_details)
        else:
            session['list_of_products'].append(product.get_details)

    # from https://www.geeksforgeeks.org/create-a-random-password-generator-using-python/
    # modified, ayoko na magisip lol
    def generate_random_password(self):
        password_length = 12

        characterList = "" + string.ascii_letters + string.digits + string.punctuation

        password = []

        for i in range(password_length):
            # Picking a random character from our
            # character list
            randomchar = random.choice(characterList)

            # appending a random character to password
            password.append(randomchar)
        return "".join(password)  # return array as string


class SummarizeThis:
    def get_percentage_of_sentiments(self, product_id, product_index):
        reviews_query = pd.read_sql(f'SELECT product_id, review_sentiment FROM product_data_reviews_table WHERE '
                                    f'product_id == {session["list_of_products"][product_index].get("product_id")}'
                                    f' LIMIT 50', db.session.bind)
        review_data = pd.DataFrame(reviews_query)

        review_index = review_data.loc[
            review_data['product_id'] == session["list_of_products"][product_index].get('product_id')]
        review_index_df = review_index.groupby(['review_sentiment'], as_index=False).size()
        review_index_df['percentage'] = (review_index_df['size'] / review_index_df['size'].sum() * 100).round(2)

        new_review_df = pd.DataFrame(review_index_df.sort_values('review_sentiment', ascending=False))
        new_review_dict = new_review_df.to_dict('records')

        return new_review_dict
