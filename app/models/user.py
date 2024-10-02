from flask import current_app
import bcrypt

class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def save(self):
        current_app.db.users.insert_one({
            'username': self.username,
            'email': self.email,
            'password': self.password
        })

    @classmethod
    def find_by_email(cls, email):
        return current_app.db.users.find_one({'email': email})

    @classmethod
    def verify_password(cls, stored_password, provided_password):
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)