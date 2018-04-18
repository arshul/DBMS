# -*- coding: utf-8 -*-
from dbms import app
from dbms.api.api import add_location, add_pricing,edit_pricing
from dbms.model.model import Route, Location
from dbms.schemas.schema import RouteSchema, LocationSchema
from flask import request, jsonify, render_template


@app.route("/home")
def pricing_data():
    return render_template("pricing.html")


@app.route('/api/v1/route', methods=['GET', 'POST','PUT'])
def pricing():
    if request.method == 'POST':
        data = request.get_json()
        print(data)
        resp = add_pricing(data)
        return resp
    elif request.method=="GET":
        args = request.args.to_dict()
        if args.get('cab_category') == 'false' or args.get('cab_category') == 'null':
            args.pop('cab_category')
        data = Route.query.filter_by(**args).all()
        data = RouteSchema(many=True).dump(data).data
        response = jsonify({"result": data})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    else:
        data = request.get_json()
        print(data)
        resp = edit_pricing(data)
        return resp


@app.route('/api/v1/route/<int:id>', methods=['DELETE'])
def delete_route(id):
    r = Route.query.filter_by(id=id).first()
    if not r:
        return jsonify({'result': {}, "message": "Not Found", 'error': True}), 404
    r.delete()
    Route.update_db()
    return jsonify({'result': {}, "message": "Deleted", 'error': True}), 204


@app.route('/api/v1/destination', methods=['GET'])
def return_route():
    source = request.args.get('source_id')
    if source:
        transport = Route.query.distinct(Route.destination_id).filter_by(source_id=source).all()
        result = RouteSchema(many=True, exclude=('src', )).dump(transport)
        return jsonify({'result': result.data, 'message': "Success", 'error': False})
    else:
        transport = Route.query.distinct(Route.source_id).all()
        results = RouteSchema(many=True, exclude=('dest',)).dump(transport)
        return jsonify({'result': results.data, 'message': "Success", 'error': False})


@app.route("/api/v1/location", methods=['GET', 'POST'])
def location():
    if request.method == 'POST':
        data = request.get_json()
        resp = add_location(data)
        return resp
    else:
        args = request.args.to_dict()
        data = Location.query.filter_by(**args).all()
        if data:
            data = LocationSchema(many=True).dump(data).data
            response = jsonify({"result": data})

        else:
            response = jsonify({"result": "NOT FOUND"})
        response.headers.add('Access-Control-Allow-Origin','*')
        return response



