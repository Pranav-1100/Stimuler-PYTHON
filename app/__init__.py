from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from pymongo import MongoClient
from .config import Config
from .utils.redis_client import get_redis_client

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

     # Initialize CORS
    CORS(app)

    print("MONGO_URI:", app.config['MONGO_URI'])

    # Initialize MongoDB with connection pooling
    app.mongo = MongoClient(app.config['MONGO_URI'], maxPoolSize=100)
    app.db = app.mongo.get_default_database()

    # Initialize JWT
    jwt = JWTManager(app)

    # Initialize API
    api = Api(app)

    # Import and register resources
    from .resources.auth import UserRegister, UserLogin, TokenRefresh
    from app.resources.error_tracker import ErrorUpdate, TopErrors, GenerateDummyData

    api.add_resource(UserRegister, '/register')
    api.add_resource(UserLogin, '/login')
    api.add_resource(TokenRefresh, '/refresh')
    api.add_resource(ErrorUpdate, '/update-error')
    api.add_resource(TopErrors, '/top-errors')
    api.add_resource(GenerateDummyData, '/generate-dummy-data')

    # Initialize Redis inside the application context
    # with app.app_context():
    #     app.redis = get_redis_client()

    return app
