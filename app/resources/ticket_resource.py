from flask_restful import Resource, request
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.csv.csv_client import CsvClient
from app.utils.chatgpt.chatgpt_client import ChatGptClient
import json
import uuid


class TicketResource(Resource):

    def get_ticket_number(self):
        return str(uuid.uuid4())
        
    def get(self):
        try:
            model_number = request.args.get('model_number')
            # issue = request.args.get('issue')
            config = ConfigClient(env='dev')
            mysql_uri = config.get_value("Database", "uri")
            mysql_client = MySQLClient(mysql_uri)
            ticket_number = self.get_ticket_number()
            ticket_obj = dict(ticket_number=ticket_number,model=model_number)
            insert_status = mysql_client.insert(table_name='ticket',column_values=ticket_obj)
            return {'status':200,'data': insert_status,'ticket_number':ticket_number}
        except Exception as e:
            print(f"{e}")
            return {'status':500,'data': []}

    def post(self):
        return {'message': 'POST request received'}
