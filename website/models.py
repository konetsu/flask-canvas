from . import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    lastpixel_date = db.Column(db.DateTime)
    number_of_pixels = db.Column(db.Integer, default=0)
    pixel_id = db.relationship('Pixel', lazy=True)

class Pixel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    placement_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    placement_ip = db.Column(db.String)
    location_x = db.Column(db.String)
    location_y = db.Column(db.String)
    color = db.Column(db.String)