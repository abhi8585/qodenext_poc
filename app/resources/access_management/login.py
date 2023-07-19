from flask import Flask, request
from flask_restful import Resource
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels
from app.utils.uuid.uuid_client import UUIDClient
import hashlib


class LoginResource(Resource):

    def __init__(self):
        self.config = ConfigClient(env='dev')
        self.mysql_client = MySQLClient(self.config.get_value("Database", "uri"))
        self.logger = LoggerClient(verbosity=VerboseLevels.INFO.value)

    @staticmethod
    def decrypt_password(plain_password, hashed_password):
        hashed_input_password = hashlib.sha256(plain_password.encode()).hexdigest()
        return hashed_input_password == hashed_password

    @staticmethod
    def generate_auth_token(email):
        uuid_client = UUIDClient()
        access_uuid = uuid_client.create_uuid(1)
        access_uuid = access_uuid[0]
        access_uuid  = access_uuid.split('-')
        access_uuid = ''.join(access_uuid)
        return access_uuid

    def post(self):
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return {'message': 'Email and password are required.'}, 400
            user = self.mysql_client.select('user', filter_condition=f"WHERE user_email = '{email}'")
            if not user:
                return {'message': 'User not found.'}, 404
            if len(user['results']) > 0:
                role_name = None
                user_id = user['results'][0]['user_id']
                user_name = user['results'][0]['user_name']
                role_id = self.mysql_client.select(table_name='user_to_role',filter_condition=f"where user_id = {user_id}")
                if role_id:
                    if len(role_id['results']) > 0:
                        role_id = role_id['results'][0]['role_id']
                        role_name = self.mysql_client.select(table_name='role',filter_condition=f"where role_id = {role_id}")
                        if role_name:
                            if len(role_name) > 0:
                                role_name = role_name['results'][0]['role_name']
                        else:
                            self.logger.log_info(f"no role name is assigned")
                else:
                    role_name = ''
                encrypted_password = user['results'][0]['user_password']
                decrypted_password = self.decrypt_password(password,encrypted_password)

                if decrypted_password:
                    auth_token = self.generate_auth_token(email)
                    self.mysql_client.insert(table_name='access_token', column_values={'access_token' :auth_token})
                    self.logger.log_info(f"User login successfully!")
                    return {"user_name":user_name,"user_id":user_id,'status':200,'message': 'Login successfull.','access_token':auth_token, 'role_name':role_name}, 200
                else:
                    self.logger.log_info(f"Invalid password!")
                    return {'message': 'Invalid password.'}, 401
            else:
                return {'message':'User not found'}, 404

        except Exception as e:
            self.logger.log_error(f"An error occurred during login: {str(e)}")
            return {'message': 'An error occurred during login.'}, 500