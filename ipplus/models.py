import base64
from itertools import chain

from django.db.models import BinaryField, CharField
from django.db.models.fields.files import ImageField


def model_to_dict(instance, fields=None, exclude=None):
    """
    Returns a dict containing the data in ``instance`` suitable for passing as a Form's ``initial`` keyword argument.

    ``fields`` is an optional list of field names. If provided, only the named
    fields will be included in the returned dict.

    ``exclude`` is an optional list of field names. If provided, the named
    fields will be excluded from the returned dict, even if they are listed in
    the ``fields`` argument.
    """
    from django.db import models
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
        if fields and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue

        if isinstance(f, models.ForeignKey):
            data[f'{f.name}_id'] = f.value_from_object(instance)
        elif isinstance(f, ImageField):
            data[f.name] = str(f.value_from_object(instance))
        elif isinstance(f, BinaryField):
            data[f.name] = base64.b64encode(f.value_from_object(instance)).decode()
        else:
            data[f.name] = f.value_from_object(instance)

        # Evaluate ManyToManyField QuerySets to prevent subsequent model
        # alteration of that field from being reflected in the data.
        if isinstance(f, models.ManyToManyField):
            data[f.name] = list(data[f.name])
            if instance.pk is None:
                data[f.name] = []
            else:
                data[f.name] = list(f.value_from_object(instance).values_list('pk', flat=True))

    return data


class VirtualField(CharField):
    """See i2p/migrations/0011_create_json_virtual_column.py"""

    description = "A virtual field"

    def get_internal_type(self):
        return "VirtualField"
