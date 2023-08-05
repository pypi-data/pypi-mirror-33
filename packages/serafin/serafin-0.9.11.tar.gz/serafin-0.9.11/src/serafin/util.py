# -*- coding: utf-8 -*-
""" Various helpers used by the serialization library. """
from __future__ import absolute_import, print_function, unicode_literals

# stdlib imports
import types
import inspect

# 3rd party imports
from six import string_types


def iterable(collection):
    """Checks if the variable is not a basestring instance and can be
    enumerated.
    """
    # strings can be iterated - that's not what we want
    if isinstance(collection, string_types):
        return False

    # avoid opening a generator
    if isinstance(collection, types.GeneratorType):
        return True

    try:
        iter(collection)
    except TypeError:
        return False

    return True


def is_file(obj):
    """ Check if the given object is file-like. """
    return hasattr(obj, 'flush') and hasattr(obj, 'readline')


def iter_public_props(obj, predicate=None):
    """ Iterate over public properties of an object.

    :param Any obj:
        The object we want to get the properties of.
    :param function predicate:
        Additional predicate to filter out properties we're interested in. This
        function will be called on every property of the object with the
        property name and value as it arguments. If it returns True, the
        property will be yielded by this generator.
    """
    predicate = predicate or (lambda n, v: True)
    obj_type = type(obj)

    if inspect.isclass(obj):
        # This is a class
        for name, value in obj.__dict__.items():
            if isinstance(value, property):
                yield name, value
    else:
        # This is an instance
        for name in dir(obj):
            if name.startswith('_'):
                continue

            member = getattr(obj_type, name)
            if not isinstance(member, property):
                continue

            try:
                value = getattr(obj, name)
                if predicate(name, value):
                    yield name, value
            except AttributeError:
                pass
