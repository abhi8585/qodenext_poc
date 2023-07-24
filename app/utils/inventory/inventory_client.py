from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from datetime import datetime


class InventoryClient:

    def __init__(self):
        self.logger = LoggerClient(verbosity=VerboseLevels.INFO.value)
        self.config = ConfigClient(env='dev')
        self.mysql_client = MySQLClient(self.config.get_value("Database", "uri"))

    def update_keg_inventory_state(self, uuid_id, status):
        is_updated = False
        try:
            ucv = dict(status=status,updated_date=datetime.now()) 
            u_keg_status = self.mysql_client.update(table='keg_inventory',column_values=ucv,filter_condition=f"where uuid_id = {uuid_id}")
            if u_keg_status and u_keg_status['status'] == 'success':
                is_updated = True
            else:
                self.logger.log_error(f"Not able to update inventory for keg {uuid_id}")
        except Exception as e:
            self.logger.log_error(f"Error while updating keg inventory for UUID_ID :  {uuid_id}")
        return is_updated

    def get_keg_type(self,upd_dict,c_count,product_code):
        try:
            if product_code == "bud_30":
                upd_dict['bud_30'] = c_count
            if product_code == "mag_30":
                upd_dict["mag_30"] = c_count
            if product_code == "hog_15":
                upd_dict["hog_15"] = c_count
            return upd_dict
        except Exception as e:
            self.logger.log_error(f"Error while getting keg type")
        return None


    def get_keg_status(self, uuid_id):
        keg_status = None
        try:
            filter_condition = f"where uuid_id = {uuid_id}"
            sel_res = self.mysql_client.select(table_name='keg_inventory',columns=['status'],filter_condition=filter_condition)
            if sel_res and len(sel_res['results']) > 0:
                keg_status = sel_res['results'][0]['status']
            else:
                self.logger.log_info(f"Failed while getting keg status from inventory")
        except Exception as e:
            self.logger.log_error(f"Error while getting keg status for {uuid_id}")
        return keg_status

    def update_keg_product_inventory_state(self, uuid_id, current_product_code):
        is_updated = False
        try:
            filter_condition = f"where keg_product_code = '{current_product_code}'"
            keg_master_code = self.mysql_client.select(table_name='keg_sku_master',columns=['keg_id'],filter_condition=filter_condition)
            if keg_master_code and len(keg_master_code['results']) > 0:
                self.logger.log_info(f"getting keg code id from the sku master")
                keg_code  = keg_master_code['results'][0]['keg_id']
            filter_condition = f"where uuid_id = {uuid_id}"
            current_count = self.mysql_client.select(table_name='keg_product_mapping',columns=[current_product_code],filter_condition=filter_condition)
            if current_count and len(current_count['results']) > 0:
                c_count = current_count['results'][0][current_product_code]
                c_count = c_count + 1
                upd_dict = dict(product_code=keg_code)
                upd_dict = self.get_keg_type(upd_dict,c_count,current_product_code)
                upd_keg_product = self.mysql_client.update(table='keg_product_mapping',column_values=upd_dict,filter_condition=f"where uuid_id = {uuid_id}")
                if upd_keg_product:
                    self.logger.log_info(f"Updated the keg : {uuid_id} product mapping to {current_product_code} with count {current_product_code}")
                    is_updated = True
                else:
                    self.logger.log_error(f"Failed while updating keg mapping")
            else:
                self.logger.log_error(f"No keg mapping to product")
        except Exception as e:
            self.logger.log_error(f"Error while updating keg inventory for UUID_ID :  {uuid_id}, {e}")
        return is_updated