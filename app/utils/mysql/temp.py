import mysql.connector
from urllib.parse import urlparse

def make_connection(mysql_uri):
    # parsed_uri = urlparse(mysql_uri)
    # print(parsed_uri)
    config = {
                'user': mysql_uri.split('://')[1].split(':')[0],
                'password': mysql_uri.split(':')[2].split('@')[0],
                'host': mysql_uri.split('@')[1].split('/')[0],
                'database': mysql_uri.split('/')[3]
            }
    # print(config)
    db = mysql.connector.connect(**config)

    # # try:
    # #     connection = mysql.connector.connect(
    # #         host=config['host'],
    # #         port=3306,
    # #         user=config['user'],
    # #         password=config['password'],
    # #         database=config['database']
    # #     )
    # #     print("Connection successful!")
    #     # return connection
    # except mysql.connector.Error as error:
    #     print(f"Error connecting to MySQL: {error}")
    #     return None

mysql_uri = "mysql://admin:admin123@poc.cxfgxsipak91.ap-south-1.rds.amazonaws.com/poc"

connection = make_connection(mysql_uri)