# -*- coding: utf-8 -*-tdg
from dbms.model.model import Location, Route
from dbms import ma


class LocationSchema(ma.ModelSchema):
    class Meta:
        model = Location
        exclude = ('created_at', 'updated_at', 'dest', 'src')


class RouteSchema(ma.ModelSchema):
    source = ma.Nested(LocationSchema)
    destination = ma.Nested(LocationSchema)
    src = ma.Nested(LocationSchema)
    dest = ma.Nested(LocationSchema)

    class Meta:
        model = Route
        exclude = ('created_at', 'updated_at', 'location_source', 'location_destination')
