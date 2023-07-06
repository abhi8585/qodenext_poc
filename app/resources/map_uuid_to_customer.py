from flask_restful import Resource, request
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.csv.csv_client import CsvClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels
from app.utils.uuid.uuid_client import UUIDClient


class MapUuidToCustomerResource(Resource):

    def get(self):
        mapped_status = dict(status=500,data="")
        logger = LoggerClient(VerboseLevels.INFO.value)
        config = ConfigClient(env='dev')
        mysql_uri = config.get_value("Database", "uri")
        mysql_client = MySQLClient(mysql_uri)
        try:
            order_detail_id = request.args.get('order_detail_id')
            if not order_detail_id:
                return {'status' : 200, 'message' : 'No order_detail_id given', 'data' : []}

            order_detail_uuid = request.args.get('order_detail_uuid')
            if not order_detail_uuid:
                return {'status' : 200, 'message' : 'No order_detail_uuid given', 'data' : []}

            user_id = request.args.get('user_id')
            if not user_id:
                return {'status' : 200, 'message' : 'No user_id given', 'data' : []}
            order_product = request.args.get('order_product')
            if not order_product:
                return {'status' : 200, 'message' : 'No order_product given', 'data' : []}

            order_detail_uuid_id = mysql_client.select(table_name='uuid',filter_condition=f"where uuid = '{order_detail_uuid}'")
            if order_detail_uuid_id:
                uuid_id = order_detail_uuid_id['results'][0]['id']
                # checking if the keg is of same category 
                # as it get mapped
                keg_code = mysql_client.select(table_name="keg_mapping",columns=["product_name"],filter_condition=f"where uuid_id = {uuid_id} and status = 'dispatched'")
                if keg_code:
                    if len(keg_code["results"]) > 0:
                        keg_code_obj = keg_code["results"][0]["product_name"]
                        if keg_code_obj == order_product:
                            logger.log_info(f"Keg code Matched!")
                            row_obj = dict(order_detail_id=order_detail_id, uuid_id=uuid_id, user_id = user_id,status="delievered")
                            insert_mapped_status = mysql_client.insert(table_name='keg_customer_mapping',column_values=row_obj)
                            if insert_mapped_status:
                                mapped_status = dict(status=200,data=insert_mapped_status)
                                # updating status in keg_mapping after customer delivery
                                keg_status_update = mysql_client.update(table='keg_mapping',column_values={'status':'delievered'},filter_condition=f"where uuid_id = {uuid_id} and status = 'dispatched'")
                                print(f"keg status update {keg_status_update}")
                                if keg_status_update['status'] == "success":
                                    return mapped_status  
                                else:
                                    logger.log_info(f"Failed while update keg {uuid_id} ")
                                    return mapped_status 
                            else:
                                logger.log_info(f"Error while mapping uuid with customer")
                                return mapped_status                        
                        else:
                            logger.log_error(f"Given keg_code not match with assigned keg code")
                            return mapped_status
                    else:
                        logger.log_info(f"No keg found for order_detail_id {order_detail_id}")
                        return mapped_status
            else:
                logger.log_info(f"No associated uuid found for order_detail_id ;{order_detail_id} & uuid : {order_detail_uuid_id}")
                return mapped_status
        except Exception as e:
            logger.log_error(f"Error while mapping order to customer, Error : {e}")
            return mapped_status


    def post(self):
        return {'message': 'POST request received'}
