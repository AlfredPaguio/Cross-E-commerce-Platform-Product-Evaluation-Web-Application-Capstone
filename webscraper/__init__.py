from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
mail = Mail(app)  # instantiate the mail class

# list_of_products = []
# https://stackoverflow.com/questions/17925674/jinja2-local-global-variable
# app.jinja_env.add_extension('jinja2.ext.do')

# database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rewrite_db3.db'
app.config['SECRET_KEY'] = '90e32cb1cc919276aa230a2f3ab77333'

# session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configuration of mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'capstone.it4f.flask@gmail.com'
app.config['MAIL_PASSWORD'] = 'qddklhqikszvqouj'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# login/app config
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'
login_manager.login_message_category = 'info'

from webscraper import routes
