
from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    jwt_required, 
    get_jwt_claims, 
    jwt_optional, 
    get_jwt_identity,
    fresh_jwt_required
)
from models.item import ItemModel

# The api works with resources and every resource has to be a class
# FLASKrestful automatically handles jsonify.
class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
      type=float,
      required=True,
      help="This price field cannot be left blank!"
    )
    parser.add_argument('store_id',
      type=int,
      required=True,
      help="Every item must be assigned to a store id!"
    )

    @jwt_required
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {'message': 'Item {} not found'.format(name)}, 404

    @fresh_jwt_required
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': "An item with name '{}' already exists".format(name)}, 400

        data = Item.parser.parse_args()
        #item = ItemModel(name, data['price'], data['store_id'])
        item = ItemModel(name, **data)
        try:
            #item.insert_item()
            item.save_to_db()
        except:
            return {"message": "Error adding item {} to database.".format(name)}, 500  # Internal Server Error

        return item.json(), 201

    @jwt_required
    def delete(self, name):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Admin privilege is required.'}, 401

        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
        return {'message': 'Item {} was deleted'.format(name)}, 201

    # PUT is an Idempotent method whick add_resource
    # guaranteed to always return the same result when called with the same arguments
    # So put can both create and update an item
    def put(self, name):
        data = Item.parser.parse_args()
        #item = ItemModel(name, data['price'])
        item = ItemModel.find_by_name(name)

        if item is None:
            #item = ItemModel(name, data['price'], data['store_id'])
            item = ItemModel(name, **data)
        else:
            item.price = data['price']
        item.save_to_db()
        return item.json()

class ItemList(Resource):
    @jwt_optional
    def get(self):
        user_id = get_jwt_identity()
        items = [item.json() for item in ItemModel.find_all()]
        if user_id:
            return {'items': items}, 200
        return {
            'items': [item['name'] for item in items],
            'message': 'Login for more data.'
            }, 200
    
