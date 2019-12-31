from app import app
from db import db

db.init_app(app)

# Use decorator to perform action before first request into app
@app.before_first_request
def create_tables():
    db.create_all() # Only creates the tables it sees from the imports
