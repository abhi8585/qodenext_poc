from flask_restful import Resource, request
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels

logger = LoggerClient(VerboseLevels.INFO.value)
config = ConfigClient(env='dev')
mysql_uri = config.get_value("Database", "uri")
mysql_client = MySQLClient(mysql_uri)

class MapUserToRoleResource(Resource):

    def get(self):
        mapped_status = []
        try:
            role_id = request.args.get('role_id')
            user_id = request.args.get('user_id')
            if not role_id or not user_id :
                return {'status' : 200, 'message' : 'User and Role id is required', 'data' : []}

            if role_id and user_id:
                row_obj = dict(role_id=role_id, user_id=user_id)
                insert_mapped_status = mysql_client.insert(table_name='user_to_role',column_values=row_obj)
                if insert_mapped_status:
                    mapped_status = dict(status=200,data=insert_mapped_status)
                else:
                    logger.log_info(f"Error while mapping user with role")
                return mapped_status
        except Exception as e:
            logger.log_error(f"Error while Mapping User To Role, Error : {e}")
            return mapped_status


    def post(self):
        return {'message': 'POST request received'}
