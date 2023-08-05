# -*- coding: utf-8 -*-
""" Serafin integration with SQLAlchemy. """
from __future__ import absolute_import, unicode_literals

# 3rd party imports
from . import serialize
from .core import serialize

# local imports
from . import util


def make_serializer(model_base_class):
    """ Create serialize for the given SQLAlchemy base model class.

    This is the class you get by calling SQLAlchemy's declarative_base()
    """
    @serialize.type(model_base_class)
    def serialize_flask_model(obj, spec, ctx):
        """ serafin serializer for ndb models. """
        if spec is True or spec.empty():
            return {}

        data = _serialize_flask_model_fields(obj, spec, ctx)

        props = list(util.iter_public_props(obj, lambda n, v: n in spec))
        data.update({
            name: serialize.raw(value, spec[name], ctx)
            for name, value in props
        })

        return data

    return serialize_flask_model


def _serialize_flask_model_fields(model, spec, ctx):
    """ Serialize SQLAlchemy model class fields. """
    ret = {}

    columns = model.__table__.columns.items()

    for name, _ in columns:
        if name in spec:
            value = getattr(model, name)
            ret[name] = serialize.raw(value, spec[name], ctx)

    return ret
