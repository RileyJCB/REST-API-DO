from datetime import timedelta

from flask import Flask
from flask_restful import Api
from flask_jwt import JWT
import uuid

from security import authenticate, identity
from resources.user import UserRegister
from resources.item import Item, ItemList
from resources.store import Store, StoreList

# Resource(s) are just things, items, they are often mapped into database tables

app = Flask(__name__)

# Tell SQLAlchemy where to find the Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'

# Turn of Flasks Database Tracker but SQLALCHEMY is still on
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# config JWT to expire within 3 hours
app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=10800)

'''
# config JWT auth key name to be 'email' instead of default 'username'
app.config['JWT_AUTH_USERNAME_KEY'] = 'email'
'''

# Set a unique key
app.secret_key = uuid.uuid4().hex

'''
# This will create a new endpoint /auth  to verify user
jwt = JWT(app, authenticate, identity)
'''

# Use decorator to perform action before first request into app
@app.before_first_request
def create_tables():
    db.create_all() # Only creates the tables it sees from the imports

# This will set the auth enpoint to /login  to verify user
app.config['JWT_AUTH_URL_RULE'] = '/login'
jwt = JWT(app, authenticate, identity)

# Makes it easy to control interface to Resource
api = Api(app)

# Status Codes
# 200 - OK (server response, most used)
# 201 - Created
# 202 - Accepted (but delaying the creation)
# 204 - No Content
# 400 - Bad Request
# 403 - Forbidden
# 404 - Not Found
# 500 - Internal Server Error

api.add_resource(Store, '/store/<string:name>') #http://127.0.0.1:8050/store/<name>
api.add_resource(Item, '/item/<string:name>') #http://127.0.0.1:8050/item/<name>
api.add_resource(ItemList, '/items')
api.add_resource(StoreList, '/stores')
api.add_resource(UserRegister, '/register')

if __name__ == '__main__':
    from db import db    
    db.init_app(app)
    app.run(port=8050, debug=True)
