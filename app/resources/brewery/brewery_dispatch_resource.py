from flask import Flask, request
from flask_restful import Resource
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels
from app.utils.uuid.uuid_client import UUIDClient
from app.utils.inventory.inventory_client import InventoryClient
from datetime import datetime



class BreweryDispatchResource(Resource):

    def __init__(self):
        self.config = ConfigClient(env='dev')
        self.mysql_client = MySQLClient(self.config.get_value("Database", "uri"))
        self.logger = LoggerClient(verbosity=VerboseLevels.INFO.value)
        self.uuid_client = UUIDClient()
        self.inventory_client = InventoryClient()

    def get_uuid_id(self, uuid):
        uuid_id = None
        try:
            uuid = self.mysql_client.select(table_name='uuid',columns=['id'],filter_condition=f"where uuid = '{uuid}'")
            if uuid and len(uuid['results']) > 0:
                uuid_id = uuid['results'][0]['id']
            else:
                self.logger.log_error(f"Selecting UUID results is None for : {uuid}")
        except Exception as e:
            self.logger.log_error(f"Error while getting uuid_id for {uuid_id}")
        return uuid_id

    def check_already_dispatched(self, uuid_id):
        is_already_dispatched = None
        try:
            is_dispatched = self.mysql_client.select(table_name='brewery_dispatch_mapping',filter_condition=f"where uuid_id = {uuid_id} and status = 'dispatched'")
            if is_dispatched and len(is_dispatched['results']) > 0:
                is_already_dispatched = True
        except Exception as e:
            self.logger.log_error(f"Error while checking if keg is already dispatched : {e}")
        return is_already_dispatched

    def check_in_inventory(self):
        self.logger.log_info(f"Checking if keg exists in inventory")
        not_in_inventory = None
        try:
            filter_condition = f"where status = 'brewery' limit 1"
            in_inventory = self.mysql_client.select(table_name='keg_inventory',columns=['uuid_id'],filter_condition=filter_condition)
            if in_inventory and len(in_inventory['results']) == 0:
                not_in_inventory = True
            else:
                self.logger.log_info(f"No Keg in Brewery to Dispatch")
        except Exception as e:
            self.logger.log_error(f"Error while checking if keg exists in inventory to dispatch:{e}")
        return not_in_inventory

    def get(self):
        dispatch_data = dict(status=500,dispatched_id="")
        try:
            uuid = request.args.get('uuid')
            if not uuid:
                return {'status' : 400, 'message' : 'No uuid given'}
            keg_code = request.args.get('keg_code')
            if not keg_code:
                return {'status' : 400, 'message' : 'No keg_code given'}
            user_id = request.args.get('user_id')
            if not user_id:
                return {'status' : 400, 'message' : 'No user_id given'}
            if self.check_in_inventory():
                dispatch_data['message'] = f"No keg in inventory to dispatch"
                return dispatch_data 
            uuid_id = self.get_uuid_id(uuid=uuid)
            if uuid_id:
                if self.check_already_dispatched(uuid_id=uuid_id):
                    dispatch_data['message'] = f"Keg is already dispatched to warehouse"
                    return dispatch_data                
                update_keg_product_code = self.inventory_client.update_keg_product_inventory_state(uuid_id=uuid_id,current_product_code=keg_code)
                if not update_keg_product_code:
                    dispatch_data['message'] = f"Error while updating keg product status"
                    return dispatch_data
                column_values = dict(uuid_id=uuid_id,user_id=user_id,status='dispatched',created_date=datetime.now())
                dispatch_keg = self.mysql_client.insert(table_name='brewery_dispatch_mapping',column_values=column_values)
                if dispatch_keg and dispatch_keg['status'] == 'success':
                    is_inventory_updated = self.inventory_client.update_keg_inventory_state(uuid_id=uuid_id,status='btw')
                    if is_inventory_updated:
                        dispatch_data['status'] = 200
                        dispatch_data['dispatched_id'] = dispatch_keg['last_row_id']
                        dispatch_data['message'] = f"Keg dispatched successfully!"
                    else:
                        self.logger.log_error(f"Error while udpating keg status to dispatch from brewery for {uuid}")
                        dispatch_data['message'] = f"Error while udpating keg status to dispatch from brewery!"
                else:
                    self.logger.log_error(f"Error while dispatching keg to warehouse from brewery for {uuid}")
                    dispatch_data['message'] = f"Error while dispatching keg to warehouse from brewery!"
            else:
                self.logger.log_info(f"No data for uuid : {uuid}")
                dispatch_data['message'] = f"Wrong UUID scanned!"
        except Exception as e:
            self.logger.log_error(f"MAIN-Error while dispatching keg from the warehouse : {e}")
        return dispatch_data
