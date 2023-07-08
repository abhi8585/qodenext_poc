from enum import Enum
class VerboseLevels(Enum):
    ERROR = 3
    WARNING = 2
    INFO = 1
    DEBUG = 4
    DEV = 'dev'
    PROD = 'prod'