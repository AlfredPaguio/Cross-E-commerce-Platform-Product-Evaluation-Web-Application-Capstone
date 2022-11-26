import time
import pandas as pd
from flask import flash, redirect, render_template, request, url_for, session
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message
from password_strength import PasswordPolicy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from wtforms import Label

from webscraper import app, db, mail
from webscraper.forms import (AddToFavoritesForm, ForgotPasswordForm,
                              LoginForm, RegisterForm, RemoveToFavoritesForm,
                              ReplaceProductModalForm, UpdateProductModalForm, ChangePasswordForm, LoadReviewsForm,
                              LoadRecommendedProductsForm, ViewRecommendedProductForm)
from webscraper.helper import HelpMe, UrlHelper, SummarizeThis
from webscraper.models import (ProductDataReviewsTable, ProductDataTable,
                               ProductDetailsTable, User)
from webscraper.productdetails import ProductDetails
from webscraper.webscraper import Webscraper


def get_reviews(reviews=None, offset=0, per_page=5):
    return reviews[offset: offset + per_page]


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard_page():
    add_to_favorites_form = AddToFavoritesForm()
    remove_to_favorites_form = RemoveToFavoritesForm()
    replace_product_modal_form = ReplaceProductModalForm()
    update_product_modal_form = UpdateProductModalForm()
    load_recommended_products_form = LoadRecommendedProductsForm()
    view_recommended_products_form = ViewRecommendedProductForm()
    load_reviews_form = LoadReviewsForm()

    if session.get('list_of_products') is None:
        session['list_of_products'] = []

    if session.get('reviews_1') is None:
        session['reviews_1'] = []

    if session.get('reviews_2') is None:
        session['reviews_2'] = []

    if session.get('reviews_summary_1') is None:
        session['reviews_summary_1'] = []

    if session.get('reviews_summary_2') is None:
        session['reviews_summary_2'] = []

    if session.get('recommended_1') is None:
        session['recommended_1'] = []

    if session.get('recommended_2') is None:
        session['recommended_2'] = []

    if request.method == 'POST':
        # Scraper Logic
        if request.args.get("req") == "search":
            _link = request.form.get('inputLink')
            url_helper = UrlHelper()
            input_link = url_helper.rebuild_url(_link)
            what_hostname = url_helper.get_hostname(input_link)
            supported_sites = {"shopee.ph", "www.lazada.com.ph"}

            if what_hostname in supported_sites:

                # check if product is already in the view
                helpme = HelpMe()
                in_dict = helpme.dict_isvalue_exist(session['list_of_products'], "link", input_link)

                if in_dict:
                    flash(f'This product is already on the view.', category='info')
                    return redirect(url_for('dashboard_page'))

                exists_in_current_user = db.session.query(ProductDataTable, ProductDetailsTable).filter(
                    ProductDetailsTable.product_link == input_link,
                    ProductDataTable.user_id == current_user.id
                ).join(ProductDetailsTable).first()

                exist_in_database = db.session.query(ProductDataTable, ProductDetailsTable).filter(
                    ProductDetailsTable.product_link == input_link
                ).join(ProductDetailsTable).first()

                # data existing in current_user
                if exists_in_current_user is not None:
                    _product = ProductDetails(product_id=exists_in_current_user[0].product_id,
                                              product_name=exists_in_current_user[1].product_name,
                                              product_price=exists_in_current_user[1].product_price,
                                              product_rating=exists_in_current_user[1].product_rating,
                                              product_sold=exists_in_current_user[1].product_sold,
                                              product_description=exists_in_current_user[1].product_description,
                                              product_image=exists_in_current_user[1].product_image,
                                              shop_rating=exists_in_current_user[1].shop_rating,
                                              shop_response_rate=exists_in_current_user[1].shop_response_rate,
                                              product_link=exists_in_current_user[1].product_link,
                                              target_website=exists_in_current_user[1].target_website,
                                              category_link=exists_in_current_user[1].category_link,
                                              product_data_owner=current_user.id)

                    # list indexing
                    helpme = HelpMe()
                    helpme.reorder_list_of_products(_product)
                    session.pop('reviews_1')
                    session.pop('reviews_2')
                    session.pop('recommended_1')
                    session.pop('recommended_2')
                    session.pop('reviews_summary_1')
                    session.pop('reviews_summary_2')
                    flash(f'This product is loaded from the database, product information might be outdated',
                          category='info')
                    flash(f'Press the "Update" button if you want to update the product information',
                          category='info')
                    return redirect(url_for('dashboard_page', ))

                # data not existing in current_user, but existing in other user
                elif exist_in_database is not None:

                    # get product info from database
                    # add new entry for current user referencing the product_id from product_details
                    prod_data = ProductDataTable(product_id=exist_in_database[0].product_id,
                                                 user_id=current_user.id)

                    db.session.add(prod_data)
                    db.session.commit()

                    _product = ProductDetails(product_id=exist_in_database[0].product_id,
                                              product_name=exist_in_database[1].product_name,
                                              product_price=exist_in_database[1].product_price,
                                              product_rating=exist_in_database[1].product_rating,
                                              product_sold=exist_in_database[1].product_sold,
                                              product_description=exist_in_database[1].product_description,
                                              product_image=exist_in_database[1].product_image,
                                              shop_rating=exist_in_database[1].shop_rating,
                                              shop_response_rate=exist_in_database[1].shop_response_rate,
                                              product_link=exist_in_database[1].product_link,
                                              target_website=exist_in_database[1].target_website,
                                              category_link=exist_in_database[1].category_link,
                                              product_data_owner=current_user.id)

                    # list indexing
                    helpme = HelpMe()
                    helpme.reorder_list_of_products(_product)
                    session.pop('reviews_1')
                    session.pop('reviews_2')
                    session.pop('recommended_1')
                    session.pop('recommended_2')
                    session.pop('reviews_summary_1')
                    session.pop('reviews_summary_2')

                    flash(f'This product is loaded from the database, product information might be outdated',
                          category='info')
                    flash(f'Press the "Update" button if you want to update the product information',
                          category='info')
                    return redirect(url_for('dashboard_page'))

                # data not existing in current_user, not existing in other users, run scraper
                else:
                    scraper = Webscraper()
                    scraper.land_first_page(input_link)

                    is_loaded = None
                    time_out = 10

                    try:
                        is_loaded = WebDriverWait(scraper.driver, time_out).until(
                            EC.visibility_of_element_located(
                                (By.CSS_SELECTOR,
                                 'div[class="app-container"]' if "shopee.ph" in what_hostname else 'div[id="container"]'
                                 )))
                    except TimeoutException:
                        flash("Timed out: Waiting for target page to load took to long.",
                              category='danger')
                        scraper.driver.quit()
                        return redirect(url_for('dashboard_page'))
                    finally:
                        if is_loaded:
                            time.sleep(3)
                            # Getting Product Information
                            try:
                                link = scraper.driver.current_url

                                prod_info = scraper.find_product_info_shopee() if 'shopee.ph' in what_hostname \
                                    else scraper.find_product_info_lazada()

                                if what_hostname == 'shopee.ph':
                                    target_website = 'Shopee'
                                else:
                                    target_website = 'Lazada'

                                # adding new product to database
                                prod_details = ProductDetailsTable(product_link=link,
                                                                   product_name=prod_info.get('prod_name'),
                                                                   product_price=prod_info.get('prod_price'),
                                                                   product_rating=prod_info.get('prod_rating'),
                                                                   product_sold=prod_info.get('prod_sold'),
                                                                   product_description=prod_info.get('prod_desc'),
                                                                   product_image=prod_info.get('prod_image'),
                                                                   shop_rating=prod_info.get('shop_rating'),
                                                                   shop_response_rate=prod_info.get('shop_res_rate'),
                                                                   category=prod_info.get('category'),
                                                                   category_link=prod_info.get('category_link'),
                                                                   target_website=target_website)
                                db.session.add(prod_details)

                                # adds the prod_details as "PENDING" into the database. will not persist
                                # into the database until db.session.commit() is called..
                                # this is needed to avoid product_details.product_id returning none
                                db.session.flush()

                                # referencing new product to current user
                                prod_data = ProductDataTable(product_id=prod_details.product_id,
                                                             user_id=current_user.id)
                                db.session.add(prod_data)
                                db.session.commit()

                                that_product = ProductDetails(product_id=prod_details.product_id,
                                                              product_name=prod_details.product_name,
                                                              product_price=prod_details.product_price,
                                                              product_rating=prod_details.product_rating,
                                                              product_sold=prod_details.product_sold,
                                                              product_description=prod_details.product_description,
                                                              product_image=prod_details.product_image,
                                                              shop_rating=prod_details.shop_rating,
                                                              shop_response_rate=prod_details.shop_response_rate,
                                                              product_link=prod_details.product_link,
                                                              target_website=prod_details.target_website,
                                                              category_link=prod_details.category_link,
                                                              product_data_owner=current_user.id)

                                # list indexing
                                helpme = HelpMe()
                                helpme.reorder_list_of_products(that_product)
                                session.pop('reviews_1')
                                session.pop('reviews_2')
                                session.pop('recommended_1')
                                session.pop('recommended_2')
                                session.pop('reviews_summary_1')
                                session.pop('reviews_summary_2')

                                # Check if webdriver is undetected
                                status = scraper.driver.execute_script('return navigator.webdriver')
                                print(f'Webdriver status: {status}')

                                # Close headless browser and webdriver instance gracefully
                                scraper.driver.quit()

                                flash(f'Displaying product information from {what_hostname}', category='success')
                                return redirect(url_for('dashboard_page'))

                            except AttributeError as e:
                                print(e)
                                flash("Something went wrong.", category='danger')
                                scraper.driver.quit()
                                return redirect(url_for('dashboard_page'))
            else:
                flash(f'This host: {what_hostname}, is not a link either from Shopee or Lazada.', category='danger')
                return redirect(url_for('dashboard_page'))

        # Update Product Logic
        if request.args.get("req") == "update_product":
            selected_product = request.form.get('selected_product')
            product_on_database = db.session.query(ProductDetailsTable).filter(
                ProductDetailsTable.product_id == selected_product
            ).first()

            if product_on_database is not None:
                scraper = Webscraper()
                scraper.land_first_page(product_on_database.product_link)

                is_loaded = None
                time_out = 10
                url_helper = UrlHelper()
                what_hostname = url_helper.get_hostname(product_on_database.product_link)
                try:
                    is_loaded = WebDriverWait(scraper.driver, time_out).until(
                        EC.visibility_of_element_located(
                            (By.CSS_SELECTOR,
                             'div[class="app-container"]' if "shopee.ph" in what_hostname else 'div[id="root"]'
                             )))
                except TimeoutException:
                    flash("Timed out: Waiting for target page to load took to long.",
                          category='danger')
                    scraper.driver.quit()
                    return redirect(url_for('dashboard_page'))
                finally:
                    print(scraper.driver.title)
                    if is_loaded:
                        time.sleep(3)
                        # Getting Product Information
                        try:

                            prod_info = scraper.find_product_info_shopee() if 'shopee.ph' in what_hostname \
                                else scraper.find_product_info_lazada()

                            if what_hostname == 'shopee.ph':
                                target_website = 'Shopee'
                            else:
                                target_website = 'Lazada'
                                # adding new product to database

                            product_on_database.product_name = prod_info.get('prod_name')
                            product_on_database.product_price = prod_info.get('prod_price')
                            product_on_database.product_rating = prod_info.get('prod_rating')
                            product_on_database.product_sold = prod_info.get('prod_sold')
                            product_on_database.product_description = prod_info.get('prod_desc')
                            product_on_database.product_image = prod_info.get('prod_image')
                            product_on_database.shop_rating = prod_info.get('shop_rating')
                            product_on_database.shop_response_rate = prod_info.get('shop_res_rate')
                            product_on_database.category = prod_info.get('category')
                            product_on_database.category_link = prod_info.get('category_link')
                            product_on_database.target_website = target_website

                            helpme = HelpMe()
                            in_dict = helpme.dict_isvalue_exist(session['list_of_products'], "link",
                                                                product_on_database.product_link)

                            if in_dict:
                                i = helpme.list_find_index_of_dict(session['list_of_products'], "link",
                                                                   product_on_database.product_link)
                                session['list_of_products'][i].update({"name": product_on_database.product_name})
                                session['list_of_products'][i].update({"price": product_on_database.product_price})
                                session['list_of_products'][i].update(
                                    {"rating": product_on_database.product_rating})
                                session['list_of_products'][i].update({"sold": product_on_database.product_sold})
                                session['list_of_products'][i].update(
                                    {"description": product_on_database.product_description})
                                session['list_of_products'][i].update(
                                    {"product_image": product_on_database.product_image})
                                session['list_of_products'][i].update(
                                    {"shop_rating": product_on_database.shop_rating})
                                session['list_of_products'][i].update(
                                    {"shop_response_rate": product_on_database.shop_response_rate})

                            db.session.commit()  # commit

                            # Check if webdriver is undetected
                            status = scraper.driver.execute_script('return navigator.webdriver')
                            print(f'Webdriver status: {status}')

                            # Close headless browser and webdriver instance gracefully
                            scraper.driver.quit()

                            flash(f"Product {product_on_database.product_name} successfully updated.",
                                  category='success')
                            return redirect(url_for('dashboard_page'))

                        except AttributeError as e:  # TimeoutError
                            print(e)
                            flash("Something went wrong.", category='danger')
                            db.session.rollback()  # nag ka error kaya rerevert yung data sa database or shit
                            scraper.driver.quit()
                            return redirect(url_for('dashboard_page'))

        # Load Reviews Logic
        if request.args.get('req') == "load_reviews":
            get_percentage = SummarizeThis()
            url_helper = UrlHelper()

            load_review_link = request.form.get('load_review_link')
            load_review_index = int(request.form.get('load_review_index'))
            load_review_item = int(request.form.get('load_review_item'))

            list_of_reviews = db.session.query(ProductDataReviewsTable).filter(
                ProductDataReviewsTable.product_id == load_review_item
            ).limit(50)

            if list_of_reviews.first() is None:
                scraper = Webscraper()
                what_hostname = url_helper.get_hostname(load_review_link)

                if what_hostname == 'shopee.ph':
                    start = load_review_link.find('-i.')
                    split_ = load_review_link[start:].strip(' ').split('.')

                    review_link = f'https://shopee.ph/shop/{split_[1]}/item/{split_[2]}/rating'
                else:
                    end = load_review_link.find('.html')
                    split = load_review_link[:end].split('-')

                    shop_id = split[-1].strip(split[-1][0])
                    item_id = split[-2].strip(split[-2][0])

                    review_link = f'https://my-m.lazada.com.ph/review/product-reviews?itemId={item_id}&skuId=' \
                                  f'{shop_id}&spm=a2o4l.pdp_revamp_css.pdp_top_tab.rating_and_review&wh_weex=true '

                # run new scraper
                scraper.land_first_page(review_link)
                reviews_loaded = None

                try:
                    print('Getting Reviews..')
                    reviews_loaded = WebDriverWait(scraper.driver, 10).until(EC.visibility_of_element_located((
                        By.CSS_SELECTOR, 'div[class="app-container"]' if "shopee.ph" in what_hostname
                        else 'div[class="rax-scrollview"]'
                    )))
                except TimeoutException:
                    flash("Timed out: Waiting for target page to load took to long.",
                          category='danger')
                    scraper.driver.quit()
                    return redirect(url_for('dashboard_page'))
                finally:
                    if reviews_loaded:
                        time.sleep(3)
                        print('Reviews loaded: Success')
                        try:
                            reviews = scraper.find_product_reviews_shopee() if 'shopee.ph' in what_hostname else \
                                scraper.find_product_reviews_lazada()

                            for review in reviews:
                                review_data = ProductDataReviewsTable(product_id=load_review_item,
                                                                      review_author=review.get('author'),
                                                                      review_data_time=review.get('date_time'),
                                                                      review_comment=review.get('comment'),
                                                                      review_sentiment=review.get(
                                                                          'review_sentiment')
                                                                      )
                                db.session.add(review_data)
                            db.session.commit()

                            new_reviews = db.session.query(ProductDataReviewsTable).filter(
                                ProductDataReviewsTable.product_id == load_review_item
                            ).limit(50)

                            print(new_reviews)

                            if load_review_index == 0:
                                for reviews in new_reviews:
                                    session['reviews_1'].append(reviews)

                                review_summary = get_percentage.get_percentage_of_sentiments(
                                    product_index=load_review_index)
                                session['reviews_summary_1'] = review_summary

                            else:
                                for reviews in new_reviews:
                                    session['reviews_2'].append(reviews)

                                review_summary = get_percentage.get_percentage_of_sentiments(
                                    product_index=load_review_index)
                                session['reviews_summary_2'] = review_summary

                            # Check if webdriver is undetected
                            status = scraper.driver.execute_script('return navigator.webdriver')
                            print(f'Webdriver status: {status}')

                            # Close headless browser and webdriver instance gracefully
                            scraper.driver.quit()

                            flash(f"Reviews loaded successfully", category='success')
                            return redirect(url_for('dashboard_page'))
                        except AttributeError:
                            if load_review_index == 0:
                                session.pop('reviews_summary_1')
                            else:
                                session.pop('reviews_summary_2')

                            flash("Something went wrong.", category='danger')
                            scraper.driver.quit()
                            return redirect(url_for('dashboard_page'))
            else:
                if load_review_index == 0:
                    for reviews in list_of_reviews:
                        session['reviews_1'].append(reviews)

                    review_summary = get_percentage.get_percentage_of_sentiments(product_index=load_review_index)
                    session['reviews_summary_1'] = review_summary
                else:
                    for reviews in list_of_reviews:
                        session['reviews_2'].append(reviews)

                    review_summary = get_percentage.get_percentage_of_sentiments(product_index=load_review_index)
                    session['reviews_summary_2'] = review_summary

                flash(f"Reviews loaded successfully", category='success')
                return redirect(url_for('dashboard_page'))

        # Load Recommended Products Logic
        if request.args.get("req") == "load_recommended_products":
            load_product_category_link = request.form.get('load_product_category_link')
            load_product_index = int(request.form.get('load_product_index'))

            if load_product_category_link == 'BreadCrumbList Empty':
                flash(f"Something went wrong, can't load recommended products. "
                      f"Please check the original website instead", category='danger')
                return redirect(url_for('dashboard_page'))
            else:
                url_helper = UrlHelper()
                scraper = Webscraper()

                # run new scraper
                what_hostname = url_helper.get_hostname(load_product_category_link)

                scraper.land_first_page(load_product_category_link)
                recommended_products_loaded = None
                try:
                    print('Getting recommended products..')
                    recommended_products_loaded = WebDriverWait(scraper.driver, 10).until(
                        EC.visibility_of_element_located((
                            By.CSS_SELECTOR, 'div[class="app-container"]' if "shopee.ph" in what_hostname
                            else 'div[class="content-list"]'
                        )))
                except TimeoutException:
                    flash("Timed out: Waiting for target page to load took to long.",
                          category='danger')
                    scraper.driver.quit()
                    return redirect(url_for('dashboard_page'))
                finally:
                    time.sleep(3)
                    if recommended_products_loaded:
                        try:
                            recommended_products = scraper.find_recommendations_shopee() if 'shopee.ph' in \
                                                    what_hostname else scraper.find_recommendations_lazada()

                            if load_product_index == 0:
                                session['recommended_1'] = recommended_products
                            else:
                                session['recommended_2'] = recommended_products

                            scraper.driver.quit()
                            flash("Recommended products loaded successfully", category='success')
                            return redirect(url_for('dashboard_page'))
                        except AttributeError as e:
                            print(e)
                            flash("Something went wrong.", category='danger')
                            scraper.driver.quit()
                            return redirect(url_for('dashboard_page'))

        # View Recommended Products Logic
        if request.args.get("req") == "view_recommended_product":
            view_product_index = request.form.get('view_product_index')
            recommended_item_link = request.form.get('recommended_item_link')

            url_helper = UrlHelper()
            input_link = url_helper.rebuild_url(recommended_item_link)
            what_hostname = url_helper.get_hostname(input_link)

            helpme = HelpMe()
            in_dict = helpme.dict_isvalue_exist(session['list_of_products'], "link", input_link)

            if in_dict:
                flash(f'This product is already on the view.', category='info')
                return redirect(url_for('dashboard_page'))

            exists_in_current_user = db.session.query(ProductDataTable, ProductDetailsTable).filter(
                ProductDetailsTable.product_link == input_link,
                ProductDataTable.user_id == current_user.id
            ).join(ProductDetailsTable).first()

            exist_in_database = db.session.query(ProductDataTable, ProductDetailsTable).filter(
                ProductDetailsTable.product_link == input_link
            ).join(ProductDetailsTable).first()

            # checking if product is in database or not
            if exists_in_current_user is not None:
                _product = ProductDetails(product_id=exists_in_current_user[0].product_id,
                                          product_name=exists_in_current_user[1].product_name,
                                          product_price=exists_in_current_user[1].product_price,
                                          product_rating=exists_in_current_user[1].product_rating,
                                          product_sold=exists_in_current_user[1].product_sold,
                                          product_description=exists_in_current_user[1].product_description,
                                          product_image=exists_in_current_user[1].product_image,
                                          shop_rating=exists_in_current_user[1].shop_rating,
                                          shop_response_rate=exists_in_current_user[1].shop_response_rate,
                                          product_link=exists_in_current_user[1].product_link,
                                          target_website=exists_in_current_user[1].target_website,
                                          category_link=exists_in_current_user[1].category_link,
                                          product_data_owner=current_user.id)

                if len(session['list_of_products']) > 1:

                    if int(view_product_index) == 0:
                        session.pop('reviews_1')
                        session.pop('recommended_1')
                        session.pop('reviews_summary_1')
                    else:
                        session.pop('reviews_2')
                        session.pop('recommended_2')
                        session.pop('reviews_summary_2')

                    session['list_of_products'][int(view_product_index)] = _product.get_details

                    flash(f"Replace success", category='success')
                    return redirect(url_for('dashboard_page'))
                else:
                    session['list_of_products'].append(_product.get_details)
                    flash(f'Showing {exists_in_current_user[1].product_name} on the view', category='success')
                    return redirect(url_for('dashboard_page'))

            elif exist_in_database is not None:

                # get product info from database
                # add new entry for current user referencing the product_id from product_details
                prod_data = ProductDataTable(product_id=exist_in_database[0].product_id,
                                             user_id=current_user.id)

                db.session.add(prod_data)
                db.session.commit()

                _product = ProductDetails(product_id=exist_in_database[0].product_id,
                                          product_name=exist_in_database[1].product_name,
                                          product_price=exist_in_database[1].product_price,
                                          product_rating=exist_in_database[1].product_rating,
                                          product_sold=exist_in_database[1].product_sold,
                                          product_description=exist_in_database[1].product_description,
                                          product_image=exist_in_database[1].product_image,
                                          shop_rating=exist_in_database[1].shop_rating,
                                          shop_response_rate=exist_in_database[1].shop_response_rate,
                                          product_link=exist_in_database[1].product_link,
                                          target_website=exist_in_database[1].target_website,
                                          category_link=exist_in_database[1].category_link,
                                          product_data_owner=current_user.id)

                if len(session['list_of_products']) > 1:
                    if int(view_product_index) == 0:
                        session.pop('reviews_1')
                        session.pop('recommended_1')
                        session.pop('reviews_summary_1')
                    else:
                        session.pop('reviews_2')
                        session.pop('recommended_2')
                        session.pop('reviews_summary_2')

                    session['list_of_products'][int(view_product_index)] = _product.get_details

                    flash(f"Replace success", category='success')
                    return redirect(url_for('dashboard_page'))
                else:
                    session['list_of_products'].append(_product.get_details)
                    flash(f'Showing {exist_in_database[1].product_name} on the view', category='success')
                    return redirect(url_for('dashboard_page'))
            else:
                scraper = Webscraper()
                scraper.land_first_page(input_link)

                is_loaded = None
                time_out = 10

                try:
                    is_loaded = WebDriverWait(scraper.driver, time_out).until(
                        EC.visibility_of_element_located(
                            (By.CSS_SELECTOR,
                             'div[class="app-container"]' if "shopee.ph" in what_hostname else 'div[id="container"]'
                             )))
                except TimeoutException:
                    flash("Timed out: Waiting for target page to load took to long.",
                          category='danger')
                    scraper.driver.quit()
                    return redirect(url_for('dashboard_page'))
                finally:
                    if is_loaded:
                        time.sleep(3)
                        # Getting Product Information
                        try:
                            link = scraper.driver.current_url

                            prod_info = scraper.find_product_info_shopee() if 'shopee.ph' in what_hostname \
                                else scraper.find_product_info_lazada()

                            if what_hostname == 'shopee.ph':
                                target_website = 'Shopee'
                            else:
                                target_website = 'Lazada'

                            # adding new product to database
                            prod_details = ProductDetailsTable(product_link=link,
                                                               product_name=prod_info.get('prod_name'),
                                                               product_price=prod_info.get('prod_price'),
                                                               product_rating=prod_info.get('prod_rating'),
                                                               product_sold=prod_info.get('prod_sold'),
                                                               product_description=prod_info.get('prod_desc'),
                                                               product_image=prod_info.get('prod_image'),
                                                               shop_rating=prod_info.get('shop_rating'),
                                                               shop_response_rate=prod_info.get('shop_res_rate'),
                                                               category=prod_info.get('category'),
                                                               category_link=prod_info.get('category_link'),
                                                               target_website=target_website)
                            db.session.add(prod_details)

                            # adds the prod_details as "PENDING" into the database. will not persist
                            # into the database until db.session.commit() is called..
                            # this is needed to avoid product_details.product_id returning none
                            db.session.flush()

                            # referencing new product to current user
                            prod_data = ProductDataTable(product_id=prod_details.product_id,
                                                         user_id=current_user.id)
                            db.session.add(prod_data)
                            db.session.commit()

                            _product = ProductDetails(product_id=prod_details.product_id,
                                                      product_name=prod_details.product_name,
                                                      product_price=prod_details.product_price,
                                                      product_rating=prod_details.product_rating,
                                                      product_sold=prod_details.product_sold,
                                                      product_description=prod_details.product_description,
                                                      product_image=prod_details.product_image,
                                                      shop_rating=prod_details.shop_rating,
                                                      shop_response_rate=prod_details.shop_response_rate,
                                                      product_link=prod_details.product_link,
                                                      target_website=prod_details.target_website,
                                                      category_link=prod_details.category_link,
                                                      product_data_owner=current_user.id)

                            # Check if webdriver is undetected
                            status = scraper.driver.execute_script('return navigator.webdriver')
                            print(f'Webdriver status: {status}')

                            # Close headless browser and webdriver instance gracefully
                            scraper.driver.quit()

                            if len(session['list_of_products']) > 1:
                                if int(view_product_index) == 0:
                                    session.pop('reviews_1')
                                    session.pop('recommended_1')
                                    session.pop('reviews_summary_1')
                                else:
                                    session.pop('reviews_2')
                                    session.pop('recommended_2')
                                    session.pop('reviews_summary_2')

                                session['list_of_products'][int(view_product_index)] = _product.get_details

                                flash(f"Replace success", category='success')
                                return redirect(url_for('dashboard_page'))
                            else:
                                session['list_of_products'].append(_product.get_details)
                                flash(f'Showing {prod_details.product_name} on the view', category='success')
                                return redirect(url_for('dashboard_page'))

                        except AttributeError as e:
                            print(e)
                            flash("Something went wrong.", category='danger')
                            scraper.driver.quit()
                            return redirect(url_for('dashboard_page'))

        # Favorites Logic
        if request.args.get("req") == "fav":
            favorite_item_id = request.form.get('favorite_item')

            # set_to_favorites[0] = a dict contains ProductDataTable
            # set_to_favorites[1] = a dict contains ProductDetailsTable

            set_to_favorites = db.session.query(ProductDataTable, ProductDetailsTable).filter(
                ProductDataTable.product_id == favorite_item_id, ProductDataTable.user_id == current_user.id
            ).join(ProductDetailsTable).first()

            if set_to_favorites[0].favorite == 1:
                flash(f"{set_to_favorites[1].product_name} is already in the favorites!", category='info')
                return redirect(url_for('dashboard_page'))
            else:
                # add to favorites
                ProductDataTable.set_to_favorite(set_to_favorites[0])
                flash(f"{set_to_favorites[1].product_name} successfully added to your favorites!", category='success')
                return redirect(url_for('dashboard_page'))

        # Remove Favorites Logic
        if request.args.get("req") == "remove":
            remove_item_id = request.form.get('remove_item')

            # remove_to_favorites[0] = a dict contains ProductDataTable
            # remove_to_favorites[1] = a dict contains ProductDetailsTable

            remove_to_favorites = db.session.query(ProductDataTable, ProductDetailsTable).filter(
                ProductDataTable.product_id == remove_item_id, ProductDataTable.user_id == current_user.id
            ).join(ProductDetailsTable).first()

            # remove to favorites
            ProductDataTable.remove_to_favorite(remove_to_favorites[0])

            flash(f"{remove_to_favorites[1].product_name} successfully removed to your favorites!", category='danger')
            return redirect(url_for('dashboard_page'))

        # Replace Logic
        if request.args.get("req") == "replace_item":
            replace_selected_item_with = request.form.get('replace_item')
            if len(session['list_of_products']) > 1:
                replace_selected_item = request.form.get('productselect')  # returns index of 'prod'

                if replace_selected_item:
                    product = db.session.query(ProductDataTable, ProductDetailsTable).filter(
                        ProductDataTable.product_id == replace_selected_item_with,
                        ProductDataTable.favorite == 1,
                        ProductDataTable.user_id == current_user.id
                    ).join(ProductDetailsTable).first()

                    if product:
                        helpme = HelpMe()

                        updated_product = ProductDetails(product_id=product[0].product_id,
                                                         product_name=product[1].product_name,
                                                         product_price=product[1].product_price,
                                                         product_rating=product[1].product_rating,
                                                         product_sold=product[1].product_sold,
                                                         product_description=product[1].product_description,
                                                         product_image=product[1].product_image,
                                                         shop_rating=product[1].shop_rating,
                                                         shop_response_rate=product[1].shop_response_rate,
                                                         product_link=product[1].product_link,
                                                         target_website=product[1].target_website,
                                                         category_link=product[1].category_link,
                                                         product_data_owner=product[0].user_id)

                        in_dict = helpme.dict_isvalue_exist(session['list_of_products'], "link", updated_product.link)

                        if in_dict:
                            flash(f'This product is already on the view', category='info')
                            return redirect(url_for('dashboard_page'))

                        if session['list_of_products']:
                            if int(replace_selected_item) == 0:
                                session.pop('reviews_1')
                                session.pop('recommended_1')
                                session.pop('reviews_summary_1')
                            else:
                                session.pop('reviews_2')
                                session.pop('recommended_2')
                                session.pop('reviews_summary_2')

                            session['list_of_products'][int(replace_selected_item)] = updated_product.get_details

                        flash(f"Replace success", category='success')
                        return redirect(url_for('dashboard_page'))
                else:
                    flash(f"Unable to swap item: Please select item to swap", category="danger")
                    return redirect(url_for('dashboard_page'))
            else:

                product = db.session.query(ProductDataTable, ProductDetailsTable).join(ProductDetailsTable).filter(
                    ProductDataTable.product_id == replace_selected_item_with,
                    ProductDataTable.favorite == 1,
                    ProductDataTable.user_id == current_user.id
                ).first()

                if product:
                    updated_product = ProductDetails(product_id=product[0].product_id,
                                                     product_name=product[1].product_name,
                                                     product_price=product[1].product_price,
                                                     product_rating=product[1].product_rating,
                                                     product_sold=product[1].product_sold,
                                                     product_description=product[1].product_description,
                                                     product_image=product[1].product_image,
                                                     shop_rating=product[1].shop_rating,
                                                     shop_response_rate=product[1].shop_response_rate,
                                                     product_link=product[1].product_link,
                                                     target_website=product[1].target_website,
                                                     category_link=product[1].category_link,
                                                     product_data_owner=product[0].user_id)
                    helpme = HelpMe()
                    in_dict = helpme.dict_isvalue_exist(session['list_of_products'],
                                                        "product_id",
                                                        updated_product.product_id)

                    if in_dict:
                        flash(f'This product is already on the view', category='info')
                        return redirect(url_for('dashboard_page'))

                    session['list_of_products'].append(updated_product.get_details)
                    flash(f'Showing {product[1].product_name} on the view', category='success')
                    return redirect(url_for('dashboard_page'))

    if request.method == 'GET':
        # ranks -- used sql statement
        # getting all queries expect if category and category_link value is Breadcrumblist Empty
        df = pd.read_sql('SELECT product_data_table.data_id, product_data_table.product_id, '
                         'product_details_table.product_name, product_details_table.category, '
                         'product_details_table.category_link, product_details_table.target_website from '
                         'product_data_table LEFT JOIN product_details_table ON product_data_table.product_id = '
                         'product_details_table.product_id WHERE category NOT LIKE "Breadcrumblist Empty%" AND '
                         'category_link NOT LIKE "Breadcrumblist Empty%"', db.session.bind)
        data = pd.DataFrame(df)

        # shopee ranking
        shopee = data.loc[data['target_website'] == 'Shopee']
        shopee_df = shopee.groupby(['category', 'category_link'], as_index=False).size()
        shopee_df['percentage'] = shopee_df['size'] / shopee_df['size'].sum() * 100
        new_shopee_df = pd.DataFrame(shopee_df.sort_values('percentage', ascending=False))
        shopee_data_dict = new_shopee_df.to_dict('records')

        # lazada ranking
        lazada = data.loc[data['target_website'] == 'Lazada']
        lazada_df = lazada.groupby(['category', 'category_link'], as_index=False).size()
        lazada_df['percentage'] = lazada_df['size'] / lazada_df['size'].sum() * 100
        new_lazada_df = pd.DataFrame(lazada_df.sort_values('percentage', ascending=False))
        lazada_data_dict = new_lazada_df.to_dict('records')

        # favorites
        list_of_favorites = []
        favourites = db.session.query(ProductDataTable, ProductDetailsTable).join(ProductDetailsTable).filter(
            ProductDataTable.favorite == 1, ProductDataTable.user_id == current_user.id  # favorite == 1 is True
        ).order_by(ProductDataTable.product_id.desc())

        for pdata, pdetails in favourites:
            list_of_favorites.append(
                {
                    'data_id': pdata.data_id,
                    'product_id': pdata.product_id,
                    'user_id': pdata.user_id,
                    'favorite': pdata.favorite,
                    'product_link': pdetails.product_link,
                    'product_name': pdetails.product_name,
                    'product_price': pdetails.product_price,
                    'product_image': pdetails.product_image,
                    'target_website': pdetails.target_website
                }
            )

        # history
        list_of_history = []
        histories = db.session.query(ProductDataTable, ProductDetailsTable).join(ProductDetailsTable).filter(
            ProductDataTable.user_id == current_user.id
        ).order_by(ProductDataTable.product_id.desc())

        for pdata, pdetails in histories:
            list_of_history.append(
                {
                    'data_id': pdata.data_id,
                    'product_id': pdata.product_id,
                    'user_id': pdata.user_id,
                    'favorite': pdata.favorite,
                    'product_link': pdetails.product_link,
                    'product_name': pdetails.product_name,
                    'target_website': pdetails.target_website
                }
            )

        # modal
        replace_product_modal_form.submit.label = Label(replace_product_modal_form.submit.id,
                                                        "Replace Item" if len(
                                                            session['list_of_products']) >= 2 else "Add product")

        view_recommended_products_form.submit.label = Label(replace_product_modal_form.submit.id,
                                                            "Replace Item" if len(
                                                                session['list_of_products']) >= 2 else "Add product")

        return render_template('dashboard.html',
                               list_of_products=session['list_of_products'],
                               add_to_favorites_form=add_to_favorites_form,
                               remove_to_favorites_form=remove_to_favorites_form,
                               list_of_favorites=list_of_favorites,
                               replace_product_modal_form=replace_product_modal_form,
                               update_product_modal_form=update_product_modal_form,
                               load_reviews_form=load_reviews_form,
                               load_recommended_products_form=load_recommended_products_form,
                               view_recommended_products_form=view_recommended_products_form,
                               list_of_history=list_of_history,
                               shopee_dataframe=shopee_data_dict,
                               lazada_dataframe=lazada_data_dict,
                               reviews_1=session['reviews_1'],
                               reviews_2=session['reviews_2'],
                               reviews_summary_1=session['reviews_summary_1'],
                               reviews_summary_2=session['reviews_summary_2'],
                               recommended_1=session['recommended_1'],
                               recommended_2=session['recommended_2'],
                               )


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account_page():
    change_password_form = ChangePasswordForm()

    if change_password_form.validate_on_submit():
        old_user_password = User.query.filter_by(username=current_user.username).first()

        if old_user_password and old_user_password.verify_password(
                attempted_password=change_password_form.old_password.data
        ):

            policy = PasswordPolicy.from_names(
                length=8,  # min length: 8
                uppercase=1,  # need min. 1 uppercase letters
                numbers=1,  # need min. 1 digits
                special=1,  # need min. 1 special characters
                nonletters=1,  # need min. 1 non-letter characters (digits, specials, anything)
            )

            if change_password_form.new_password.data and old_user_password.verify_password(
                    attempted_password=change_password_form.new_password.data
            ):
                flash("New password can't be the same as the old password.", category='danger')

            else:
                if len(policy.test(change_password_form.new_password.data)) == 0:
                    # update new password
                    old_user_password.password = change_password_form.new_password.data
                    db.session.commit()

                    session.clear()
                    logout_user()
                    flash("Password change successfully, please login again with the new password", category='success')
                    return redirect(url_for('login_page'))
                else:
                    for e in policy.test(change_password_form.new_password.data):
                        flash(f'Password needs atleast: {e}', category='danger')
        else:
            flash("Username and old password didn't match, please try again", category='danger')

    if change_password_form.errors != {}:  # If there are no errors from the validations
        for err_msg in change_password_form.errors.values():
            if err_msg == ['Field must be equal to new_password.']:
                flash(f"There is an error creating the user: ['Password didn't match.']", category='danger')
            else:
                flash(f'There is an error with creating the user: {err_msg}', category='danger')

    return render_template('account.html', change_password_form=change_password_form)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    register_form = RegisterForm()
    if current_user.is_authenticated:
        return redirect(url_for('dashboard_page'))
    # if registration is sucessful
    if register_form.validate_on_submit():
        policy = PasswordPolicy.from_names(
            length=8,  # min length: 8
            uppercase=1,  # need min. 1 uppercase letters
            numbers=1,  # need min. 1 digits
            special=1,  # need min. 1 special characters
            nonletters=1,  # need min. 1 non-letter characters (digits, specials, anything)
        )

        if len(policy.test(register_form.password1.data)) == 0:
            # Create the user
            user_to_create = User(username=register_form.username.data,
                                  email_address=register_form.email_address.data,
                                  password=register_form.password1.data)
            # password is passed to password setter in models.py for encryption

            # Save the new user to database
            db.session.add(user_to_create)
            db.session.commit()

            login_user(user_to_create)
            flash(f'Registration Successful. You are now logged in as {user_to_create.username}', category='success')
            return redirect(url_for('dashboard_page',
                                    page_of_list1=1,
                                    page_of_list2=1
                                    ))
        else:
            for e in policy.test(register_form.password1.data):
                flash(f'Password needs atleast: {e}', category='danger')

    if register_form.errors != {}:  # If there are no errors from the validations
        for err_msg in register_form.errors.values():
            if err_msg == ['Field must be equal to password1.']:
                flash(f"There is an error creating the user: ['Password didn't match.']", category='danger')
            else:
                flash(f'There is an error with creating the user: {err_msg}', category='danger')

    # register_form was passed for user to input and create user account
    return render_template('register.html', register_form=register_form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    login_form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('dashboard_page'))

    if login_form.validate_on_submit():
        attempted_user_login_username = User.query.filter_by(username=login_form.username.data).first()
        attempted_user_login_email = User.query.filter_by(email_address=login_form.username.data).first()

        if attempted_user_login_username is not None:
            if attempted_user_login_username and attempted_user_login_username.verify_password(
                    attempted_password=login_form.password.data):

                login_user(attempted_user_login_username)
                flash(f'Login Successful. You are now logged in as {attempted_user_login_username.username}',
                      category='success')
                return redirect(url_for('dashboard_page',
                                        page_of_list1=1,
                                        page_of_list2=1))

            else:
                flash("Username and password didn't match, please try again", category='danger')
        elif attempted_user_login_email is not None:
            if attempted_user_login_email and attempted_user_login_email.verify_password(
                    attempted_password=login_form.password.data):

                login_user(attempted_user_login_email)
                flash(f'Login Successful. You are now logged in as {attempted_user_login_email.username}',
                      category='success')
                return redirect(url_for('dashboard_page',
                                        page_of_list1=1,
                                        page_of_list2=1))

            else:
                flash("Email and password didn't match, please try again", category='danger')
        else:
            # user/email not in db..
            flash(f'This user is not yet registered. Please Sign Up.', category='info')

    return render_template('login.html', login_form=login_form)


@app.route('/logout')
@login_required
def logout_page():
    session.clear()
    logout_user()
    flash('You have been logged out successfully.', category='info')
    return redirect(url_for('home_page'))


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password_page():
    forgot_password_form = ForgotPasswordForm()
    if current_user.is_authenticated:
        return redirect(url_for('dashboard_page'))
    # if form submission is sucessful
    if forgot_password_form.validate_on_submit():
        registered_user = User.query.filter_by(username=forgot_password_form.username.data).first()
        existing_email = User.query.filter_by(email_address=forgot_password_form.email.data).first()

        if registered_user.email_address and existing_email:
            helpme = HelpMe()
            generatedpassword = helpme.generate_random_password()
            existing_email.password = generatedpassword
            db.session.commit()
            msg = Message(
                'New Password',
                sender=app.config["MAIL_USERNAME"],
                # recipients=['ivandeposoy01@gmail.com']
                recipients=[existing_email.email_address]
            )

            msg.body = f'Hello {existing_email.username}, \nYou are receiving this notification because you have' \
                       f' requested a new password to be sent to your email' + \
                       f'\nYou will be able to login using the following password: \nPassword: {generatedpassword}' + \
                       f'\n\nYou can of course change this password yourself via the account page. If you have any ' \
                       f'difficulties please contact the administrator at capstone.it4f.flask@gmail.com'
            mail.send(msg)
            flash(f'Reset Successful. You may check your email {existing_email.email_address} for the new password',
                  category='success')
            return redirect(url_for('login_page'))
        else:
            flash(f"Registered Username and Email don't match", category='danger')

    # forgot_password_form was passed for user to input and forgot the password
    return render_template('forgot_password.html', forgot_password_form=forgot_password_form)
