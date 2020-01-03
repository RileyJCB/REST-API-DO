
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
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

    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {'message': 'Item {} not found'.format(name)}, 404

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

    @jwt_required()
    def delete(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()

        '''
        if not ItemModel.find_by_name(name):
            return {'message': "No item by name '{}' exists".format(name)}, 400

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "DELETE FROM items WHERE name=?"
        cursor.execute(query, (name,))

        connection.commit()
        connection.close()
        '''
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
        '''
        if ItemModel.find_by_name(name): # Update item
            try:
                item.update_item()
                return {'message': 'update', 'item': item.json()}
            except:
                return {"message": "Error updating item {} in database.".format(name)}, 500  # Internal Server Error
        else:                       # Create/add item
            try:
                item.insert_item()
                return {'message': 'create', 'item': item.json()}
            except:
                return {"message": "Error adding item {} to database.".format(name)}, 500  # Internal Server Error
        '''

class ItemList(Resource):
    def get(self):
        # Pythonic approach with list comprehension
        #return {'items': [item.json() for item in ItemModel.query.all()]}
        return {'items': [item.json() for item in ItemModel.find_all()]}
        # or using map and lambda if using Javascript may want to list map
        # return {'items': list(map(lambda x: x.json(), ItemModel.query.all()))}
        '''
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM items"
        result = cursor.execute(query)
        items = result.fetchall()
        connection.close()
        if items:
            return {'items': [{'name': n, 'price': p} for i, n, p in items]}
        return {'message': 'No items in database!'}
        '''
