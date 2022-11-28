from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from configuration import APP_CONFIG

# create the extension
db = SQLAlchemy()
# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = APP_CONFIG.FLOKER_CONN_STR
# initialize the app with the extension
db.init_app(app)
