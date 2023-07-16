from flask_restful import Resource, request
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.csv.csv_client import CsvClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels
from app.utils.uuid.uuid_client import UUIDClient
from datetime import datetime

class MapUuidToCustomerResource(Resource):

    def __init__(self):
        self.config = ConfigClient(env='dev')
        self.logger = LoggerClient(VerboseLevels.INFO.value)
        self.mysql_client = MySQLClient(self.config.get_value("Database", "uri"))

    def check_duplicate(self,order_detail_id, order_detail_uuid ):
        self.logger.log_info(f"checking for duplicates")
        is_duplicate = False
        try:
            dup = self.mysql_client.select(table_name='keg_customer_mapping',columns=['id'],filter_condition=f"where order_detail_id = {order_detail_id} and uuid_id = '{order_detail_uuid}' and status = 'delievered'")
            print(f"dup {dup}")
            if dup and len(dup['results']) > 0:
                is_duplicate = True
        except Exception as e:
            self.logger.log_error(f"HELPER-ERROR while checking duplicate for customer mapping for order_detail_id {order_detail_id} & order_detail_uuid {order_detail_uuid}")
        return is_duplicate


    def get(self):
        mapped_status = dict(status=500,data="")
        try:
            order_detail_id = request.args.get('order_detail_id')
            if not order_detail_id:
                return {'status' : 400, 'message' : 'No order_detail_id given', 'data' : []}

            order_detail_uuid = request.args.get('order_detail_uuid')
            if not order_detail_uuid:
                return {'status' : 400, 'message' : 'No order_detail_uuid given', 'data' : []}

            user_id = request.args.get('user_id')
            if not user_id:
                return {'status' : 400, 'message' : 'No user_id given', 'data' : []}
            order_product = request.args.get('order_product')
            if not order_product:
                return {'status' : 400, 'message' : 'No order_product given', 'data' : []}

            order_detail_uuid_id = self.mysql_client.select(table_name='uuid',filter_condition=f"where uuid = '{order_detail_uuid}'")
            if order_detail_uuid_id:
                uuid_id = order_detail_uuid_id['results'][0]['id']
                # checking if the keg is of same category 
                # as it get mapped
                # check for duplicate
                if  self.check_duplicate(order_detail_id, uuid_id):
                    mapped_status['message'] = f"keg is already delievered"
                    return mapped_status
                keg_code = self.mysql_client.select(table_name="keg_mapping",columns=["product_name"],filter_condition=f"where uuid_id = {uuid_id} and status = 'dispatched'")
                if keg_code:
                    if len(keg_code["results"]) > 0:
                        keg_code_obj = keg_code["results"][0]["product_name"]
                        if keg_code_obj == order_product:
                            self.logger.log_info(f"Keg code Matched!")
                            
                            row_obj = dict(order_detail_id=order_detail_id, uuid_id=uuid_id, user_id = user_id,
                                        status="delievered", created_date=datetime.now(),update_date=datetime.now(),keg_product_code=order_product)
                            insert_mapped_status = self.mysql_client.insert(table_name='keg_customer_mapping',column_values=row_obj)
                            if insert_mapped_status:
                                mapped_status = dict(status=200,data=insert_mapped_status)
                                # updating status in keg_mapping after customer delivery
                                keg_status_update = self.mysql_client.update(table='keg_mapping',column_values={'status':'delievered','update_date':datetime.now()},filter_condition=f"where uuid_id = {uuid_id} and status = 'dispatched'")
                                self.logger.log_info(f"Updating keg status in keg_mapping{keg_status_update}")
                                if keg_status_update['status'] == "success":
                                    self.logger.log_info(f"Updated keg status in keg_mapping")
                                else:
                                    self.logger.log_info(f"Failed while update keg {uuid_id} ")
                            else:
                                self.logger.log_info(f"Error while mapping uuid with customer")                       
                        else:
                            self.logger.log_error(f"Given keg_code not match with assigned keg code") 
                            mapped_status['message'] = f"Given keg_code does not match with assigned product code"
                    else:
                        self.logger.log_info(f"No keg found for order_detail_id {order_detail_id}")
                        mapped_status['message'] = f"The keg is not dispatched yet"
            else:
                self.logger.log_info(f"No associated uuid found for order_detail_id ;{order_detail_id} & uuid : {order_detail_uuid_id}")
                mapped_status['message'] = f"No associated uuid found in Database"
        except Exception as e:
            self.logger.log_error(f"Error while mapping order to customer, Error : {e}")
        return mapped_status
