from models import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text)
    phone_number = db.Column(db.Text, nullable=False)
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __init__(self, name, password, phone_number):
        self.name = name
        self.password = password
        self.phone_number = phone_number