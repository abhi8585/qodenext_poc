from enum import Enum
class StaticValues(Enum):
    ENV_DEV = "dev"
    SMTP_SERVER = "smtppro.zoho.in"
    EMAIL_PORT = 465
    CUSTOMER = 'customer'
    WAREHOUSE = 'warehouse'
    BREWERY = 'brewery'
    DISPATCHED = 'dispatched'
    DELIVERED = 'delivered'
    RECEIVED = 'received'
    CUSTOMER_DISPATCH_FROM_WAREHOUSE = 'cdispatch'
    BREWERY_DISPATCH_FROM_WAREHOUSE = 'bdispatch'
    WAREHOUSE_TO_CUSTOMER = 'wtc'
    WAREHOUSE_TO_BREWERY = 'wtb'
    PICKED = 'picked'
    

