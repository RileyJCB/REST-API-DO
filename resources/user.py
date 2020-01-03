from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
  create_access_token, 
  create_refresh_token, 
  jwt_required, 
  get_jwt_claims, 
  jwt_refresh_token_required,
  get_jwt_identity,
  jwt_required,
  get_raw_jwt
)

from models.user import UserModel
from blacklist import BLACKLIST

_user_parser = reqparse.RequestParser()
_user_parser.add_argument(
  'username',
  type=str,
  required=True,
  help="Username cannot be left blank!"
)
_user_parser.add_argument(
  'password',
  type=str,
  required=True,
  help="Password cannot be left blank!"
)

class UserRegister(Resource):
  def post(self):
    data = _user_parser.parse_args()
    if UserModel.find_by_username(data['username']):
        return {"message": "User {} already exists.".format(data['username'])}, 400

    #user = UserModel(data['username'], data['password'])
    user = UserModel(**data)
    user.save_to_db()

    return {"message": "User {} create successfully.".format(data['username'])}, 201

class User(Resource):
  @classmethod
  def get(cls, user_id):
    user = UserModel.find_by_id(user_id)
    if not user:
      return {'message': 'User not found'}, 404
    return user.json()

  @classmethod
  def delete(cls, user_id):
    user = UserModel.find_by_id(user_id)
    if not user:
      return {'message': 'User not found'}, 404

    user.delete_from_db()
    return {'message': 'User {} deleted.'.format(user.username)}


class UserLogin(Resource):
  @classmethod
  def post(cls):
    # get data from parser
    data = _user_parser.parse_args()

    # find user in database
    user = UserModel.find_by_username(data['username'])

    # check password
    if user and safe_str_cmp(user.password, data['password']):
      # create access token
      access_token = create_access_token(identity=user.id, fresh=True)
      # create refresh token
      refresh_token = create_refresh_token(user.id)
  
      # return them
      return {
        'access_token': access_token,
        'refresh_token': refresh_token
      }, 200

    return {'message': 'Invalid Username or Password.'}, 401


class UserLogout(Resource):
  @jwt_required
  def post(self):
    jti = get_raw_jwt()['jti'] # jit is "JWT ID", a unique identifier for that JWT
    user = UserModel.find_by_id(get_jwt_identity()).json()['username']
    BLACKLIST.add(jti)
    return {'message': '{} has successfully logged out.'.format(user)}


class UserList(Resource):
  @jwt_required
  def get(self):
    claims = get_jwt_claims()
    if not claims['is_admin']:
      return {'message': 'Admin privilege is required.'}, 401

    return {'users': [user.json() for user in UserModel.find_all()]}


class TokenRefresh(Resource):
  @jwt_refresh_token_required
  def post(self):
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user, fresh=False)
    return {'access_token': new_token}, 200