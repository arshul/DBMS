# -*- coding: utf-8 -*-
from tdg.model.model import Route, Location
from flask import jsonify


def add_pricing(data):
    print("in api")
    source = Location.query.filter_by(name=data.get('source')).first()
    if source:
        data['source_id'] = source.id
        
    else:
        add_location({"name" : data.get('source')})
        data['source_id'] = Location.query.filter_by(name=data.get('source')).first().id
    dest = Location.query.filter_by(name=data.get('destination')).first()
    if dest:
        data['destination_id'] = dest.id
    else:
        add_location({"name" : data.get('destination')})
        data['destination_id'] = Location.query.filter_by(name=data.get('destination')).first().id
    data.pop('source')
    data.pop('destination')
    for cab_type in data.get('price'):
        obj = Route(**{
            "source_id": data['source_id'],
            "destination_id": data['destination_id'],
            "cab_category": cab_type,
            "price": data.get('price')[cab_type]
        })
        obj.save()
    return jsonify({'message': 'Pricing added'})

def add_location(data):
    query = Location.query.filter_by(**data).first()
    if not query:
        Location(**data).save()
        return jsonify({'message': 'Location added'})
    else:
        return jsonify({'message': 'Location already present'})

