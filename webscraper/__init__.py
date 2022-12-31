from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
import os

app = Flask(__name__)

# database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rewrite_db3.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db_base64.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mixed_db.db'
# SQLAlchemy v1.4++ can't 'postgres' as it was depricated..
# https://help.heroku.com/ZKNTJQSK/why-is-sqlalchemy-1-4-x-not-connecting-to-heroku-postgres
# uri = os.getenv("DATABASE_URL")
# if uri.startswith("postgres://"):
#     uri = uri.replace("postgres://", "postgresql://", 1)
#
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://nyoixirdeqgsqd' \
# ':60c3e957f5f1c1c4dd82d66a08fe405f0207170b417b4e7c5ceef1374007c257@ec2-3-219' \
# '-135-162.compute-1.amazonaws.com:5432/drsnji53tq24b '
app.config['SECRET_KEY'] = '90e32cb1cc919276aa230a2f3ab77333'

# rest of connection code using the connection string `uri`

# session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configuration of mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'capstone.it4f.flask@gmail.com'
app.config['MAIL_PASSWORD'] = 'jvwvzripfhmbrykf'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# login/app config
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'
login_manager.login_message_category = 'info'

from webscraper import routes, models
