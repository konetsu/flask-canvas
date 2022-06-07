from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect()
db = SQLAlchemy()
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_CHECK_DEFAULT'] = False #csrf tokens expire, that can cause a problem with the new pixel placements if users stay on the page for a long time so i'm not enabling it by default.
    app.config['SECRET_KEY'] = "change this to something random"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'db uri'
    db.init_app(app)
    csrf.init_app(app)
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    from .models import User
    create_database(app)
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app):
    db.create_all(app=app)
    print("db created")
