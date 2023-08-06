from __future__ import absolute_import

import types as _types

__author__ = 'Michael'

MethodDescriptorType = type(list.append)
SlotWrapperType = type(list.__add__)


class __C1:
    pass


class __C2(object):
    pass


ClassTypes = (type(__C1), type(__C2))


def is_class(obj):
    return isinstance(obj, ClassTypes[0]) or isinstance(obj, ClassTypes[1])


def is_func(obj):
    return isinstance(obj, _types.FunctionType)


def is_method(obj):
    return isinstance(obj, _types.MethodType)


def is_method_descriptor(obj):
    return isinstance(obj, MethodDescriptorType)


def is_slot_wrapper(obj):
    return isinstance(obj, SlotWrapperType)


def is_class_method(obj):
    return is_func(obj) or is_method(obj) \
           or is_method_descriptor(obj) \
           or is_slot_wrapper(obj)


def is_func_or_method(obj):
    return is_func(obj) or is_method(obj)
