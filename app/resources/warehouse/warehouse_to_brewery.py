from flask import Flask, request
from flask_restful import Resource
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels
from app.utils.uuid.uuid_client import UUIDClient
from app.utils.inventory.inventory_client import InventoryClient
from app.utils.statics.statics import StaticValues
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

    def update_warehouse_inventory(self, uuid_id):
        is_updated = None
        try:
            filter_condition =  f"where uuid_id = {uuid_id} and status = '{StaticValues.RECEIVED.value}' and received_from = '{StaticValues.CUSTOMER.value}'"
            col_values = dict(status=StaticValues.DISPATCHED.value,updated_date=datetime.now())
            upd_brewery = self.mysql_client.update(table='warehouse_inventory',column_values=col_values,filter_condition=filter_condition)
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

    def check_is_empty_keg(self, uuid_id):
        is_empty = False
        try:
            filter_condition =  f"where uuid_id = {uuid_id} and status = '{StaticValues.RECEIVED.value}' and received_from = '{StaticValues.CUSTOMER.value}'"
            sel_res = self.mysql_client.select(table_name='warehouse_inventory',filter_condition=filter_condition)
            if sel_res and len(sel_res['results']) > 0:
                is_empty = True
        except Exception as e:
            self.logger.log_error(f"Error while checking if actually empty keg is dispatchin, {e}")
        return is_empty

    def get(self):
        receiving_data = dict(status=500,dispatched_id="")
        try:
            uuid = request.args.get('uuid')
            if not uuid:
                return {'status' : 400, 'message' : 'No uuid given'}
            user_id = request.args.get('user_id')
            if not user_id:
                return {'status' : 400, 'message' : 'No user_id given'}
            uuid_id = self.get_uuid_id(uuid=uuid)
            if uuid_id:
                # check status if getting from brewery
                current_status = self.get_current_state(uuid_id)
                if current_status != 'warehouse':
                    self.logger.log_info(f"Keg is not in warehouse to dispatch : {uuid_id}")
                    receiving_data['message'] = f"Keg is not in warehouse to dispatch"
                    return receiving_data
                    
                elif current_status == 'warehouse':
                    self.logger.log_info(f"Dispatching Empty keg To Brewery from WareHouse")
                    if not self.check_is_empty_keg(uuid_id=uuid_id):
                        receiving_data['message'] = "Filled keg cannot dispatch back to Brewery"
                        return receiving_data
                    col_values = dict(uuid_id=uuid_id,user_id=user_id,status=StaticValues.DISPATCHED.value,created_date=datetime.now())
                    ins_res = self.mysql_client.insert(table_name='warehouse_to_brewery_dispatch',column_values=col_values)
                    if ins_res:
                        is_udpated = self.update_warehouse_inventory(uuid_id)
                        if is_udpated:
                            self.logger.log_info(f"Updated keg state from warehouse to brewery dispatch")
                            is_state_updated = self.inventory_client.update_keg_inventory_state(uuid_id=uuid_id,status=StaticValues.WAREHOUSE_TO_BREWERY.value)
                            if is_state_updated:
                                self.logger.log_info("keg inventory state updated to warehouse to brewery dispatch")
                                receiving_data['message'] = "keg dispatched to brewery"
                                receiving_data['status'] = 200
                                receiving_data['dispatched_id'] = ins_res['last_row_id']
                            else:
                                self.logger.log_info("failed while updating keg inventory state updated to warehouse to brewery dispatch")
                        else:
                            self.logger.log_info(f"Failed while updating keg state from warehouse to brewery dispatch")
                    else:
                        self.logger.log_error(f"Failed while inserting new row in warehouse to brewery dispatch resource")

                else:
                    self.logger.log_info(f"Keg is not either in warehouse to dispatch")
        except Exception as e:
            self.logger.log_error(f"MAIN-Error while dispatching keg from the warehouse : {e}")
        return receiving_data
