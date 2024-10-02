from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.models.user import User

class UserRegister(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        data = parser.parse_args()

        if User.find_by_email(data['email']):
            return {'message': 'User with that email already exists'}, 400

        user = User(data['username'], data['email'], data['password'])
        user.save()

        access_token = create_access_token(identity=data['email'])
        refresh_token = create_refresh_token(identity=data['email'])

        return {
            'message': 'User created successfully',
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 201

class UserLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        data = parser.parse_args()

        user = User.find_by_email(data['email'])
        if user and User.verify_password(user['password'], data['password']):
            access_token = create_access_token(identity=data['email'])
            refresh_token = create_refresh_token(identity=data['email'])
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
        return {'message': 'Invalid credentials'}, 401

class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200