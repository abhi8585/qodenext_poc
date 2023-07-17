from flask_restful import Resource
from flask import Flask, request
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels

class GetOrderDetailsWebResource(Resource):

    def __init__(self):
        self.config = ConfigClient(env='dev')
        self.logger = LoggerClient(VerboseLevels.INFO.value)
        self.mysql_client = MySQLClient(self.config.get_value("Database", "uri"))
    
    def get_order_id_data(self):
        order_id_data = None
        try:
            odr_data = self.mysql_client.select(table_name='order_header',columns=['order_id', 'order_date'])
            if odr_data and len(odr_data['results']) > 0:
                order_id_data = odr_data['results']
        except Exception as e:
            self.logger.log_error(f"HELPER-Error while getting list of order_id data : {e}")
        return order_id_data


    def get_keg_issue_count(self, order_id, product_key):
        count = None
        try:
            query = f"select count(*) as issue_count from keg_mapping where order_id = {order_id} and product_name = '{product_key}'"
            keg_count = self.mysql_client.execute_query(query=query)
            if keg_count and len(keg_count['results']) > 0:
                count  = keg_count['results'][0]['issue_count']
            else:
                self.logger.log_info(f"HELPER-No data for given order : {order_id} and product : {product_key}")
        except Exception as e:
            self.logger.log_error(f"HELPER-ERROR while getting keg issuse count for order : {order_id} and product : {product_key}")
        return count

    def get_keg_count(self, order_id):
        keg_count = None
        order_details = []
        try:
            query = f"""SELECT sum(bud_30) as bud_30 ,sum(mag_30) as mag_30, sum(hog_15) as hog_15
             FROM order_details where order_id = {order_id}"""
            keg_count = self.mysql_client.execute_query(query=query)
            if keg_count:
                keg_count = keg_count['results'][0]
                integer_dict = {key: int(value) for key, value in keg_count.items()}
            for key, value in integer_dict.items():
                keg_name = ""
                order_obj = dict(keg_name=keg_name,
                                keg_count=value,keg_code=key)
                order_details.append(order_obj)                    
            return order_details
        except Exception as e:
            self.logger.log_error(f"Error while getting kegs count for order_id , {order_id}, Error : {e}")
        return keg_count

    def get(self):
        orders_data = dict(status=500,orders_data=[])
        try:
            order_id_data = self.get_order_id_data()    
            if order_id_data:
                for order in order_id_data:
                    order_id = order['order_id']
                    order_keg_count = self.get_keg_count(order_id)
                    for order_keg in order_keg_count:
                        if order_keg['keg_code'] == "bud_30":
                            order['bud_30_count'] = order_keg['keg_count']
                        if order_keg['keg_code'] == "mag_30":
                            order['mag_30_count'] = order_keg['keg_count']
                        if order_keg['keg_code'] == "hog_15":
                            order['hog_15_count'] = order_keg['keg_count']
                        order['status'] = 'completed'
                orders_data['orders_data']  = order_id_data
                orders_data['orders_data'][-1]['status'] = "pending"
                orders_data['status'] = 200
            else:
                self.logger.log_info(f"MAIN-NO orders data in Database")
        except Exception as e:
            self.logger.log_error(f"MAIN-ERROR while getting uuid keg code {e}")
        return orders_data

        
