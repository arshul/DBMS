# -*- coding: utf-8 -*-
from tdg.model.model import Route, Location
from flask import jsonify


def add_pricing(data):
    query = Route.query.filter_by(**data).first()
    if not query:
        Route(**data).save()
        return jsonify({'message': 'Pricing added'})
    else:
        return jsonify({'message': 'Pricing already present'})


def add_location(data):
    query = Location.query.filter_by(**data).first()
    if not query:
        Location(**data).save()
        return jsonify({'message': 'Location added'})
    else:
        return jsonify({'message': 'Location already present'})

