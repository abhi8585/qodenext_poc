from flask import Blueprint
from app.resources.mysql_resource import MySQLResource
from app.resources.csv_resource import CsvResource
from app.resources.item_resource import ItemResource
from app.resources.issue_resource import IssueResource
from app.resources.chatgpt_resource import ChatGptResource
from app.resources.ticket_resource import TicketResource
from app.resources.proccess_order import ProcessOrderResource
from app.resources.order_details import OrderDetailsResource
from app.resources.uuid_resource import UUIDResource
from app.resources.map_uuid_to_order import MapUuidToOrderResource
from app.resources.access_management.user_resource import UserResource
from app.resources.access_management.role_resource import RoleResource
from app.resources.access_management.permission_resource import PermissionResource
from app.resources.access_management.login import LoginResource
from app.resources.access_management.logout import LogoutResource
from app.resources.access_management.map_role_to_permission import MapRoleToPermissionResource
from app.resources.access_management.map_user_to_role import MapUserToRoleResource
from app.resources.access_management.user_to_role import GetUserToRolesList
from app.resources.access_management.user_to_role import GetUsersAndRolesList
from app.resources.map_uuid_to_customer import MapUuidToCustomerResource

from app.resources.get_customer_list import GetCustomersList
from app.resources.map_uuid_to_pickup import MapUuidToPickupResource

from app.resources.uuid_resource import UUIDValidationResource
from app.resources.upload_sales_order import UploadSalesOrderResource

from app.resources.map_uuid_to_warehouse import MapUuidToWareHouseResource
from app.resources.map_uuid_to_product import MapUuidToProductResource
from app.resources.get_keg_code import GetKegCodeResource
from app.resources.get_order_details import GetOrderDetailsWebResource
from app.resources.get_order_header_details import GetOrderHeaderDetailsResource

# Create a blueprint for the route
example_route = Blueprint('example_route', __name__)

# -----BREWERY URL'S START

# adding url for creating new inventory kegs, by default brewery stage

from app.resources.brewery.create_inventory_kegs import CreateInventoryKegsResource
create_inventory_kegs_resource = CreateInventoryKegsResource.as_view('create_inventory_kegs_resource')
example_route.add_url_rule('/cikr', view_func=create_inventory_kegs_resource)

# adding url for receiving keg in brewery from either customer or warehouse

# from app.resources.brewery.brewery_receiving import BreweryReceivingResource
# brewery_receiving_keg_resource = BreweryReceivingResource.as_view('brewery_receiving_keg_resource')
# example_route.add_url_rule('/bwr', view_func=brewery_receiving_keg_resource)

# # adding url for dispatching keg to warehouse

from app.resources.brewery.brewery_dispatch_resource import BreweryDispatchResource
brewery_dispatch_resource = BreweryDispatchResource.as_view('brewery_dispatch_resource')
example_route.add_url_rule('/bdw', view_func=brewery_dispatch_resource)


# -----BREWERY URL'S END




# # ----WAREHOUSE URL'S

from app.resources.warehouse.warehouse_receiving import WareHouseReceivingResource
warehouse_receiving_resource = WareHouseReceivingResource.as_view('warehouse_receiving_resource')
example_route.add_url_rule('/mwuuid', view_func=warehouse_receiving_resource)

from app.resources.warehouse.warehouse_to_brewery import WareHouseToBreweryDispatchResource
warehouse_to_brewery = WareHouseToBreweryDispatchResource.as_view('warehouse_to_brewery')
example_route.add_url_rule('/wtb', view_func=warehouse_to_brewery)

# # ----WAREHOUSE URL'S END

# # ----TESTING EMAIL URL'S

# from app.resources.reports.send_email import SendEmail
# email_resource = SendEmail.as_view('email_resource')
# example_route.add_url_rule('/sm', view_func=email_resource)

# # ----TESTING EMAIL URL'S END



# ----MAPPING KEG TO SERIAL NUMBER URL'S

from app.resources.master.map_serial_to_keg import MapSerialToKeg
map_serial_to_keg_resource = MapSerialToKeg.as_view('map_serial_to_keg_resource')
example_route.add_url_rule('/mstk', view_func=map_serial_to_keg_resource)

# ----MAPPING KEG TO SERIAL NUMBER URL'S END



# --URL for creating/getting SKU
from app.resources.master.get_sku_master import SkuResource
sku_resource = SkuResource.as_view('sku_resource')
# Add route for creating a new user
# example_route.add_url_rule('/user', view_func=user_resource, methods=['POST'])

# Add route for retrieving user(s)
example_route.add_url_rule('/sku', view_func=sku_resource, defaults={'sku_id': None}, methods=['GET'])
example_route.add_url_rule('/sku/<int:sku_id>', view_func=sku_resource, methods=['GET'])





# Add resource(s) to the blueprint

mysql_resource = MySQLResource()
csv_resource = CsvResource()
item_resource = ItemResource()
issue_resource = IssueResource()
chatgpt_resource = ChatGptResource()
ticket_resource = TicketResource()
process_order_resource = ProcessOrderResource
order_details_resource = OrderDetailsResource
uuid_resource = UUIDResource
map_uuid_resource = MapUuidToOrderResource
map_uuid_customer_resource = MapUuidToCustomerResource
user_resource = UserResource.as_view('user_resource')
role_resource = RoleResource.as_view('role_resource')
permission_resource = PermissionResource.as_view('permission_resource')
login_resource = LoginResource.as_view('login_resource')
logout_resource = LogoutResource.as_view('logout_resource')
map_role_to_permission_resource = MapRoleToPermissionResource.as_view('map_role_to_permission')
map_role_to_user_resource = MapUserToRoleResource.as_view('map_user_to_permission')
get_customer_list_resource = GetCustomersList.as_view('get_customers_list')
map_uuid_to_pickup_resouce = MapUuidToPickupResource.as_view('map_uuid_to_pickup_resouce')
uuid_validation_resource = UUIDValidationResource.as_view('uuid_validation_resource')
upload_sales_order_resource = UploadSalesOrderResource.as_view('upload_sales_order_resource')

map_uuid_to_warehouse_resource = MapUuidToWareHouseResource.as_view('map_uuid_to_warehouse_resource') 
user_to_role_resource = GetUserToRolesList.as_view('user_to_role_resource') 

user_and_role_resource = GetUsersAndRolesList.as_view('user_and_role_resource')
map_uuid_to_product_resource = MapUuidToProductResource.as_view('map_uuid_to_product_resource')
get_keg_code_resource = GetKegCodeResource.as_view('get_keg_code_resource')

get_order_details_web_resource = GetOrderDetailsWebResource.as_view('get_order_details_web_resource')
get_order_details_with_resource = GetOrderHeaderDetailsResource.as_view('get_order_details_with_resource')


example_route.add_url_rule('/mysql', view_func=mysql_resource.as_view('mysql'))
# example_route.add_url_rule('/csv', view_func=csv_resource.as_view('csv'))
example_route.add_url_rule('/item', view_func=item_resource.as_view('item'))
example_route.add_url_rule('/issue', view_func=issue_resource.as_view('issue'))
example_route.add_url_rule('/solution', view_func=chatgpt_resource.as_view('solution'))
example_route.add_url_rule('/raise', view_func=ticket_resource.as_view('raise'))
example_route.add_url_rule('/process-order', view_func=process_order_resource.as_view('process-order'))
example_route.add_url_rule('/sodetail', view_func=order_details_resource.as_view('sodetail'))
example_route.add_url_rule('/guuid', view_func=uuid_resource.as_view('guuid'))
example_route.add_url_rule('/muuid', view_func=map_uuid_resource.as_view('muuid'))
example_route.add_url_rule('/usorder', view_func=upload_sales_order_resource)

# example_route.add_url_rule('/muuid', view_func=map_uuid_resource.as_view('muuid'))

# ---User Resource

# Add route for creating a new user
example_route.add_url_rule('/user', view_func=user_resource, methods=['POST'])

# Add route for retrieving user(s)
example_route.add_url_rule('/user', view_func=user_resource, defaults={'user_id': None}, methods=['GET'])
example_route.add_url_rule('/user/<int:user_id>', view_func=user_resource, methods=['GET'])


# ---Role Resource

# Add route for adding a new role
example_route.add_url_rule('/role', view_func=role_resource, methods=['POST'])

# Add route for retrieving role(s)
example_route.add_url_rule('/role', view_func=role_resource, defaults={'role_id': None}, methods=['GET'])
example_route.add_url_rule('/role/<int:role_id>', view_func=role_resource, methods=['GET'])

# ---Permission Resource
# Add route for adding a permission role
example_route.add_url_rule('/permission', view_func=permission_resource, methods=['POST'])

# Add route for retrieving permission(s)
example_route.add_url_rule('/permission', view_func=permission_resource, defaults={'permission_id': None}, methods=['GET'])
example_route.add_url_rule('/permission/<int:permission_id>', view_func=permission_resource, methods=['GET'])

# ---Login Resource
example_route.add_url_rule('/login', view_func=login_resource, methods=['POST'])

# ---Logout Resource
example_route.add_url_rule('/logout', view_func=logout_resource, methods=['POST'])

# Map Role to Permission
example_route.add_url_rule('/mrp', view_func=map_role_to_permission_resource)

# Map User to Role
example_route.add_url_rule('/mur', view_func=map_role_to_user_resource)

# Map uuid to customer
example_route.add_url_rule('/mcuuid', view_func=map_uuid_customer_resource.as_view('mcuuid'))

# Get Customer List
example_route.add_url_rule('/gcust', view_func=get_customer_list_resource)

# Map uuid to Pickup 
example_route.add_url_rule('/mpuuid', view_func=map_uuid_to_pickup_resouce)

# check if the valid uuid is scanned
example_route.add_url_rule('/vuuid', view_func=uuid_validation_resource)

# Map uuid to warehouse
# example_route.add_url_rule('/mwuuid', view_func=map_uuid_to_warehouse_resource)

example_route.add_url_rule('/gutor', view_func=user_to_role_resource)
example_route.add_url_rule('/gunr', view_func=user_and_role_resource)

example_route.add_url_rule('/mutp', view_func=map_uuid_to_product_resource)

example_route.add_url_rule('/guki', view_func=get_keg_code_resource)

example_route.add_url_rule('/godr', view_func=get_order_details_web_resource)

example_route.add_url_rule('/godhdr', view_func=get_order_details_with_resource)







