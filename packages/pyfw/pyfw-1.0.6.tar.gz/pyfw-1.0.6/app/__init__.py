from flask import Flask
from flask_bootstrap import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail
from flask_moment import Moment
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()


login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
login_manager.login_message = u"请登录系统后进行操作！"
login_manager.login_message_category = "info"


def create_app(config_name):

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    db.app = app

    toolbar = DebugToolbarExtension()
    toolbar.init_app(app)

    login_manager.init_app(app)

    api = Api(app)


    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/main')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .system import system as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/system')

    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')



    return app

