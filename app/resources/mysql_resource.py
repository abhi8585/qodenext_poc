from flask_restful import Resource
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient

class MySQLResource(Resource):
    def get(self):
        config = ConfigClient(env='dev')
        mysql_uri = config.get_value("Database", "uri")
        mysql_client = MySQLClient(mysql_uri)
        update_status = mysql_client.delete(table='user',filter_condition="username = 'temp'")
        return {'message': update_status}

    def post(self):
        return {'message': 'POST request received'}
