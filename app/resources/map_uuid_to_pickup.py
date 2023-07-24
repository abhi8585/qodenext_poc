from flask_restful import Resource, request
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels
from app.utils.statics.statics import StaticValues
from app.utils.inventory.inventory_client import InventoryClient
from datetime import datetime



class MapUuidToPickupResource(Resource):

    def __init__(self):
        self.config = ConfigClient(env='dev')
        self.logger = LoggerClient(VerboseLevels.INFO.value)
        self.mysql_client = MySQLClient(self.config.get_value("Database", "uri"))
        self.inventory_client = InventoryClient()


    def update_keg_customer_mapping(self, uuid_id):
        is_updated = False
        try:
            self.logger.log_info(f"updating keg customer mapping for {uuid_id}")
            condition = f"where uuid_id = {uuid_id} and status = 'delievered'"
            update_mapping = self.mysql_client.update(table='keg_customer_mapping',
                            column_values={'status' : 'picked','update_date':datetime.now()},
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
            dup = self.mysql_client.select(table_name='keg_pickup_mapping',columns=['id'],filter_condition=f"where uuid_id = '{order_detail_uuid}' and status = 'picked'")
            print(f"dup {dup}")
            if dup and len(dup['results']) > 0:
                is_duplicate = True
        except Exception as e:
            self.logger.log_error(f"HELPER-ERROR while checking duplicate for customer mapping order_detail_uuid {order_detail_uuid}")
        return is_duplicate


    def get(self):
        mapped_status = dict(status=500,data={})
        insert_mapped_status = None
        try:
            customer_name = request.args.get('customer_name')
            if not customer_name:
                return {'status' : 200, 'message' : 'No customer_name given', 'data' : []}

            keg_uuid = request.args.get('keg_uuid')
            if not keg_uuid:
                return {'status' : 200, 'message' : 'No keg_uuid given', 'data' : []}

            user_id = request.args.get('user_id')
            if not user_id:
                return {'status' : 200, 'message' : 'No user_id given', 'data' : []}
            keg_uuid_id = self.mysql_client.select(table_name='uuid',filter_condition=f"where uuid = '{keg_uuid}'")
            if keg_uuid_id:
                
                uuid_id = keg_uuid_id['results'][0]['id']
                keg_order_detail_id = self.mysql_client.select(table_name='keg_customer_mapping',columns=['order_detail_id'],
                                                    filter_condition=f"where uuid_id = {uuid_id} and status = 'delievered'")
                current_status = self.inventory_client.get_keg_status(uuid_id=uuid_id)
                if current_status and current_status != StaticValues.CUSTOMER.value:
                    mapped_status['message'] = f"Keg is not delivered at Customer"
                    return mapped_status                
                if self.check_duplicate(uuid_id):
                    mapped_status['message'] = f"Keg is already picked"
                    return mapped_status
                if keg_order_detail_id and len(keg_order_detail_id["results"]) > 0:
                    order_detail_id = keg_order_detail_id["results"][0]['order_detail_id']
                    assigned_customer_name = self.mysql_client.select(table_name="order_details", columns=["outlets_name"],
                    filter_condition=f"where order_detail_id = {order_detail_id}")
                    asg_customer_name = assigned_customer_name["results"][0]["outlets_name"]
                    asf_customer_name = asg_customer_name.lower().replace(" ", "")
                    given_customer_name = customer_name.lower().replace(" ", "")
                    if asf_customer_name == given_customer_name:
                        self.logger.log_info(f"Given customer name {given_customer_name} matched with assigned name")
                        row_obj = dict(order_detail_id=order_detail_id, uuid_id=uuid_id,
                                        user_id=user_id,status="picked",created_date=datetime.now(),update_date=datetime.now())
                        insert_mapped_status = self.mysql_client.insert(table_name='keg_pickup_mapping',column_values=row_obj)
                    if insert_mapped_status:
                        mapped_status = dict(status=200,data=insert_mapped_status)
                        update_keg_mapping = self.update_keg_customer_mapping(uuid_id)
                        if update_keg_mapping:
                            self.logger.log_info(f"Update keg_customer_mapping succed for {uuid_id}")
                            is_updated = self.inventory_client.update_keg_inventory_state(uuid_id=uuid_id,status=StaticValues.PICKED.value)
                            if is_updated:
                                self.logger.log_info(f"Keg marked to picked status successfully")
                            else:
                                self.logger.log_info(f"Failed while marking Keg to picked status")
                        else:
                            self.logger.log_error(f"Error while updating keg_customer_mapping for {uuid_id}")
                    else:
                        self.logger.log_info(f"Error while mapping uuid with pickup")
                        mapped_status['message'] = f"Keg is not associated with selected customer"
                else:
                    self.logger.log_info(f"Given UUID is not mapped with any customer")
                    mapped_status['message'] = f"Given UUID is not mapped with any customer"
            else:
                self.logger.log_info(f"No uuid found in Database")
                mapped_status['message'] = f"UUID not exist in Database"
        except Exception as e:
            self.logger.log_error(f"Error while Picking up the keg with UUID : {uuid_id}, Error : {e}")
        return mapped_status