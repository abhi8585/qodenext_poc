from flask_restful import Resource
from flask import Flask, request
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient

class IssueResource(Resource):
    def get(self):
        ret_obj = dict()
        model_number = request.args.get('model_number')
        if model_number:
            config = ConfigClient(env='dev')
            mysql_uri = config.get_value("Database", "uri")
            mysql_client = MySQLClient(mysql_uri)
            item_exist = mysql_client.select(table_name='issue',filter_condition=f"where model = '{model_number}'")
            if item_exist:
                if item_exist['status'] == 'success':
                    ret_obj['status'] = item_exist['status']
                    ret_obj['data'] = item_exist['results']
                    ret_obj['code'] = 200
            else:
                ret_obj['status'] = 'failed'
                ret_obj['code'] = 500
                ret_obj['data'] = []
            return ret_obj
        else:
            return {'message': 'No model_number parameter provided'}, 400

    def post(self):
        return {'message': 'POST request received'}
