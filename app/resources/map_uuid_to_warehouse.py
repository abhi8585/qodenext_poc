from flask_restful import Resource, request
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels
from datetime import datetime



class MapUuidToWareHouseResource(Resource):

    def __init__(self):
        self.config = ConfigClient(env='dev')
        self.logger = LoggerClient(VerboseLevels.INFO.value)
        self.mysql_client = MySQLClient(self.config.get_value("Database", "uri"))


    def update_keg_pickup_mapping(self, uuid_id, order_detail_id):
        is_updated = False
        try:
            self.logger.log_info(f"updating keg warehouse mapping for {uuid_id} and {order_detail_id}")
            condition = f"where order_detail_id = {order_detail_id} and uuid_id = {uuid_id} and status = 'picked'"
            update_mapping = self.mysql_client.update(table='keg_pickup_mapping',
                            column_values={'status' : 'submitted','update_date':datetime.now()},
                            filter_condition=condition)
            if update_mapping:
                is_updated = True
        except Exception as e:
            self.logger.log_error(f"MAIN-ERROR : {e} while udpating keg_customer_mapping table for {uuid_id}")
        return is_updated

    def check_duplicate(self,order_detail_uuid ):
        self.logger.log_info(f"checking for duplicates")
        is_duplicate = False
        try:
            dup = self.mysql_client.select(table_name='keg_warehouse_mapping',columns=['id'],filter_condition=f"where uuid_id = '{order_detail_uuid}' and status = 'submitted'")
            print(f"dup {dup}")
            if dup and len(dup['results']) > 0:
                is_duplicate = True
        except Exception as e:
            self.logger.log_error(f"HELPER-ERROR while checking duplicate for customer mapping order_detail_uuid {order_detail_uuid}")
        return is_duplicate


    def get(self):
        mapped_status = dict(status=500,data="")
        try:
            keg_uuid = request.args.get('keg_uuid')
            if not keg_uuid:
                return {'status' : 200, 'message' : 'No keg_uuid given', 'data' : []}
            user_id = request.args.get('user_id')
            if not user_id:
                return {'status' : 200, 'message' : 'No user_id given', 'data' : []}
            keg_uuid_id = self.mysql_client.select(table_name='uuid',filter_condition=f"where uuid = '{keg_uuid}'")
            if keg_uuid_id and len(keg_uuid_id['results']) > 0:
                uuid_id = keg_uuid_id['results'][0]['id']
                if self.check_duplicate(uuid_id):
                    mapped_status['message'] = f"Keg already submitted to WareHouse"
                    return mapped_status
                keg_order_detail_id = self.mysql_client.select(table_name='keg_pickup_mapping',columns=['order_detail_id'],
                                                    filter_condition=f"where uuid_id = {uuid_id} and status = 'picked'")
                if keg_order_detail_id and len(keg_order_detail_id["results"]) > 0:
                    order_detail_id = keg_order_detail_id["results"][0]['order_detail_id']
                    row_obj = dict(order_detail_id=order_detail_id, uuid_id=uuid_id,
                                    user_id=user_id,status="submitted",created_date=datetime.now(),update_date=datetime.now())
                    insert_mapped_status = self.mysql_client.insert(table_name='keg_warehouse_mapping',column_values=row_obj)
                    if insert_mapped_status:
                        mapped_status = dict(status=200,data=insert_mapped_status)
                        update_keg_mapping = self.update_keg_pickup_mapping(uuid_id, order_detail_id)
                        if update_keg_mapping:
                            self.logger.log_info(f"Update keg_customer_mapping successfull for {uuid_id}")
                        else:
                            self.logger.log_error(f"Error while updating keg_customer_mapping for {uuid_id}")
                    else:
                        self.logger.log_info(f"Error while mapping uuid with warehouse")
                        mapped_status['message'] = f"Error while mapping uuid to warehouse"
                else:
                    self.logger.log_info(f"Given UUID is not picked up yet")
                    mapped_status['message'] = f"Given UUID is not picked up or already submitted"
            else:
                self.logger.log_info(f"No uuid found in Database")
                mapped_status['message'] = f"UUID not exist in Database"
        except Exception as e:
            self.logger.log_error(f"Error while generating UUI, Error : {e}")
        return mapped_status