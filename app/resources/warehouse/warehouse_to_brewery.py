from flask import Flask, request
from flask_restful import Resource
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels
from app.utils.uuid.uuid_client import UUIDClient
from app.utils.inventory.inventory_client import InventoryClient
from datetime import datetime



class WareHouseToBreweryDispatchResource(Resource):

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

    def check_already_received(self, uuid_id):
        is_already_received = None
        try:
            is_received = self.mysql_client.select(table_name='warehouse_inventory',filter_condition=f"where uuid_id = {uuid_id} and status = 'received'")
            if is_received and len(is_received['results']) > 0:
                is_already_received = True
        except Exception as e:
            self.logger.log_error(f"Error while checking if keg is already dispatched : {e}")
        return is_already_received

    def check_inventory_status(self, uuid_id):
        inventory_status = False
        try:
            filter_condition = f"where uuid_id = {uuid_id} and status = 'btw'"
            status = self.mysql_client.select(table_name='keg_inventory',filter_condition=filter_condition)
            if status and len(status['results']) > 0:
                inventory_status = True
        except Exception as e:
            self.logger.log_error(f"Error while checking if inventory status is dispatched to warehouse : {e}")
        return inventory_status

    def update_brewery_status(self, uuid_id):
        is_updated = None
        try:
            col_values, filter_condition  = dict(status='delivered',updated_date=datetime.now()), f"where uuid_id = {uuid_id} and status = 'dispatched'"
            upd_brewery = self.mysql_client.update(table='brewery_dispatch_mapping',column_values=col_values,filter_condition=filter_condition)
            if upd_brewery:
                is_updated = True
        except Exception as e:
            self.logger.log_error(f"Error while updating brewery status to delivered for keg {uuid_id}")
        return is_updated

    def get_current_state(self, uuid_id):
        current_state = None
        try:
            filter_condition = f"where uuid_id = {uuid_id}"
            sel_res = self.mysql_client.select(table_name='keg_inventory',columns=['status'],filter_condition=filter_condition)
            if sel_res and len(sel_res['results']) > 0:
                current_state = sel_res['results'][0]['status']
            else:
                self.logger.log_info(f"Failed while selecting current state for keg with UUID {uuid_id}")
        except Exception as e:
            self.logger.log_error(f"Error while getting current state of the keg with UUID {uuid_id}")
        return current_state


    def receive_from_brewery(self, uuid_id):
        is_received = None
        try:
            column_values = dict(uuid_id=uuid_id,user_id=user_id,status='received',created_date=datetime.now(),received_from='brewery')
            received_keg = self.mysql_client.insert(table_name='warehouse_inventory',column_values=column_values)
            if received_keg and received_keg['status'] == 'success':
                is_inventory_updated = self.inventory_client.update_keg_inventory_state(uuid_id=uuid_id,status='warehouse')
                if is_inventory_updated:
                    upd_brewery_status = self.update_brewery_status(uuid_id=uuid_id)
                    if upd_brewery_status:
                        self.logger.log_info(f"Updated Brewery status to delivered for keg {uuid_id}")
                        is_received = True
                    else:
                        self.logger.log_error(f"Failed while udpating keg state in Brewery disaptch mapping for keg  with UUID {uuid_id}")
                    self.logger.log_info(f"Updated Brewery status to delivered for keg {uuid_id}")
                else:
                    self.logger.log_error(f"Failed while udpating keg state in Brewery disaptch mapping for keg  with UUID {uuid_id}")
            else:
                self.logger.log_error(f"Failed while udpating keg inventory state to warehouse for keg  with UUID {uuid_id}")
        except Exception as e:
            self.logger.log_error(f"Error while receiving keg from Brewery , {e}")
        return is_received
    
    def get(self):
        return dict(status=200,message="keg dispatched successfully")
        receiving_data = dict(status=500,receiving_id="")
        try:
            uuid = request.args.get('uuid')
            if not uuid:
                return {'status' : 400, 'message' : 'No uuid given'}
            user_id = request.args.get('user_id')
            if not user_id:
                return {'status' : 400, 'message' : 'No user_id given'}
            uuid_id = self.get_uuid_id(uuid=uuid)
            if uuid_id:
                if self.check_already_received(uuid_id=uuid_id):
                    receiving_data['message'] = f"Keg is already received at warehouse"
                    return receiving_data
                if not self.check_inventory_status(uuid_id):
                    receiving_data['message'] = f"Keg is not dispatched from brewery yet!"
                    return receiving_data
                # check status if getting from brewery
                current_status = self.get_current_state(uuid_id)
                if current_status == 'btw':
                    self.logger.log_info(f"Receiving keg from Brewery with UUID : {uuid_id}")
                    # is_received = self.
                elif current_status == 'picked':
                    self.logger.log_info(f"Receiving Empty keg from the Customer in WareHouse")
                else:
                    self.logger.log_info(f"Keg is not either receiving from Brewery or Customer")
                return
                
                if received_keg and received_keg['status'] == 'success':
                    is_inventory_updated = self.inventory_client.update_keg_inventory_state(uuid_id=uuid_id,status='warehouse')
                    if is_inventory_updated:
                        upd_brewery_status = self.update_brewery_status(uuid_id=uuid_id)
                        if upd_brewery_status:
                            self.logger.log_info(f"Updated Brewery status to delivered for keg {uuid_id}")
                            receiving_data['status'] = 200
                            receiving_data['message'] = f"Keg received in the warehouse"
                            receiving_data['receiving_id'] = received_keg['last_row_id']
                        else:
                            self.logger.log_error(f"Failed while updating brewery status for keg : {uuid_id}")
                    else:
                        self.logger.log_error(f"Error while udpating keg inventory status to received at warehouse for {uuid}")
                        received_keg['message'] = f"Error while udpating keg inventory status to received at warehouse!"
                else:
                    self.logger.log_error(f"Error while inserting for receiving keg at warehouse {uuid}")
                    received_keg['message'] = f"Error while inserting for receiving keg at warehouse"
            else:
                self.logger.log_info(f"No data for uuid : {uuid}")
        except Exception as e:
            self.logger.log_error(f"MAIN-Error while dispatching keg from the warehouse : {e}")
        return receiving_data
