#import sqlite3
from flask_restful import Resource, reqparse
from models.user import UserModel

class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
      type=str,
      required=True,
      help="Username cannot be left blank!"
    )
    parser.add_argument('password',
      type=str,
      required=True,
      help="Password cannot be left blank!"
    )
    def post(self):
        data = UserRegister.parser.parse_args()
        if UserModel.find_by_username(data['username']):
            return {"message": "User {} already exists.".format(data['username'])}, 400

        #user = UserModel(data['username'], data['password'])
        user = UserModel(**data)
        user.save_to_db()
        '''
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "INSERT INTO users VALUES (NULL, ?, ?)"
        cursor.execute(query, (data['username'], data['password']))

        connection.commit()
        connection.close()
        '''
        return {"message": "User {} create successfully.".format(data['username'])}, 201
