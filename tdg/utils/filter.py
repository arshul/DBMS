# -*- coding: utf-8 -*-
__author__ = 'himanshujain.2792'


def ret_filter(x, q, filter_key, filter_value, model_obj):
    return {
        '=': q.filter(getattr(model_obj, filter_key) == filter_value),
        '<': q.filter(getattr(model_obj, filter_key) < filter_value),
        '>': q.filter(getattr(model_obj, filter_key) > filter_value),
        '<=': q.filter(getattr(model_obj, filter_key) <= filter_value),
        '>=': q.filter(getattr(model_obj, filter_key) >= filter_value),
        '!=': q.filter(getattr(model_obj, filter_key) != filter_value),
    }[x]

