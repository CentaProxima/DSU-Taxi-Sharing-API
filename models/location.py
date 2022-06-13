from models import db
from datetime import datetime

class Location(db.Model):
    __tablename__ = 'loc'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', onupdate='CASCADE'), nullable=False)
    location = db.Column(db.Text, nullable=False)
    dest = db.Column(db.Text, nullable=False)
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __init__(self, user_id, location, dest):
        self.user_id = user_id
        self.location = location
        self.dest = dest