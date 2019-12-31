from flask_restful import Resource
from models.store import StoreModel

class Store(Resource):
    def get(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json() # The default is 200, so not needed
        return {"message": 'Store: {} not found in database'.format(name)}, 404

    def post(self, name):
        if StoreModel.find_by_name(name):
            return {"message": 'Store: {} already exists in database'.format(name)}, 400
        store = StoreModel(name)
        try:
            store.save_to_db()
        except:
            return {"message": "Error adding store {} to database.".format(name)}, 500  # Internal Server Error

        return store.json(), 201

    def delete(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()
        return {"message": "Store: {} was deleted".format(name)}

class StoreList(Resource):
    def get(self):
        return {'stores': [store.json() for store in StoreModel.query.all()]}
