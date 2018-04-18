# -*- coding: utf-8 -*-
from dbms.model.model import Route, Location
from flask import jsonify


def add_pricing(data):
    source = Location.query.filter_by(name=data.get('source')).first()
    if source:
        data['source_id'] = source.id

    else:
        add_location({"name": data.get('source')})
        data['source_id'] = Location.query.filter_by(name=data.get('source')).first().id
    dest = Location.query.filter_by(name=data.get('destination')).first()
    if dest:
        data['destination_id'] = dest.id
    else:
        add_location({"name": data.get('destination')})
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


def edit_pricing(data):
    try:
        db_obj = Route.query.filter_by(id=data.get('id')).first()
        if db_obj.source.name is not data.get('source').get('name'):
            update_loc(db_obj.source.name, data.get('source').get('name'))
        if db_obj.destination.name is not data.get('destination').get('name'):
            update_loc(db_obj.destination.name, data.get('destination').get('name'))
        if db_obj.price is not data.get('price'):
            Route.query.filter_by(id=data.get('id')).update({'price': int(data.get('price'))})
            Route.update_db()
        return jsonify({'message':'updated'})
    except Exception:
        import traceback
        return jsonify({'message': traceback.print_exc()})


def update_loc(from_name, to_name):
    Location.query.filter_by(name=from_name).update({'name': to_name})


def add_location(data):
    query = Location.query.filter_by(**data).first()
    if not query:
        Location(**data).save()
        return jsonify({'message': 'Location added'})
    else:
        return jsonify({'message': 'Location already present'})
