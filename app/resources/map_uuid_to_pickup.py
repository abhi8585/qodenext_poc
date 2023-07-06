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

class MapUuidToPickupResource(Resource):

    def get(self):
        mapped_status = dict(status=500,data="")
        try:
            customer_name = request.args.get('customer_name')
            if not customer_name:
                return {'status' : 200, 'message' : 'No customer_name given', 'data' : []}

            keg_uuid = request.args.get('keg_uuid')
            if not keg_uuid:
                return {'status' : 200, 'message' : 'No keg_uuid given', 'data' : []}

            user_id = request.args.get('user_id')
            if not user_id:
                return {'status' : 200, 'message' : 'No user_id given', 'data' : []}
            # order_product = request.args.get('order_product')
            # if not order_product:
            #     return {'status' : 200, 'message' : 'No order_product given', 'data' : []}
            keg_uuid_id = mysql_client.select(table_name='uuid',filter_condition=f"where uuid = '{keg_uuid}'")
            if keg_uuid_id:
                uuid_id = keg_uuid_id['results'][0]['id']
                keg_order_detail_id = mysql_client.select(table_name='keg_customer_mapping',columns=['order_detail_id'],
                                                    filter_condition="where status = 'delievered'")
                if keg_order_detail_id:
                    order_detail_id = keg_order_detail_id["results"][0]['order_detail_id']
                    assigned_customer_name = mysql_client.select(table_name="order_details", columns=["outlets_name"],
                    filter_condition=f"where order_detail_id = {order_detail_id}")
                    asg_customer_name = assigned_customer_name["results"][0]["outlets_name"]
                    asf_customer_name = asg_customer_name.lower().replace(" ", "")
                    given_customer_name = customer_name.lower().replace(" ", "")
                    if asf_customer_name == given_customer_name:
                        logger.log_info(f"Given customer name {given_customer_name} matched with assigned name")
                        row_obj = dict(order_detail_id=order_detail_id, uuid_id=uuid_id,
                                        user_id=user_id,status="picked")
                        insert_mapped_status = mysql_client.insert(table_name='keg_pickup_mapping',column_values=row_obj)
                    if insert_mapped_status:
                        mapped_status = dict(status=200,data=insert_mapped_status)
                    else:
                        logger.log_info(f"Error while mapping uuid with pickup")
                    return mapped_status
            else:
                logger.log_info(f"No uuid found")
        except Exception as e:
            logger.log_error(f"Error while generating UUI, Error : {e}")
            return mapped_status


    def post(self):
        return {'message': 'POST request received'}
