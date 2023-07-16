from flask_restful import Resource
from flask import Flask, request
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels

class GetOrderHeaderDetailsResource(Resource):

    def __init__(self):
        self.config = ConfigClient(env='dev')
        self.logger = LoggerClient(VerboseLevels.INFO.value)
        self.mysql_client = MySQLClient(self.config.get_value("Database", "uri"))
    
    def get(self):
        order_details_data = dict(status=500,data=[])
        try:
            order_id = request.args.get('order_id')
            if not order_id:
                return {'status' : 400, 'message' : 'No order_detail_id given', 'data' : []}
            columns = ['area','bud_30','draught_code','hog_15','mag_30','order_detail_id','outlets_name']
            order_details = self.mysql_client.select(table_name='order_details',columns=columns,filter_condition=f"where order_id = {order_id}")
            if order_details and len(order_details['results']) > 0:
                order_details_data['data'] = order_details['results']
                order_details_data['status'] = 200
        except Exception as e:
            self.logger.log_error(f"MAIN-ERROR while getting order header details : {e}")
        return order_details_data


        
