from sanic.exceptions import NotFound
from functools import partial

from longitude.models.sql import SQLCRUDModel
from .exceptions import ValidationError


def validate_obj_attr_uniqueness(
    crudmodel: SQLCRUDModel,
    obj_id: int,
    attr_name: str,
    attr_value
):
    try:
        clashed_obj = crudmodel.get(
            columns=['id'],
            sync=True,
            **{
                attr_name: attr_value
            }
        )

        if clashed_obj and clashed_obj['id'] != obj_id:
            raise ValidationError(
                '{} is already used.'.format(attr_name), attr_name
            )
    except NotFound:
        pass


def validate_obj_attr_existence(model, field_name, oid):
    if not model.exists(oid=oid, sync=True):
        raise ValidationError('Object does not exists.', field_name)


def validate_max_length(maxl, x):
    if len(x) > maxl:
        raise ValidationError('length cannot be higher than {}'.format(maxl))


def validate_not_blank(x):
    if not x:
        raise ValidationError('cannot be empty')


def validate_choices_in(choices, x):
    if choices and x not in choices:
        raise ValidationError('value {} not in available choices'.format(x))


def validate_min_value(minv, x):
    if x < minv:
        raise ValidationError('value must be higher than {}'.format(minv))


max_length = lambda maxl: partial(validate_max_length, maxl)
not_blank = validate_not_blank
choices_in = lambda choices: partial(validate_choices_in, choices)
min_value = lambda minv: partial(validate_min_value, minv)


def combine_validations(*validators):
    def combined_validator(x):
        valid = True

        for validate in validators:
            ret = validate(x)
            valid = valid and (ret is None or ret)

        return valid

    return combined_validator
