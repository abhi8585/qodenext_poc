from flask_restful import Resource, request
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels


class OrderDetailsResource(Resource):


    def __init__(self):
        self.logger = LoggerClient(VerboseLevels.INFO.value)
        self.config = ConfigClient(env=VerboseLevels.DEV.value)
        self.mysql_client = MySQLClient(self.config.get_value("Database", "uri"))


    def get_keg_name(self, key):
        if key == "bud_30":
            return dict(keg_name = "Budweiser Premium Beer", keg_quantity = 30)
        if key == "mag_30":
            return dict(keg_name = "Bud Magnum Beer", keg_quantity = 30)
        if key == "hog_15":
            return dict(keg_name = "Hoegaarden Witbier", keg_quantity = 15)
    

    def delete_key(self,dictionary, key):
        if key in dictionary:
            del dictionary[key]
        return dictionary


    def get_customer_keg_mapping(self, order_detail_id, keg_code):
        issue_count = 0
        try:
            query = f"select count(*) as issue_count from keg_customer_mapping where order_detail_id = {order_detail_id} and keg_product_code = '{keg_code}' and status = 'delievered'"
            keg_count = self.mysql_client.execute_query(query=query)
            if keg_count and len(keg_count['results']) > 0:
                issue_count  = keg_count['results'][0]['issue_count']
            else:
                self.logger.log_info(f"HELPER-No data for given order_detail_id : {order_detail_id}")
        except Exception as e:
            self.logger.log_error(f"HELPER-Error while getting customer keg issue count for {order_detail_id} : {e}")
        return issue_count
        

    def get_order_details(self, order_id):
        try:
            if order_id:
                columns = ['area','bud_30','draught_code','hog_15','license_billing_name','mag_30','order_detail_id','order_id','outlets_name']
                order_details_data = self.mysql_client.select(table_name='order_details',columns=columns,filter_condition=f"where order_id = {order_id}")
                if order_details_data:
                    order_detail_results = order_details_data['results']
                    for order_detail in order_detail_results:
                        order_detail["keg_data"] = []
                        for key, value in order_detail.items():
                            if key == "bud_30":
                                keg_obj = self.get_keg_name(key)
                                keg_obj['keg_count'] = value
                                keg_obj["keg_code"] = "bud_30"
                                keg_issue_count = self.get_customer_keg_mapping(order_detail['order_detail_id'], keg_obj["keg_code"])
                                keg_obj["keg_issue_count"] = keg_issue_count
                                keg_obj["keg_balance_count"] = value - keg_issue_count
                                order_detail["keg_data"].append(keg_obj)
                            if key == "mag_30":
                                keg_obj = self.get_keg_name(key)
                                keg_obj['keg_count'] = value
                                keg_obj["keg_code"] = "mag_30"
                                keg_issue_count = self.get_customer_keg_mapping(order_detail['order_detail_id'], keg_obj["keg_code"])
                                keg_obj["keg_issue_count"] = keg_issue_count
                                keg_obj["keg_balance_count"] = value - keg_issue_count                                
                                order_detail["keg_data"].append(keg_obj)
                            if key == "hog_15":
                                keg_obj = self.get_keg_name(key)
                                keg_obj['keg_count'] = value
                                keg_obj["keg_code"] = "hog_15"
                                keg_issue_count = self.get_customer_keg_mapping(order_detail['order_detail_id'], keg_obj["keg_code"])
                                keg_obj["keg_issue_count"] = keg_issue_count
                                keg_obj["keg_balance_count"] = value - keg_issue_count                                
                                order_detail["keg_data"].append(keg_obj)
                    return order_details_data
        except Exception as e:
            self.logger.log_error(f"Error while getting order details, Error : {e}")

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
                keg_name, keg_quantity = "", ""
                if key == "bud_30":
                    keg_name = "Budweiser Premium Beer"
                    keg_quantity = 30
                    # keg_issue_count = self.get_keg_issue_count(order_id,key)
                if key == "mag_30":
                    keg_name = "Bud Magnum Beer"
                    keg_quantity = 30
                    # keg_issue_count = self.get_keg_issue_count(order_id,key)
                if key == "hog_15":
                    keg_name = "Hoegaarden Witbier"
                    keg_quantity = 15
                    # keg_issue_count = self.get_keg_issue_count(order_id,key)
                keg_issue_count = self.get_keg_issue_count(order_id, key)
                keg_balance_count = value - keg_issue_count
                order_obj = dict(keg_name=keg_name,keg_quantity=keg_quantity,
                                keg_count=value,keg_code=key,keg_issue_count=keg_issue_count,
                                keg_balance_count=keg_balance_count)
                order_details.append(order_obj)                    
            return order_details
        except Exception as e:
            self.logger.log_error(f"Error while getting kegs count for order_id , {order_id}, Error : {e}")
        return keg_count
        
    def get(self):
        order_data = dict()
        order_date = request.args.get('order_date')
        if order_date:
            try:
                order_header_data = self.mysql_client.select(table_name='order_header',filter_condition=f"where order_date = '{order_date}'  order by created_date desc limit 1;")
                if order_header_data:
                    if len(order_header_data['results']) > 0:
                        order_id = order_header_data['results'][0]['order_id']
                        order_details = self.get_order_details(order_id=order_id)
                        if order_details:
                            keg_count = self.get_keg_count(order_id=order_id)
                            order_data['order_id'] = order_id
                            order_data['order_details'] = order_details
                            order_data['order_keg_details'] = keg_count
                            return {'status':200,'data': order_data}
                        else:
                            self.logger.log_info(f"Error while getting order details with order_id {order_id}")
                            return {'status':200,'data': []}
                    else:
                        self.logger.log_info(f"No data for given order date")
                        return {'status':200,'data': []}
                else:
                    self.logger.log_info(f"Error while getting orded  details")
                    return {'status':200,'data': []}
            except Exception as e:
                self.logger.log_info(f"Error while getting order data for date, {order_date}, Error :  {e}")
                return {'status':500,'data': []}, 500
        else:
            return {'status' : 400, 'message' : 'No order date provided'}, 400

    def post(self):
        return {'message': 'POST request received'}
