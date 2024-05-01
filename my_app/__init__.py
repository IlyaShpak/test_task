import logging
from logging.handlers import RotatingFileHandler


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)
app.logger.setLevel(logging.INFO)
file_handler = RotatingFileHandler('app.log', maxBytes=10240, backupCount=10)
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
app.logger.addHandler(console_handler)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

app = Flask(__name__)
app.secret_key = 'some secret salt'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ilya:test@localhost/test_bd'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.app_context().push()
db = SQLAlchemy(app)
manager = LoginManager(app)

from my_app import models, routes

db.create_all()
