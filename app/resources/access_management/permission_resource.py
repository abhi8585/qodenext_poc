from flask import Flask, request
from flask_restful import Resource
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient

config = ConfigClient(env='dev')
mysql_uri = config.get_value("Database", "uri")
mysql_client = MySQLClient(mysql_uri)


class PermissionResource(Resource):
    def post(self):
        permission_data = request.get_json()

        if not permission_data or 'permission_name' not in permission_data or 'permission_description' not in permission_data:
            return {'error': 'Missing required parameters'}, 400

        permission_name = permission_data['permission_name']
        permission_description = permission_data['permission_description']

        try:
            # Check if the permission with the same name already exists
            select_status = mysql_client.select('permission', filter_condition=f"where permission_name = '{permission_name}'")
            if select_status['status'] == 'success' and select_status['results']:
                return {'error': 'Permission with the same name already exists'}, 409

            # Insert the new permission
            insert_status = mysql_client.insert('permission', {'permission_name': permission_name, 'permission_description': permission_description})
            if insert_status['status'] == 'success':
                permission_id = insert_status['last_row_id']
                return {'message': 'Permission created successfully', 'permission_id': permission_id}, 201
            else:
                return {'error': 'Failed to create permission'}, 500
        except Exception as e:
            return {'error': str(e)}, 500

    def get(self, permission_id=None):
        if permission_id is None:
            try:
                # Fetch the complete list of permissions
                select_status = mysql_client.select('permission')
                if select_status['status'] == 'success':
                    permissions = select_status['results']
                    return {'permissions': permissions}, 200
                else:
                    return {'error': 'Failed to fetch permissions'}, 500
            except Exception as e:
                return {'error': str(e)}, 500
        else:
            try:
                # Fetch the permission by ID
                select_status = mysql_client.select('permission', filter_condition=f"where permission_id = {permission_id}")
                if select_status['status'] == 'success' and select_status['results']:
                    permission = select_status['results'][0]
                    return {'permission': permission}, 200
                else:
                    return {'error': 'Permission not found'}, 404
            except Exception as e:
                return {'error': str(e)}, 500