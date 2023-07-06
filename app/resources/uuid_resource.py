from flask_restful import Resource, request
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.csv.csv_client import CsvClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels
from app.utils.uuid.uuid_client import UUIDClient


class UUIDResource(Resource):

    def get(self):
        logger = LoggerClient(VerboseLevels.INFO.value)
        config = ConfigClient(env='dev')
        mysql_uri = config.get_value("Database", "uri")
        mysql_client = MySQLClient(mysql_uri)
        uuid_client = UUIDClient()
        generated_uuids = None
        try:
            total = request.args.get('total')
            generated_uuids = uuid_client.create_uuid(total_uuid=int(total))
            generated_status = False
            for uuid in generated_uuids:
                
                uuid_insert = mysql_client.insert(table_name='uuid',column_values={'uuid' : uuid})
                if uuid_insert:
                    generated_status = True
            if generated_status:
                return {'status' : 200, 'uuid' : generated_uuids}
            else:
                return {'status' : 200, 'uuid' : []}
        except Exception as e:
            logger.log_error(f"Error while generating UUI, Error : {e}")
            return generated_uuids


    def post(self):
        return {'message': 'POST request received'}


class UUIDValidationResource(Resource):

    def get(self):
        logger = LoggerClient(VerboseLevels.INFO.value)
        config = ConfigClient(env='dev')
        mysql_uri = config.get_value("Database", "uri")
        mysql_client = MySQLClient(mysql_uri)
        ret_obj = dict(is_valid=False,status=200)
        try:
            keg_uuid = request.args.get('uuid')
            if not keg_uuid:
                return {'status' : 200, 'message' : 'No keg_uuid given'}
            check_uuid = mysql_client.select(table_name='uuid',filter_condition=f"where uuid = '{keg_uuid}'")
            if check_uuid:
                if len(check_uuid['results']) > 0:
                    logger.log_info(f"Valid UUID {keg_uuid} found in database")
                    ret_obj['is_valid'] = True
                    ret_obj['status'] = 200
                else:
                    logger.log_info(f"Invalid UUID {keg_uuid} not found in database")
        except Exception as e:
            logger.log_error(f"Error while generating UUI, Error : {e}")
            ret_obj['status'] = 500
        return ret_obj


    def post(self):
        return {'message': 'POST request received'}
