from flask_restful import Resource, request
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.xlsx.xlsx_client import XlsxClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels
import json
import uuid

logger = LoggerClient(verbosity=VerboseLevels.INFO.value)

class ProcessOrderResource(Resource):

    def read_order(self,file_path, sheet_name):
        order_data = None
        try:
            selected_cols = ['Date','Lisence/Billing Name','Outlets Name','Area','BUD 30L','Mag 30','Hog 15','Draught Code']
            xlsx_client = XlsxClient(file_path=file_path,sheet_name=sheet_name)
            order_data = xlsx_client.read(cols_list=selected_cols)
        except Exception as e:
            logger(e)
        return order_data
   
    def create_order_headers(self, mysql_client, order_date):
        order_id = None
        try:
            insert_status = mysql_client.insert(table_name='order_header',column_values={'order_date':order_date})
            if insert_status["status"] == "success":
                insert_order_id = insert_status['last_row_id']
                if insert_order_id:
                    order_id = insert_order_id
                    logger.log_info(f"Order headers created successfully!")
            else:
                logger.log_info(f"Error while creating order headers for {order_date}")  
        except Exception as e:
            logger.log_info(f"Error while creating order detail entry, Error : {e}")
        return order_id

    def process_order_data(self, order_row):
        print(f"receiver order row  {order_row}")
        import math
        process_status = None
        try:
            if order_row:
                process_status = dict()
                for key, value in order_row.items():
                    if key == 'Draught Code':
                        process_status['draught_code'] = value
                    if key == 'Lisence/Billing Name':
                        process_status['license_billing_name'] = value
                    if key == "Outlets Name":
                        process_status["outlets_name"] = value
                    if key == "Area":
                        process_status["area"] = value
                    if key == "Hog 15":
                        if math.isnan(value):
                            value = 0
                        process_status["hog_15"] = int(value)
                    if key == "BUD 30L":
                        if math.isnan(value):
                            value = 0
                        process_status["bud_30"] = int(value)
                    if key == "Mag 30":
                        if math.isnan(value):
                            value = 0
                        process_status['mag_30'] = int(value)
                return process_status        
        except Exception as e:
            logger.log_info(e)
        return process_status


    def save_order(self, file_path):
        ret_obj = dict(status=None,order_id=None)
        try:
            sheet_name = 'Unix'
            config = ConfigClient(env='dev')
            mysql_uri = config.get_value("Database", "uri")
            mysql_client = MySQLClient(mysql_uri)
            order_data = self.read_order(file_path=file_path,sheet_name=sheet_name)
            if order_data:
                order_date = order_data[0]['Date'].strftime('%Y-%m-%d')
                order_id = self.create_order_headers(mysql_client=mysql_client,order_date=order_date)
                for order in order_data:
                    prc_order_data = self.process_order_data(order)
                    if prc_order_data:
                        prc_order_data['order_id'] = order_id
                    order_detail_status = mysql_client.insert(table_name='order_details',column_values=prc_order_data)
                    if order_detail_status['status'] == "success":
                        logger.log_info(f"Order detail row created successfully {prc_order_data}")
                    else:
                        logger.log_error(f"Error while creating order row {prc_order_data}")
                ret_obj['status'] = 200
                ret_obj['order_id'] = order_id
            else:
                logger(f"No order data to process")
                ret_obj["status"] = 200
                ret_obj["order_id"] = ""
        except Exception as e:
            logger.log_error(f"Error in Process order get request {e}")
        return ret_obj

    def post(self):
        return {'message': 'POST request received'}
