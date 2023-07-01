import uuid
from app.utils.logger.logger_client import LoggerClient
from app.utils.logger.logger_verbose import VerboseLevels

logger = LoggerClient(VerboseLevels.INFO.value)

class UUIDClient:

    def __init__(self):
        logger.log_info(f"UUID client created successfully!")

    def create_uuid(self, total_uuid):
        uuid_list = None
        try:
            logger.log_info(f"UUID range : {total_uuid}")
            uuid_list = [str(uuid.uuid4()) for _ in range(total_uuid)]
            logger.log_info(f"Generate total {total_uuid} new UUID")
            return uuid_list
        except ValueError as e:
            print(f"Error occurred while creating UUIDs: {e}")
        return uuid_list
