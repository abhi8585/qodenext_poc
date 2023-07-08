from flask_restful import Resource, request
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.csv.csv_client import CsvClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels
from app.utils.uuid.uuid_client import UUIDClient
from app.utils.s3.s3_client import S3Client
from app.resources.proccess_order import ProcessOrderResource
import os
from datetime import date


class UploadSalesOrderResource(Resource):

    def __init__(self):
        self.logger = LoggerClient(VerboseLevels.INFO.value)
        self.config = ConfigClient(env=VerboseLevels.DEV.value)
        self.process_client = ProcessOrderResource()

    def get(self):
        return {'message' : 'from get request'}


    def create_local_folder(self,folder_name):
        # Get the current working directory
        is_created = None
        try:
            current_dir = os.getcwd()
            is_created = os.path.join(current_dir, folder_name)
            os.makedirs(is_created)
        except Exception as e:
            self.logger.log_error(f"HELPER-Error while creating local folder : {e}")
        return is_created

    def save_file(self, order_file):
        is_saved = None
        try:
            # saved_dir = self.create_local_folder('uploaded_orders')
            saved_dir = 'uploaded_orders'
            file_path = os.path.join(saved_dir, order_file.filename)
            order_file.save(file_path)
            is_saved = file_path
            self.logger.log_info(f"HELPER-Order File saved successfully : {order_file} in path : {saved_dir}")
        except Exception as e:
            self.logger.log_error(f"HELPER-Error while saving file : {order_file} in path : {saved_dir} : {e}")
        return is_saved


    def create_s3_client(self):
        s3_client = None
        try:
            aws_access_key_id = self.config.get_value("s3", "aws_access_key_id")
            aws_secret_access_key = self.config.get_value("s3", "aws_secret_access_key")
            aws_bucket_name = self.config.get_value("s3", "aws_bucket_name")
            s3_client = S3Client(aws_access_key_id, aws_secret_access_key, aws_bucket_name)
        except Exception as e:
            self.logger.log_error(f"HELPER-Error while creating S3 client {e}")
        return s3_client

    
    def upload_file(self, file_path, s3_file_name):
        is_uploaded = None
        try:
            s3_client = self.create_s3_client()
            is_uploaded = s3_client.upload_file(file_path,s3_file_name)
            self.logger.log_info(f"HELPER-Order File uploaded successfully to s3 : {file_path}")
        except Exception as e:
            self.logger.log_error(f"HELPER-Error while uploading file : {file_path},  to S3 {e}")
        return is_uploaded

    
    def create_s3_folder(self, folder_name):
        is_created = None
        try:
            s3_client = self.create_s3_client()
            is_created = s3_client.create_new_folder(folder_name)
        except Exception as e:
            self.logger.log_error(f"Error while creating folder : {e}")
        return is_created



    def get_today_date(self):
        today_str = None
        try:
            today = date.today()
            today_str = today.strftime('%Y-%m-%d')
        except Exception as e:
            self.logger.log_error(f"HELPER-Error while getting today date : {e}")
        return today_str

    def post(self):
        ret_obj = dict(status=500,message="")
        try:
            order_file = request.files['order_file']
            if not order_file:
                return {'status' : 200, 'message' : 'No order file given'}
            is_file_saved = self.save_file(order_file)

            is_folder_created = self.create_s3_folder(self.get_today_date())
            s3_file_name = is_folder_created + is_file_saved.split('/')[1]
            if is_file_saved:
                is_uploaded = self.upload_file(is_file_saved,s3_file_name)
                if is_uploaded:
                    is_order_stored = self.process_client.save_order(is_file_saved)
                    if is_order_stored['status']:
                        ret_obj['status'] = 200
                        ret_obj['message'] = f"Order created successfully for {is_file_saved}"
                        ret_obj['order_id'] = is_order_stored['order_id']
                    else:
                        self.logger.log_error(f"MAIN-Error while storing data in DB for {order_file}")
                else:
                    self.logger.log_error(f"MAIN-Error while uploading order file to S3 : {order_file}")
            else:
                self.logger.log_error(f"MAIN-Error while saving order file : {order_file}")
            return ret_obj, 201
        except Exception as e:
            self.logger.log_error(f"MAIN-Error while uploading Sales order : {e}")
            return ret_obj, 500
