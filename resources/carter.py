from flask_restful import Resource
from models.carter import CartersModel

class Carter(Resource):
    def get(self):
        return CartersModel.json()