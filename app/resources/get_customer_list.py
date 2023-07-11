from flask_restful import Resource, request
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels


class GetCustomersList(Resource):

    def __init__(self):
        self.config = ConfigClient(env='dev')
        self.logger = LoggerClient(VerboseLevels.INFO.value)
        self.mysql_client = MySQLClient(self.config.get_value("Database", "uri"))

    def get(self):
        customers_data = dict(status=500,customer_data=None)
        try:
            query = f"select distinct outlets_name from order_details"
            customers_data = self.mysql_client.execute_query(query)
            if customers_data:
                if customers_data["status"] == "success":
                    customers_data["status"] = 200
                    customers_data['customer_data'] = customers_data["results"]
                    self.logger.log_info(f"Retreived customers list successfully!")
                else:
                    self.logger.log_error(f"select customers list failed")
            else:
                self.logger.log_error(f"No customer data found")
        except Exception as e:
            self.logger.log_error(f"Internal Error while selecting customers list, Error : {e}")
        return customers_data