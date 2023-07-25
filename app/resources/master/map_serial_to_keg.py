from flask_restful import Resource, request
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels
from datetime import datetime

class MapSerialToKeg(Resource):

    def __init__(self):
        self.config = ConfigClient(env='dev')
        self.logger = LoggerClient(VerboseLevels.INFO.value)
        self.mysql_client = MySQLClient(self.config.get_value("Database", "uri"))

    def check_duplicate(self, uuid_id):
        self.logger.log_info(f"checking if the keg is already mapped to any serial number")
        is_duplicate = False
        try:
            dup = self.mysql_client.select(table_name='keg_serial_number_mapping',columns=['id'],filter_condition=f"where uuid_id = {uuid_id}")
            if dup and len(dup['results']) > 0:
                is_duplicate = True
        except Exception as e:
            self.logger.log_error(f"HELPER-ERROR while checking is keg is already mappped : {e}")
        return is_duplicate


    def check_duplicate_serial_number(self, serial_number):
        is_duplicate = None
        try:
            filter_condition = f"where serial_number = '{serial_number}'"
            sel_res = self.mysql_client.select(table_name='keg_serial_number_mapping',columns=['serial_number'],filter_condition=filter_condition)
            if sel_res and len(sel_res['results']) > 0:
                is_duplicate = True
            else:
                self.logger.log_info(f"Failed while check serial number duplicate")
        except Exception as e:
            self.logger.log_error(f"Error while checking if serial number is duplicate")
        return is_duplicate

    def get(self):
        mapped_status = dict(status=500,mapped_id="")
        try:
            uuid = request.args.get('uuid')
            if not uuid:
                return {'status' : 400, 'message' : 'No uuid given', 'data' : []}

            serial_number = request.args.get('serial_number')
            if not serial_number:
                return {'status' : 400, 'message' : 'No serial_number given', 'data' : []}

            user_id = request.args.get('user_id')
            if not user_id:
                return {'status' : 400, 'message' : 'No user_id given', 'data' : []}

            order_detail_uuid_id = self.mysql_client.select(table_name='uuid',filter_condition=f"where uuid = '{uuid}'")
            if order_detail_uuid_id and len(order_detail_uuid_id['results']) > 0:
                uuid_id = order_detail_uuid_id['results'][0]['id']
                # checking if the serial number is already mapped 
                if  self.check_duplicate(uuid_id):
                    mapped_status['message'] = f"keg is already mapped"
                    return mapped_status 
                if self.check_duplicate_serial_number(serial_number=serial_number):
                    mapped_status['message'] = f"Serial Number already mapped"
                    return mapped_status 
                row_obj = dict(uuid_id=uuid_id, user_id=user_id,
                            serial_number=serial_number, created_date=datetime.now())
                insert_mapped_status = self.mysql_client.insert(table_name='keg_serial_number_mapping',column_values=row_obj)
                if insert_mapped_status:
                    if insert_mapped_status['status'] == "success":
                        self.logger.log_info(f"Keg {uuid} mapped successfully with serial number {serial_number}")
                        mapped_status['message'] = f"Keg mapped successfully with serial number"
                        mapped_status['status'] = 200
                        mapped_status['mapped_id'] = insert_mapped_status['last_row_id']
                    else:
                        self.logger.log_info(f"Failed while mapping keg {uuid_id} to {serial_number}")
                        mapped_status['message'] = f"Error while mapping keg"
                else:
                    mapped_status['message'] = f"Error while mapping keg"
            else:
                self.logger.log_info(f"No associated uuid found for - {uuid}")
                mapped_status['message'] = f"No associated uuid found in Database"
        except Exception as e:
            self.logger.log_error(f"Error while mapping keg to serial number, Error : {e}")
        return mapped_status
