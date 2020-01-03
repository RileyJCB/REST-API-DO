#import sqlite3
from db import db

class ItemModel(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    price = db.Column(db.Float(precision=2))

    # Link the items to the store and vice versus
    # Blocks deleting the store if it has active foreign key references
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))
    store = db.relationship('StoreModel')
    # Also do a back reference in StoreModel


    def __init__(self, name, price, store_id):
        self.name = name
        self.price = price
        self.store_id = store_id

    def json(self):
        return {
            'id': self.id, 
            'name': self.name, 
            'price': self.price, 
            'store_id': self.store_id
        }

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()
        #return ItemModel.query.filter_by(name=name).first()
        '''
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM items WHERE name=?"
        print(query, name)
        result = cursor.execute(query, (name,))
        row = result.fetchone()
        connection.close()
        if row: # All of the below are the same...
            #return {'item': {'name': row[0], 'price': row[1]}}
            #return cls(row[0], row[1])
            return cls(*row)
        return None
        '''

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self):
#    def insert_item(self):
        db.session.add(self)
        db.session.commit()
        '''
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "INSERT INTO items VALUES (?, ?)"
        print("insert_item({}, {})".format(self.name, self.price))
        cursor.execute(query, (self.name, self.price))
        connection.commit()
        connection.close()
        '''

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
    '''
    def update_item(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "UPDATE items SET price=? WHERE name=?"
        cursor.execute(query, (self.price, self.name))

        connection.commit()
        connection.close()
    '''
