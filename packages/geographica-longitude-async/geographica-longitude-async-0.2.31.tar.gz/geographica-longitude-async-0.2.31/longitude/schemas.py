from marshmallow import Schema, fields, validates_schema
from .validators import validate_obj_attr_uniqueness, validate_obj_attr_existence


def bind_uniqueness_schema_validator(schema, field_name):

    def validate(self, data):
        if getattr(self, 'model', None) is None:
            raise RuntimeError('To bind a uniqueness validator, please pass a model to the schema.')

        field_value = data.get(field_name, None)
        obj_id = data.get('id', None)

        if field_value is not None:
            validate_obj_attr_uniqueness(self.model, obj_id, field_name, field_value)

    validator = validates_schema(validate)
    validator_name = '_validate_{}_uniqueness'.format(field_name)
    _add_processor_to_schema(schema, validator_name, validator)


def bind_fkexists_schema_validator(schema, field_name, foreign_model_class):

    def validate(self, data):
        if getattr(self, 'model', None) is None:
            raise RuntimeError('To bind a fkexists validator, please pass a model to the schema.')

        fk = data.get(field_name, None)

        foreign_model = foreign_model_class(self.model.db_model)

        if fk is not None:
            validate_obj_attr_existence(foreign_model, field_name, fk)

    validator = validates_schema(validate)
    validator_name = '_validate_{}_fkexists'.format(field_name)
    _add_processor_to_schema(schema, validator_name, validator)


def _add_processor_to_schema(schema, name, fn):
    setattr(schema, name, fn)
    for tag in fn.__marshmallow_tags__:
        schema.__processors__[tag].insert(0, name)


class ModelSchema(Schema):

    id = fields.Integer(
        required=False
    )

    def __init__(self, model=None, **kwargs):
        super().__init__(**kwargs)
        self.model = model
