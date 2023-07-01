# from app import app
import mysql.connector
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels

logger = LoggerClient(verbosity=VerboseLevels.INFO.value)

class MySQLClient:

    def __init__(self, mysql_uri):
        self.mysql_uri = mysql_uri
        db_conn = self.make_connection()
        self.db = db_conn if self.make_connection else None
        self.cursor = self.db.cursor()

        
    def make_connection(self):
        db = None
        try:
            config = {
                'user': self.mysql_uri.split('://')[1].split(':')[0],
                'password': self.mysql_uri.split(':')[2].split('@')[0],
                'host': self.mysql_uri.split('@')[1].split('/')[0],
                'database': self.mysql_uri.split('/')[3]
            }
            # print([config['host'],config['user'],config['password'],config['database']])
            db = mysql.connector.connect(**config)
            if db:
                logger.log_info("Database connection created successfully!")
            else:
                error_message = f"Database connection failed!"
                logger.log_error(error_message)
                raise ConnectionError(error_message)
        except Exception as e:
                error_message = f"Error while creating Database Connection! Error : {e}"
                logger.log_error(error_message)
        return db


    def select(self, table_name, columns=None, filter_condition=None):
        logger.log_info(f"Executing select statement for table : {table_name} and columns {columns}")
        select_status = None
        results = []
        try:
            if self.db is not None:
                if columns is None:
                    query = f"SELECT * FROM {table_name}"
                else:
                    columns_str = ', '.join(columns)
                    query = f"SELECT {columns_str} FROM {table_name}"
                if filter_condition:
                    query += f" {filter_condition}"
                logger.log_info(f"Executing select sql query : {query}")
                self.cursor.execute(query)
                rows = self.cursor.fetchall()
                results = [dict(zip(self.cursor.column_names, row)) for row in rows]
                select_status = dict(status="success",results=results)
                logger.log_info(f"Select Execution Completed!")
            else:
                error_message = f"Please make the connection first"
                logger.log_error(error_message)
        except Exception as e:
            logger.log_error(f"{e}")
            logger.log_error(f"Error while executing select statement")
        return select_status



    def update(self, table, column_values, filter_condition=None):
        logger.log_info(f"Executing update statement for table : {table},columns {column_values},filter_condition : {filter_condition}")
        update_status = None
        try:
            set_clause = ", ".join([f"{column} = %s" for column in column_values.keys()])
            values = list(column_values.values())
            query = f"UPDATE {table} SET {set_clause}"
            if filter_condition:
                query += f" {filter_condition}"
            logger.log_info(f"Executing udpate query {query}")
            self.cursor.execute(query, values)
            self.db.commit()
            affected_rows = self.cursor.rowcount
            update_status = dict(status="success",affected_rows=affected_rows)
            logger.log_info(f"Update Execution Completed!")
        except Exception as e:
            error_message = f"Error : {e} while udpating {table} for {column_values} with filter condition {filter_condition}"
            logger.log_error(error_message)
        return update_status


    def insert(self, table_name, column_values, filter_condition=None):
        logger.log_info(f"Executing insert statement for table : {table_name},column_values {column_values},filter_condition : {filter_condition}")
        insert_status = None
        try:
            columns = ", ".join(column_values.keys())
            placeholders = ", ".join(["%s"] * len(column_values))
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            data = tuple(column_values.values())
            logger.log_info(f"Executing insert sql query : {query}")
            self.cursor.execute(query, data)
            self.db.commit()
            last_row_id = self.cursor.lastrowid
            logger.log_info(f"Insert Execution Completed!")
            insert_status = dict(status="success",affected_rows = self.cursor.rowcount,last_row_id=last_row_id)
        except Exception as e:
            error_message = f"Error : {e} while inserting in {table_name}, filter_condition : {filter_condition},columns_values : {column_values}"
            logger.log_error(error_message)
        return insert_status

    def delete(self, table, filter_condition=None):
        logger.log_info(f"Executing delete statement for table : {table},filter_condition : {filter_condition}")
        delete_status = None
        try:
            query = f"DELETE FROM {table}"
            if filter_condition:
                query += f" {filter_condition}"
            logger.log_info(f"Executing delete sql query : {query}")
            self.cursor.execute(query)
            self.db.commit()
            affected_rows = self.cursor.rowcount
            delete_status = dict(status="success",affected_rows=affected_rows)
            logger.log_info(f"Delete Execution Completed!")
            return delete_status
        except Exception as e:
            error_message = f"Error : {e} while deleting {table} with filter_conditon {filter_condition}"
            logger.log_error(error_message)
        return delete_status

    def inner_join(self):
        query = f"""
                    SELECT c.customer_name
                    FROM product p
                    JOIN customer c ON p.customer_id = c.customer_id
                    WHERE p.model = 'RS35'
                    limit 1;
                """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        results = [dict(zip(self.cursor.column_names, row)) for row in rows]
        select_status = dict(status="success",results=results)
        return select_status

    def execute_query(self, query):
        query_results = None
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            results = [dict(zip(self.cursor.column_names, row)) for row in rows]
            query_results = dict(status="success",results=results)
        except Exception as e:
            logger.log_error(f"Error while executing direct query, Error : {e}")
        return query_results






    


