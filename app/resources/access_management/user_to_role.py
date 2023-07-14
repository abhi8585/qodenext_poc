from flask_restful import Resource, request
from app.utils.mysql.mysql_client import MySQLClient
from app.utils.config.config_client import ConfigClient
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels


class GetUserToRolesList(Resource):

    def __init__(self):
        self.config = ConfigClient(env='dev')
        self.logger = LoggerClient(VerboseLevels.INFO.value)
        self.mysql_client = MySQLClient(self.config.get_value("Database", "uri"))

    def get_user_to_role(self):
        user_to_role_data = None
        try:
            query = f"""
                        SELECT u.user_id, u.user_name,u.user_email, r.role_name
                        FROM user u
                        JOIN user_to_role ur ON u.user_id = ur.user_id
                        JOIN role r ON ur.role_id = r.role_id;
                    """
            u_t_r_d = self.mysql_client.execute_query(query)
            if u_t_r_d and len(u_t_r_d['results']) > 0:
                user_to_role_data = u_t_r_d['results']
            else:
                self.logger(f"No User To Role Data")
        except Exception as e:
            self.logger.log_error(f"HELPER-ERROR while getting user to role data")
        return user_to_role_data

    def get(self):
        u_t_r = dict(status=500,data=[])
        try:
            user_to_role_data = self.get_user_to_role()
            if user_to_role_data:
                u_t_r['data'] = user_to_role_data
                u_t_r["status"] = 200  
                return u_t_r, 200  
            else:
                self.logger.log_error(f"MAIN-Error while selecting users and roles")
        except Exception as e:
            self.logger.log_error(f"Internal Error while selecting customers list, Error : {e}")
            u_t_r['message'] = f"Internal Error while getting user to role mapping"
            return u_t_r, 500



class GetUsersAndRolesList(Resource):

    def __init__(self):
        self.config = ConfigClient(env='dev')
        self.logger = LoggerClient(VerboseLevels.INFO.value)
        self.mysql_client = MySQLClient(self.config.get_value("Database", "uri"))

    
    def get_users_data(self):
        users_data = None
        try:
            db_users_data = self.mysql_client.select(table_name='user',columns=['user_id','user_name'])
            if db_users_data and len(db_users_data['results']):
                users_data = db_users_data['results']
            else:
                self.logger.log_error(f"HELPER-No data for USERS list ")
        except Exception as e:
            self.logger.log_error(f"HELPER-ERROR while getting user data : {e}")
        return users_data

    def get_roles_data(self):
        roles_data = None
        try:
            db_roles_data = self.mysql_client.select(table_name='role',columns=['role_id','role_name'])
            if db_roles_data and len(db_roles_data['results']):
                roles_data = db_roles_data['results']
            else:
                self.logger.log_error(f"HELPER-No data for ROLES list ")
        except Exception as e:
            self.logger.log_error(f"HELPER-ERROR while getting user data : {e}")
        return roles_data

    def get(self):
        u_t_r = dict(roles_data=[],user_data=[])
        try:
            user_data = self.get_users_data()
            if user_data:
                u_t_r['user_data'] = user_data
            else:
                self.logger.log_info(f"No user data in database")
            role_data = self.get_roles_data()
            if role_data:
                u_t_r['roles_data'] = role_data
            else:
                self.logger.log_info(f"No role data in database")  
            return u_t_r, 200  
        except Exception as e:
            self.logger.log_error(f"MAIN-Internal Error while getting users and roles list, Error : {e}")
            u_t_r['message'] = f"Internal Error while getting users and roles data"
            return u_t_r, 500
