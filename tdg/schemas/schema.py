# -*- coding: utf-8 -*-tdg
from tdg.model.model import Location,Route
from tdg import ma
from tdg.schemas import safe_execute



class LocationSchema(ma.ModelSchema):


    class Meta:
        model = Location
        # fields = ('name', "state")
        exclude = ('created_at', 'updated_at', 'destination', 'source')


class RouteSchema(ma.ModelSchema):
    source = ma.Nested(LocationSchema)
    destination = ma.Nested(LocationSchema)
    src=ma.Nested(LocationSchema)
    dest=ma.Nested(LocationSchema)
    class Meta:
        model = Route
        # fields = ('cab_from', 'cab_to', 'our_price', 'market_price', 'car_name', 'car_category')
        exclude = ('created_at', 'updated_at', 'id','location_source','location_destination')