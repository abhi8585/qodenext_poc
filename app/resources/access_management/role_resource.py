from flask import Flask, request
from flask_restful import Resource
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
import hashlib

config = ConfigClient(env='dev')
mysql_uri = config.get_value("Database", "uri")
mysql_client = MySQLClient(mysql_uri)


class RoleResource(Resource):
    def post(self):
        role_data = request.get_json()

        if not role_data or 'role_name' not in role_data or 'role_description' not in role_data:
            return {'error': 'Missing required parameters'}, 400

        role_name = role_data['role_name']
        role_description = role_data['role_description']

        try:
            # Check if the role with the same name already exists
            select_status = mysql_client.select('role', filter_condition=f"where role_name = '{role_name}'")
            if select_status['status'] == 'success' and select_status['results']:
                return {'error': 'Role with the same name already exists'}, 409

            # Insert the new role
            insert_status = mysql_client.insert('role', {'role_name': role_name, 'role_description': role_description})
            if insert_status['status'] == 'success':
                role_id = insert_status['last_row_id']
                return {'message': 'Role created successfully', 'role_id': role_id}, 201
            else:
                return {'error': 'Failed to create role'}, 500
        except Exception as e:
            return {'error': str(e)}, 500


    def get(self, role_id=None):
        try:
            if role_id:
                # Fetch role with specific role_id
                select_status = mysql_client.select('role', filter_condition=f"where role_id = {role_id}")
            else:
                # Fetch all roles
                select_status = mysql_client.select('role')

            if select_status['status'] == 'success':
                roles = select_status['results']
                return {'roles': roles}, 200
            else:
                return {'error': 'Failed to fetch roles'}, 500
        except Exception as e:
            return {'error': str(e)}, 500