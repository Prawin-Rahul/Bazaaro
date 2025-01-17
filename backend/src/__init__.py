from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
import os

from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)  
    app.config["TESTING"] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app,db)

    from src.routes.user_route import user_bp
    from src.routes.product_route import product_bp
    from src.routes.order_route import order_bp

    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(product_bp,url_prefix="/api/products")
    app.register_blueprint(order_bp,url_prefix="/api/orders")

    return app 