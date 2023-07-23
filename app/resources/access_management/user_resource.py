from flask import Flask, request
from flask_restful import Resource
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
import hashlib

class UserResource(Resource):

    def __init__(self):
        self.config = ConfigClient(env='dev')
        self.mysql_client = MySQLClient(self.config.get_value("Database", "uri"))

    def encrypt_password(self,password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        return hashed_password

    def get(self, user_id):
        try:
            if user_id:
                select_status = self.mysql_client.select('user', filter_condition=f"where user_id = {user_id}")
                if select_status['status'] == 'success':
                    user = select_status['results']
                    return {'users' : user}, 200
                else:
                    return {'error': 'Failed to fetch user'}, 500
            else:
                # Fetch a complete list of users
                select_status = self.mysql_client.select('user')
                if select_status['status'] == 'success':
                    print('going right')
                    users = select_status['results']
                    return {'users' : users}, 200
                else:
                    return {'error': 'Failed to fetch users'}, 500
        except Exception as e:
            return {'error': str(e)}, 500


    def post(self):

        user_data = request.get_json()
        if not user_data or 'email' not in user_data or 'name' not in user_data or 'password' not in user_data:
            return {'error': 'Missing required parameters'}, 400

        email = user_data['email']
        name = user_data['name']
        password = user_data['password']
        
        select_status = self.mysql_client.select('user', filter_condition=f"where user_email = '{email}'")
        if select_status['status'] == 'success' and select_status['results']:
            return {'error': 'User with the same email already exists'}, 409

        encrypted_password = self.encrypt_password(password)

        # Insert the new user using the MySQLClient class
        user_data = {
            'user_email': email,
            'user_name': name,
            'user_password': encrypted_password
        }

        try:
            # Insert the new user into the database
            insert_status = self.mysql_client.insert('user', user_data)
            if insert_status['status'] == 'success':
                # Return the corresponding JSON response
                response_data = {
                    'message': 'User created successfully',
                    'user_id': insert_status['last_row_id']
                }
                return response_data, 201
            else:
                return {'error': 'Failed to create user'}, 500
        except Exception as e:
            return {'error': str(e)}, 500


