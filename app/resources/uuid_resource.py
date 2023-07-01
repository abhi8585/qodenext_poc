from flask_restful import Resource, request
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.csv.csv_client import CsvClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels
from app.utils.uuid.uuid_client import UUIDClient

logger = LoggerClient(VerboseLevels.INFO.value)
config = ConfigClient(env='dev')
mysql_uri = config.get_value("Database", "uri")
mysql_client = MySQLClient(mysql_uri)
uuid_client = UUIDClient()

class UUIDResource(Resource):

    def get(self):
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
