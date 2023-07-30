# import logging

# class LoggerClient:
#     _instance = None

#     def __new__(cls, verbosity):
#         if cls._instance is None:
#             cls._instance = super().__new__(cls)
#             cls._instance.logger = logging.getLogger(__name__)
#             cls._instance.logger.setLevel(verbosity)
#             console_handler = logging.StreamHandler()
#             console_handler.setLevel(verbosity)
#             formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
#             console_handler.setFormatter(formatter)
#             cls._instance.logger.addHandler(console_handler)
#         return cls._instance

#     def log_info(self, message):
#         self.logger.info(message)

#     def log_error(self, message):
#         self.logger.error(message)

#     def log_warning(self, message):
#         self.logger.warning(message)



import logging
import os
import datetime

class LoggerClient:
    _instance = None

    def __new__(cls, verbosity):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logger = logging.getLogger(__name__)
            cls._instance.logger.setLevel(verbosity)

            # Create the "logs" folder if it doesn't exist
            logs_folder = os.path.join(os.path.dirname(__file__), "logs")
            if not os.path.exists(logs_folder):
                os.mkdir(logs_folder)

            # Set up the file handler to write logs to the date-specific text file
            current_date = datetime.date.today().strftime("%Y-%m-%d")
            log_file_path = os.path.join(logs_folder, f"{current_date}.txt")
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setLevel(verbosity)

            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            cls._instance.logger.addHandler(file_handler)

            # Set up the console handler for displaying logs on the console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(verbosity)
            console_handler.setFormatter(formatter)
            cls._instance.logger.addHandler(console_handler)

        return cls._instance

    def log_info(self, message):
        self.logger.info(message)

    def log_error(self, message):
        self.logger.error(message)

    def log_warning(self, message):
        self.logger.warning(message)
