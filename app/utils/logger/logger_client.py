import logging

class LoggerClient:
    def __init__(self, verbosity):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(verbosity)

        # Create a console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(verbosity)

        # Create a formatter and add it to the console handler
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)

        # Add the console handler to the logger
        self.logger.addHandler(console_handler)

    def log_info(self, message):
        self.logger.info(message)

    def log_error(self, message):
        self.logger.error(message)

    def log_warning(self, message):
        self.logger.warning(message)

