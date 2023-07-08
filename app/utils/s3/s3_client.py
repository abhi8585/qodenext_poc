import uuid
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels
import boto3

logger = LoggerClient(VerboseLevels.INFO.value)

class S3Client:

    def __init__(self, aws_access_key_id, aws_secret_access_key, bucket_name):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.bucket_name = bucket_name
        self.client = self.create_client()

    
    def create_client(self):
        client = None
        try:
            client = boto3.client(
            's3',
            aws_access_key_id = self.aws_access_key_id,
            aws_secret_access_key = self.aws_secret_access_key
            )
            logger.log_info(f"S3 client created successfully!")
        except Exception as e:
            logger.log_error(f"Errow while creating S3 client")
        return client

    def upload_file(self, file_path, s3_file_name):
        is_uploaded = None
        try:
            upload_file = self.client.upload_file(file_path, self.bucket_name, s3_file_name)
            is_uploaded = True
        except Exception as e:
            logger.log_error(f"Error whiel uploading file to S3 : {file_path}")
        return is_uploaded


    def create_new_folder(self, folder_name):
        # Create S3 client
        # s3 = boto3.client('s3')

        # Create the folder key
        folder_key = f'daily_sales_order/{folder_name}/'

        # Upload an empty file with the folder key as the object key
        self.client.put_object(Bucket=self.bucket_name, Key=folder_key)

        return folder_key




# bucket_name = 'abinbev-orders'
# file_name = 'keg-order.xlsx'  # Replace with the actual file path
# object_key = 'keg-order.xlsx'  # Replace with the desired object key in the bucket

# s3.upload_file(file_name, bucket_name, object_key)