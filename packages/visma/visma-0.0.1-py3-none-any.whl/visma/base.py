import copy
import os
from pprint import pprint

from marshmallow import Schema, post_load
from marshmallow.base import FieldABC
from marshmallow.utils import _Missing

from visma.manager import Manager
from visma.utils import is_instance_or_subclass, import_string


class VismaSchema(Schema):
    visma_model = None

    @post_load
    def make_instance(self, data):
        pprint(data)
        return self.visma_model(**data)


def _get_fields(attrs, field_class):
    fields = [
        (field_name, field_value)
        for field_name, field_value in attrs.items()
        if is_instance_or_subclass(field_value, field_class)
    ]

    return fields


class VismaModelMeta(type):
    """Base metaclass for all VismaModels"""

    def __new__(mcs, name, bases, attrs):

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        parents = [b for b in bases if isinstance(b, VismaModelMeta)]
        if not parents:
            return super().__new__(mcs, name, bases, attrs)

        schema_attrs = _get_fields(attrs, FieldABC)
        # print(f'All attrs: {attrs}')

        # print(f'Schema attrs: {schema_attrs}')

        new_attrs = attrs
        # TODO: add meta data

        new_class = super().__new__(mcs, name, bases, new_attrs)
        schema_name = name + 'Schema'
        schema_dict = dict(schema_attrs)
        new_class._schema_items = dict(schema_attrs)
        schema_dict['visma_model'] = new_class

        schema_klass = type(schema_name, (VismaSchema,), schema_dict)

        attr_meta = attrs.pop('Meta', None)
        meta = attr_meta or getattr(new_class, 'Meta', None)
        try:
            endpoint = getattr(meta, 'endpoint')
            manager = Manager()
            manager.register_model(new_class, 'objects')
            manager.endpoint = endpoint
            manager.register_schema(schema_klass)
            api_klass_path = os.environ.get('VISMA_API_CLASS',
                                            default='visma.api.VismaAPI')
            api_klass = import_string(api_klass_path)
            manager.api = api_klass.load()
            new_class.objects = manager

        except AttributeError:
            pass

        return new_class


class VismaModel(metaclass=VismaModelMeta):
    id = None

    def __init__(self, *args, **kwargs):
        self.schema_fields = copy.deepcopy(self._schema_items)
        # TODO: go throuhg and create all items and fill them with data.

        # There is two ways to create the object. Either directly suing
        # ModelName(etc) or we get a new object from the APIs serializer. Both
        # will call the __init__() with a couple of kwargs. The first initializer
        # might not have all values. but the seiralizer will. So first thing
        # should be to set all values to None and then update them with the kwargs.

        # If we write a function for updating the fields it could be reused after
        # we post things to the API and get back new info. Like id etc. The
        # serializer would then retun a new object and we should go through
        # that object and update the fileds on the current object. Marshmallow
        # do this so we can get ideas there

        self._init_fields(kwargs=kwargs)

        # TODO: As of now we are just using the marshmallow fields. We would
        # want to be sure when we are creating an object from scratch that we
        # have all the necessary data to be able to create it.  We can do this by
        # checking if all fields exept the load only has been filled. And alos
        # check if allow_none is on the field.

    def _init_fields(self, kwargs=None):

        for field_name, field_value in self.schema_fields.items():
            try:
                value = kwargs[field_name]
            except KeyError:
                value = field_value.default
                if is_instance_or_subclass(value, _Missing):
                    value = None

            allow_none = field_value.allow_none or field_value.load_only

            if value is None and not allow_none:
                raise AttributeError(
                    f'{self.__class__.__name__} :: {field_name} '
                    f'is not allowed to be None')

            setattr(self, field_name, value)

    def _update_value(self, obj=None):

        if obj is None:
            return

        else:
            for field_name, field_value in self.schema_fields.items():
                value = getattr(obj, field_name)
                setattr(self, field_name, value)

    def save(self):

        if self.id is None:
            # create a new model
            print('Saving data')
            updated_obj = self.objects.create(self)
            self._update_value(obj=updated_obj)

        else:
            # update model
            print('Updating object')
            self.objects.update(self)

    def delete(self):
        print('Deleting object ')
        self.objects.delete(self.id)

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self)

    def __str__(self):
        return '%s object (%s)' % (self.__class__.__name__, self.id)