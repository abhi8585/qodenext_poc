from flask_restful import Resource, request
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.csv.csv_client import CsvClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels
from app.utils.uuid.uuid_client import UUIDClient

logger = LoggerClient(VerboseLevels.INFO.value)
config = ConfigClient(env='dev')
mysql_uri = config.get_value("Database", "uri")
mysql_client = MySQLClient(mysql_uri)
uuid_client = UUIDClient()

class MapUuidToOrderResource(Resource):

    def get(self):
        mapped_status = dict(status=500,data="")
        try:
            order_id = request.args.get('order_id')
            if not order_id:
                return {'status' : 200, 'message' : 'No order_id given', 'data' : []}

            order_uuid = request.args.get('order_uuid')
            if not order_uuid:
                return {'status' : 200, 'message' : 'No order_uuid given', 'data' : []}

            user_id = request.args.get('user_id')
            if not user_id:
                return {'status' : 200, 'message' : 'No user_id given', 'data' : []}
            order_product = request.args.get('order_product')
            if not order_product:
                return {'status' : 200, 'message' : 'No order_product given', 'data' : []}
            order_uuid_id = mysql_client.select(table_name='uuid',filter_condition=f"where uuid = '{order_uuid}'")
            if order_uuid_id:
                uuid_id = order_uuid_id['results'][0]['id']
                row_obj = dict(order_id=order_id, uuid_id=uuid_id, product_name = order_product,status="dispatched")
                insert_mapped_status = mysql_client.insert(table_name='keg_mapping',column_values=row_obj)
                if insert_mapped_status:
                    mapped_status = dict(status=200,data=insert_mapped_status)
                else:
                    logger.log_info(f"Error while mapping uuid with product")
                return mapped_status
            else:
                logger.log_info(f"No uuid found")
        except Exception as e:
            logger.log_error(f"Error while generating UUI, Error : {e}")
            return mapped_status


    def post(self):
        return {'message': 'POST request received'}
