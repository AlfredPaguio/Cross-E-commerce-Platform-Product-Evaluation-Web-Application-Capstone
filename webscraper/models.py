from webscraper import db, login_manager
from webscraper import bcrypt
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):  # User has one-to-many relationship with ProductData
    # Keys
    id = db.Column(db.Integer(), primary_key=True)  # Account_ID PK

    # Info's
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)

    # Relationships
    datas = db.relationship('ProductReferenceTable', backref='prod_data_owner', lazy=True)

    @property
    def password(self):
        return self.password

    # Encrypt password
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def verify_password(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)


class ProductReferenceTable(db.Model):
    # Keys
    data_id = db.Column(db.Integer(), primary_key=True)
    product_id = db.Column(db.Integer(), db.ForeignKey('product_details_table.product_id'))
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))

    # Infos
    favorite = db.Column(db.Boolean(), nullable=False, default=False)

    def set_to_favorite(self):
        self.favorite = True
        db.session.commit()

    def remove_to_favorite(self):
        self.favorite = False
        db.session.commit()


class ProductDetailsTable(db.Model):  # ProductData has one-to-many relationship with ProductDataReviews
    # Keys
    product_id = db.Column(db.Integer(), primary_key=True)  # Data_ID PK

    # Infos
    product_link = db.Column(db.String(), nullable=False)
    product_name = db.Column(db.String(length=100), nullable=False)
    product_price = db.Column(db.String(length=10), nullable=False)
    product_rating = db.Column(db.String(length=10), nullable=False)
    product_sold = db.Column(db.String(length=10), nullable=False)
    product_description = db.Column(db.String(), nullable=False)
    product_image = db.Column(db.String(), nullable=False)
    shop_rating = db.Column(db.String(length=10), nullable=False)
    shop_response_rate = db.Column(db.String(length=10), nullable=False)
    category = db.Column(db.String(length=50), nullable=False)
    category_link = db.Column(db.String(), nullable=False)
    target_website = db.Column(db.String(length=10), nullable=False)
    sku = db.Column(db.String(), nullable=False)

    # Relationships
    datas = db.relationship('ProductReferenceTable', backref='owned_item', lazy=True)
    reviews = db.relationship('ProductDataReviewsTable', backref='review_owner', lazy=True, passive_deletes=True,
                              cascade="all, delete")


class ProductDataReviewsTable(db.Model):
    # Keys
    review_id = db.Column(db.Integer(), primary_key=True)  # Review_ID PK
    product_id = db.Column(db.Integer(), db.ForeignKey('product_details_table.product_id', ondelete="CASCADE"))

    # Infos
    review_author = db.Column(db.String(length=30), nullable=False)
    # review_star is removed update documentation
    review_data_time = db.Column(db.String(length=30), nullable=False)
    review_comment = db.Column(db.String(), nullable=False)
    review_sentiment = db.Column(db.Integer(), nullable=False)

# https://docs.sqlalchemy.org/en/14/orm/cascades.html#using-delete-cascade-with-many-to-many-relationships
