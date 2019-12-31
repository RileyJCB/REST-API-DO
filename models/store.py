from db import db

class StoreModel(db.Model):
    __tablename__ = 'stores'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    # Back reference to ItemModel
    #items = db.relationship('ItemModel') # List of item models, unique items by store, expensive at creation
    items = db.relationship('ItemModel', lazy='dynamic') # List of item models, non-unique

    def __init__(self, name):
        self.name = name

    def json(self):
        #return {'name': self.name}
        #return {'name': self.name, 'items': [item.json() for item in self.items]} # Faster response
        return {'name': self.name, 'id': self.id, 'items': [item.json() for item in self.items.all()]} # Slower as query builder of items table

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
