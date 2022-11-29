class ProductDetails:
    def __init__(self, product_id=0, product_name=None, product_price=0, product_rating=0, product_sold=0,
                 product_description=None, product_image=None, shop_rating=0, shop_response_rate=0, product_link=None,
                 target_website=None, product_data_owner=None, category_link=None, sku=None):
        self.product_id = product_id
        self.name = product_name
        self.price = product_price
        self.rating = product_rating
        self.sold = product_sold
        self.description = product_description
        self.product_image = product_image
        self.shop_rating = shop_rating
        self.shop_response_rate = shop_response_rate
        self.link = product_link
        self.target_website = target_website
        self.product_details_owner = product_data_owner
        self.category_link = category_link
        self.sku = sku

    @property
    def get_details(self):
        details = {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "rating": self.rating,
            "sold": self.sold,
            "description": self.description,
            "product_image": self.product_image,
            "shop_rating": self.shop_rating,
            "shop_response_rate": self.shop_response_rate,
            "link": self.link,
            "target_website": self.target_website,
            "product_details_owner": self.product_details_owner,
            "category_link": self.category_link,
            "sku": self.sku
        }
        return details
