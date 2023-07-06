from flask_restful import Resource, request
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.csv.csv_client import CsvClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels
from app.utils.uuid.uuid_client import UUIDClient


class GetCustomersList(Resource):

    def get(self):
        customers_data = dict(status=500,customer_data=None)
        logger = LoggerClient(VerboseLevels.INFO.value)
        config = ConfigClient(env='dev')
        mysql_uri = config.get_value("Database", "uri")
        mysql_client = MySQLClient(mysql_uri)
        try:
            query = f"select distinct outlets_name from order_details"
            customers_data = mysql_client.execute_query(query)
            if customers_data:
                if customers_data["status"] == "success":
                    customers_data["status"] = 200
                    customers_data['customer_data'] = customers_data["results"]
                else:
                    logger.log_error(f"select customers list failed")
            else:
                logger.log_error(f"No customer data found")
        except Exception as e:
            logger.log_error(f"Internal Error while selecting customers list, Error : {e}")
        return customers_data


    def post(self):
        return {'message': 'POST request received'}
