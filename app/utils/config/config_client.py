import json

dev_conf = {
    "Database": {
        "uri" : ""
    },
    "ChatGpt" : {
        "api-key" : ""
    }
}

prod_conf = {
    "Database": {
        "uri" : ""
    }
}

class ConfigClient:
    def __init__(self, env):
        if env == 'dev':
            self.config = dev_conf
        else:
            self.config = prod_conf

    def get_value(self, section, key):
        if section in self.config and key in self.config[section]:
            return self.config[section][key]
        else:
            return None
