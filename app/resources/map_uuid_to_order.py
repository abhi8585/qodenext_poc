from flask_restful import Resource, request
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels
from app.utils.inventory.inventory_client import InventoryClient
from app.utils.statics.statics import StaticValues
from datetime import datetime

class MapUuidToOrderResource(Resource):

    def __init__(self):
        self.logger = LoggerClient(VerboseLevels.INFO.value)
        self.config = ConfigClient(env=VerboseLevels.DEV.value)
        self.mysql_client = MySQLClient(self.config.get_value("Database", "uri"))
        self.inventory_client = InventoryClient()

    def is_duplicate(self, order_id, uuid_id):
        is_duplicate = False
        try:
            condition = f"where order_id = {order_id} and uuid_id = {uuid_id} and status='dispatched'"
            check_duplicate = self.mysql_client.select(table_name='keg_mapping', filter_condition=condition)
            if check_duplicate and len(check_duplicate['results']) > 0:
                is_duplicate = True
        except Exception as e:
            self.logger.log_error(f"Error {e} while checking UUID duplicate order.")
        return is_duplicate


    def update_warehouse_inventory(self, uuid_id, user_id):
        is_updated = None
        try:
            filter_condition = f"where uuid_id = {uuid_id} and status = '{StaticValues.RECEIVED.value}'"
            col_values = dict(status=StaticValues.CUSTOMER_DISPATCH_FROM_WAREHOUSE.value,updated_date=datetime.now())
            upd_res = self.mysql_client.update(table='warehouse_inventory',column_values=col_values,filter_condition=filter_condition)
            if upd_res:
                is_updated=True
            else:
                self.logger.log_info(f"Failed while updating warehouse inventory while dispatching to customer")
        except Exception as e:
            self.logger.log_error(f"Error while updating warehouse inventory")
        return is_updated


    def get(self):
        mapped_status = dict(status=200,data={})
        try:
            order_id = request.args.get('order_id')
            if not order_id:
                return {'status' : 400, 'message' : 'No order_id given', 'data' : []}

            order_uuid = request.args.get('order_uuid')
            if not order_uuid:
                return {'status' : 400, 'message' : 'No order_uuid given', 'data' : []}

            user_id = request.args.get('user_id')
            if not user_id:
                return {'status' : 400, 'message' : 'No user_id given', 'data' : []}
            order_product = request.args.get('order_product')
            if not order_product:
                return {'status' : 400, 'message' : 'No order_product given', 'data' : []}
            order_uuid_id = self.mysql_client.select(table_name='uuid',filter_condition=f"where uuid = '{order_uuid}'")
            print(f"order uuid {order_uuid_id}")
            if order_uuid_id and len(order_uuid_id['results']) > 0:
                uuid_id = order_uuid_id['results'][0]['id']
                is_duplicate = self.is_duplicate(order_id, uuid_id)
                if is_duplicate:
                    mapped_status['message'] = f"{order_uuid} is already mapped"
                    return mapped_status
                # udpating code to add check if keg actually receive in warehoyse to dispatch
                current_status = self.inventory_client.get_keg_status(uuid_id=uuid_id)
                if current_status and current_status != StaticValues.WAREHOUSE.value:
                    mapped_status['message'] = f"Keg is not in the Warehouse"
                    return mapped_status
                row_obj = dict(order_id=order_id, uuid_id=uuid_id, product_name = order_product
                                ,status="dispatched", created_date = datetime.now())
                insert_mapped_status = self.mysql_client.insert(table_name='keg_mapping',column_values=row_obj)
                if insert_mapped_status:
                    # TODO : update the warehouse_inventory status to disptached to customer
                    is_state_updated = self.inventory_client.update_keg_inventory_state(uuid_id=uuid_id,status='wtc')
                    if is_state_updated:
                        self.logger.log_info(f"Updated keg state to dispatch from warehouse to customer")
                        # updating warehouse inventory mapping to dispatch to customer
                        if self.update_warehouse_inventory(uuid_id=uuid_id,user_id=user_id):
                            self.logger.log_info(f"Update warehouse inventory to dispatch to customer")
                        else:
                            self.logger.log_info(f"failed while updating warehouse inventory to dispatch to customer")
                    else:
                        self.logger.log_info(f"Failed while updating keg state in inventory")
                    mapped_status = dict(status=200,data=insert_mapped_status)
                    self.logger.log_info(f"UUID : {order_uuid} successfully mapped to Order with ID :  {order_id}")
                else:
                    self.logger.log_info(f"Error while mapping UUID with order")
            else:
                self.logger.log_info(f"No uuid found for : {order_uuid}")
        except Exception as e:
            mapped_status['status'] = 500
            mapped_status['data'] = ""
            self.logger.log_error(f"INTERNAL-Error while mapping UUID, Error : {e}")
        return mapped_status