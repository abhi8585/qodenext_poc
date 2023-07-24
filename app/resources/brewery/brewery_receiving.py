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



class BreweryReceivingResource(Resource):

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
            is_received = self.mysql_client.select(table_name='keg_inventory',filter_condition=f"where uuid_id = {uuid_id} and status = 'brewery'")
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

    def update_pickup_status(self, uuid_id):
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


    def get_current_order_detail(self, uuid_id):
        # keg_pickup_mapping
        order_detail_id = None
        try:
            filter_condition = f"where uuid_id = {uuid_id} and status = 'picked'"
            sel_res = self.mysql_client.select(table_name='keg_pickup_mapping',columns=['order_detail_id'],filter_condition=filter_condition)
            if sel_res and len(sel_res['results']) > 0:
                order_detail_id = sel_res['results'][0]['order_detail_id']
            else:
                self.logger.log_error(f"Failed while selecting last order detail id for keg {uuid_id}")
        except Exception as e:
            self.logger.log_error(f"Error while getting the last order_detail_id for keg UUID : {uuid_id}, {e}")
        return order_detail_id

    def update_keg_pickup_mapping(self, uuid_id):
        is_updated = False
        try:
            order_detail_id  = self.get_current_order_detail(uuid_id=uuid_id)
            if order_detail_id:
                self.logger.log_info(f"updating keg warehouse mapping for {uuid_id} and {order_detail_id}")
                condition = f"where order_detail_id = {order_detail_id} and uuid_id = {uuid_id} and status = 'picked'"
                update_mapping = self.mysql_client.update(table='keg_pickup_mapping',
                                column_values={'status' : 'submitted','update_date':datetime.now()},
                                filter_condition=condition)
                if update_mapping:
                    is_updated = True
                else:
                    self.logger.log_error(f"Failed while updating mapping of pickup to delivered for {uuid_id}")
            else:
                self.logger.log_info(f"Failed while updating keg pickup state to delivered while delivering at Brewery")
        except Exception as e:
            self.logger.log_error(f"MAIN-ERROR : {e} while udpating keg_pickup_mapping table for {uuid_id}")
        return is_updated


    def update_keg_warehouse_mapping(self, uuid_id):
        is_updated = False
        try:
            self.logger.log_info(f"updating keg warehouse brewery dispatch mapping for {uuid_id}")
            condition = f"where uuid_id =  {uuid_id} and status = '{StaticValues.DISPATCHED.value}'"
            update_mapping = self.mysql_client.update(table='warehouse_to_brewery_dispatch',
                            column_values={'status' : StaticValues.DELIVERED.value,'updated_date':datetime.now()},
                            filter_condition=condition)
            if update_mapping:
                is_updated = True
            else:
                self.logger.log_error(f"Failed while updating mapping of warehouse brewery dispatch mapping to delivered for {uuid_id}")
        except Exception as e:
            self.logger.log_error(f"MAIN-ERROR : {e} while udpating warehouse_to_brewery_dispatch table for {uuid_id}")
        return is_updated


    def receive_from_customer(self, uuid_id, user_id):
        is_received = None
        try:
            column_values = dict(uuid_id=uuid_id,user_id=user_id,status='received',created_date=datetime.now(),received_from=StaticValues.CUSTOMER.value)
            received_keg = self.mysql_client.insert(table_name='brewery_keg_received',column_values=column_values)
            if received_keg and received_keg['status'] == 'success':
                # TODO: add code for updating pickup state
                update_keg_pickup_mapping = self.update_keg_pickup_mapping(uuid_id=uuid_id)
                if update_keg_pickup_mapping:
                    is_inventory_updated = self.inventory_client.update_keg_inventory_state(uuid_id=uuid_id,status='brewery')
                    if is_inventory_updated:
                            self.logger.log_info(f"Updated keg inventory status to brewery for keg {uuid_id} after receiving from customer")
                            is_received = received_keg['last_row_id']
                    else:
                        self.logger.log_error(f"Failed while udpating keg state in Brewery disaptch mapping for keg  with UUID {uuid_id}")
                else:
                    self.logger.log_error(f"Failed while updating keg pickup mapping")
            else:
                self.logger.log_error(f"Failed while creating brewery receiving entry for keg from customer with UUID {uuid_id}")
        except Exception as e:
            self.logger.log_error(f"Error while receiving keg from Brewery , {e}")
        return is_received


    def receive_from_warehouse(self, uuid_id, user_id):
        is_received = None
        try:
            column_values = dict(uuid_id=uuid_id,user_id=user_id,status='received',created_date=datetime.now(),received_from=StaticValues.WAREHOUSE.value)
            received_keg = self.mysql_client.insert(table_name='brewery_keg_received',column_values=column_values)
            if received_keg and received_keg['status'] == 'success':
                # TODO: add code for updating pickup state
                update_keg_pickup_mapping = self.update_keg_warehouse_mapping(uuid_id=uuid_id)
                if update_keg_pickup_mapping:
                    is_inventory_updated = self.inventory_client.update_keg_inventory_state(uuid_id=uuid_id,status='brewery')
                    if is_inventory_updated:
                            self.logger.log_info(f"Updated keg inventory status to brewery for keg {uuid_id} after receiving from warehouse")
                            is_received = received_keg['last_row_id']
                    else:
                        self.logger.log_error(f"Failed while udpating keg state in Brewery disaptch mapping for keg  with UUID {uuid_id}")
                else:
                    self.logger.log_error(f"Failed while updating keg warehouse dispatch mapping")
            else:
                self.logger.log_error(f"Failed while creating brewery receiving entry for keg from warehouse  with UUID {uuid_id}")
        except Exception as e:
            self.logger.log_error(f"Error while receiving keg from Brewery , {e}")
        return is_received
        
    
    def get(self):
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
                # if self.check_already_received(uuid_id=uuid_id):
                #     receiving_data['message'] = f"Keg is already at Brewery"
                #     return receiving_data
                # check status if receving from customer or warehouse
                current_status = self.inventory_client.get_keg_status(uuid_id=uuid_id)
                if current_status == 'brewery':
                    receiving_data['message'] = f"Keg is already at Brewery"
                    return receiving_data                    
                if current_status == 'picked':
                    self.logger.log_info(f"Receiving keg from Customer at Brewery with UUID : {uuid_id}")
                    is_received = self.receive_from_customer(uuid_id,user_id)
                    if is_received:
                        self.logger.log_info(f"Keg received successfully at Brewery from Customer with UUID : {uuid_id}")
                        receiving_data['status'] = 200
                        receiving_data['message'] = f"Empty Keg received in the Brewery from Customer"
                        receiving_data['receiving_id'] = is_received
                elif current_status == 'wtb':
                    self.logger.log_info(f"Receiving Empty keg from the Warehouse in Brewery with UUID : {uuid_id}")
                    is_received = self.receive_from_warehouse(uuid_id,user_id)
                    if is_received:
                        self.logger.log_info(f"Keg received successfully at Brewery from Customer with UUID : {uuid_id}")
                        receiving_data['status'] = 200
                        receiving_data['message'] = f"Empty Keg received in the Brewery from Warehouse"
                        receiving_data['receiving_id'] = is_received
                else:
                    self.logger.log_info(f"Keg is not either receiving from Warehouse or Customer")
                    receiving_data['message'] = f"Keg is not in Dispatched/Picked state."
                
                # if received_keg and received_keg['status'] == 'success':
                #     is_inventory_updated = self.inventory_client.update_keg_inventory_state(uuid_id=uuid_id,status='warehouse')
                #     if is_inventory_updated:
                #         upd_brewery_status = self.update_brewery_status(uuid_id=uuid_id)
                #         if upd_brewery_status:
                #             self.logger.log_info(f"Updated Brewery status to delivered for keg {uuid_id}")
                #             receiving_data['status'] = 200
                #             receiving_data['message'] = f"Keg received in the warehouse"
                #             receiving_data['receiving_id'] = received_keg['last_row_id']
                #         else:
                #             self.logger.log_error(f"Failed while updating brewery status for keg : {uuid_id}")
                #     else:
                #         self.logger.log_error(f"Error while udpating keg inventory status to received at warehouse for {uuid}")
                #         received_keg['message'] = f"Error while udpating keg inventory status to received at warehouse!"
                # else:
                #     self.logger.log_error(f"Error while inserting for receiving keg at warehouse {uuid}")
                #     received_keg['message'] = f"Error while inserting for receiving keg at warehouse"
            else:
                self.logger.log_info(f"No data for uuid : {uuid}")
        except Exception as e:
            self.logger.log_error(f"MAIN-Error while dispatching keg from the warehouse : {e}")
        return receiving_data
