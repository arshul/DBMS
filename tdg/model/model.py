# -*- coding: utf-8 -*-
from tdg import db
from tdg.model.base import Base


class Location(Base):
    __tablename__ = 'location'
    name = db.Column(db.String(100), nullable=False)
    src = db.relationship("Route", foreign_keys="[Route.source_id]", backref='location_source')
    dest = db.relationship("Route", foreign_keys="[Route.destination_id]", backref='location_destination')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return "<{}>".format(self.title)


class Route(Base):
    __tablename__ = 'route'
    price = db.Column(db.Integer)
    cab_category = db.Column(db.String(20))
    source_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    source = db.relationship("Location", foreign_keys=source_id)
    destination = db.relationship("Location", foreign_keys=destination_id)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return "<{}>".format(self.price)





