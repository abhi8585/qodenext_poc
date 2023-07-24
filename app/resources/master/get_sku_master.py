from flask import Flask, request
from flask_restful import Resource
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
import hashlib

config = ConfigClient(env='dev')
mysql_uri = config.get_value("Database", "uri")
mysql_client = MySQLClient(mysql_uri)


class SkuResource(Resource):

    def get(self, sku_id):
        try:
            cols = ['keg_id','keg_name','keg_product_code','keg_quantity']
            if sku_id:
                select_status = mysql_client.select('keg_sku_master',columns=cols, filter_condition=f"where keg_id = {sku_id}")
                if select_status['status'] == 'success':
                    user = select_status['results']
                    return {'users' : user}, 200
                else:
                    return {'error': 'Failed to fetch sku'}, 500
            else:
                # Fetch a complete list of users
                select_status = mysql_client.select('keg_sku_master',columns=cols)
                if select_status['status'] == 'success':
                    print('going right')
                    users = select_status['results']
                    return {'users' : users}, 200
                else:
                    return {'error': 'Failed to fetch sku list'}, 500
        except Exception as e:
            return {'error': str(e)}, 500


    # def post(self):

    #     user_data = request.get_json()
    #     if not user_data or 'email' not in user_data or 'name' not in user_data or 'password' not in user_data:
    #         return {'error': 'Missing required parameters'}, 400

    #     email = user_data['email']
    #     name = user_data['name']
    #     password = user_data['password']
        
    #     select_status = mysql_client.select('user', filter_condition=f"where user_email = '{email}'")
    #     if select_status['status'] == 'success' and select_status['results']:
    #         return {'error': 'User with the same email already exists'}, 409

    #     encrypted_password = self.encrypt_password(password)

    #     # Insert the new user using the MySQLClient class
    #     user_data = {
    #         'user_email': email,
    #         'user_name': name,
    #         'user_password': encrypted_password
    #     }

    #     try:
    #         # Insert the new user into the database
    #         insert_status = mysql_client.insert('user', user_data)
    #         if insert_status['status'] == 'success':
    #             # Return the corresponding JSON response
    #             response_data = {
    #                 'message': 'User created successfully',
    #                 'user_id': insert_status['last_row_id']
    #             }
    #             return response_data, 201
    #         else:
    #             return {'error': 'Failed to create user'}, 500
    #     except Exception as e:
    #         return {'error': str(e)}, 500


