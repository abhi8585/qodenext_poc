from flask import Blueprint
from app.resources.mysql_resource import MySQLResource
from app.resources.csv_resource import CsvResource
from app.resources.item_resource import ItemResource
from app.resources.issue_resource import IssueResource
from app.resources.chatgpt_resource import ChatGptResource
from app.resources.ticket_resource import TicketResource


# Create a blueprint for the route
example_route = Blueprint('example_route', __name__)

# Add resource(s) to the blueprint

mysql_resource = MySQLResource()
csv_resource = CsvResource()
item_resource = ItemResource()
issue_resource = IssueResource()
chatgpt_resource = ChatGptResource()
ticket_resource = TicketResource()



# example_route.add_url_rule('/mysql', view_func=mysql_resource.as_view('mysql'))
# example_route.add_url_rule('/csv', view_func=csv_resource.as_view('csv'))
example_route.add_url_rule('/item', view_func=item_resource.as_view('item'))
example_route.add_url_rule('/issue', view_func=issue_resource.as_view('issue'))
example_route.add_url_rule('/solution', view_func=chatgpt_resource.as_view('solution'))
example_route.add_url_rule('/raise', view_func=ticket_resource.as_view('raise'))

