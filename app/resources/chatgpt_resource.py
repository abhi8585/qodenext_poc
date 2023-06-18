from flask_restful import Resource, request
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.csv.csv_client import CsvClient
from app.utils.chatgpt.chatgpt_client import ChatGptClient
import json


class ChatGptResource(Resource):

    def get_solution_instructions(self, model_number, company_name,issue):
        text = f"""
        I have ‘{model_number}’ device of ‘{company_name}’ \ 
        I am facing issue about ‘{issue}’ \ 
        Provide me the possible list of solutions for above issue \
        Provide the output in the json format. 
        """
        return text

    def get(self):
        try:
            model_number = request.args.get('model_number')
            issue = request.args.get('issue')
            config = ConfigClient(env='dev')
            mysql_uri = config.get_value("Database", "uri")
            mysql_client = MySQLClient(mysql_uri)
            company_name = mysql_client.inner_join()['results'][0]['customer_name']
            text = self.get_solution_instructions(model_number,company_name,issue)
            prompt = f"""
            Your task is to perform the instructions given in the text delimited by triple backticks\ 
            ```{text}```
            """
            response = ChatGptClient.get_completion(prompt)
            response = json.loads(response)
            response['model_number'] = model_number
            return {'status':200,'data': response}
        except Exception as e:
            print(f"{e}")
            return {'status':500,'data': []}

    def post(self):
        return {'message': 'POST request received'}
