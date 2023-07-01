from flask_restful import Resource, request
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels


logger = LoggerClient(VerboseLevels.INFO.value)
config = ConfigClient(env='dev')
mysql_uri = config.get_value("Database", "uri")
mysql_client = MySQLClient(mysql_uri)


class OrderDetailsResource(Resource):

    def get_order_details(self, order_id):
        try:
            if order_id:
                columns = ['area','bud_30','draught_code','hog_15','license_billing_name','mag_30','order_detail_id','order_id','outlets_name']
                order_details_data = mysql_client.select(table_name='order_details',columns=columns,filter_condition=f"where order_id = {order_id}")
                if order_details_data:
                    return order_details_data['results']
        except Exception as e:
            logger.log_error(f"Error while getting order details, Error : {e}")


    def get_keg_count(self, order_id):
        keg_count = None
        order_details = []
        try:
            query = f"""SELECT sum(bud_30) as bud_30 ,sum(mag_30) as mag_30, sum(hog_15) as hog_15
             FROM order_details where order_id = {order_id}"""
            keg_count = mysql_client.execute_query(query=query)
            print(f"count")
            print(keg_count)
            if keg_count:
                keg_count = keg_count['results'][0]
                integer_dict = {key: int(value) for key, value in keg_count.items()}
            for key, value in integer_dict.items():
                keg_name, keg_quantity = "", ""
                if key == "bud_30":
                    keg_name = "Budweiser Premium Beer"
                    keg_quantity = 30
                if key == "mag_30":
                    keg_name = "Bud Magnum Beer"
                    keg_quantity = 30
                if key == "hog_15":
                    keg_name = "Hoegaarden Witbier"
                    keg_quantity = 15
                order_obj = dict(keg_name=keg_name,keg_quantity=keg_quantity,keg_count=value,keg_code=key)
                order_details.append(order_obj)                    
            return order_details
        except Exception as e:
            logger.log_error(f"Error while getting kegs count for order_id , {order_id}, Error : {e}")
        return keg_count
        
    def get(self):
        order_data = dict()
        order_date = request.args.get('order_date')
        if order_date:
            try:
                order_header_data = mysql_client.select(table_name='order_header',filter_condition=f"where order_date = '{order_date}' limit 1;")
                print(order_header_data)
                if order_header_data:
                    if len(order_header_data['results']) > 0:
                        print('got order header data')
                        order_id = order_header_data['results'][0]['order_id']
                        order_id = 7
                        order_details = self.get_order_details(order_id=order_id)
                        if order_details:
                            keg_count = self.get_keg_count(order_id=order_id)
                            order_data['order_id'] = order_id
                            order_data['order_details'] = order_details
                            order_data['order_keg_details'] = keg_count
                            return {'status':200,'data': order_data}
                        else:
                            logger.log_info(f"Error while getting order details with order_id {order_id}")
                            return {'status':200,'data': []}
                    else:
                        logger.log_info(f"Error while getting orded header details")
                        return {'status':200,'data': []}
                else:
                    logger.log_info(f"Getting data from order header failed")
                    return {'status':200,'data': []}
            except Exception as e:
                logger.log_info(f"Error while getting order data for date, {order_date}, Error :  {e}")
                return {'status':500,'data': []}
        else:
            return {'status' : 500, 'message' : 'No order date provided'}

    def post(self):
        return {'message': 'POST request received'}
