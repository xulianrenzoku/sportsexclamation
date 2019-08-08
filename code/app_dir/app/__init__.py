from flask import Flask
from config import Config
from flask_login import LoginManager


# Initialization
# Create an application instance
# (an object of class Flask)  which handles all requests.
application = Flask(__name__)
application.config.from_object(Config)

# commented out until we have use for the SQL database
# db = SQLAlchemy(application)
# db.create_all()
# db.session.commit()

# login_manager needs to be initiated before running the app
login_manager = LoginManager()
login_manager.init_app(application)

# Added at the bottom to avoid circular dependencies.
# (Altough it violates PEP8 standards)

# commented out until needed
from app import classes
from app import routes
