from flask import Flask, request
from flask_restful import Resource
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels
import hashlib

config = ConfigClient(env='dev')
mysql_uri = config.get_value("Database", "uri")
mysql_client = MySQLClient(mysql_uri)
logger = LoggerClient(verbosity=VerboseLevels.INFO.value)

class LogoutResource(Resource):

    def check_access_token(self, access_token):
        token_id = None
        token_data = mysql_client.select(table_name='access_token',filter_condition=f"where access_token = '{access_token}'")
        if token_data['status'] == 'success':
            if len(token_data['results']) > 0:
                token_id = token_data['results'][0]['token_id']
        return token_id

    def delete_access_token(self, access_token_id):
        is_deleted = False
        token_data = mysql_client.delete(table='access_token',filter_condition=f"where token_id = {access_token_id}")
        if token_data:
            is_deleted = True
        return is_deleted

    # check after deleting
    def post(self):
        # Get the email and access token from the request body
        data = request.get_json()
        email = data.get('email')
        access_token = data.get('access_token')

        # Check if any of the required parameters is missing
        if not email or not access_token:
            return {'message': 'Missing email or access_token parameter'}, 400

        try:
            # Check if the access token exists in the database
            token_exists = self.check_access_token(access_token)
            if not token_exists:
                return {'message': 'Invalid access token'}, 401

            # # Delete the access token
            is_deleted = self.delete_access_token(token_exists)
            if is_deleted:
                # # Log the successful logout
                logger.log_info(f"User {email} logged out successfully.")
                return {'message': 'Logged out successfully'}, 200

        except Exception as e:
            # Log the error
            logger.log_error(f"Error occurred during logout: {str(e)}")

            return {'message': 'An error occurred during logout'}, 500