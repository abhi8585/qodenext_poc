from flask_restful import Resource, request
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels
from app.utils.uuid.uuid_client import UUIDClient
from datetime import datetime

class MapUuidToProductResource(Resource):

    def __init__(self):
        self.config = ConfigClient(env='dev')
        self.logger = LoggerClient(VerboseLevels.INFO.value)
        self.mysql_client = MySQLClient(self.config.get_value("Database", "uri"))
        self.uuid_client = UUIDClient()

    def get(self):
        try:
            total_count = request.args.get('total_count')
            if not total_count:
                return {'status' : 400, 'message' : 'No total_count given', 'data' : []}
            product_code = request.args.get('product_code')
            if not product_code:
                return {'status' : 400, 'message' : 'No product_code given', 'data' : []}   
            product_data = self.mysql_client.select(table_name='keg_sku_master',filter_condition=f"where keg_product_code = '{product_code}'")
            if product_data and len(product_data['results']) > 0:
                product_id = product_data['results'][0]['keg_id']
            new_uuids = self.uuid_client.create_uuid(int(total_count))
            for u in new_uuids:
                u_i = self.mysql_client.insert(table_name='uuid',column_values={'uuid' : u})
                if u_i and u_i['status'] == 'success':
                    u_id = u_i['last_row_id']
                    p_u_m = dict(uuid_id=u_id,keg_id=product_id,created_date=datetime.now())
                    p_u_i = self.mysql_client.insert(table_name='keg_to_uuid',column_values=p_u_m)
            return dict(status=200,data=new_uuids)
        except Exception as e:
            self.logger.log_error(f"Error while mapping UUID to products")