from flask_restful import Resource
from flask import Flask, request
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels

class GetKegCodeResource(Resource):

    def __init__(self):
        self.config = ConfigClient(env='dev')
        self.logger = LoggerClient(VerboseLevels.INFO.value)
        self.mysql_client = MySQLClient(self.config.get_value("Database", "uri"))
    
    def get(self):
        keg_code_data = dict(status=500,keg_code='')
        try:
            uuid = request.args.get('uuid')
            if not uuid:
                return {'status' : 400, 'message' : 'No uuid given', 'data' : ''}
            uuid_id = self.mysql_client.select(table_name='uuid',filter_condition=f"where uuid = '{uuid}'")
            if uuid_id and len(uuid_id['results']) > 0:
                u_id =  uuid_id['results'][0]['id']
                k_id = self.mysql_client.select(table_name='keg_to_uuid',filter_condition=f"where uuid_id = {u_id}")
                if k_id and len(k_id['results']) > 0:
                    keg_id = k_id['results'][0]['keg_id']
                    keg_code = self.mysql_client.select(table_name='keg_sku_master',columns=['keg_product_code'],filter_condition=f"where keg_id = {keg_id}")
                    if keg_code and len(keg_code['results']) > 0:
                        keg_code_data['keg_code'] = keg_code['results'][0]['keg_product_code']
                        keg_code_data['status'] = 200
                    else:
                        self.logger.log_info(f"No master for the associated keg_id {keg_id}")
                else:
                    self.logger.log_info(f"Given UUID : {uuid} is not associated with any keg")
            else:
                self.logger.log_info(f"MAIN-No data for the given UUID {uuid}")  
        except Exception as e:
            self.logger.log_error(f"MAIN-ERROR while getting uuid keg code {e}")
        return keg_code_data

        
