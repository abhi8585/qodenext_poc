from flask_restful import Resource, request
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels
from datetime import datetime

class MapUuidToOrderResource(Resource):

    def __init__(self):
        self.logger = LoggerClient(VerboseLevels.INFO.value)
        self.config = ConfigClient(env=VerboseLevels.DEV.value)
        self.mysql_client = MySQLClient(self.config.get_value("Database", "uri"))

    def is_duplicate(self, order_id, uuid_id):
        is_duplicate = False
        try:
            condition = f"where order_id = {order_id} and uuid_id = {uuid_id} and status='dispatched'"
            check_duplicate = self.mysql_client.select(table_name='keg_mapping', filter_condition=condition)
            if check_duplicate and len(check_duplicate['results']) > 0:
                is_duplicate = True
        except Exception as e:
            self.logger.log_error(f"Error {e} while checking UUID duplicate order.")
        return is_duplicate

    def get(self):
        mapped_status = dict(status=200,data={})
        try:
            order_id = request.args.get('order_id')
            if not order_id:
                return {'status' : 400, 'message' : 'No order_id given', 'data' : []}

            order_uuid = request.args.get('order_uuid')
            if not order_uuid:
                return {'status' : 400, 'message' : 'No order_uuid given', 'data' : []}

            user_id = request.args.get('user_id')
            if not user_id:
                return {'status' : 400, 'message' : 'No user_id given', 'data' : []}
            order_product = request.args.get('order_product')
            if not order_product:
                return {'status' : 400, 'message' : 'No order_product given', 'data' : []}
            order_uuid_id = self.mysql_client.select(table_name='uuid',filter_condition=f"where uuid = '{order_uuid}'")
            print(f"order uuid {order_uuid_id}")
            if order_uuid_id and len(order_uuid_id['results']) > 0:
                uuid_id = order_uuid_id['results'][0]['id']
                is_duplicate = self.is_duplicate(order_id, uuid_id)
                if is_duplicate:
                    mapped_status['message'] = f"{order_uuid} is already mapped"
                    return mapped_status
                row_obj = dict(order_id=order_id, uuid_id=uuid_id, product_name = order_product
                                ,status="dispatched", created_date = datetime.now(),update_date = datetime.now())
                insert_mapped_status = self.mysql_client.insert(table_name='keg_mapping',column_values=row_obj)
                if insert_mapped_status:
                    mapped_status = dict(status=200,data=insert_mapped_status)
                    self.logger.log_info(f"UUID : {order_uuid} successfully mapped to Order with ID :  {order_id}")
                else:
                    self.logger.log_info(f"Error while mapping UUID with order")
            else:
                self.logger.log_info(f"No uuid found for : {order_uuid}")
        except Exception as e:
            mapped_status['status'] = 500
            self.logger.log_error(f"INTERNAL-Error while mapping UUID, Error : {e}")
        return mapped_status