from flask_restful import Resource, request
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.csv.csv_client import CsvClient
from app.utils.chatgpt.chatgpt_client import ChatGptClient
import json
import uuid
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels
logger = LoggerClient(VerboseLevels.INFO.value)
config = ConfigClient(env='dev')
mysql_uri = config.get_value("Database", "uri")
mysql_client = MySQLClient(mysql_uri)


class OrderDetailsResource(Resource):

    def get_order_details(self, order_id):
        order_data = None
        try:
            if order_id:
                order_details_data = mysql_client.select(table_name='order_details',filter_condition=f"where order_id = {order_id}")
                if order_details_data:
                    return order_details_data['results']
        except Exception as e:
            logger.log_error(f"Error while getting order details, Error : {e}")


        
    def get(self):
        order_data = dict()
        order_date = request.args.get('order_date')
        if order_date:
            try:
                order_header_data = mysql_client.select(table_name='order_header',filter_condition=f"where order_date = '{order_date}' limit 1;")
                # mysql_client.close_connection()
                if order_header_data['status'] == 'success':
                    order_id = order_header_data['results'][0]['order_id']
                    # remove comment 
                    order_id = 7
                    order_details = self.get_order_details(order_id=order_id)
                    if order_details:
                        order_data['order_id'] = order_id
                        order_data['order_details'] = order_details
                else:
                    logger.log_info(f"Getting data from order header failed")
                return {'status':200,'data': order_data}
            except Exception as e:
                logger.log_info(f"Error while getting order data for date, {order_data}, Error :  {e}")
                return {'status':500,'data': []}
        else:
            return {'status' : 500, 'message' : 'No order date provided'}

    def post(self):
        return {'message': 'POST request received'}
