# -*- coding: utf-8 -*-

from .base import is_expression, EvaluateValueDef


def eval_value_expression_in_dict(d, variables=None, container=None, deep=True):
    for k, v in d.items():
        if is_expression(v):
            d[k] = EvaluateValueDef(v).get_actual_value(container, variables)
        elif isinstance(v, (list, tuple)) and deep:
            d[k] = eval_value_expression_in_list(v, variables, container, deep)
        elif isinstance(v, dict) and deep:
            d[k] = eval_value_expression_in_dict(v, variables, container, deep)
        else:
            d[k] = v
    return d


def eval_value_expression_in_list(l, variables=None, container=None, deep=True):
    for i, v in enumerate(l):
        if is_expression(v):
            l[i] = EvaluateValueDef(v).get_actual_value(container, variables)
        elif isinstance(v, (list, tuple)) and deep:
            l[i] = eval_value_expression_in_list(v, variables, container, deep)
        elif isinstance(v, dict) and deep:
            l[i] = eval_value_expression_in_dict(v, variables, container, deep)
        else:
            l[i] = v
    return l
