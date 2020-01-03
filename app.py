##################################
# Heroku postgress specific code to get from environment
import os
##################################

from datetime import timedelta

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
import uuid

from resources.user import UserRegister, User, UserLogin, UserList, UserLogout, TokenRefresh
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from resources.carter import Carter

from blacklist import BLACKLIST

# Resource(s) are just things, items, they are often mapped into database tables

app = Flask(__name__)

##################################
# Heroku postgress specific code, uses the Environment Variable else use sqlite
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
##################################

# Turn of Flasks Database Tracker but SQLALCHEMY is still on
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Pass the actual error code to pass through flask and be communicated 
app.config['PROPAGATE_EXCEPTIONS'] = True

# Setup a BLACKLIST using JWT
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

# config JWT to expire within 3 hours
#app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=10800)

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

# This will set the auth enpoint to /login  to verify user
#app.config['JWT_AUTH_URL_RULE'] = '/login'
jwt = JWTManager(app) # This is not creating the /auth endpoint

@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1: # Instead of hard-coding, you should read from a config file or a database
        return {'is_admin': True}
    return {'is_admin': False}

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
#    return decrypted_token['identity'] in BLACKLIST # Now using JTI vs user identity
    return decrypted_token['jti'] in BLACKLIST


@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        'description': 'The token has expired.',
        'error': 'token_expired'
    }), 401


# Called when bad token string sent
@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'description': 'Signature verification failed.',
        'error': 'invalid_token'
    }), 401

# Call when a JWT is not sent at all
@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'description': 'Request does not contain an access token.',
        'error': 'authorization_required'
    }), 401

# This handles the case when we require a fresh token but then did not sent one
@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return jsonify({
        'description': 'The token is not fresh.',
        'error': 'fresh_token_required'
    }), 401

# Sets the token as invalid, this would handle a logout
@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        'description': 'The token has been revoked.',
        'error': 'token_revoked'
    }), 401

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
api.add_resource(Carter, '/games')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserList, '/users')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(TokenRefresh, '/refresh')

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=8050, debug=True)
