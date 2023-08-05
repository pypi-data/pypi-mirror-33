# -*- coding: utf-8 -*-
""" Serafin integration with django ORM. """
from __future__ import absolute_import, unicode_literals

# 3rd party imports
from django.db.models import Model

# local imports
from . import serialize
from . import util


@serialize.type(Model)
def serialize_django_model(obj, spec, ctx):
    """ serafin serializer for django Model instances. """
    if spec is True or spec.empty():
        return {}

    data = serialize_model_fields(obj, spec, ctx)

    props = list(util.iter_public_props(obj, lambda n, v: n in spec))
    data.update({
        name: serialize.raw(value, spec[name], ctx)
        for name, value in props
    })

    return data


def serialize_model_fields(model, fieldspec, context):
    """ Serialize django Model fields

    :param DjangoModel model:
        The model we want to serialize.
    :param Fieldspec fieldspec:
        Defines what fields will be included in the result.
    :param dict context:
        Serialization context. For more information, refer to **serafin**
        documentation.
    :return dict:
        A dictionary containing the serialized data. The layout of the
        dictionary will depend on the fieldspec passed.
    """
    model_fields = [f for f in model._meta.get_fields() if f.name in fieldspec]

    data = {}
    for field in model_fields:
        name = field.name
        value = getattr(model, name)

        if field.is_relation:
            if field.one_to_many:
                rel_spec = fieldspec[name]

                if rel_spec is True or rel_spec.empty():
                    data[name] = []
                else:
                    data[name] = serialize.raw(value.all(), rel_spec, context)
            elif field.many_to_one:
                data[name] = serialize_django_model(
                    value, fieldspec[name], context
                )
            else:
                pass
        else:
            data[name] = value

    return data
