from flask_restful import Resource, request
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels
import random


class GetCustomersList(Resource):

    def __init__(self):
        self.config = ConfigClient(env='dev')
        self.logger = LoggerClient(VerboseLevels.INFO.value)
        self.mysql_client = MySQLClient(self.config.get_value("Database", "uri"))


    def get_customer_data(self):
        customer_data = None
        try:
            query = f"""
                    with order_data as (
                            SELECT k.order_detail_id,k.created_date as delivered_date, o.outlets_name as outlet_name,
                            IF(DATEDIFF(CURDATE(), k.created_date) > 10 * 30, TRUE, FALSE) AS is_due
                            FROM keg_customer_mapping k
                            join order_details o
                            on k.order_detail_id = o.order_detail_id
                            WHERE k.created_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
                            and k.uuid_id < 432 and k.uuid_id > 228
                            group by k.created_date
                        )

                    select outlet_name as outlets_name ,count(*) as delivered_kegs, CONVERT(sum(is_due), CHAR) as due_kegs from order_data
                    group by outlet_name;
                    """
            db_customers_data = self.mysql_client.execute_query(query)
            if db_customers_data and len(db_customers_data['results']) > 0:
                customer_data = db_customers_data['results']
        except Exception as e:
            self.logger.log_error(f"Error while getting customer delivered kegs data, {e}")
        return customer_data


    def get(self):
        customers_data = dict(status=500,customer_data=[])
        try:
            db_customers_data = self.get_customer_data()
            if db_customers_data and len(db_customers_data) > 0:
                for i in db_customers_data:
                    # i['customer_id'] = random.randint(4,12)
                    i['StatusBg'] = 'red'
                customers_data["customer_data"] = db_customers_data
            else:
                self.logger.log_error(f"No customer data found")
                customers_data['message'] = f"No customer data found"
        except Exception as e:
            self.logger.log_error(f"Internal Error while selecting customers list, Error : {e}")
            customers_data['message'] = f"Internal Error while selecting customers"
        return customers_data