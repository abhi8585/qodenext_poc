from flask import Flask
from flask_restful import Api
from app.routes.example_route import example_route
from flask_cors import CORS
# Create an instance of the BigQuery client
import mysql.connector



app = Flask(__name__)
api = Api(app)
CORS(app)
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'root'
# app.config['MYSQL_DB'] = 'srctrac'


# # Create a MySQL connection
# db = mysql.connector.connect(
#     host=app.config['MYSQL_HOST'],
#     user=app.config['MYSQL_USER'],
#     password=app.config['MYSQL_PASSWORD'],
#     database=app.config['MYSQL_DB']
# )


# Register blueprints
app.register_blueprint(example_route, url_prefix='/api')

if __name__ == '__main__':
    app.run()
