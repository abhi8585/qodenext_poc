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
        customers_data = dict(status=500,customer_data=[])
        try:
            query = f"select distinct outlets_name from order_details"
            db_customers_data = self.mysql_client.execute_query(query)
            if db_customers_data and len(db_customers_data["results"]) > 0:
                customers_data["status"] = 200
                customers_data['customer_data'] = db_customers_data["results"]
                c_d = customers_data["customer_data"]
                import random
                for i in range(1, len(c_d)):
                    c_d[i]['customer_id'] = i+1
                    c_d[i]['delivered_kegs'] = random.randint(20,50)
                    c_d[i]['due_kegs'] = random.randint(4,12)
                    c_d[i]['StatusBg'] = 'red'
                customers_data["customer_data"][0]['customer_id'] = 1
                customers_data["customer_data"][0]['delivered_kegs'] = random.randint(20,50)
                customers_data["customer_data"][0]['due_kegs'] = random.randint(4,12)
                customers_data["customer_data"][0]['StatusBg'] = 'red'
                self.logger.log_info(f"Retreived customers list successfully!")
            else:
                self.logger.log_error(f"No customer data found")
                customers_data['message'] = f"No customer data found"
        except Exception as e:
            self.logger.log_error(f"Internal Error while selecting customers list, Error : {e}")
            customers_data['message'] = f"Internal Error while selecting customers"
        return customers_data